"""End-to-end smoke coverage for the local, no-cloud command-line path."""

import os
import subprocess
import sys
from pathlib import Path

from onprem_agentic_mas.contracts import ActionStatus, WorkflowResult


def test_cli_returns_a_safe_pending_approval_result(tmp_path: Path) -> None:
    """Run the installed module and confirm it makes no default external action."""
    database_path = tmp_path / "cli-demo.sqlite3"
    environment = {**os.environ, "ONPREM_MAS_DB": str(database_path)}

    completed = subprocess.run(
        [sys.executable, "-m", "onprem_agentic_mas"],
        capture_output=True,
        check=False,
        cwd=Path(__file__).resolve().parents[1],
        env=environment,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    result = WorkflowResult.model_validate_json(completed.stdout)
    assert result.status is ActionStatus.PENDING_APPROVAL
    assert result.action_receipt is None
    assert database_path.is_file()
