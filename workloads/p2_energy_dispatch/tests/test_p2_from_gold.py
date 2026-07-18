from __future__ import annotations

from datetime import datetime, timezone

from novasteel_core.models import MarketSignal, Origin
from workloads.p2_energy_dispatch.dispatch_model import Job, build_energy_plan
from workloads.p2_energy_dispatch.from_gold import job_from_row, market_signal_from_row
from workloads.p2_energy_dispatch.generate_energy_scenario import generate_energy_scenario


def test_market_signal_from_medallion_row_snake_case() -> None:
    # gold_market_signals row shape produced by the medallion pivot.
    row = {
        "market": "LU", "timestamp": datetime(2026, 7, 18, 2, 0, tzinfo=timezone.utc),
        "spot_price_eur_mwh": 42.0, "grid_carbon_grams_per_kwh": 175.0,
        "origin": "Synthetic", "source_ids": ["sim:LU-UTL1"], "_layer": "gold",
    }
    ms = market_signal_from_row(row)
    assert isinstance(ms, MarketSignal)
    assert ms.market == "LU"
    assert ms.spot_price_eur_mwh == 42.0
    assert ms.grid_carbon_grams_per_kwh == 175.0


def test_job_from_row_camel_case() -> None:
    row = {
        "jobId": "HEAT-LU-01", "furnaceId": "LU-EAF1", "site": "LU", "tons": 150.0,
        "productionMwh": 20.0, "durationSlots": 2, "readySlot": 4, "deadlineSlot": 47,
        "origin": "Synthetic",
    }
    job = job_from_row(row)
    assert isinstance(job, Job)
    assert job.job_id == "HEAT-LU-01" and job.furnace_id == "LU-EAF1"
    assert job.duration_slots == 2 and job.origin == Origin.Synthetic


def test_end_to_end_plan_from_adapted_rows_meets_targets() -> None:
    # Materialize the scenario as Gold rows, adapt them back, and confirm the plan still holds.
    s = generate_energy_scenario()
    market_rows = [m.model_dump(by_alias=False) for m in s.market]  # snake_case like the mart
    job_rows = [{
        "jobId": j.job_id, "furnaceId": j.furnace_id, "site": j.site, "tons": j.tons,
        "productionMwh": j.production_mwh, "durationSlots": j.duration_slots,
        "readySlot": j.ready_slot, "deadlineSlot": j.deadline_slot, "origin": j.origin.value,
    } for j in s.jobs]

    market = [market_signal_from_row(r) for r in market_rows]
    jobs = [job_from_row(r) for r in job_rows]
    plan = build_energy_plan(jobs, market, base_time=s.base_time)

    assert plan.expected_energy_per_ton < plan.baseline_comparison.baseline_energy_per_ton
    assert plan.expected_co2_per_ton < plan.baseline_comparison.baseline_co2_per_ton
    assert len(plan.scheduled_jobs) == len(s.jobs)
