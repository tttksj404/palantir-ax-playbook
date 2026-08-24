"""Typed contracts at the boundary between agents, policy, and action."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import ClassVar, override

from pydantic import BaseModel, ConfigDict, Field


class ActionType(StrEnum):
    """The allowlisted business actions available to the workflow."""

    CREATE_REVIEW_TASK = "create_review_task"


class RiskLevel(StrEnum):
    """Risk classification owned by the server-side use-case policy."""

    LOW = "low"
    HIGH = "high"


class PolicyStatus(StrEnum):
    """The policy decision before any external side effect."""

    ALLOWED = "allowed"
    BLOCKED = "blocked"
    PENDING_APPROVAL = "pending_approval"


class ActionStatus(StrEnum):
    """Observable end states for a workflow run."""

    BLOCKED = "blocked"
    PENDING_APPROVAL = "pending_approval"
    COMMITTED = "committed"


class EvidenceReference(BaseModel):
    """An untrusted request for an evidence record held by the system of record."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    evidence_id: str = Field(min_length=1)


class VerifiedEvidence(BaseModel):
    """A source record authorized and verified by the server-side evidence resolver."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    evidence_id: str = Field(min_length=1)
    tenant_id: str = Field(min_length=1)
    case_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    source_version: str = Field(min_length=1)
    content_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    excerpt: str = Field(min_length=1)
    source_as_of: datetime
    valid_until: datetime
    authorized_actor_ids: tuple[str, ...]


class CaseRequest(BaseModel):
    """Validated workflow input; raw user and integration input stops here."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    request_id: str = Field(min_length=1)
    tenant_id: str = Field(min_length=1)
    actor_id: str = Field(min_length=1)
    case_id: str = Field(min_length=1)
    objective: str = Field(min_length=1)
    action_type: ActionType
    evidence_ids: tuple[str, ...]


class VerifiedApproval(BaseModel):
    """An approval record already verified by a trusted approval-system adapter."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    approval_id: str = Field(min_length=1)
    tenant_id: str = Field(min_length=1)
    case_id: str = Field(min_length=1)
    request_id: str = Field(min_length=1)
    action_type: ActionType
    policy_version: str = Field(min_length=1)
    proposal_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    approved_by: str = Field(min_length=1)
    approved_at: datetime
    valid_until: datetime
    revoked_at: datetime | None = None


class ProposalCandidate(BaseModel):
    """A structured model candidate that cannot directly create a side effect."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    action_type: ActionType
    rationale: str = Field(min_length=1)


class ActionProposal(BaseModel):
    """A model or rule proposal that still requires policy enforcement."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    action_id: str = Field(min_length=1)
    action_type: ActionType
    case_id: str = Field(min_length=1)
    actor_id: str = Field(min_length=1)
    idempotency_key: str = Field(min_length=1)
    evidence_ids: tuple[str, ...]
    policy_version: str = Field(min_length=1)
    proposal_digest: str = Field(pattern=r"^[0-9a-f]{64}$")


class PolicyDecision(BaseModel):
    """A deterministic policy decision with an operator-readable reason."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    status: PolicyStatus
    reason: str = Field(min_length=1)
    approval_id: str | None = None


class AuthorizedAction(BaseModel):
    """An action capsule created only after a policy decision permits execution."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    action_id: str = Field(min_length=1)
    action_type: ActionType
    case_id: str = Field(min_length=1)
    actor_id: str = Field(min_length=1)
    idempotency_key: str = Field(min_length=1)
    evidence_ids: tuple[str, ...]
    policy_version: str = Field(min_length=1)
    proposal_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    approval_id: str | None = None


class ActionReceipt(BaseModel):
    """The typed acknowledgement from the action gateway."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    action_id: str = Field(min_length=1)
    idempotency_key: str = Field(min_length=1)
    proposal_digest: str = Field(pattern=r"^[0-9a-f]{64}$")


class WorkflowResult(BaseModel):
    """The externally observable result without hidden chain-of-thought."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    status: ActionStatus
    reason: str = Field(min_length=1)
    recalled_memory_ids: tuple[str, ...]
    action_receipt: ActionReceipt | None


@dataclass(frozen=True, slots=True)
class WorkflowInvariantError(RuntimeError):
    """Raised when a graph edge violates a declared state contract."""

    reason: str

    @override
    def __str__(self) -> str:
        return self.reason
