"""Tests for the document-layout to ETL boundary."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from onprem_agentic_mas.layout import (
    BoundingBox,
    LayoutBlock,
    LayoutBlockKind,
    LayoutDocument,
    layout_document_to_events,
)


def test_layout_result_projects_to_versioned_ingestion_events() -> None:
    """Preserve document, tenant, case, and model provenance in the ETL event."""
    document = LayoutDocument(
        document_id="document-001",
        model_version="layout-v1",
        processed_at=datetime(2026, 8, 24, tzinfo=UTC),
        blocks=(
            LayoutBlock(
                block_id="block-001",
                page_number=1,
                kind=LayoutBlockKind.PARAGRAPH,
                text="Cited layout text.",
                confidence=0.98,
                bbox=BoundingBox(left=0, top=0, right=1, bottom=1),
            ),
        ),
    )

    events = layout_document_to_events(
        document,
        tenant_id="tenant-a",
        case_id="case-001",
    )

    assert events[0].event_id == "document-001:block-001"
    assert events[0].source == "layout:layout-v1"
    assert events[0].tenant_id == "tenant-a"
    assert events[0].schema_version == "1"
    assert events[0].layout_provenance is not None
    assert events[0].layout_provenance.model_version == "layout-v1"
    assert events[0].layout_provenance.page_number == 1
    assert events[0].layout_provenance.bbox == (0, 0, 1, 1)


def test_layout_rejects_inverted_bounding_boxes() -> None:
    """A layout result with an impossible box cannot become governed evidence."""
    with pytest.raises(ValidationError, match="bounding_box_coordinates_invalid"):
        _ = BoundingBox(left=0.8, top=0.1, right=0.2, bottom=0.9)
