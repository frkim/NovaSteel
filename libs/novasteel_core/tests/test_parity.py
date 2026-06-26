"""Cross-language parity: Python models must round-trip the shared golden fixtures."""

import json
import pathlib
from datetime import datetime
from typing import Any

import pytest
from pydantic import ValidationError

from novasteel_core.models import (
    AuditRecord,
    AuditSubjectType,
    DecisionSubjectType,
    DecisionType,
    EnergyPlan,
    EnergyPlanStatus,
    HumanDecision,
    MarketSignal,
    Origin,
    Pillar,
    Prediction,
    PredictionKind,
    PredictionStatus,
    Recommendation,
    RecommendationPillar,
    RecommendationStatus,
    RetentionClass,
    ReviewerRole,
    Solver,
    TelemetryReading,
)

FIX = pathlib.Path(__file__).parents[2] / "fixtures"


def _read_json_lines(name: str) -> list[dict]:
    return [
        json.loads(line)
        for line in (FIX / name).read_text().splitlines()
        if line.strip()
    ]


DATETIME_KEYS = {
    "timestamp",
    "predictedAt",
    "from",
    "to",
    "slotStart",
    "slotEnd",
    "deadline",
    "decidedAt",
}


def _normalize(value: Any, key: str | None = None) -> Any:
    """Normalize timestamp string differences (C# 'Z' vs pydantic '+00:00')."""
    if isinstance(value, dict):
        return {k: _normalize(v, k) for k, v in value.items()}
    if isinstance(value, list):
        return [_normalize(item, key) for item in value]
    if key in DATETIME_KEYS and isinstance(value, str):
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    return value


def _dump(model) -> dict:
    return json.loads(model.model_dump_json(by_alias=True))


def test_telemetry_round_trips_camel():
    raw = _read_json_lines("telemetry_reading.json")[0]
    r = TelemetryReading.model_validate(raw)
    assert r.asset_id == "LU-BF1"
    assert r.metric == "ThermocoupleTemp"
    assert r.origin is Origin.Real
    assert r.source_id == "ot:LU-historian"
    dumped = _dump(r)
    assert _normalize(dumped) == _normalize(raw)


def test_telemetry_preserves_synthetic_origin_and_source_id():
    raws = _read_json_lines("telemetry_reading.json")
    synthetic = [TelemetryReading.model_validate(raw) for raw in raws if raw["origin"] == "Synthetic"]

    assert len(synthetic) == 1
    assert synthetic[0].origin is Origin.Synthetic
    assert synthetic[0].source_id == "sim:steel_factory_simulator@v1"
    dumped = _dump(synthetic[0])
    assert dumped["origin"] == "Synthetic"
    assert dumped["sourceId"] == "sim:steel_factory_simulator@v1"


def test_telemetry_missing_provenance_uses_non_breaking_defaults():
    raw = {
        "assetId": "LU-BF1",
        "assetType": "BlastFurnace",
        "site": "LU",
        "metric": "ThermocoupleTemp",
        "value": 1487.2,
        "unit": "C",
        "timestamp": "2026-06-21T10:00:00Z",
        "quality": "Good",
    }

    r = TelemetryReading.model_validate(raw)

    assert r.origin is Origin.Real
    assert r.source_id == ""


def test_market_round_trips_camel():
    raw = _read_json_lines("market_signal.json")[0]
    m = MarketSignal.model_validate(raw)
    assert m.market == "LU"
    assert m.spot_price_eur_mwh == 92.4
    dumped = _dump(m)
    assert _normalize(dumped) == _normalize(raw)


def test_prediction_round_trips_fixture_and_contract_values():
    raw = _read_json_lines("prediction.json")[0]
    prediction = Prediction.model_validate(raw)

    assert prediction.pillar is Pillar.Maintenance
    assert prediction.kind is PredictionKind.LiningFailureRisk
    assert prediction.time_to_failure_days >= 21
    assert prediction.status is PredictionStatus.Raised
    assert prediction.origin is Origin.Synthetic
    dumped = _dump(prediction)
    assert dumped["kind"] == "LiningFailureRisk"
    assert isinstance(dumped["kind"], str)
    assert _normalize(dumped) == _normalize(raw)


def test_recommendation_round_trips_fixture_and_string_enums():
    raw = _read_json_lines("recommendation.json")[0]
    recommendation = Recommendation.model_validate(raw)

    assert recommendation.pillar is RecommendationPillar.Knowledge
    assert recommendation.status is RecommendationStatus.Approved
    assert recommendation.citations and recommendation.citations[0].source_id.startswith("knowledge:")
    dumped = _dump(recommendation)
    assert dumped["pillar"] == "Knowledge"
    assert dumped["status"] == "Approved"
    assert _normalize(dumped) == _normalize(raw)


def test_energy_plan_round_trips_fixture_and_string_enums():
    raw = _read_json_lines("energy_plan.json")[0]
    plan = EnergyPlan.model_validate(raw)

    assert plan.solver is Solver.Milp
    assert plan.status is EnergyPlanStatus.Proposed
    dumped = _dump(plan)
    assert dumped["planningHorizon"]["from"] == raw["planningHorizon"]["from"]
    assert dumped["solver"] == "Milp"
    assert _normalize(dumped) == _normalize(raw)


def test_human_decision_round_trips_fixture_and_string_enums():
    raw = _read_json_lines("human_decision.json")[0]
    decision = HumanDecision.model_validate(raw)

    assert decision.subject_type is DecisionSubjectType.Prediction
    assert decision.decision is DecisionType.Confirm
    assert decision.reviewer_role is ReviewerRole.Maintenance
    dumped = _dump(decision)
    assert dumped["subjectType"] == "Prediction"
    assert dumped["decision"] == "Confirm"
    assert _normalize(dumped) == _normalize(raw)


def test_audit_record_round_trips_fixture_and_preserves_synthetic_origin():
    raw = _read_json_lines("audit_record.json")[0]
    audit = AuditRecord.model_validate(raw)

    assert audit.subject_type is AuditSubjectType.Prediction
    assert audit.origin is Origin.Synthetic
    assert audit.retention_class is RetentionClass.PredictionDecisionAudit
    dumped = _dump(audit)
    assert dumped["retentionClass"] == "PredictionDecisionAudit"
    assert dumped["origin"] == "Synthetic"
    assert _normalize(dumped) == _normalize(raw)


@pytest.mark.parametrize(
    ("model", "field_name"),
    [
        (Prediction, "predictionId"),
        (Recommendation, "summary"),
        (EnergyPlan, "energyPlanId"),
        (HumanDecision, "reviewerId"),
        (AuditRecord, "modelOrLogicVersion"),
    ],
)
def test_required_string_fields_reject_null(model, field_name):
    raw = _read_json_lines(
        {
            Prediction: "prediction.json",
            Recommendation: "recommendation.json",
            EnergyPlan: "energy_plan.json",
            HumanDecision: "human_decision.json",
            AuditRecord: "audit_record.json",
        }[model]
    )[0]
    raw[field_name] = None

    with pytest.raises(ValidationError):
        model.model_validate(raw)
