"""A minimal local OpenAI-compatible client for an internal model gateway."""

from dataclasses import dataclass, field
from enum import StrEnum
from http.client import HTTPConnection, HTTPException, HTTPSConnection
from ipaddress import ip_address
from typing import ClassVar, override
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field

_HTTP_ERROR_STATUS_MINIMUM = 400
_DEFAULT_MAX_RESPONSE_BYTES = 1_048_576


class ChatRole(StrEnum):
    """The message roles accepted by the local completion gateway."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class LocalChatMessage(BaseModel):
    """A structured message passed to an approved local model endpoint."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    role: ChatRole
    content: str = Field(min_length=1)


class LocalChatRequest(BaseModel):
    """The OpenAI-compatible subset used by vLLM and similar local servers."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    model: str = Field(min_length=1)
    messages: tuple[LocalChatMessage, ...]
    temperature: float = Field(default=0, ge=0, le=2)


class LocalChatChoice(BaseModel):
    """One response choice returned by a compatible local model server."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    message: LocalChatMessage


class LocalChatResponse(BaseModel):
    """Validated response envelope; unrecognized vendor fields are ignored."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    choices: tuple[LocalChatChoice, ...]


@dataclass(frozen=True, slots=True)
class LocalModelTransportError(RuntimeError):
    """Raised when the internal model gateway cannot complete a request."""

    reason: str

    @override
    def __str__(self) -> str:
        """Return the safe, operator-facing error reason."""
        return self.reason


@dataclass(frozen=True, slots=True)
class LocalOpenAICompatibleClient:
    """Call an allowlisted internal OpenAI-compatible endpoint without a cloud SDK."""

    base_url: str
    api_key: str = field(repr=False)
    model: str
    allowed_hosts: frozenset[str]
    allow_insecure_loopback: bool = False
    timeout_seconds: float = 30
    max_response_bytes: int = _DEFAULT_MAX_RESPONSE_BYTES

    def complete(self, messages: tuple[LocalChatMessage, ...]) -> str:
        """Return candidate text without automatically executing an action."""
        request_payload = LocalChatRequest(model=self.model, messages=messages)
        encoded_payload = request_payload.model_dump_json().encode()
        connection, endpoint = self._connection_and_endpoint()
        try:
            connection.request(
                "POST",
                endpoint,
                body=encoded_payload,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
            )
            response = connection.getresponse()
            response_body: bytes = response.read(self.max_response_bytes + 1)
        except (HTTPException, OSError) as error:
            reason = f"local_model_transport_{type(error).__name__.lower()}"
            raise LocalModelTransportError(reason=reason) from error
        finally:
            connection.close()
        if response.status >= _HTTP_ERROR_STATUS_MINIMUM:
            reason = f"local_model_http_{response.status}"
            raise LocalModelTransportError(reason=reason)
        if len(response_body) > self.max_response_bytes:
            raise LocalModelTransportError(reason="local_model_response_too_large")

        completion = LocalChatResponse.model_validate_json(response_body)
        if not completion.choices:
            raise LocalModelTransportError(reason="local_model_empty_choices")
        return completion.choices[0].message.content

    def _connection_and_endpoint(self) -> tuple[HTTPConnection, str]:
        """Validate an internal HTTP(S) URL and build its direct connection."""
        parsed = urlsplit(self.base_url)
        if parsed.scheme not in {"http", "https"}:
            raise LocalModelTransportError(reason="local_model_url_scheme_invalid")
        if parsed.username is not None or parsed.password is not None:
            raise LocalModelTransportError(
                reason="local_model_url_credentials_forbidden"
            )
        if parsed.hostname is None:
            raise LocalModelTransportError(reason="local_model_url_host_missing")
        hostname = parsed.hostname.lower()
        if _is_unsafe_ip_host(hostname):
            raise LocalModelTransportError(reason="local_model_url_unsafe_host")
        if hostname not in {host.lower() for host in self.allowed_hosts}:
            raise LocalModelTransportError(
                reason="local_model_url_host_not_allowlisted"
            )
        if parsed.scheme == "http" and not (
            self.allow_insecure_loopback and _is_loopback_host(hostname)
        ):
            raise LocalModelTransportError(reason="local_model_https_required")
        if parsed.query or parsed.fragment:
            raise LocalModelTransportError(reason="local_model_url_query_forbidden")
        try:
            port = parsed.port
        except ValueError as error:
            raise LocalModelTransportError(
                reason="local_model_url_port_invalid"
            ) from error

        connection: HTTPConnection
        if parsed.scheme == "https":
            connection = HTTPSConnection(
                host=hostname,
                port=port,
                timeout=self.timeout_seconds,
            )
        else:
            connection = HTTPConnection(
                host=hostname,
                port=port,
                timeout=self.timeout_seconds,
            )
        return connection, f"{parsed.path.rstrip('/')}/chat/completions"


def _is_loopback_host(hostname: str) -> bool:
    """Return whether a hostname is an explicitly recognized loopback target."""
    if hostname == "localhost":
        return True
    try:
        return ip_address(hostname).is_loopback
    except ValueError:
        return False


def _is_unsafe_ip_host(hostname: str) -> bool:
    """Reject metadata, multicast, and unspecified IP endpoints before sending a key."""
    try:
        address = ip_address(hostname)
    except ValueError:
        return False
    return address.is_link_local or address.is_multicast or address.is_unspecified
