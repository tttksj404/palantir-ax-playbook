"""Contract and integration tests for the local OpenAI-compatible model adapter."""

import json
import threading
from collections.abc import Generator
from contextlib import contextmanager
from datetime import UTC, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import override

import pytest

from onprem_agentic_mas.actions import InMemoryActionGateway
from onprem_agentic_mas.contracts import (
    ActionStatus,
    ActionType,
    CaseRequest,
    RiskLevel,
    VerifiedEvidence,
)
from onprem_agentic_mas.evidence import InMemoryEvidenceResolver
from onprem_agentic_mas.local_model import (
    ChatRole,
    LocalChatMessage,
    LocalChatRequest,
    LocalModelTransportError,
    LocalOpenAICompatibleClient,
)
from onprem_agentic_mas.memory import InMemoryMemoryStore
from onprem_agentic_mas.policy import StaticPolicyAuthority
from onprem_agentic_mas.proposal import LocalModelProposalGenerator
from onprem_agentic_mas.workflow import build_system


@contextmanager
def _local_model_server(response_body: bytes) -> Generator[str, None, None]:
    """Serve one local-only OpenAI-compatible response for an integration test."""

    class _Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            """Return the injected fixture body on the expected local endpoint."""
            _ = self.rfile.read(int(self.headers["Content-Length"]))
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(response_body)))
            self.end_headers()
            _ = self.wfile.write(response_body)

        @override
        def log_message(self, format: str, *args: object) -> None:
            """Silence the standard-library test server's request log."""

    server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/v1"
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


def _local_client(
    base_url: str,
    *,
    allowed_hosts: frozenset[str] | None = None,
    max_response_bytes: int = 1_048_576,
) -> LocalOpenAICompatibleClient:
    resolved_allowed_hosts = (
        frozenset({"127.0.0.1"}) if allowed_hosts is None else allowed_hosts
    )
    return LocalOpenAICompatibleClient(
        base_url=base_url,
        api_key="test-secret-key",
        model="local-sllm",
        allowed_hosts=resolved_allowed_hosts,
        allow_insecure_loopback=True,
        max_response_bytes=max_response_bytes,
    )


def _verified_evidence() -> VerifiedEvidence:
    return VerifiedEvidence(
        evidence_id="evidence-1",
        tenant_id="tenant-a",
        case_id="case-42",
        source_id="source-1",
        source_version="source-v1",
        content_sha256="a" * 64,
        excerpt="The source establishes the review condition.",
        source_as_of=datetime(2026, 8, 24, tzinfo=UTC),
        valid_until=datetime(2099, 1, 1, tzinfo=UTC),
        authorized_actor_ids=("reviewer-7",),
    )


def _request() -> CaseRequest:
    return CaseRequest(
        request_id="request-001",
        tenant_id="tenant-a",
        actor_id="reviewer-7",
        case_id="case-42",
        objective="Create a review task from verified evidence.",
        action_type=ActionType.CREATE_REVIEW_TASK,
        evidence_ids=("evidence-1",),
    )


def test_local_chat_request_serializes_an_explicit_local_model_contract() -> None:
    """Keep the portable local-server request separate from workflow policy."""
    request = LocalChatRequest(
        model="local-sllm",
        messages=(
            LocalChatMessage(
                role=ChatRole.USER,
                content="Return a structured proposal candidate.",
            ),
        ),
    )

    serialized = request.model_dump_json()

    assert '"model":"local-sllm"' in serialized
    assert '"role":"user"' in serialized


def test_local_client_rejects_non_http_or_unsafe_endpoints_before_connecting() -> None:
    """Do not send prompts or keys to custom schemes or metadata endpoints."""
    file_client = _local_client("file:///not-an-internal-model-server")
    metadata_client = _local_client(
        "http://169.254.169.254/v1",
        allowed_hosts=frozenset({"169.254.169.254"}),
    )

    with pytest.raises(
        LocalModelTransportError, match="local_model_url_scheme_invalid"
    ):
        _ = file_client.complete(())
    with pytest.raises(LocalModelTransportError, match="local_model_url_unsafe_host"):
        _ = metadata_client.complete(())


def test_local_client_hides_api_key_and_limits_response_size() -> None:
    """Logging and oversized responses cannot expose credentials or exhaust data."""
    client = _local_client(
        "https://models.internal/v1", allowed_hosts=frozenset({"models.internal"})
    )

    assert "test-secret-key" not in repr(client)

    with _local_model_server(b"x" * 8) as base_url:
        capped_client = _local_client(base_url, max_response_bytes=4)
        with pytest.raises(
            LocalModelTransportError,
            match="local_model_response_too_large",
        ):
            _ = capped_client.complete(())


def test_local_model_candidate_is_structured_then_held_at_policy_gate() -> None:
    """A real local HTTP response becomes only a candidate before high-risk approval."""
    response_body = json.dumps(
        {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": json.dumps(
                            {
                                "action_type": "create_review_task",
                                "rationale": "The verified source supports review.",
                            }
                        ),
                    }
                }
            ]
        }
    ).encode()
    actions = InMemoryActionGateway()

    with _local_model_server(response_body) as base_url:
        system = build_system(
            memory=InMemoryMemoryStore(),
            actions=actions,
            evidence=InMemoryEvidenceResolver(records=(_verified_evidence(),)),
            proposals=LocalModelProposalGenerator(_local_client(base_url)),
            policy=StaticPolicyAuthority(
                risk_by_action={ActionType.CREATE_REVIEW_TASK: RiskLevel.HIGH}
            ),
        )
        result = system.run(_request())

    assert result.status is ActionStatus.PENDING_APPROVAL
    assert actions.committed_idempotency_keys == ()
