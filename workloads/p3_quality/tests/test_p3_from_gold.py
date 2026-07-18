from __future__ import annotations

from datetime import datetime, timezone

from novasteel_core.models import Origin, PredictionKind
from workloads.p3_quality.from_gold import heat_from_row, heats_from_rows
from workloads.p3_quality.generate_quality_scenario import Heat
from workloads.p3_quality.quality_model import predict_heat, score_batch, spc_drift_prediction


def _row(site, asset, ts, tap, sulfur, incl):
    # gold_quality_features row shape (Spark PascalCase keys + snake feature columns).
    return {
        "Site": site, "AssetId": asset, "Timestamp": ts,
        "tapping_temp_c": tap, "sulfur_pct": sulfur, "inclusion_index": incl,
        "origin": "Synthetic",
    }


def test_heat_from_row_derives_id_grade_and_actual() -> None:
    ts = datetime(2026, 7, 18, 2, 0, tzinfo=timezone.utc)
    heat = heat_from_row(_row("DE", "DE-BF1", ts, 1650.0, 0.007, 1.4), sequence=0)
    assert isinstance(heat, Heat)
    assert heat.site == "DE"
    assert heat.heat_id.startswith("HEAT-DE-DE-BF1-")
    assert heat.grade_target == "AutoDP800"
    assert heat.tapping_temp_c == 1650.0 and heat.sulfur_pct == 0.007
    assert heat.actual_high_grade is True  # in-spec derived outcome
    assert heat.origin == Origin.Synthetic


def test_out_of_spec_row_is_not_high_grade_and_scores_at_risk() -> None:
    ts = datetime(2026, 7, 18, 2, 0, tzinfo=timezone.utc)
    heat = heat_from_row(_row("LU", "LU-BF1", ts, 1650.0, 0.015, 2.6), sequence=0)  # high S + inclusion
    assert heat.actual_high_grade is False
    a = predict_heat(heat)
    assert a.at_risk and a.recoverable
    assert a.prediction.kind == PredictionKind.QualityOutcome


def test_heats_from_rows_assigns_per_site_sequence_and_scores() -> None:
    base = datetime(2026, 7, 18, 2, 0, tzinfo=timezone.utc)
    rows = [_row("DE", "DE-BF1", base.replace(minute=m), 1650.0, 0.007, 1.4) for m in range(3)]
    heats = heats_from_rows(rows)
    assert [h.sequence for h in heats] == [0, 1, 2]
    assessments = score_batch(heats)
    assert len(assessments) == 3
    assert all(a.prediction.heat_id == h.heat_id for a, h in zip(assessments, heats))
