"""Model-candidate and deterministic proposal construction behind typed contracts."""

import json
from dataclasses import dataclass
from hashlib import sha256
from typing import Protocol, override

from pydantic import ValidationError

from onprem_agentic_mas.contracts import (
    ActionProposal,
    CaseRequest,
    ProposalCandidate,
    VerifiedEvidence,
)
from onprem_agentic_mas.local_model import (
    ChatRole,
    LocalChatMessage,
    LocalModelTransportError,
    LocalOpenAICompatibleClient,
)

_LOCAL_MODEL_UNAVAILABLE = "local_model_unavailable"
_LOCAL_MODEL_CANDIDATE_INVALID = "local_model_candidate_invalid"
_PROPOSAL_ACTION_TYPE_MISMATCH = "proposal_action_type_mismatch"


class ProposalGenerator(Protocol):
    """Create a candidate only; the workflow owns policy and all side effects."""

    def generate(
        self,
        request: CaseRequest,
        evidence: tuple[VerifiedEvidence, ...],
    ) -> ProposalCandidate:
        """Return a structured candidate from trusted context."""
        ...


@dataclass(frozen=True, slots=True)
class ProposalGenerationError(RuntimeError):
    """Raised when a proposal candidate cannot meet its typed contract."""

    reason: str

    @override
    def __str__(self) -> str:
        """Return the safe operator-visible failure reason."""
        return self.reason


@dataclass(frozen=True, slots=True)
class DeterministicProposalGenerator:
    """Safe default generator used by the no-network demo and unit tests."""

    def generate(
        self,
        request: CaseRequest,
        evidence: tuple[VerifiedEvidence, ...],
    ) -> ProposalCandidate:
        """Create a candidate from the requested allowlisted action only."""
        return ProposalCandidate(
            action_type=request.action_type,
            rationale=f"verified_evidence_count={len(evidence)}",
        )


@dataclass(frozen=True, slots=True)
class LocalModelProposalGenerator:
    """Adapt a local OpenAI-compatible model response into a candidate contract."""

    client: LocalOpenAICompatibleClient

    def generate(
        self,
        request: CaseRequest,
        evidence: tuple[VerifiedEvidence, ...],
    ) -> ProposalCandidate:
        """Ask a local model for JSON and fail closed on malformed output."""
        messages = (
            LocalChatMessage(
                role=ChatRole.SYSTEM,
                content=(
                    "Return only a JSON object with action_type and rationale. "
                    "Do not call tools or execute actions."
                ),
            ),
            LocalChatMessage(
                role=ChatRole.USER,
                content=_candidate_prompt(request, evidence),
            ),
        )
        try:
            response = self.client.complete(messages)
            return ProposalCandidate.model_validate_json(response)
        except LocalModelTransportError as error:
            raise ProposalGenerationError(_LOCAL_MODEL_UNAVAILABLE) from error
        except ValidationError as error:
            raise ProposalGenerationError(_LOCAL_MODEL_CANDIDATE_INVALID) from error


def build_action_proposal(
    request: CaseRequest,
    evidence: tuple[VerifiedEvidence, ...],
    candidate: ProposalCandidate,
    *,
    policy_version: str,
) -> ActionProposal:
    """Bind a candidate to trusted evidence before policy sees the proposal."""
    if candidate.action_type is not request.action_type:
        raise ProposalGenerationError(_PROPOSAL_ACTION_TYPE_MISMATCH)
    proposal_digest = proposal_digest_for(
        request,
        evidence,
        candidate,
        policy_version=policy_version,
    )
    return ActionProposal(
        action_id=f"action:{request.tenant_id}:{request.request_id}",
        action_type=candidate.action_type,
        case_id=request.case_id,
        actor_id=request.actor_id,
        idempotency_key=(
            f"{request.tenant_id}:{request.request_id}:{candidate.action_type.value}"
        ),
        evidence_ids=tuple(item.evidence_id for item in evidence),
        policy_version=policy_version,
        proposal_digest=proposal_digest,
    )


def proposal_digest_for(
    request: CaseRequest,
    evidence: tuple[VerifiedEvidence, ...],
    candidate: ProposalCandidate,
    *,
    policy_version: str,
) -> str:
    """Hash the exact request, model candidate, and verified evidence scope."""
    payload = {
        "request": {
            "request_id": request.request_id,
            "tenant_id": request.tenant_id,
            "actor_id": request.actor_id,
            "case_id": request.case_id,
            "objective": request.objective,
            "action_type": request.action_type.value,
        },
        "candidate": candidate.model_dump(mode="json"),
        "evidence": [
            {
                "evidence_id": item.evidence_id,
                "source_id": item.source_id,
                "source_version": item.source_version,
                "content_sha256": item.content_sha256,
                "source_as_of": item.source_as_of.isoformat(),
                "valid_until": item.valid_until.isoformat(),
            }
            for item in sorted(evidence, key=lambda item: item.evidence_id)
        ],
        "policy_version": policy_version,
    }
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return sha256(serialized.encode()).hexdigest()


def _candidate_prompt(
    request: CaseRequest,
    evidence: tuple[VerifiedEvidence, ...],
) -> str:
    """Create an auditable local-model prompt from trusted records only."""
    payload = {
        "objective": request.objective,
        "requested_action_type": request.action_type.value,
        "evidence": [
            {
                "evidence_id": item.evidence_id,
                "source_id": item.source_id,
                "source_version": item.source_version,
                "excerpt": item.excerpt,
            }
            for item in evidence
        ],
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))
