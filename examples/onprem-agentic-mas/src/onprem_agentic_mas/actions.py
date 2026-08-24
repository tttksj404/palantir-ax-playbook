"""The isolated side-effect boundary for policy-authorized business actions."""

from dataclasses import dataclass, field
from typing import Protocol

from onprem_agentic_mas.contracts import ActionReceipt, AuthorizedAction


class ActionGateway(Protocol):
    """The only interface that may create a business side effect."""

    def commit(self, action: AuthorizedAction) -> ActionReceipt:
        """Commit an allowlisted, policy-authorized action idempotently."""
        ...


class ActionAuthorizationError(RuntimeError):
    """Raised when code attempts to bypass the authorized-action boundary."""


class ActionIdempotencyConflictError(RuntimeError):
    """Raised when a key is reused with a different policy-authorized payload."""


@dataclass(slots=True)
class InMemoryActionGateway:
    """Observable test adapter without any external write capability."""

    _receipts: dict[str, tuple[str, ActionReceipt]] = field(default_factory=dict)

    @property
    def committed_idempotency_keys(self) -> tuple[str, ...]:
        """Return committed action keys in insertion order for observable tests."""
        return tuple(self._receipts)

    def commit(self, action: object) -> ActionReceipt:
        """Commit once per idempotency key and return the same receipt on retry."""
        if not isinstance(action, AuthorizedAction):
            reason = "authorized_action_required"
            raise ActionAuthorizationError(reason)
        existing = self._receipts.get(action.idempotency_key)
        if existing is not None:
            existing_digest, receipt = existing
            if existing_digest != action.proposal_digest:
                reason = "idempotency_key_payload_conflict"
                raise ActionIdempotencyConflictError(reason)
            return receipt
        receipt = ActionReceipt(
            action_id=action.action_id,
            idempotency_key=action.idempotency_key,
            proposal_digest=action.proposal_digest,
        )
        self._receipts[action.idempotency_key] = (action.proposal_digest, receipt)
        return receipt
