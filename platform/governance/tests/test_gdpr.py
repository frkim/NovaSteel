from __future__ import annotations

import pathlib
import sys
from datetime import datetime, timezone

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "platform"))

from novasteel_core.audit import AuditLog, ImmutableAuditError  # noqa: E402
from governance.gdpr import KnowledgeStore, PersonalContentItem, erase_subject  # noqa: E402


def _store():
    return KnowledgeStore(items=[
        PersonalContentItem("k1", "operator-jane", "DE", "Jane said: reline at 21 days", "Reline threshold ~21 days"),
        PersonalContentItem("k2", "operator-jane", "DE", "Jane's phone 555-1234", "Contact captured"),
        PersonalContentItem("k3", "operator-bob", "LU", "Bob's notes", "Furnace notes"),
    ])


def test_erasure_removes_raw_personal_content_keeps_derived() -> None:
    store = _store()
    log = AuditLog()
    n = erase_subject("operator-jane", store, log, erased_at=datetime(2026, 7, 18, tzinfo=timezone.utc))

    assert n == 2
    jane_items = [i for i in store.items if i.subject_id == "operator-jane"]
    assert all(i.raw_personal_content == "" and i.erased for i in jane_items)
    assert all(i.derived_content for i in jane_items)  # de-identified knowledge retained
    # Other subjects untouched.
    bob = next(i for i in store.items if i.subject_id == "operator-bob")
    assert bob.raw_personal_content == "Bob's notes" and not bob.erased


def test_erasure_appends_audit_and_never_deletes_history() -> None:
    store = _store()
    log = AuditLog()
    erase_subject("operator-jane", store, log)

    assert len(log) == 2  # one audit per erased item
    assert all(a.action == "PersonalContentErased" for a in log.entries)
    assert all(a.output["derivedContentRetained"] is True for a in log.entries)
    # Audit records are exempt from erasure — the log stays append-only.
    with pytest.raises(ImmutableAuditError):
        log.pop()
    with pytest.raises(ImmutableAuditError):
        log.clear()


def test_re_erasure_is_idempotent() -> None:
    store = _store()
    log = AuditLog()
    erase_subject("operator-jane", store, log)
    n2 = erase_subject("operator-jane", store, log)  # already erased
    assert n2 == 0
    assert len(log) == 2
