"""Governed self-improvement with verified replay artifacts and release approval."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import ClassVar, Protocol

from pydantic import BaseModel, ConfigDict, Field


class FeedbackCategory(StrEnum):
    """Failure modes that should become regression cases after review."""

    WRONG_SOURCE = "wrong_source"
    STALE_DATA = "stale_data"
    MISSING_CONTEXT = "missing_context"
    WRONG_ACTION = "wrong_action"


class FeedbackEvent(BaseModel):
    """A user or operator signal that can be triaged into the evaluation backlog."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    feedback_id: str = Field(min_length=1)
    category: FeedbackCategory
    case_id: str = Field(min_length=1)
    detail: str = Field(min_length=1)


class PromotionRequest(BaseModel):
    """An untrusted request to consider a named candidate for promotion."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    candidate_id: str = Field(min_length=1)


class EvaluationArtifact(BaseModel):
    """A replay result generated and stored by a trusted evaluation pipeline."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    artifact_id: str = Field(min_length=1)
    candidate_id: str = Field(min_length=1)
    evaluation_case_ids: tuple[str, ...] = Field(min_length=1)
    blocker_failures: int = Field(ge=0)
    artifact_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    completed_at: datetime


class VerifiedReleaseApproval(BaseModel):
    """A release-system record already authenticated before this gate consumes it."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    approval_id: str = Field(min_length=1)
    candidate_id: str = Field(min_length=1)
    artifact_id: str = Field(min_length=1)
    artifact_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    approved_by: str = Field(min_length=1)
    approved_at: datetime
    valid_until: datetime
    revoked_at: datetime | None = None


class PromotionDecision(BaseModel):
    """The release gate result; no downstream service is mutated here."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    promotable: bool
    reason: str = Field(min_length=1)
    approval_id: str | None = None


class ReleaseAuthority(Protocol):
    """Trusted lookup for immutable evaluation artifacts and release approvals."""

    def decide(self, request: PromotionRequest, *, now: datetime) -> PromotionDecision:
        """Return a fail-closed promotion decision for one candidate."""
        ...


@dataclass(frozen=True, slots=True)
class InMemoryReleaseAuthority:
    """Reference adapter standing in for a signed evaluation and release system."""

    artifacts: tuple[EvaluationArtifact, ...]
    verified_approvals: tuple[VerifiedReleaseApproval, ...] = ()

    def decide(self, request: PromotionRequest, *, now: datetime) -> PromotionDecision:
        """Require one immutable clean replay artifact and one active bound approval."""
        artifact = next(
            (
                candidate
                for candidate in self.artifacts
                if candidate.candidate_id == request.candidate_id
            ),
            None,
        )
        if artifact is None:
            return PromotionDecision(
                promotable=False, reason="evaluation_artifact_missing"
            )
        if artifact.blocker_failures > 0:
            return PromotionDecision(
                promotable=False, reason="blocker_failures_present"
            )
        if artifact.completed_at > now:
            return PromotionDecision(
                promotable=False, reason="evaluation_artifact_not_complete"
            )
        approval = self._matching_approval(artifact, now=now)
        if approval is None:
            return PromotionDecision(promotable=False, reason="human_approval_required")
        return PromotionDecision(
            promotable=True,
            reason="approved_after_replay_gate",
            approval_id=approval.approval_id,
        )

    def _matching_approval(
        self,
        artifact: EvaluationArtifact,
        *,
        now: datetime,
    ) -> VerifiedReleaseApproval | None:
        """Return an active approval tied to the exact immutable evaluation artifact."""
        return next(
            (
                approval
                for approval in self.verified_approvals
                if approval.candidate_id == artifact.candidate_id
                and approval.artifact_id == artifact.artifact_id
                and approval.artifact_sha256 == artifact.artifact_sha256
                and artifact.completed_at <= approval.approved_at <= now
                and approval.valid_until > now
                and approval.revoked_at is None
            ),
            None,
        )


def evaluate_promotion(
    request: PromotionRequest,
    release_authority: ReleaseAuthority,
    *,
    now: datetime,
) -> PromotionDecision:
    """Delegate promotion to the trusted release authority, never caller booleans."""
    return release_authority.decide(request, now=now)
