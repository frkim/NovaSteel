"""T026 provenance-propagation gate + T032 data-quality gate (Constitution VIII/IX).

Authored test-first: proves that `origin`/`sourceId`/`site`/`quality` survive
Bronze -> Silver -> Gold and that synthetic-origin data is bucketed separately and
never counted in a real KPI. Reads the SAME golden fixtures the contract tests use.

Run: `python -m pytest platform/medallion/tests -q`
"""

from __future__ import annotations

import json
import pathlib
import sys
from datetime import datetime, timezone

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
# `platform` is a Python stdlib module, so we do NOT make it a package; instead put
# the `platform/` folder on sys.path and import the `medallion` package directly.
sys.path.insert(0, str(REPO_ROOT / "platform"))

from novasteel_core.models import Origin, TelemetryReading  # noqa: E402
from medallion.transforms import (  # noqa: E402
    PROVENANCE_FIELDS,
    to_bronze,
    to_gold_kpi,
    to_silver,
)
from medallion.data_quality import DataQualityError, run_all  # noqa: E402

FIXTURE = REPO_ROOT / "libs" / "fixtures" / "telemetry_reading.json"
# Fixed processing clock so freshness/staleness is deterministic (fixtures are dated 2026-06-21).
NOW = datetime(2026, 6, 21, 10, 5, 0, tzinfo=timezone.utc)


def _load_readings() -> list[TelemetryReading]:
    lines = [ln for ln in FIXTURE.read_text(encoding="utf-8").splitlines() if ln.strip()]
    return [TelemetryReading.model_validate(json.loads(ln)) for ln in lines]


def test_fixture_has_real_and_synthetic() -> None:
    readings = _load_readings()
    origins = {r.origin for r in readings}
    assert Origin.Real in origins and Origin.Synthetic in origins, "need both origins to exercise IX"


def test_provenance_survives_bronze_silver_gold() -> None:
    readings = _load_readings()
    bronze = to_bronze(readings, ingested_at=NOW)
    silver = to_silver(bronze, now=NOW)

    # Every source reading's (site, metric, origin, sourceId) is still present downstream.
    def prov_set(rows):
        return {(r["site"], r["metric"], r["origin"], r["source_id"]) for r in rows}

    src = {(r.site, r.metric, r.origin.value, r.source_id) for r in readings}
    assert prov_set(bronze) == src
    assert prov_set(silver) == src

    for layer in (bronze, silver):
        for rec in layer:
            for field in PROVENANCE_FIELDS:
                assert rec.get(field) not in (None, ""), f"{field} lost in {rec['_layer']}"


def test_synthetic_excluded_from_real_gold_kpi() -> None:
    readings = _load_readings()
    gold = to_gold_kpi(to_silver(to_bronze(readings, ingested_at=NOW), now=NOW))

    classes = {m["data_class"] for m in gold}
    assert "synthetic" in classes, "synthetic reading must produce a synthetic-classed mart"

    # No real mart may aggregate a synthetic source.
    for mart in gold:
        if mart["data_class"] == "real":
            assert all(not sid.startswith("sim:") for sid in mart["source_ids"])
        else:
            assert mart["count"] >= 1


def test_full_data_quality_gate_passes() -> None:
    readings = _load_readings()
    bronze = to_bronze(readings, ingested_at=NOW)
    silver = to_silver(bronze, now=NOW)
    gold = to_gold_kpi(silver)
    run_all(bronze, silver, gold)  # must not raise


def test_missing_provenance_is_rejected() -> None:
    readings = _load_readings()
    bronze = to_bronze(readings, ingested_at=NOW)
    bronze[0]["source_id"] = ""  # simulate a provenance drop
    with pytest.raises(DataQualityError):
        run_all(bronze, to_silver(bronze, now=NOW), [])
