"""CLI demo assembly that runs without a cloud model endpoint."""

import os
import sys
from datetime import UTC, datetime
from pathlib import Path

from onprem_agentic_mas.actions import InMemoryActionGateway
from onprem_agentic_mas.contracts import (
    ActionType,
    CaseRequest,
    RiskLevel,
    VerifiedEvidence,
)
from onprem_agentic_mas.evidence import InMemoryEvidenceResolver
from onprem_agentic_mas.memory import SqliteMemoryStore
from onprem_agentic_mas.policy import StaticPolicyAuthority
from onprem_agentic_mas.proposal import DeterministicProposalGenerator
from onprem_agentic_mas.workflow import build_system


def run_demo(database_path: Path) -> str:
    """Return the JSON result of a high-risk request awaiting human approval."""
    system = build_system(
        memory=SqliteMemoryStore(database_path),
        actions=InMemoryActionGateway(),
        evidence=InMemoryEvidenceResolver(
            records=(
                VerifiedEvidence(
                    evidence_id="demo-evidence-001",
                    tenant_id="demo-tenant",
                    case_id="demo-case-001",
                    source_id="demo-source-001",
                    source_version="demo-source-v1",
                    content_sha256="a" * 64,
                    excerpt="This is a locally stored, cited demonstration fact.",
                    source_as_of=datetime(2026, 8, 24, tzinfo=UTC),
                    valid_until=datetime(2099, 1, 1, tzinfo=UTC),
                    authorized_actor_ids=("demo-operator",),
                ),
            )
        ),
        proposals=DeterministicProposalGenerator(),
        policy=StaticPolicyAuthority(
            risk_by_action={ActionType.CREATE_REVIEW_TASK: RiskLevel.HIGH}
        ),
    )
    result = system.run(
        CaseRequest(
            request_id="demo-request-001",
            tenant_id="demo-tenant",
            actor_id="demo-operator",
            case_id="demo-case-001",
            objective="Create a review task using the cited source.",
            action_type=ActionType.CREATE_REVIEW_TASK,
            evidence_ids=("demo-evidence-001",),
        )
    )
    return result.model_dump_json()


def main() -> int:
    """Print the safe default result to stdout for an end-to-end smoke test."""
    configured_path = os.environ.get("ONPREM_MAS_DB")
    database_path = (
        Path(configured_path)
        if configured_path is not None
        else Path(".local") / "onprem-agentic-mas.sqlite3"
    )
    _ = sys.stdout.write(f"{run_demo(database_path)}\n")
    return 0
