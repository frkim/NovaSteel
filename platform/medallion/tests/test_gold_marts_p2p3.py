"""P2/P3 Gold-mart derivation from simulator quality + tariff telemetry (Constitution IX).

Proves the medallion pivots the new simulator signals (SpotPriceEurMwh/GridCarbonGPerKwh and
TappingTemp/SulfurPct/InclusionIndex) into MarketSignal- and quality-feature-shaped Gold rows,
preserving provenance and only emitting fully-observed points.
"""

from __future__ import annotations

import pathlib
import sys
from datetime import datetime, timezone

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "platform"))

from medallion.transforms import (  # noqa: E402
    to_gold_market_signals,
    to_gold_quality_features,
)

TS = datetime(2026, 7, 18, 2, 0, tzinfo=timezone.utc)


def _silver(site, asset_id, metric, value, origin="Synthetic", ts=TS):
    return {
        "asset_id": asset_id, "asset_type": "BlastFurnace", "site": site, "metric": metric,
        "value": value, "unit": "", "timestamp": ts, "quality": "Good",
        "origin": origin, "source_id": f"sim:{asset_id}", "_layer": "silver",
    }


def test_market_signals_pivot_and_preserve_provenance() -> None:
    rows = [
        _silver("LU", "LU-UTL1", "SpotPriceEurMwh", 45.0),
        _silver("LU", "LU-UTL1", "GridCarbonGPerKwh", 180.0),
        _silver("DE", "DE-UTL1", "SpotPriceEurMwh", 60.0, origin="Real"),
        _silver("DE", "DE-UTL1", "GridCarbonGPerKwh", 250.0, origin="Real"),
    ]
    out = to_gold_market_signals(rows)
    assert len(out) == 2
    lu = next(r for r in out if r["market"] == "LU")
    assert lu["spot_price_eur_mwh"] == 45.0 and lu["grid_carbon_grams_per_kwh"] == 180.0
    assert lu["origin"] == "Synthetic"  # provenance preserved
    de = next(r for r in out if r["market"] == "DE")
    assert de["origin"] == "Real"


def test_market_signal_requires_both_metrics() -> None:
    rows = [_silver("LU", "LU-UTL1", "SpotPriceEurMwh", 45.0)]  # missing grid carbon
    assert to_gold_market_signals(rows) == []


def test_quality_features_pivot_all_three_signals() -> None:
    rows = [
        _silver("DE", "DE-BF1", "TappingTemp", 1650.0),
        _silver("DE", "DE-BF1", "SulfurPct", 0.007),
        _silver("DE", "DE-BF1", "InclusionIndex", 1.4),
    ]
    out = to_gold_quality_features(rows)
    assert len(out) == 1
    f = out[0]
    assert f["site"] == "DE" and f["asset_id"] == "DE-BF1"
    assert f["tapping_temp_c"] == 1650.0 and f["sulfur_pct"] == 0.007 and f["inclusion_index"] == 1.4
    assert f["origin"] == "Synthetic"


def test_quality_feature_requires_all_signals() -> None:
    rows = [
        _silver("DE", "DE-BF1", "TappingTemp", 1650.0),
        _silver("DE", "DE-BF1", "SulfurPct", 0.007),
    ]  # missing InclusionIndex
    assert to_gold_quality_features(rows) == []


def test_non_pillar_metrics_are_ignored() -> None:
    rows = [_silver("LU", "LU-BF1", "HeatFlux", 42.0)]
    assert to_gold_market_signals(rows) == []
    assert to_gold_quality_features(rows) == []
