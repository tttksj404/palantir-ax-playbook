from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from onprem_agentic_mas.actions import (
    ActionAuthorizationError,
    ActionIdempotencyConflictError,
    InMemoryActionGateway,
)
from onprem_agentic_mas.contracts import (
    ActionStatus,
    ActionType,
    AuthorizedAction,
    CaseRequest,
    RiskLevel,
    VerifiedApproval,
    VerifiedEvidence,
)
from onprem_agentic_mas.evidence import InMemoryEvidenceResolver
from onprem_agentic_mas.memory import InMemoryMemoryStore
from onprem_agentic_mas.policy import StaticPolicyAuthority
from onprem_agentic_mas.proposal import (
    DeterministicProposalGenerator,
    build_action_proposal,
    proposal_digest_for,
)
from onprem_agentic_mas.workflow import AgenticSystem, build_system

_FAR_FUTURE = datetime(2099, 1, 1, tzinfo=UTC)


def _request(
    *,
    evidence_ids: tuple[str, ...] = ("evidence-1",),
    objective: str = "Create a review task from the supplied evidence.",
) -> CaseRequest:
    return CaseRequest(
        request_id="request-001",
        tenant_id="tenant-a",
        actor_id="reviewer-7",
        case_id="case-42",
        objective=objective,
        action_type=ActionType.CREATE_REVIEW_TASK,
        evidence_ids=evidence_ids,
    )


def _evidence(**changes: object) -> VerifiedEvidence:
    payload: dict[str, object] = {
        "evidence_id": "evidence-1",
        "tenant_id": "tenant-a",
        "case_id": "case-42",
        "source_id": "source-1",
        "source_version": "source-v1",
        "content_sha256": "a" * 64,
        "excerpt": "The source establishes the review condition.",
        "source_as_of": datetime(2026, 8, 24, tzinfo=UTC),
        "valid_until": _FAR_FUTURE,
        "authorized_actor_ids": ("reviewer-7",),
    }
    payload.update(changes)
    return VerifiedEvidence.model_validate(payload)


def _approval(
    request: CaseRequest,
    evidence: tuple[VerifiedEvidence, ...],
    **changes: object,
) -> VerifiedApproval:
    candidate = DeterministicProposalGenerator().generate(request, evidence)
    payload: dict[str, object] = {
        "approval_id": "approval-001",
        "tenant_id": request.tenant_id,
        "case_id": request.case_id,
        "request_id": request.request_id,
        "action_type": request.action_type,
        "policy_version": "policy-v1",
        "proposal_digest": proposal_digest_for(
            request,
            evidence,
            candidate,
            policy_version="policy-v1",
        ),
        "approved_by": "approver-9",
        "approved_at": datetime(2026, 8, 24, tzinfo=UTC),
        "valid_until": _FAR_FUTURE,
    }
    payload.update(changes)
    return VerifiedApproval.model_validate(payload)


def _system(
    actions: InMemoryActionGateway,
    *,
    evidence: tuple[VerifiedEvidence, ...] = (),
    risk: RiskLevel = RiskLevel.HIGH,
    approvals: tuple[VerifiedApproval, ...] = (),
) -> AgenticSystem:
    return build_system(
        memory=InMemoryMemoryStore(),
        actions=actions,
        evidence=InMemoryEvidenceResolver(records=evidence),
        proposals=DeterministicProposalGenerator(),
        policy=StaticPolicyAuthority(
            risk_by_action={ActionType.CREATE_REVIEW_TASK: risk},
            verified_approvals=approvals,
        ),
    )


def test_workflow_blocks_action_when_evidence_is_missing() -> None:
    """No requested evidence must fail before model, policy, or action execution."""
    actions = InMemoryActionGateway()
    result = _system(actions).run(_request(evidence_ids=()))

    assert result.status is ActionStatus.BLOCKED
    assert result.reason == "evidence_required"
    assert actions.committed_idempotency_keys == ()


def test_action_gateway_rejects_a_raw_proposal_without_policy_authorization() -> None:
    """The side-effect adapter has a runtime guard as well as a typed contract."""
    actions = InMemoryActionGateway()
    request = _request()
    evidence = (_evidence(),)
    raw_proposal = build_action_proposal(
        request,
        evidence,
        DeterministicProposalGenerator().generate(request, evidence),
        policy_version="policy-v1",
    )

    with pytest.raises(ActionAuthorizationError, match="authorized_action_required"):
        _ = actions.commit(raw_proposal)


def test_action_gateway_rejects_an_idempotency_key_reused_for_another_payload() -> None:
    """A conflicting retry cannot look like the receipt for an earlier action."""
    actions = InMemoryActionGateway()
    first = AuthorizedAction(
        action_id="action-first",
        action_type=ActionType.CREATE_REVIEW_TASK,
        case_id="case-42",
        actor_id="reviewer-7",
        idempotency_key="tenant-a:request-001:create_review_task",
        evidence_ids=("evidence-1",),
        policy_version="policy-v1",
        proposal_digest="a" * 64,
    )
    conflicting = first.model_copy(
        update={"action_id": "action-second", "proposal_digest": "b" * 64}
    )

    receipt = actions.commit(first)

    assert receipt.proposal_digest == "a" * 64
    with pytest.raises(
        ActionIdempotencyConflictError,
        match="idempotency_key_payload_conflict",
    ):
        _ = actions.commit(conflicting)


def test_workflow_blocks_unresolved_evidence_even_for_low_risk_action() -> None:
    """A caller-supplied evidence ID cannot bypass the trusted resolver."""
    actions = InMemoryActionGateway()
    result = _system(actions, risk=RiskLevel.LOW).run(_request())

    assert result.status is ActionStatus.BLOCKED
    assert result.reason == "verified_evidence_required"
    assert actions.committed_idempotency_keys == ()


@pytest.mark.parametrize(
    "evidence_changes",
    [
        {"tenant_id": "tenant-b"},
        {"case_id": "case-other"},
        {"authorized_actor_ids": ("different-actor",)},
        {"source_as_of": _FAR_FUTURE},
        {"valid_until": datetime(2000, 1, 1, tzinfo=UTC)},
    ],
)
def test_evidence_resolver_requires_tenant_case_acl_and_freshness(
    evidence_changes: dict[str, object],
) -> None:
    """Any failed source-of-record boundary blocks a low-risk action as well."""
    actions = InMemoryActionGateway()
    result = _system(
        actions,
        evidence=(_evidence(**evidence_changes),),
        risk=RiskLevel.LOW,
    ).run(_request())

    assert result.status is ActionStatus.BLOCKED
    assert result.reason == "verified_evidence_required"
    assert actions.committed_idempotency_keys == ()


def test_workflow_waits_for_human_approval_when_risk_is_high() -> None:
    """Verified evidence alone cannot authorize a high-risk business write."""
    actions = InMemoryActionGateway()
    result = _system(actions, evidence=(_evidence(),)).run(_request())

    assert result.status is ActionStatus.PENDING_APPROVAL
    assert actions.committed_idempotency_keys == ()


def test_workflow_executes_one_bound_approved_action_once_when_retried() -> None:
    """The exact verified proposal may retry, but its action key commits once."""
    actions = InMemoryActionGateway()
    request = _request()
    evidence = (_evidence(),)
    system = _system(
        actions,
        evidence=evidence,
        approvals=(_approval(request, evidence),),
    )

    first_result = system.run(request)
    second_result = system.run(request)

    assert first_result.status is ActionStatus.COMMITTED
    assert second_result.status is ActionStatus.COMMITTED
    assert actions.committed_idempotency_keys == (
        "tenant-a:request-001:create_review_task",
    )


@pytest.mark.parametrize(
    ("field", "value"),
    [("risk_level", "low"), ("approval_granted", True)],
)
def test_request_rejects_caller_supplied_policy_or_approval_claim(
    field: str,
    value: object,
) -> None:
    """A caller cannot lower risk or approve itself by adding an input field."""
    payload = _request().model_dump(mode="json")
    payload[field] = value

    with pytest.raises(ValidationError):
        _ = CaseRequest.model_validate(payload)


@pytest.mark.parametrize(
    "approval_changes",
    [
        {"tenant_id": "tenant-b"},
        {"case_id": "case-other"},
        {"policy_version": "policy-v0"},
    ],
)
def test_mismatched_approval_scope_does_not_permit_an_action(
    approval_changes: dict[str, str],
) -> None:
    """A verified record must bind to this tenant, case, action, and policy."""
    actions = InMemoryActionGateway()
    request = _request()
    evidence = (_evidence(),)
    system = _system(
        actions,
        evidence=evidence,
        approvals=(_approval(request, evidence, **approval_changes),),
    )

    result = system.run(request)

    assert result.status is ActionStatus.PENDING_APPROVAL
    assert actions.committed_idempotency_keys == ()


@pytest.mark.parametrize(
    "approval_changes",
    [
        {"valid_until": datetime(2000, 1, 1, tzinfo=UTC)},
        {"revoked_at": datetime(2026, 8, 25, tzinfo=UTC)},
        {"approved_at": _FAR_FUTURE},
    ],
)
def test_expired_or_revoked_approval_does_not_permit_an_action(
    approval_changes: dict[str, datetime],
) -> None:
    """Approval expiry and revocation are evaluated at the policy boundary."""
    actions = InMemoryActionGateway()
    request = _request()
    evidence = (_evidence(),)
    system = _system(
        actions,
        evidence=evidence,
        approvals=(_approval(request, evidence, **approval_changes),),
    )

    result = system.run(request)

    assert result.status is ActionStatus.PENDING_APPROVAL
    assert actions.committed_idempotency_keys == ()


def test_approval_cannot_be_reused_for_changed_request_or_evidence() -> None:
    """Changing request or source content invalidates the proposal-bound approval."""
    actions = InMemoryActionGateway()
    original_request = _request()
    original_evidence = (_evidence(),)
    alternate_evidence = _evidence(
        evidence_id="evidence-2",
        content_sha256="b" * 64,
        source_version="source-v2",
    )
    system = _system(
        actions,
        evidence=(*original_evidence, alternate_evidence),
        approvals=(_approval(original_request, original_evidence),),
    )

    committed = system.run(original_request)
    changed_request = system.run(
        _request(objective="Create a materially different review task.")
    )
    changed_evidence = system.run(_request(evidence_ids=("evidence-2",)))

    assert committed.status is ActionStatus.COMMITTED
    assert changed_request.status is ActionStatus.PENDING_APPROVAL
    assert changed_evidence.status is ActionStatus.PENDING_APPROVAL
    assert actions.committed_idempotency_keys == (
        "tenant-a:request-001:create_review_task",
    )
