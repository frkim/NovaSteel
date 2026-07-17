"""Human-review and immutable audit support for P3 quality predictions (Constitution I/II)."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import NAMESPACE_URL, uuid4, uuid5

from novasteel_core.audit import AuditLog
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

LOGIC_VERSION = "p3-human-review-v1"


def _now(decided_at: datetime | None = None) -> datetime:
    if decided_at is None:
        return datetime.now(timezone.utc)
    return decided_at if decided_at.tzinfo else decided_at.replace(tzinfo=timezone.utc)


def audit_quality_prediction(prediction: Prediction, audit_log: AuditLog) -> AuditRecord:
    """Append the immutable audit entry for a raised quality/SPC prediction."""
    record = AuditRecord(
        audit_id=str(uuid5(NAMESPACE_URL, f"audit:{prediction.prediction_id}:raised")),
        subject_type=AuditSubjectType.Prediction,
        subject_id=prediction.prediction_id,
        site=prediction.site,
        action="QualityPredictionRaised",
        inputs_ref=[prediction.input_window_ref or ""],
        model_or_logic_version=prediction.model_version,
        output=prediction.model_dump(by_alias=True, mode="json"),
        reviewer_id=None,
        rationale="Quality prediction raised for metallurgist review; no automatic process change.",
        timestamp=prediction.predicted_at,
        origin=prediction.origin,
        retention_class=RetentionClass.PredictionDecisionAudit,
    )
    audit_log.append(record)
    return record


def record_quality_decision(
    prediction: Prediction,
    *,
    decision: DecisionType,
    reviewer_id: str,
    rationale: str,
    audit_log: AuditLog,
    decided_at: datetime | None = None,
) -> HumanDecision:
    """Record a confirm/edit/reject decision and append the traceability audit entry."""
    decided_at = _now(decided_at)
    decision_id = str(uuid4())
    human_decision = HumanDecision(
        decision_id=decision_id,
        subject_type=DecisionSubjectType.Prediction,
        subject_id=prediction.prediction_id,
        site=prediction.site,
        decision=decision,
        reviewer_id=reviewer_id,
        reviewer_role=ReviewerRole.Quality,
        rationale=rationale,
        decided_at=decided_at,
    )
    action = {
        DecisionType.Confirm: "QualityDecisionConfirmed",
        DecisionType.Edit: "QualityDecisionEdited",
        DecisionType.Reject: "QualityDecisionRejected",
    }[decision]
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
            "noAutomaticActuation": True,
        },
        reviewer_id=reviewer_id,
        rationale=rationale,
        timestamp=decided_at,
        origin=Origin.Synthetic if prediction.origin == Origin.Synthetic else Origin.Real,
        retention_class=RetentionClass.PredictionDecisionAudit,
    ))
    return human_decision
