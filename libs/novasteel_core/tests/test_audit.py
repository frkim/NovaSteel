from __future__ import annotations

from datetime import datetime, timezone

import pytest
from novasteel_core.audit import AuditLog, ImmutableAuditError
from novasteel_core.models import AuditRecord, AuditSubjectType, Origin, RetentionClass


def _record(i: int) -> AuditRecord:
    return AuditRecord(
        audit_id=f"audit-{i}",
        subject_type=AuditSubjectType.Prediction,
        subject_id=f"subj-{i}",
        site="LU",
        action="Raised",
        inputs_ref=["ref"],
        model_or_logic_version="v1",
        output={"i": i},
        timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
        origin=Origin.Synthetic,
        retention_class=RetentionClass.PredictionDecisionAudit,
    )


def test_append_only_and_deep_copied() -> None:
    log = AuditLog()
    r = _record(1)
    log.append(r)
    assert len(log) == 1
    # Entry is deep-copied: mutating the source output must not affect the stored record.
    r.output["i"] = 999
    assert log.entries[0].output["i"] == 1


def test_mutation_is_forbidden() -> None:
    log = AuditLog()
    log.append(_record(1))
    with pytest.raises(ImmutableAuditError):
        log.pop()
    with pytest.raises(ImmutableAuditError):
        log.clear()
    with pytest.raises(ImmutableAuditError):
        del log[0]
    with pytest.raises(ImmutableAuditError):
        log[0] = _record(2)  # type: ignore[index]
    with pytest.raises(ImmutableAuditError):
        log.remove(log.entries[0])
    assert len(log) == 1  # unchanged
