from __future__ import annotations

from datetime import datetime, timezone

import pytest
from novasteel_core.models import (
    AuditSubjectType,
    DecisionType,
    Origin,
    Pillar,
    PredictionKind,
    PredictionStatus,
    RetentionClass,
)

from workloads.p1_predictive_maintenance.decision_service import (
    AuditLog,
    ImmutableAuditError,
    audit_prediction_raised,
    record_human_decision,
)
from workloads.p1_predictive_maintenance.generate_degrading_furnace import (
    generate_degrading_furnace,
    generate_healthy_furnace,
    readings_up_to,
)
from workloads.p1_predictive_maintenance.rul_model import (
    EXPEDITED_REVIEW_PATH,
    MIN_ADVANCE_WARNING_DAYS,
    MODEL_VERSION,
    score_rul,
)


def test_independent_advance_warning_confirm_and_audit_flow() -> None:
    readings = generate_degrading_furnace(failure_day=60, horizon_days=60, seed=7)
    replay_window = readings_up_to(readings, 39)

    assessment = score_rul(replay_window)

    assert assessment is not None
    prediction = assessment.prediction
    assert prediction.pillar == Pillar.Maintenance
    assert prediction.kind == PredictionKind.LiningFailureRisk
    assert prediction.status == PredictionStatus.Raised
    assert prediction.time_to_failure_days is not None
    assert prediction.time_to_failure_days >= MIN_ADVANCE_WARNING_DAYS
    assert prediction.evidence
    assert prediction.model_version == MODEL_VERSION
    assert prediction.input_window_ref
    assert prediction.origin == Origin.Synthetic
    assert not assessment.escalated

    audit_log = AuditLog()
    raised_record = audit_prediction_raised(prediction, audit_log)
    decision = record_human_decision(
        prediction,
        decision=DecisionType.Confirm,
        reviewer_id="maintenance-engineer-01",
        rationale="Thermal trend matches lining-wear inspection plan.",
        audit_log=audit_log,
        decided_at=datetime(2026, 2, 9, 9, 0, tzinfo=timezone.utc),
    )

    assert decision.decision == DecisionType.Confirm
    assert decision.resulting_work_order_id is not None
    assert decision.resulting_work_order_id.startswith("WO-PROP-")
    assert len(audit_log) == 2
    assert raised_record.origin == Origin.Synthetic

    decision_audit = audit_log.entries[-1]
    assert decision_audit.subject_type == AuditSubjectType.HumanDecision
    assert decision_audit.action == "DecisionConfirmed"
    assert decision_audit.retention_class == RetentionClass.PredictionDecisionAudit
    assert decision_audit.origin == Origin.Synthetic
    assert decision_audit.output["proposedOnly"] is True
    assert decision_audit.output["noAutomaticActuation"] is True
    assert decision_audit.output["humanDecision"]["resultingWorkOrderId"] == decision.resulting_work_order_id

    with pytest.raises(ImmutableAuditError):
        audit_log.pop()
    with pytest.raises(ImmutableAuditError):
        audit_log.clear()
    with pytest.raises(ImmutableAuditError):
        audit_log[0] = decision_audit  # type: ignore[index]
    with pytest.raises(ImmutableAuditError):
        del audit_log[0]


def test_healthy_furnace_raises_no_false_alarm() -> None:
    readings = generate_healthy_furnace(horizon_days=60, seed=99)

    assert score_rul(readings) is None


def test_sub_21_day_prediction_is_escalated() -> None:
    readings = generate_degrading_furnace(failure_day=60, horizon_days=60, seed=7)
    late_window = readings_up_to(readings, 45)

    assessment = score_rul(late_window)

    assert assessment is not None
    assert assessment.prediction.time_to_failure_days is not None
    assert assessment.prediction.time_to_failure_days < MIN_ADVANCE_WARNING_DAYS
    assert assessment.escalated is True
    assert assessment.priority == "High"
    assert assessment.review_path == EXPEDITED_REVIEW_PATH
    assert assessment.escalation_reason
    assert assessment.prediction.origin == Origin.Synthetic


def test_prediction_contract_shape_uses_camel_case_fields() -> None:
    assessment = score_rul(readings_up_to(generate_degrading_furnace(), 39))

    assert assessment is not None
    payload = assessment.prediction.model_dump(by_alias=True, mode="json")
    assert set(payload) == {
        "predictionId",
        "pillar",
        "site",
        "assetId",
        "heatId",
        "kind",
        "timeToFailureDays",
        "predictedAt",
        "confidence",
        "evidence",
        "modelVersion",
        "inputWindowRef",
        "origin",
        "status",
    }
    assert 0.0 <= payload["confidence"] <= 1.0
    assert payload["evidence"]
    assert payload["origin"] == "Synthetic"
