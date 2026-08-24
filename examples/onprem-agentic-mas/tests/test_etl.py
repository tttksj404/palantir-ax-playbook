from pathlib import Path

from onprem_agentic_mas.etl import ingest_jsonl


def test_ingestion_quarantines_invalid_records_without_stopping_valid_records(
    tmp_path: Path,
) -> None:
    # Given: one valid event, malformed JSON, and a schema-invalid event.
    source = tmp_path / "events.jsonl"
    valid_event = (
        '{"schema_version":"1","event_id":"event-1","tenant_id":"tenant-a","case_id":"case-1",'
        '"source":"erp","occurred_at":"2026-08-24T00:00:00Z","text":"valid"}'
    )
    schema_invalid_event = (
        '{"schema_version":"1","event_id":"event-2","tenant_id":"tenant-a","source":"erp",'
        '"occurred_at":"2026-08-24T00:00:00Z","text":"missing case"}'
    )
    _ = source.write_text(
        f"{valid_event}\n{{malformed-json}}\n{schema_invalid_event}\n",
        encoding="utf-8",
    )

    # When: the input is ingested.
    result = ingest_jsonl(source)

    # Then: the valid event is preserved and both invalid records are quarantined.
    assert tuple(event.event_id for event in result.accepted) == ("event-1",)
    assert tuple(item.reason for item in result.quarantined) == (
        "invalid_json",
        "invalid_schema",
    )


def test_ingestion_quarantines_schema_drift_and_duplicate_event_ids(
    tmp_path: Path,
) -> None:
    """Unexpected fields and duplicate IDs must fail instead of losing data."""
    source = tmp_path / "events.jsonl"
    first = (
        '{"schema_version":"1","event_id":"event-1","tenant_id":"tenant-a",'
        '"case_id":"case-1","source":"erp","occurred_at":"2026-08-24T00:00:00Z",'
        '"text":"valid"}'
    )
    duplicate = first.replace('"text":"valid"', '"text":"retry"')
    drifted = first.replace('"text":"valid"', '"text":"unknown","upstream_flag":true')
    _ = source.write_text(f"{first}\n{duplicate}\n{drifted}\n", encoding="utf-8")

    result = ingest_jsonl(source)

    assert tuple(event.event_id for event in result.accepted) == ("event-1",)
    assert tuple(item.reason for item in result.quarantined) == (
        "duplicate_event_id",
        "invalid_schema",
    )
