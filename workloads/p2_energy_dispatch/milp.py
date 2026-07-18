"""MILP energy-dispatch solver (PuLP/CBC) — the optimal counterpart to the heuristic.

Formulates furnace-heat load-shifting as a mixed-integer program: choose each heat's start slot
to minimize weighted energy cost + CO2, subject to readiness, deadlines and single-heat-per-slot
furnace capacity. Produces the same contract-shaped ``EnergyPlan`` (Solver.Milp). PuLP is an
optional dependency; import lazily so the heuristic path never requires a solver.

Note: this MILP optimizes *placement* (shift to cheap/green slots). The warm-up *batching* lever
(the extra energy saving) is modelled by the heuristic; the MILP result is emitted with a single
campaign warm-up per furnace to remain comparable.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from uuid import NAMESPACE_URL, uuid5

from novasteel_core.models import (
    BaselineComparison,
    EnergyPlan,
    EnergyPlanStatus,
    MarketSignal,
    Origin,
    PlanningHorizon,
    ScheduledJob,
    Solver,
)

from workloads.p2_energy_dispatch.dispatch_model import (
    WARMUP_MWH,
    DispatchResult,
    Job,
    Placement,
    _evaluate,
    baseline_dispatch,
)

LOGIC_VERSION = "p2-dispatch-milp-v1"


class SolverUnavailableError(RuntimeError):
    """Raised when PuLP/CBC is not installed."""


def optimize_dispatch_milp(jobs: list[Job], market: list[MarketSignal], *, co2_weight: float = 1.0,
                           cost_weight: float = 0.01) -> DispatchResult:
    """Solve the placement MILP; return a DispatchResult (one warm-up per furnace campaign)."""
    try:
        import pulp  # lazy optional import
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise SolverUnavailableError("PuLP is required for the MILP solver (pip install pulp)") from exc

    horizon = len(market)
    prob = pulp.LpProblem("energy_dispatch", pulp.LpMinimize)

    # x[j, s] = 1 if job j starts at slot s (feasible slots only).
    x: dict[tuple[str, int], "pulp.LpVariable"] = {}
    feasible: dict[str, list[int]] = {}
    for j in jobs:
        slots = [s for s in range(j.ready_slot, min(j.deadline_slot - j.duration_slots + 1, horizon - j.duration_slots) + 1)]
        feasible[j.job_id] = slots
        for s in slots:
            x[(j.job_id, s)] = pulp.LpVariable(f"x_{j.job_id}_{s}", cat="Binary")

    # Each job starts exactly once.
    for j in jobs:
        if not feasible[j.job_id]:
            raise ValueError(f"job {j.job_id} has no feasible start slot (deadline before ready)")
        prob += pulp.lpSum(x[(j.job_id, s)] for s in feasible[j.job_id]) == 1

    # Single heat per furnace per slot (no overlap).
    by_furnace: dict[str, list[Job]] = {}
    for j in jobs:
        by_furnace.setdefault(j.furnace_id, []).append(j)
    for furnace_jobs in by_furnace.values():
        for slot in range(horizon):
            occupying = []
            for j in furnace_jobs:
                for s in feasible[j.job_id]:
                    if s <= slot < s + j.duration_slots:
                        occupying.append(x[(j.job_id, s)])
            if occupying:
                prob += pulp.lpSum(occupying) <= 1

    # Objective: weighted (CO2 + cost) of the energy placed in each slot.
    terms = []
    for j in jobs:
        per_slot = j.production_mwh / j.duration_slots
        for s in feasible[j.job_id]:
            for off in range(j.duration_slots):
                sig = market[s + off]
                unit = co2_weight * per_slot * sig.grid_carbon_grams_per_kwh + cost_weight * per_slot * sig.spot_price_eur_mwh
                terms.append(unit * x[(j.job_id, s)])
    prob += pulp.lpSum(terms)

    prob.solve(pulp.PULP_CBC_CMD(msg=False))
    if pulp.LpStatus[prob.status] != "Optimal":
        raise RuntimeError(f"MILP not solved to optimality: {pulp.LpStatus[prob.status]}")

    # Extract placements; charge one warm-up per furnace (earliest heat).
    placements: list[Placement] = []
    starts: dict[str, int] = {}
    for j in jobs:
        for s in feasible[j.job_id]:
            if pulp.value(x[(j.job_id, s)]) and pulp.value(x[(j.job_id, s)]) > 0.5:
                starts[j.job_id] = s
    earliest_by_furnace = {
        fid: min(js, key=lambda j: starts[j.job_id]).job_id for fid, js in by_furnace.items()
    }
    for j in jobs:
        placements.append(Placement(job=j, start_slot=starts[j.job_id],
                                    warmup=(earliest_by_furnace[j.furnace_id] == j.job_id)))

    energy, cost, co2 = _evaluate(placements, market)
    return DispatchResult(placements, energy, cost, co2)


def build_energy_plan_milp(jobs: list[Job], market: list[MarketSignal], *, base_time: datetime,
                           site: str | None = None) -> EnergyPlan:
    """Assemble a contract-shaped EnergyPlan (Solver.Milp) from the MILP placement."""
    if not jobs:
        raise ValueError("at least one job is required")
    site = site or jobs[0].site
    baseline = baseline_dispatch(jobs, market)
    optimized = optimize_dispatch_milp(jobs, market)
    total_tons = sum(j.tons for j in jobs) or 1.0

    scheduled = [
        ScheduledJob(
            job_id=p.job.job_id,
            slot_start=base_time + timedelta(hours=p.start_slot),
            slot_end=base_time + timedelta(hours=p.start_slot + p.job.duration_slots),
            deadline=base_time + timedelta(hours=p.job.deadline_slot + 1),
            energy_mwh=round(p.job.production_mwh + (WARMUP_MWH if p.warmup else 0.0), 6),
        )
        for p in sorted(optimized.placements, key=lambda p: p.start_slot)
    ]
    origin = Origin.Synthetic if any(j.origin == Origin.Synthetic for j in jobs) else Origin.Real
    return EnergyPlan(
        energy_plan_id=str(uuid5(NAMESPACE_URL, f"{LOGIC_VERSION}:{site}:{base_time.isoformat()}")),
        site=site,
        planning_horizon=PlanningHorizon.model_validate(
            {"from": base_time, "to": base_time + timedelta(hours=len(market))}
        ),
        scheduled_jobs=scheduled,
        expected_energy_per_ton=round(optimized.energy_mwh / total_tons, 6),
        expected_co2_per_ton=round(optimized.co2_kg / total_tons, 6),
        expected_cost_eur=round(optimized.cost_eur, 4),
        baseline_comparison=BaselineComparison(
            baseline_energy_per_ton=round(baseline.energy_mwh / total_tons, 6),
            baseline_co2_per_ton=round(baseline.co2_kg / total_tons, 6),
            baseline_cost_eur=round(baseline.cost_eur, 4),
        ),
        deadline_breaches=[],
        solver=Solver.Milp,
        origin=origin,
        status=EnergyPlanStatus.Proposed,
    )
