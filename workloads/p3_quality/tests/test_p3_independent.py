from __future__ import annotations

from datetime import datetime, timezone

import pytest
from novasteel_core.audit import AuditLog, ImmutableAuditError
from novasteel_core.models import (
    AuditSubjectType,
    DecisionType,
    Origin,
    Pillar,
    PredictionKind,
    PredictionStatus,
    RecommendationStatus,
)

from workloads.p3_quality.decision_service import (
    audit_quality_prediction,
    record_quality_decision,
)
from workloads.p3_quality.generate_quality_scenario import generate_quality_scenario
from workloads.p3_quality.quality_model import (
    MODEL_VERSION,
    baseline_yield,
    predict_heat,
    recommended_yield,
    score_batch,
    spc_drift_prediction,
    yield_uplift,
)
from workloads.p3_quality.spc import control_limits, first_drift

YIELD_TARGET_UPLIFT = 0.08  # SC-004: +8% high-grade yield


def test_predicted_matches_actual_outcome_per_heat() -> None:
    heats = generate_quality_scenario()
    assessments = score_batch(heats)
    assert len(assessments) == len(heats)
    for a, h in zip(assessments, heats):
        assert a.prediction.kind == PredictionKind.QualityOutcome
        assert a.prediction.pillar == Pillar.Quality
        assert a.prediction.heat_id == h.heat_id  # predicted-vs-actual linkage per heat
        assert a.predicted_high_grade == a.actual_high_grade  # model tracks ground truth
        assert a.prediction.status == PredictionStatus.Raised
        assert a.prediction.origin == Origin.Synthetic


def test_recommendations_recover_at_least_8pct_yield() -> None:
    assessments = score_batch(generate_quality_scenario())
    base = baseline_yield(assessments)
    improved = recommended_yield(assessments)
    assert improved > base
    assert yield_uplift(assessments) >= YIELD_TARGET_UPLIFT
    assert improved <= 1.0


def test_only_recoverable_at_risk_heats_get_a_reviewable_recommendation() -> None:
    assessments = score_batch(generate_quality_scenario())
    for a in assessments:
        if a.recommendation is not None:
            assert a.at_risk and a.recoverable
            assert a.recommendation.status == RecommendationStatus.Proposed  # human-in-the-loop
            assert a.recommendation.related_heat_id == a.prediction.heat_id
            assert a.recommendation.rationale
            assert a.recommendation.content_safety_passed is True
    # At least one non-recoverable at-risk heat exists and gets NO auto-fix.
    assert any(a.at_risk and not a.recoverable and a.recommendation is None for a in assessments)


def test_spc_detects_late_temperature_drift() -> None:
    heats = generate_quality_scenario()
    drift = spc_drift_prediction(heats, metric="tapping_temp_c", in_control_count=10)
    assert drift is not None
    assert drift.kind == PredictionKind.SpcDrift
    assert drift.status == PredictionStatus.Raised
    assert drift.evidence
    # Drift is raised on a late heat (the injected upward trend starts at sequence 15).
    late_ids = {h.heat_id for h in heats if h.sequence >= 15}
    assert drift.heat_id in late_ids


def test_stable_process_raises_no_spc_drift() -> None:
    # A perfectly flat series has zero sigma; a constant equal to the mean stays in control.
    from workloads.p3_quality.spc import ControlLimits
    limits = ControlLimits(mean=1650.0, sigma=3.0)
    assert first_drift([1650.0, 1651.0, 1649.0, 1650.5, 1650.0], limits) is None


def test_prediction_contract_shape_camel_case() -> None:
    heats = generate_quality_scenario()
    payload = predict_heat(heats[0]).prediction.model_dump(by_alias=True, mode="json")
    assert set(payload) == {
        "predictionId", "pillar", "site", "assetId", "heatId", "kind",
        "timeToFailureDays", "predictedAt", "confidence", "evidence",
        "modelVersion", "inputWindowRef", "origin", "status",
    }
    assert payload["kind"] == "QualityOutcome"
    assert payload["modelVersion"] == MODEL_VERSION
    assert 0.0 <= payload["confidence"] <= 1.0


def test_quality_audit_and_decision_flow_is_immutable() -> None:
    heats = generate_quality_scenario()
    at_risk = next(a for a in score_batch(heats) if a.at_risk and a.recoverable)
    log = AuditLog()

    raised = audit_quality_prediction(at_risk.prediction, log)
    assert raised.subject_type == AuditSubjectType.Prediction
    assert raised.origin == Origin.Synthetic

    decision = record_quality_decision(
        at_risk.prediction,
        decision=DecisionType.Confirm,
        reviewer_id="metallurgist-01",
        rationale="Desulphurization extension approved for this heat.",
        audit_log=log,
        decided_at=datetime(2026, 4, 6, 12, 0, tzinfo=timezone.utc),
    )
    assert decision.decision == DecisionType.Confirm
    assert len(log) == 2
    assert log.entries[-1].subject_type == AuditSubjectType.HumanDecision
    assert log.entries[-1].output["noAutomaticActuation"] is True

    with pytest.raises(ImmutableAuditError):
        log.clear()
    with pytest.raises(ImmutableAuditError):
        log[0] = raised  # type: ignore[index]
