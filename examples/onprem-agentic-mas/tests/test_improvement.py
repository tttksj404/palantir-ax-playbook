from datetime import UTC, datetime

from onprem_agentic_mas.improvement import (
    EvaluationArtifact,
    InMemoryReleaseAuthority,
    PromotionRequest,
    VerifiedReleaseApproval,
    evaluate_promotion,
)

_NOW = datetime(2026, 8, 24, tzinfo=UTC)
_FAR_FUTURE = datetime(2099, 1, 1, tzinfo=UTC)


def _artifact(**changes: object) -> EvaluationArtifact:
    payload: dict[str, object] = {
        "artifact_id": "evaluation-001",
        "candidate_id": "candidate-1",
        "evaluation_case_ids": ("case-1", "case-2"),
        "blocker_failures": 0,
        "artifact_sha256": "a" * 64,
        "completed_at": _NOW,
    }
    payload.update(changes)
    return EvaluationArtifact.model_validate(payload)


def _approval(
    artifact: EvaluationArtifact, **changes: object
) -> VerifiedReleaseApproval:
    payload: dict[str, object] = {
        "approval_id": "release-approval-001",
        "candidate_id": artifact.candidate_id,
        "artifact_id": artifact.artifact_id,
        "artifact_sha256": artifact.artifact_sha256,
        "approved_by": "release-manager-1",
        "approved_at": _NOW,
        "valid_until": _FAR_FUTURE,
    }
    payload.update(changes)
    return VerifiedReleaseApproval.model_validate(payload)


def test_improvement_candidate_requires_verified_release_approval() -> None:
    """A clean replay artifact cannot self-promote without a trusted approval record."""
    artifact = _artifact()
    request = PromotionRequest(candidate_id=artifact.candidate_id)
    pending = evaluate_promotion(
        request,
        InMemoryReleaseAuthority(artifacts=(artifact,)),
        now=_NOW,
    )

    assert pending.promotable is False
    assert pending.reason == "human_approval_required"

    approved = evaluate_promotion(
        request,
        InMemoryReleaseAuthority(
            artifacts=(artifact,),
            verified_approvals=(_approval(artifact),),
        ),
        now=_NOW,
    )

    assert approved.promotable is True
    assert approved.approval_id == "release-approval-001"


def test_improvement_blocks_missing_or_failing_evaluation_artifacts() -> None:
    """Zero caller-supplied booleans cannot bypass a missing or failing replay run."""
    missing = evaluate_promotion(
        PromotionRequest(candidate_id="candidate-1"),
        InMemoryReleaseAuthority(artifacts=()),
        now=_NOW,
    )
    failing_artifact = _artifact(blocker_failures=1)
    failing = evaluate_promotion(
        PromotionRequest(candidate_id=failing_artifact.candidate_id),
        InMemoryReleaseAuthority(
            artifacts=(failing_artifact,),
            verified_approvals=(_approval(failing_artifact),),
        ),
        now=_NOW,
    )

    assert missing.reason == "evaluation_artifact_missing"
    assert failing.reason == "blocker_failures_present"


def test_improvement_rejects_inactive_or_temporally_invalid_release_approval() -> None:
    """A release approval must follow a completed artifact and be active now."""
    artifact = _artifact()
    request = PromotionRequest(candidate_id=artifact.candidate_id)
    expired = evaluate_promotion(
        request,
        InMemoryReleaseAuthority(
            artifacts=(artifact,),
            verified_approvals=(
                _approval(artifact, valid_until=datetime(2000, 1, 1, tzinfo=UTC)),
            ),
        ),
        now=_NOW,
    )
    revoked = evaluate_promotion(
        request,
        InMemoryReleaseAuthority(
            artifacts=(artifact,),
            verified_approvals=(_approval(artifact, revoked_at=_NOW),),
        ),
        now=_NOW,
    )
    future_approved = evaluate_promotion(
        request,
        InMemoryReleaseAuthority(
            artifacts=(artifact,),
            verified_approvals=(_approval(artifact, approved_at=_FAR_FUTURE),),
        ),
        now=_NOW,
    )
    approved_before_evaluation = evaluate_promotion(
        request,
        InMemoryReleaseAuthority(
            artifacts=(artifact,),
            verified_approvals=(
                _approval(artifact, approved_at=datetime(2020, 1, 1, tzinfo=UTC)),
            ),
        ),
        now=_NOW,
    )

    assert expired.reason == "human_approval_required"
    assert revoked.reason == "human_approval_required"
    assert future_approved.reason == "human_approval_required"
    assert approved_before_evaluation.reason == "human_approval_required"
