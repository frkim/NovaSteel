"""Shared append-only audit log (Constitution II — end-to-end traceability).

An immutable, in-memory sequence of ``AuditRecord`` used by the pillar decision
services and Fabric notebook wrappers. Every mutation that would alter or remove an
existing entry raises ``ImmutableAuditError`` so audit history can only ever grow —
mirroring the immutability guarantee of the production Purview/OneLake audit store.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence

from novasteel_core.models import AuditRecord


class ImmutableAuditError(RuntimeError):
    """Raised when code attempts to alter or remove an existing audit entry."""


class AuditLog(Sequence[AuditRecord]):
    """Append-only audit log; entries are deep-copied on append and never mutated."""

    def __init__(self) -> None:
        self._entries: tuple[AuditRecord, ...] = ()

    def append(self, record: AuditRecord) -> None:
        self._entries = (*self._entries, record.model_copy(deep=True))

    @property
    def entries(self) -> tuple[AuditRecord, ...]:
        return self._entries

    def __len__(self) -> int:
        return len(self._entries)

    def __iter__(self) -> Iterator[AuditRecord]:
        return iter(self._entries)

    def __getitem__(self, index):  # type: ignore[no-untyped-def]
        return self._entries[index]

    def __setitem__(self, index, value) -> None:  # type: ignore[no-untyped-def]
        raise ImmutableAuditError("audit entries are append-only; replacement is forbidden")

    def __delitem__(self, index) -> None:  # type: ignore[no-untyped-def]
        raise ImmutableAuditError("audit entries are append-only; deletion is forbidden")

    def clear(self) -> None:
        raise ImmutableAuditError("audit entries are append-only; clearing is forbidden")

    def pop(self, index: int = -1) -> AuditRecord:
        raise ImmutableAuditError("audit entries are append-only; removal is forbidden")

    def remove(self, record: AuditRecord) -> None:
        raise ImmutableAuditError("audit entries are append-only; removal is forbidden")

    def replace(self, index: int, record: AuditRecord) -> None:
        raise ImmutableAuditError("audit entries are append-only; replacement is forbidden")
