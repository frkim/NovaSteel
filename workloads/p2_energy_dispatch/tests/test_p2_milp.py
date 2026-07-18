from __future__ import annotations

import pytest

from workloads.p2_energy_dispatch.dispatch_model import baseline_dispatch, co2_savings_pct
from workloads.p2_energy_dispatch.generate_energy_scenario import generate_energy_scenario

pulp = pytest.importorskip("pulp")  # skip the whole module when the solver isn't installed

from workloads.p2_energy_dispatch.milp import (  # noqa: E402
    build_energy_plan_milp,
    optimize_dispatch_milp,
)
from novasteel_core.models import EnergyPlanStatus, Solver  # noqa: E402


def test_milp_beats_baseline_on_co2_and_respects_constraints() -> None:
    s = generate_energy_scenario()
    baseline = baseline_dispatch(s.jobs, s.market)
    milp = optimize_dispatch_milp(s.jobs, s.market)

    # Optimal placement is no worse than the naive baseline on carbon.
    assert co2_savings_pct(baseline, milp) > 0.0
    assert milp.co2_kg <= baseline.co2_kg
    # Feasibility: readiness, deadline, one warm-up per furnace.
    for p in milp.placements:
        assert p.start_slot >= p.job.ready_slot
        assert p.start_slot + p.job.duration_slots <= p.job.deadline_slot + 1
    assert sum(1 for p in milp.placements if p.warmup) == 1


def test_milp_plan_is_contract_shaped_and_proposed() -> None:
    s = generate_energy_scenario()
    plan = build_energy_plan_milp(s.jobs, s.market, base_time=s.base_time)
    assert plan.solver == Solver.Milp
    assert plan.status == EnergyPlanStatus.Proposed
    assert plan.expected_co2_per_ton < plan.baseline_comparison.baseline_co2_per_ton
    assert len(plan.scheduled_jobs) == len(s.jobs)
