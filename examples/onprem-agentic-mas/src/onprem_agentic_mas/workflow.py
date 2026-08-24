"""LangGraph orchestration for evidence-verified, policy-authorized work."""

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal, Protocol, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from onprem_agentic_mas.actions import ActionGateway
from onprem_agentic_mas.contracts import (
    ActionProposal,
    ActionReceipt,
    ActionStatus,
    AuthorizedAction,
    CaseRequest,
    PolicyDecision,
    PolicyStatus,
    VerifiedEvidence,
    WorkflowInvariantError,
    WorkflowResult,
)
from onprem_agentic_mas.evidence import EvidenceResolver
from onprem_agentic_mas.memory import MemoryEntry, MemoryStore
from onprem_agentic_mas.policy import PolicyAuthority
from onprem_agentic_mas.proposal import (
    ProposalGenerationError,
    ProposalGenerator,
    build_action_proposal,
)


class Clock(Protocol):
    """Time boundary that keeps graph behavior and expiry checks testable."""

    def now(self) -> datetime:
        """Return the current UTC time."""
        ...


@dataclass(frozen=True, slots=True)
class SystemClock:
    """Production clock implementation for the local reference runtime."""

    def now(self) -> datetime:
        """Return an aware UTC timestamp."""
        return datetime.now(tz=UTC)


@dataclass(frozen=True, slots=True)
class WorkflowDependencies:
    """Explicit ports used by graph nodes instead of direct infrastructure access."""

    memory: MemoryStore
    actions: ActionGateway
    evidence: EvidenceResolver
    proposals: ProposalGenerator
    policy: PolicyAuthority
    clock: Clock


class WorkflowState(TypedDict):
    """State passed between specialized graph nodes."""

    request: CaseRequest
    recalled_memory: tuple[MemoryEntry, ...]
    verified_evidence: tuple[VerifiedEvidence, ...]
    proposal: ActionProposal | None
    proposal_error: str | None
    decision: PolicyDecision | None
    authorized_action: AuthorizedAction | None
    receipt: ActionReceipt | None
    result: WorkflowResult | None


class ProposalUpdate(TypedDict):
    """State written by the candidate-generation graph node."""

    proposal: ActionProposal | None
    proposal_error: str | None


class PolicyUpdate(TypedDict):
    """State written by the deterministic policy graph node."""

    decision: PolicyDecision
    authorized_action: AuthorizedAction | None


type CompiledWorkflow = CompiledStateGraph[
    WorkflowState,
    None,
    WorkflowState,
    WorkflowState,
]


@dataclass(frozen=True, slots=True)
class AgenticSystem:
    """Runnable facade that exposes a typed request/result contract."""

    _graph: CompiledWorkflow

    def run(self, request: CaseRequest) -> WorkflowResult:
        """Run the graph and require its terminal node to produce a result."""
        final_state = self._graph.invoke(
            {
                "request": request,
                "recalled_memory": (),
                "verified_evidence": (),
                "proposal": None,
                "proposal_error": None,
                "decision": None,
                "authorized_action": None,
                "receipt": None,
                "result": None,
            }
        )
        result = final_state["result"]
        if result is None:
            raise WorkflowInvariantError(reason="graph_completed_without_result")
        return result


@dataclass(frozen=True, slots=True)
class _WorkflowNodes:
    """Small graph nodes that share the same explicitly injected dependencies."""

    _dependencies: WorkflowDependencies

    def retrieve_memory(
        self, state: WorkflowState
    ) -> dict[str, tuple[MemoryEntry, ...]]:
        """Recall tenant-scoped operational memory before proposal generation."""
        request = state["request"]
        return {
            "recalled_memory": self._dependencies.memory.search(
                tenant_id=request.tenant_id,
                query=request.objective,
                limit=5,
            )
        }

    def resolve_evidence(
        self, state: WorkflowState
    ) -> dict[str, tuple[VerifiedEvidence, ...]]:
        """Resolve only source-of-record evidence that the requester may access."""
        request = state["request"]
        return {
            "verified_evidence": self._dependencies.evidence.resolve(
                request,
                now=self._dependencies.clock.now(),
            )
        }

    def evidence_agent(self, state: WorkflowState) -> ProposalUpdate:
        """Generate a typed candidate from verified evidence, never an action write."""
        request = state["request"]
        evidence = state["verified_evidence"]
        try:
            candidate = self._dependencies.proposals.generate(request, evidence)
            proposal = build_action_proposal(
                request,
                evidence,
                candidate,
                policy_version=self._dependencies.policy.policy_version,
            )
        except ProposalGenerationError as error:
            return {"proposal": None, "proposal_error": error.reason}
        return {"proposal": proposal, "proposal_error": None}

    def policy_agent(self, state: WorkflowState) -> PolicyUpdate:
        """Apply complete-evidence and approval gates outside the model prompt."""
        request = state["request"]
        evidence = state["verified_evidence"]
        if not request.evidence_ids:
            return _blocked_policy_update("evidence_required")
        if not _has_complete_verified_evidence(request, evidence):
            return _blocked_policy_update("verified_evidence_required")
        proposal_error = state["proposal_error"]
        if proposal_error is not None:
            return _blocked_policy_update(proposal_error)
        proposal = state["proposal"]
        if proposal is None:
            raise WorkflowInvariantError(reason="policy_received_no_proposal")
        decision = self._dependencies.policy.decide(
            request,
            proposal,
            now=self._dependencies.clock.now(),
        )
        return {
            "decision": decision,
            "authorized_action": _authorized_action_for(proposal, decision),
        }

    def route_after_policy(
        self,
        state: WorkflowState,
    ) -> Literal["execute", "record_memory"]:
        """Route only an allowed decision to the isolated action gateway."""
        decision = state["decision"]
        if decision is None:
            raise WorkflowInvariantError(reason="router_received_no_decision")
        match decision.status:
            case PolicyStatus.ALLOWED:
                return "execute"
            case PolicyStatus.BLOCKED | PolicyStatus.PENDING_APPROVAL:
                return "record_memory"

    def execute(self, state: WorkflowState) -> dict[str, ActionReceipt]:
        """Commit only a policy-issued authorization capsule through the action port."""
        action = state["authorized_action"]
        if action is None:
            raise WorkflowInvariantError(reason="execute_received_no_authorized_action")
        return {"receipt": self._dependencies.actions.commit(action)}

    def record_memory(self, state: WorkflowState) -> dict[str, WorkflowResult]:
        """Persist an auditable outcome without storing model chain-of-thought."""
        decision = state["decision"]
        if decision is None:
            raise WorkflowInvariantError(reason="record_received_no_decision")
        recalled_memory_ids = tuple(
            entry.memory_id for entry in state["recalled_memory"]
        )
        result = _result_for_decision(
            decision=decision,
            receipt=state["receipt"],
            recalled_memory_ids=recalled_memory_ids,
        )
        request = state["request"]
        self._dependencies.memory.record(
            MemoryEntry(
                memory_id=f"{request.tenant_id}:{request.request_id}:outcome",
                tenant_id=request.tenant_id,
                case_id=request.case_id,
                summary=request.objective,
                outcome=result.status.value,
                recorded_at=self._dependencies.clock.now(),
            )
        )
        return {"result": result}


def _has_complete_verified_evidence(
    request: CaseRequest,
    evidence: tuple[VerifiedEvidence, ...],
) -> bool:
    """Require exactly one verified source record for every requested evidence ID."""
    requested_ids = frozenset(request.evidence_ids)
    resolved_ids = frozenset(item.evidence_id for item in evidence)
    return (
        len(requested_ids) == len(request.evidence_ids)
        and requested_ids == resolved_ids
    )


def _blocked_policy_update(reason: str) -> PolicyUpdate:
    """Return the single fail-closed update shared by all pre-policy failures."""
    return {
        "decision": PolicyDecision(status=PolicyStatus.BLOCKED, reason=reason),
        "authorized_action": None,
    }


def _authorized_action_for(
    proposal: ActionProposal,
    decision: PolicyDecision,
) -> AuthorizedAction | None:
    """Create the only type accepted by the action gateway after an allow decision."""
    if decision.status is not PolicyStatus.ALLOWED:
        return None
    return AuthorizedAction(
        action_id=proposal.action_id,
        action_type=proposal.action_type,
        case_id=proposal.case_id,
        actor_id=proposal.actor_id,
        idempotency_key=proposal.idempotency_key,
        evidence_ids=proposal.evidence_ids,
        policy_version=proposal.policy_version,
        proposal_digest=proposal.proposal_digest,
        approval_id=decision.approval_id,
    )


def _result_for_decision(
    decision: PolicyDecision,
    receipt: ActionReceipt | None,
    recalled_memory_ids: tuple[str, ...],
) -> WorkflowResult:
    """Map every policy status to an observable, non-chain-of-thought result."""
    match decision.status:
        case PolicyStatus.BLOCKED:
            return WorkflowResult(
                status=ActionStatus.BLOCKED,
                reason=decision.reason,
                recalled_memory_ids=recalled_memory_ids,
                action_receipt=None,
            )
        case PolicyStatus.PENDING_APPROVAL:
            return WorkflowResult(
                status=ActionStatus.PENDING_APPROVAL,
                reason=decision.reason,
                recalled_memory_ids=recalled_memory_ids,
                action_receipt=None,
            )
        case PolicyStatus.ALLOWED:
            if receipt is None:
                raise WorkflowInvariantError(reason="allowed_action_has_no_receipt")
            return WorkflowResult(
                status=ActionStatus.COMMITTED,
                reason=decision.reason,
                recalled_memory_ids=recalled_memory_ids,
                action_receipt=receipt,
            )


def build_system(
    memory: MemoryStore,
    actions: ActionGateway,
    evidence: EvidenceResolver,
    proposals: ProposalGenerator,
    policy: PolicyAuthority,
) -> AgenticSystem:
    """Compose the graph with explicit storage, model, policy, and action ports."""
    nodes = _WorkflowNodes(
        _dependencies=WorkflowDependencies(
            memory=memory,
            actions=actions,
            evidence=evidence,
            proposals=proposals,
            policy=policy,
            clock=SystemClock(),
        )
    )
    graph = (
        StateGraph[WorkflowState, None, WorkflowState, WorkflowState](
            state_schema=WorkflowState
        )
        .add_node("retrieve_memory", nodes.retrieve_memory)
        .add_node("resolve_evidence", nodes.resolve_evidence)
        .add_node("evidence_agent", nodes.evidence_agent)
        .add_node("policy_agent", nodes.policy_agent)
        .add_node("execute", nodes.execute)
        .add_node("record_memory", nodes.record_memory)
        .add_edge(START, "retrieve_memory")
        .add_edge("retrieve_memory", "resolve_evidence")
        .add_edge("resolve_evidence", "evidence_agent")
        .add_edge("evidence_agent", "policy_agent")
        .add_conditional_edges("policy_agent", nodes.route_after_policy)
        .add_edge("execute", "record_memory")
        .add_edge("record_memory", END)
    )
    return AgenticSystem(_graph=graph.compile())
