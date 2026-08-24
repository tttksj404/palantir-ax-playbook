from datetime import UTC, datetime
from pathlib import Path

from onprem_agentic_mas.memory import (
    InMemoryMemoryStore,
    MemoryEntry,
    MemoryStore,
    SqliteMemoryStore,
)


def _entry(*, memory_id: str, tenant_id: str, outcome: str) -> MemoryEntry:
    return MemoryEntry(
        memory_id=memory_id,
        tenant_id=tenant_id,
        case_id=f"{tenant_id}-case",
        summary="supplier evidence requires a human review",
        outcome=outcome,
        recorded_at=datetime(2026, 8, 24, tzinfo=UTC),
    )


def test_memory_returns_only_entries_from_the_request_tenant(tmp_path: Path) -> None:
    # Given: two tenant records with overlapping text.
    store = SqliteMemoryStore(tmp_path / "memory.sqlite3")
    store.record(
        _entry(memory_id="memory-a", tenant_id="tenant-a", outcome="pending_approval")
    )
    store.record(
        _entry(memory_id="memory-b", tenant_id="tenant-b", outcome="committed")
    )

    # When: tenant-a asks for a matching memory.
    result = store.search(tenant_id="tenant-a", query="supplier evidence", limit=5)

    # Then: tenant-b data is absent even though it has the same lexical match.
    assert tuple(entry.memory_id for entry in result) == ("memory-a",)


def test_memory_id_is_scoped_by_tenant_in_every_reference_store(tmp_path: Path) -> None:
    """Same memory IDs for different tenants must not overwrite one another."""
    stores: tuple[MemoryStore, ...] = (
        InMemoryMemoryStore(),
        SqliteMemoryStore(tmp_path / "memory.sqlite3"),
    )

    for store in stores:
        store.record(
            _entry(
                memory_id="same-id", tenant_id="tenant-a", outcome="pending_approval"
            )
        )
        store.record(
            _entry(memory_id="same-id", tenant_id="tenant-b", outcome="committed")
        )

        tenant_a = store.search("tenant-a", "supplier evidence", limit=5)
        tenant_b = store.search("tenant-b", "supplier evidence", limit=5)

        assert tuple(entry.outcome for entry in tenant_a) == ("pending_approval",)
        assert tuple(entry.outcome for entry in tenant_b) == ("committed",)
