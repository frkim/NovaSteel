from __future__ import annotations

import pathlib
import sys
from datetime import date, datetime, timezone

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
# `platform` is a Python stdlib module, so put `platform/` on sys.path and import `kpi.*`.
sys.path.insert(0, str(REPO_ROOT / "platform"))

from kpi.kpi_baseline import (  # noqa: E402
    ProductionRecord,
    compute_baseline,
    improvement_vs_baseline,
)
from kpi.generate_history import default_as_of, generate_history  # noqa: E402


def test_baseline_is_frozen_and_normalized_per_ton() -> None:
    history = generate_history(site="LU")
    as_of = default_as_of()
    baseline = compute_baseline(history, site="LU", as_of=as_of, months=12)

    assert baseline.frozen is True
    assert baseline.as_of == as_of
    assert baseline.window_start == date(2025, 5, 1)
    assert baseline.window_end == as_of
    assert baseline.total_tons > 0
    # Normalized per-ton KPIs are physically sane.
    assert 0.4 < baseline.energy_mwh_per_ton < 0.9
    assert baseline.co2_kg_per_ton > 0
    assert baseline.cost_eur_per_ton > 0
    assert 0.0 <= baseline.high_grade_yield <= 1.0
    assert round(baseline.high_grade_yield, 1) == 0.8  # generator seeds ~80% high-grade


def test_window_excludes_out_of_range_records() -> None:
    history = generate_history(site="LU")
    as_of = default_as_of()
    full = compute_baseline(history, site="LU", as_of=as_of, months=12)
    # A record before the window must not change the baseline sample set.
    older = ProductionRecord(
        timestamp=datetime(2024, 1, 1, tzinfo=timezone.utc), site="LU", tons=1000.0,
        energy_mwh=9999.0, co2_kg=9999.0, cost_eur=9999.0, high_grade=False,
    )
    with_old = compute_baseline([*history, older], site="LU", as_of=as_of, months=12)
    assert with_old.sample_count == full.sample_count
    assert with_old.energy_mwh_per_ton == full.energy_mwh_per_ton


def test_per_site_isolation() -> None:
    history = generate_history(site="LU") + generate_history(site="DE", seed=9)
    lu = compute_baseline(history, site="LU", as_of=default_as_of())
    de = compute_baseline(history, site="DE", as_of=default_as_of())
    assert lu.site == "LU" and de.site == "DE"
    # DE records never leak into LU's baseline sample count.
    lu_only = compute_baseline(generate_history(site="LU"), site="LU", as_of=default_as_of())
    assert lu.sample_count == lu_only.sample_count


def test_empty_window_raises() -> None:
    with pytest.raises(ValueError):
        compute_baseline(generate_history(site="LU"), site="ES", as_of=default_as_of())


def test_improvement_vs_baseline_pct() -> None:
    assert improvement_vs_baseline(0.86, 1.0) == 14.0
    assert improvement_vs_baseline(1.0, 0.0) == 0.0


def test_baseline_dict_is_json_shaped() -> None:
    baseline = compute_baseline(generate_history(site="LU"), site="LU", as_of=default_as_of())
    d = baseline.to_dict()
    assert d["site"] == "LU"
    assert d["frozen"] is True
    assert set(d) >= {"energyMwhPerTon", "co2KgPerTon", "costEurPerTon", "highGradeYield", "windowStart"}
