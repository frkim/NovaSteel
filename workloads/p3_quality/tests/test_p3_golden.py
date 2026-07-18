from __future__ import annotations

import json
import pathlib

from novasteel_core.models import Prediction
from workloads.p3_quality.generate_quality_scenario import generate_quality_scenario
from workloads.p3_quality.quality_model import predict_heat

GOLDEN = pathlib.Path(__file__).resolve().parents[3] / "libs" / "fixtures" / "p3_quality_prediction_golden.json"


def test_quality_prediction_matches_golden_fixture() -> None:
    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
    parsed = Prediction.model_validate(golden)
    assert parsed.kind.value == "QualityOutcome"
    assert parsed.heat_id == "HEAT-DE-004"

    heats = generate_quality_scenario()
    fresh = predict_heat(heats[3]).prediction.model_dump(by_alias=True, mode="json")
    assert fresh == golden
