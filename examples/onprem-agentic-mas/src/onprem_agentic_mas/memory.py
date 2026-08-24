"""Tenant-isolated episodic memory with a replaceable persistence adapter."""

import sqlite3
from contextlib import closing
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Protocol, TypeGuard, final

_MEMORY_ROW_LENGTH = 6
_MEMORY_ROW_COUNT_ERROR = "memory_row_column_count_invalid"
_MEMORY_RECORDED_AT_ERROR = "memory_recorded_at_invalid"
_MEMORY_TEXT_ERROR = "memory_text_column_invalid"


@dataclass(frozen=True, slots=True)
class MemoryEntry:
    """A compact outcome record; source evidence remains in its system of record."""

    memory_id: str
    tenant_id: str
    case_id: str
    summary: str
    outcome: str
    recorded_at: datetime


class MemoryStore(Protocol):
    """The minimum tenant-scoped memory contract used by graph nodes."""

    def record(self, entry: MemoryEntry) -> None:
        """Upsert a memory entry."""
        ...

    def search(self, tenant_id: str, query: str, limit: int) -> tuple[MemoryEntry, ...]:
        """Recall only entries belonging to one tenant."""
        ...


@dataclass(slots=True)
class InMemoryMemoryStore:
    """Mutable in-process memory fake for deterministic workflow tests."""

    _entries: dict[tuple[str, str], MemoryEntry] = field(default_factory=dict)

    def record(self, entry: MemoryEntry) -> None:
        """Upsert an entry by its tenant-scoped stable memory identifier."""
        self._entries[(entry.tenant_id, entry.memory_id)] = entry

    def search(self, tenant_id: str, query: str, limit: int) -> tuple[MemoryEntry, ...]:
        """Return lexical matches after enforcing the tenant filter in code."""
        if limit < 1:
            return ()
        terms = tuple(term.lower() for term in query.split() if term)
        if not terms:
            return ()
        matches = [
            entry
            for entry in self._entries.values()
            if entry.tenant_id == tenant_id
            and all(term in entry.summary.lower() for term in terms)
        ]
        matches.sort(key=lambda entry: entry.recorded_at, reverse=True)
        return tuple(matches[:limit])


@final
class SqliteMemoryStore:
    """Mutable SQLite adapter that keeps tenant filtering in the storage query."""

    def __init__(self, path: Path) -> None:
        """Create the schema at the explicitly supplied local path."""
        path.parent.mkdir(parents=True, exist_ok=True)
        self._path: Path = path
        with closing(sqlite3.connect(self._path)) as connection, connection:
            _ = connection.execute(
                """
                CREATE TABLE IF NOT EXISTS agent_memory_v2 (
                    tenant_id TEXT NOT NULL,
                    memory_id TEXT NOT NULL,
                    case_id TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    recorded_at TEXT NOT NULL,
                    PRIMARY KEY (tenant_id, memory_id)
                )
                """
            )

    def record(self, entry: MemoryEntry) -> None:
        """Upsert an entry without retaining an open database connection."""
        with closing(sqlite3.connect(self._path)) as connection, connection:
            _ = connection.execute(
                """
                INSERT INTO agent_memory_v2 (
                    tenant_id, memory_id, case_id, summary, outcome, recorded_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(tenant_id, memory_id) DO UPDATE SET
                    case_id = excluded.case_id,
                    summary = excluded.summary,
                    outcome = excluded.outcome,
                    recorded_at = excluded.recorded_at
                """,
                (
                    entry.tenant_id,
                    entry.memory_id,
                    entry.case_id,
                    entry.summary,
                    entry.outcome,
                    entry.recorded_at.isoformat(),
                ),
            )

    def search(self, tenant_id: str, query: str, limit: int) -> tuple[MemoryEntry, ...]:
        """Return lexical matches after SQL-level tenant isolation."""
        if limit < 1:
            return ()
        terms = tuple(term.lower() for term in query.split() if term)
        if not terms:
            return ()
        with closing(sqlite3.connect(self._path)) as connection:
            rows: list[object] = connection.execute(
                """
                SELECT memory_id, tenant_id, case_id, summary, outcome, recorded_at
                FROM agent_memory_v2
                WHERE tenant_id = ?
                ORDER BY recorded_at DESC
                """,
                (tenant_id,),
            ).fetchall()
        entries = [_memory_entry_from_row(row) for row in rows]
        matches = [
            entry
            for entry in entries
            if all(term in entry.summary.lower() for term in terms)
        ]
        return tuple(matches[:limit])


class MemoryRowDecodeError(RuntimeError):
    """Raised when persisted memory does not match the table's text contract."""


def _memory_entry_from_row(row: object) -> MemoryEntry:
    """Decode one database row after verifying every storage boundary value."""
    if not _is_storage_row(row) or len(row) != _MEMORY_ROW_LENGTH:
        raise MemoryRowDecodeError(_MEMORY_ROW_COUNT_ERROR)
    memory_id, tenant_id, case_id, summary, outcome, recorded_at = (
        _required_text(value) for value in row
    )
    try:
        parsed_recorded_at = datetime.fromisoformat(recorded_at)
    except ValueError as error:
        raise MemoryRowDecodeError(_MEMORY_RECORDED_AT_ERROR) from error
    return MemoryEntry(
        memory_id=memory_id,
        tenant_id=tenant_id,
        case_id=case_id,
        summary=summary,
        outcome=outcome,
        recorded_at=parsed_recorded_at,
    )


def _required_text(value: object) -> str:
    """Return one required database text value or stop on corrupted storage."""
    if isinstance(value, str):
        return value
    raise MemoryRowDecodeError(_MEMORY_TEXT_ERROR)


def _is_storage_row(value: object) -> TypeGuard[tuple[object, ...]]:
    """Narrow an untyped sqlite row before its values receive validation."""
    return isinstance(value, tuple)
