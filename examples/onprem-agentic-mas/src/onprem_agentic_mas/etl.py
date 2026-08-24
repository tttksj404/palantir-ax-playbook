"""Small, replayable ETL boundary that quarantines bad JSONL records."""

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from typing import ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class LayoutProvenance(BaseModel):
    """Document-layout metadata retained with an event for replay and audit."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    document_id: str = Field(min_length=1)
    model_version: str = Field(min_length=1)
    page_number: int = Field(ge=1)
    block_kind: str = Field(min_length=1)
    bbox: tuple[float, float, float, float]
    confidence: float = Field(ge=0, le=1)


class IngestionEvent(BaseModel):
    """Validated event shape before it can become curated business context."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    schema_version: Literal["1"]
    event_id: str = Field(min_length=1)
    tenant_id: str = Field(min_length=1)
    case_id: str = Field(min_length=1)
    source: str = Field(min_length=1)
    occurred_at: datetime
    text: str = Field(min_length=1)
    layout_provenance: LayoutProvenance | None = None


@dataclass(frozen=True, slots=True)
class QuarantinedRecord:
    """A bad source line stored as a hash rather than potentially sensitive text."""

    line_number: int
    reason: str
    raw_sha256: str


@dataclass(frozen=True, slots=True)
class IngestionResult:
    """The accepted and quarantined records from one deterministic input file."""

    accepted: tuple[IngestionEvent, ...]
    quarantined: tuple[QuarantinedRecord, ...]


def ingest_jsonl(source: Path) -> IngestionResult:
    """Parse one JSONL source without letting invalid records halt the batch."""
    accepted: list[IngestionEvent] = []
    quarantined: list[QuarantinedRecord] = []
    accepted_event_ids: set[str] = set()
    with source.open(encoding="utf-8") as input_file:
        for line_number, raw_line in enumerate(input_file, start=1):
            serialized = raw_line.strip()
            if not serialized:
                continue
            try:
                event = IngestionEvent.model_validate_json(serialized)
            except ValidationError as error:
                reason = (
                    "invalid_json"
                    if '"json_invalid"' in error.json()
                    else "invalid_schema"
                )
                quarantined.append(
                    QuarantinedRecord(
                        line_number=line_number,
                        reason=reason,
                        raw_sha256=sha256(serialized.encode()).hexdigest(),
                    )
                )
                continue
            if event.event_id in accepted_event_ids:
                quarantined.append(
                    QuarantinedRecord(
                        line_number=line_number,
                        reason="duplicate_event_id",
                        raw_sha256=sha256(serialized.encode()).hexdigest(),
                    )
                )
                continue
            accepted_event_ids.add(event.event_id)
            accepted.append(event)
    return IngestionResult(
        accepted=tuple(accepted),
        quarantined=tuple(quarantined),
    )
