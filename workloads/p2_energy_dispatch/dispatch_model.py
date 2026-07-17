"""Physics-lite energy-dispatch heuristic producing a contract-shaped ``EnergyPlan``.

Model (decision-support only — no actuation):
- Each furnace *heat* has a fixed production energy plus a one-off warm-up (cold-start)
  energy every time a campaign begins. Coordinating heats into a single back-to-back
  campaign removes redundant warm-ups; deferring that campaign into the overnight trough
  buys the cheapest, lowest-carbon slots.
- Baseline ("run each heat as its charge arrives") starts every heat at its ready slot as
  a standalone campaign — many warm-ups, spread across the daytime carbon peak.
- Optimized batches each furnace's heats into one campaign placed in the greenest feasible
  contiguous window that respects readiness and deadlines.

CO2(kg) = energy_MWh * grid_carbon(g/kWh)  (units cancel to kg); cost = energy_MWh * spot.
The plan is emitted ``Proposed`` for human review (Constitution I).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
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

LOGIC_VERSION = "p2-dispatch-heuristic-v1"
WARMUP_MWH = 6.0  # cold-start energy to bring an EAF to tapping temperature


@dataclass(frozen=True)
class Job:
    job_id: str
    furnace_id: str
    site: str
    tons: float
    production_mwh: float
    duration_slots: int
    ready_slot: int
    deadline_slot: int
    origin: Origin = Origin.Synthetic


@dataclass(frozen=True)
class Placement:
    job: Job
    start_slot: int  # inclusive
    warmup: bool  # whether this placement pays a cold-start warm-up


@dataclass(frozen=True)
class DispatchResult:
    placements: list[Placement]
    energy_mwh: float
    cost_eur: float
    co2_kg: float
    deadline_breaches: list[str] = field(default_factory=list)


def _placement_slot_energy(placement: Placement) -> dict[int, float]:
    """Distribute a placement's energy over the slots it occupies (warm-up on slot 0)."""
    job = placement.job
    per_slot = job.production_mwh / job.duration_slots
    slots: dict[int, float] = {}
    for offset in range(job.duration_slots):
        slots[placement.start_slot + offset] = per_slot
    if placement.warmup:
        slots[placement.start_slot] = slots.get(placement.start_slot, 0.0) + WARMUP_MWH
    return slots


def _cost_co2(slot_energy: dict[int, float], market: list[MarketSignal]) -> tuple[float, float]:
    cost = 0.0
    co2 = 0.0
    for slot, energy in slot_energy.items():
        if slot < 0 or slot >= len(market):
            continue
        cost += energy * market[slot].spot_price_eur_mwh
        co2 += energy * market[slot].grid_carbon_grams_per_kwh
    return cost, co2


def _evaluate(placements: list[Placement], market: list[MarketSignal]) -> tuple[float, float, float]:
    total_energy = 0.0
    total_cost = 0.0
    total_co2 = 0.0
    for placement in placements:
        slot_energy = _placement_slot_energy(placement)
        total_energy += sum(slot_energy.values())
        cost, co2 = _cost_co2(slot_energy, market)
        total_cost += cost
        total_co2 += co2
    return total_energy, total_cost, total_co2


def baseline_dispatch(jobs: list[Job], market: list[MarketSignal]) -> DispatchResult:
    """Naive policy: every heat is a standalone campaign starting at its ready slot.

    Heats sharing a furnace are pushed later to avoid overlap, but each still pays its own
    warm-up (no batching), representing today's uncoordinated operation.
    """
    placements: list[Placement] = []
    next_free: dict[str, int] = {}
    for job in sorted(jobs, key=lambda j: (j.furnace_id, j.ready_slot)):
        start = max(job.ready_slot, next_free.get(job.furnace_id, 0))
        placements.append(Placement(job=job, start_slot=start, warmup=True))
        next_free[job.furnace_id] = start + job.duration_slots
    energy, cost, co2 = _evaluate(placements, market)
    return DispatchResult(placements, energy, cost, co2)


def _greenest_window(length: int, earliest: int, latest_end: int, market: list[MarketSignal]) -> int | None:
    """Return the start slot of the lowest-carbon contiguous window of ``length`` slots
    with ``earliest <= start`` and ``start + length <= latest_end``; None if infeasible."""
    best_start: int | None = None
    best_score: float | None = None
    horizon = min(latest_end, len(market))
    for start in range(earliest, horizon - length + 1):
        window = market[start:start + length]
        # primary: carbon, tiebreak: cost, then earliest start
        score = (sum(s.grid_carbon_grams_per_kwh for s in window),
                 sum(s.spot_price_eur_mwh for s in window))
        if best_score is None or score < best_score:
            best_score = score
            best_start = start
    return best_start


def optimize_dispatch(jobs: list[Job], market: list[MarketSignal]) -> DispatchResult:
    """Batch each furnace's heats into one campaign placed in the greenest feasible window."""
    placements: list[Placement] = []
    breaches: list[str] = []
    by_furnace: dict[str, list[Job]] = {}
    for job in jobs:
        by_furnace.setdefault(job.furnace_id, []).append(job)

    for furnace_id, furnace_jobs in by_furnace.items():
        ordered = sorted(furnace_jobs, key=lambda j: j.ready_slot)
        total_len = sum(j.duration_slots for j in ordered)
        earliest = max(j.ready_slot for j in ordered)
        latest_end = min(j.deadline_slot for j in ordered) + 1  # deadline slot is inclusive
        start = _greenest_window(total_len, earliest, latest_end, market)
        if start is None:
            # Infeasible batch -> flag and fall back to per-heat baseline placement.
            breaches.append(furnace_id)
            fallback = baseline_dispatch(ordered, market)
            placements.extend(fallback.placements)
            continue
        offset = 0
        for i, job in enumerate(ordered):
            placements.append(Placement(job=job, start_slot=start + offset, warmup=(i == 0)))
            offset += job.duration_slots

    energy, cost, co2 = _evaluate(placements, market)
    return DispatchResult(placements, energy, cost, co2, breaches)


def _pct(before: float, after: float) -> float:
    if before <= 0:
        return 0.0
    return round((before - after) / before * 100.0, 4)


def energy_savings_pct(baseline: DispatchResult, optimized: DispatchResult) -> float:
    return _pct(baseline.energy_mwh, optimized.energy_mwh)


def co2_savings_pct(baseline: DispatchResult, optimized: DispatchResult) -> float:
    return _pct(baseline.co2_kg, optimized.co2_kg)


def cost_savings_pct(baseline: DispatchResult, optimized: DispatchResult) -> float:
    return _pct(baseline.cost_eur, optimized.cost_eur)


def _plan_id(site: str, start: datetime, jobs: list[Job]) -> str:
    key = f"{LOGIC_VERSION}:{site}:{start.isoformat()}:{'|'.join(sorted(j.job_id for j in jobs))}"
    return str(uuid5(NAMESPACE_URL, key))


def build_energy_plan(
    jobs: list[Job],
    market: list[MarketSignal],
    *,
    base_time: datetime,
    site: str | None = None,
) -> EnergyPlan:
    """Run baseline + optimized dispatch and assemble a contract-shaped EnergyPlan (Proposed)."""
    if not jobs:
        raise ValueError("at least one job is required")
    site = site or jobs[0].site
    baseline = baseline_dispatch(jobs, market)
    optimized = optimize_dispatch(jobs, market)

    total_tons = sum(j.tons for j in jobs) or 1.0
    from datetime import timedelta

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
    horizon_from = base_time
    horizon_to = base_time + timedelta(hours=len(market))

    return EnergyPlan(
        energy_plan_id=_plan_id(site, horizon_from, jobs),
        site=site,
        planning_horizon=PlanningHorizon.model_validate(
            {"from": horizon_from, "to": horizon_to}
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
        deadline_breaches=optimized.deadline_breaches,
        solver=Solver.Heuristic,
        origin=origin,
        status=EnergyPlanStatus.Proposed,  # human-in-the-loop gate (Constitution I)
    )
