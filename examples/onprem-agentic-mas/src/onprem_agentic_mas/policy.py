"""Server-owned policy and verified-approval decisions for workflow proposals."""

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from onprem_agentic_mas.contracts import (
    ActionProposal,
    ActionType,
    CaseRequest,
    PolicyDecision,
    PolicyStatus,
    RiskLevel,
    VerifiedApproval,
)


class PolicyAuthority(Protocol):
    """Trusted policy boundary; request payload never decides risk or approval."""

    @property
    def policy_version(self) -> str:
        """Return the policy version bound into each proposal and approval."""
        ...

    def decide(
        self,
        request: CaseRequest,
        proposal: ActionProposal,
        *,
        now: datetime,
    ) -> PolicyDecision:
        """Return a deterministic policy result for the complete proposal scope."""
        ...


@dataclass(frozen=True, slots=True)
class StaticPolicyAuthority:
    """Reference adapter that consumes only approval records verified upstream.

    A production adapter must authenticate the approval-system record before it
    constructs ``VerifiedApproval``.  The match below is intentionally narrow:
    tenant, case, request, action, policy version, proposal digest, expiry, and
    revocation must all be valid before a high-risk action can proceed.
    """

    risk_by_action: Mapping[ActionType, RiskLevel]
    verified_approvals: tuple[VerifiedApproval, ...] = ()
    policy_version: str = "policy-v1"

    def decide(
        self,
        request: CaseRequest,
        proposal: ActionProposal,
        *,
        now: datetime,
    ) -> PolicyDecision:
        """Fail closed unless configured policy and any required approval match."""
        if proposal.policy_version != self.policy_version:
            return PolicyDecision(
                status=PolicyStatus.BLOCKED,
                reason="policy_version_mismatch",
            )
        risk_level = self.risk_by_action.get(proposal.action_type)
        if risk_level is None:
            return PolicyDecision(
                status=PolicyStatus.BLOCKED,
                reason="risk_policy_missing",
            )
        if risk_level is RiskLevel.LOW:
            return PolicyDecision(
                status=PolicyStatus.ALLOWED,
                reason="policy_gate_passed",
            )
        approval = self._matching_approval(request, proposal, now=now)
        if approval is None:
            return PolicyDecision(
                status=PolicyStatus.PENDING_APPROVAL,
                reason="human_approval_required",
            )
        return PolicyDecision(
            status=PolicyStatus.ALLOWED,
            reason="policy_gate_passed",
            approval_id=approval.approval_id,
        )

    def _matching_approval(
        self,
        request: CaseRequest,
        proposal: ActionProposal,
        *,
        now: datetime,
    ) -> VerifiedApproval | None:
        """Return one active approval with the complete authorization scope."""
        return next(
            (
                approval
                for approval in self.verified_approvals
                if approval.tenant_id == request.tenant_id
                and approval.case_id == request.case_id
                and approval.request_id == request.request_id
                and approval.action_type is proposal.action_type
                and approval.policy_version == proposal.policy_version
                and approval.proposal_digest == proposal.proposal_digest
                and approval.approved_at <= now
                and approval.valid_until > now
                and approval.revoked_at is None
            ),
            None,
        )
