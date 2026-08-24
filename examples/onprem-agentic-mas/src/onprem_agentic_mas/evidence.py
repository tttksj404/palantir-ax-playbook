"""Trusted evidence resolution between untrusted requests and policy evaluation."""

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from onprem_agentic_mas.contracts import CaseRequest, VerifiedEvidence


class EvidenceResolver(Protocol):
    """Resolve only evidence that the authenticated request may use."""

    def resolve(
        self,
        request: CaseRequest,
        *,
        now: datetime,
    ) -> tuple[VerifiedEvidence, ...]:
        """Return tenant, case, ACL, source-version, and freshness-verified records."""
        ...


@dataclass(frozen=True, slots=True)
class InMemoryEvidenceResolver:
    """Reference resolver for records verified by a source-of-record adapter."""

    records: tuple[VerifiedEvidence, ...]

    def resolve(
        self,
        request: CaseRequest,
        *,
        now: datetime,
    ) -> tuple[VerifiedEvidence, ...]:
        """Return only requested records that meet every authorization boundary."""
        requested_ids = frozenset(request.evidence_ids)
        return tuple(
            record
            for record in self.records
            if record.evidence_id in requested_ids
            and record.tenant_id == request.tenant_id
            and record.case_id == request.case_id
            and request.actor_id in record.authorized_actor_ids
            and record.source_as_of <= now
            and record.valid_until > now
        )
