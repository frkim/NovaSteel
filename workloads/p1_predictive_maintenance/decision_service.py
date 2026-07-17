"""Human-review and immutable audit support for P1 maintenance predictions."""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from datetime import datetime, timezone
from uuid import NAMESPACE_URL, uuid4, uuid5

from novasteel_core.models import (
    AuditRecord,
    AuditSubjectType,
    DecisionSubjectType,
    DecisionType,
    HumanDecision,
    Origin,
    Prediction,
    RetentionClass,
    ReviewerRole,
)

LOGIC_VERSION = "p1-human-review-v1"


class ImmutableAuditError(RuntimeError):
    """Raised when code attempts to alter an existing audit entry."""


class AuditLog(Sequence[AuditRecord]):
    """Append-only in-memory audit log used by local tests and notebook wrappers."""

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


def _now(decided_at: datetime | None = None) -> datetime:
    if decided_at is None:
        return datetime.now(timezone.utc)
    return decided_at if decided_at.tzinfo else decided_at.replace(tzinfo=timezone.utc)


def proposed_work_order_id(prediction: Prediction) -> str:
    """Return a proposed work-order id only; no MES/EAM action is executed."""
    return f"WO-PROP-{prediction.prediction_id[:8].upper()}"


def audit_prediction_raised(prediction: Prediction, audit_log: AuditLog) -> AuditRecord:
    """Append the immutable audit entry for a raised prediction."""
    record = AuditRecord(
        audit_id=str(uuid5(NAMESPACE_URL, f"audit:{prediction.prediction_id}:raised")),
        subject_type=AuditSubjectType.Prediction,
        subject_id=prediction.prediction_id,
        site=prediction.site,
        action="PredictionRaised",
        inputs_ref=[prediction.input_window_ref or ""],
        model_or_logic_version=prediction.model_version,
        output=prediction.model_dump(by_alias=True, mode="json"),
        reviewer_id=None,
        rationale="Prediction raised for human maintenance review; no automatic actuation.",
        timestamp=prediction.predicted_at,
        origin=prediction.origin,
        retention_class=RetentionClass.PredictionDecisionAudit,
    )
    audit_log.append(record)
    return record


def record_human_decision(
    prediction: Prediction,
    *,
    decision: DecisionType,
    reviewer_id: str,
    rationale: str,
    audit_log: AuditLog,
    decided_at: datetime | None = None,
    resulting_work_order_id: str | None = None,
) -> HumanDecision:
    """Record a confirm/reject decision and append the traceability audit entry."""
    decided_at = _now(decided_at)
    work_order_id = resulting_work_order_id
    if decision == DecisionType.Confirm and work_order_id is None:
        work_order_id = proposed_work_order_id(prediction)

    decision_id = str(uuid4())
    human_decision = HumanDecision(
        decision_id=decision_id,
        subject_type=DecisionSubjectType.Prediction,
        subject_id=prediction.prediction_id,
        site=prediction.site,
        decision=decision,
        reviewer_id=reviewer_id,
        reviewer_role=ReviewerRole.Maintenance,
        rationale=rationale,
        decided_at=decided_at,
        resulting_work_order_id=work_order_id,
    )
    action = "DecisionConfirmed" if decision == DecisionType.Confirm else "DecisionRejected"
    audit_log.append(AuditRecord(
        audit_id=str(uuid4()),
        subject_type=AuditSubjectType.HumanDecision,
        subject_id=decision_id,
        site=prediction.site,
        action=action,
        inputs_ref=[ref for ref in (prediction.input_window_ref, prediction.prediction_id) if ref],
        model_or_logic_version=LOGIC_VERSION,
        output={
            "humanDecision": human_decision.model_dump(by_alias=True, mode="json"),
            "prediction": prediction.model_dump(by_alias=True, mode="json"),
            "proposedOnly": True,
            "noAutomaticActuation": True,
        },
        reviewer_id=reviewer_id,
        rationale=rationale,
        timestamp=decided_at,
        origin=Origin.Synthetic if prediction.origin == Origin.Synthetic else Origin.Real,
        retention_class=RetentionClass.PredictionDecisionAudit,
    ))
    return human_decision
