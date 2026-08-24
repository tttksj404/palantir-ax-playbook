"""Typed handoff from a document-layout model to the governed ETL boundary."""

from datetime import datetime
from enum import StrEnum
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field, model_validator

from onprem_agentic_mas.etl import IngestionEvent, LayoutProvenance


class LayoutBlockKind(StrEnum):
    """The layout categories retained for downstream evidence handling."""

    PARAGRAPH = "paragraph"
    TABLE = "table"
    TITLE = "title"


class BoundingBox(BaseModel):
    """Normalized page coordinates emitted by the selected layout model."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    left: float = Field(ge=0, le=1)
    top: float = Field(ge=0, le=1)
    right: float = Field(ge=0, le=1)
    bottom: float = Field(ge=0, le=1)

    @model_validator(mode="after")
    def has_nonempty_area(self) -> "BoundingBox":
        """Reject inverted or zero-area regions before downstream ingestion."""
        if self.left >= self.right or self.top >= self.bottom:
            reason = "bounding_box_coordinates_invalid"
            raise ValueError(reason)
        return self


class LayoutBlock(BaseModel):
    """One text-bearing layout region with model confidence and provenance."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    block_id: str = Field(min_length=1)
    page_number: int = Field(ge=1)
    kind: LayoutBlockKind
    text: str = Field(min_length=1)
    confidence: float = Field(ge=0, le=1)
    bbox: BoundingBox


class LayoutDocument(BaseModel):
    """A complete, versioned layout result before it becomes curated context."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    document_id: str = Field(min_length=1)
    model_version: str = Field(min_length=1)
    processed_at: datetime
    blocks: tuple[LayoutBlock, ...]


def layout_document_to_events(
    document: LayoutDocument,
    *,
    tenant_id: str,
    case_id: str,
) -> tuple[IngestionEvent, ...]:
    """Project text-bearing layout blocks into replayable ETL events."""
    return tuple(
        IngestionEvent(
            schema_version="1",
            event_id=f"{document.document_id}:{block.block_id}",
            tenant_id=tenant_id,
            case_id=case_id,
            source=f"layout:{document.model_version}",
            occurred_at=document.processed_at,
            text=block.text,
            layout_provenance=LayoutProvenance(
                document_id=document.document_id,
                model_version=document.model_version,
                page_number=block.page_number,
                block_kind=block.kind.value,
                bbox=(
                    block.bbox.left,
                    block.bbox.top,
                    block.bbox.right,
                    block.bbox.bottom,
                ),
                confidence=block.confidence,
            ),
        )
        for block in document.blocks
    )
