"""P2 energy-dispatch workload (Constitution I/VI, SC-001/SC-002).

Decision-support furnace campaign scheduling: shift and batch flexible heats into the
cheapest, lowest-carbon slots ahead of their deadlines to cut energy, cost and CO2 —
while NEVER actuating plant equipment. Every plan is emitted ``Proposed`` for an energy
manager to approve or adjust (human-in-the-loop).
"""

from workloads.p2_energy_dispatch.dispatch_model import (
    Job,
    build_energy_plan,
    co2_savings_pct,
    cost_savings_pct,
    energy_savings_pct,
    optimize_dispatch,
)
from workloads.p2_energy_dispatch.explainer import EnergyPlanExplainer, PlanExplanation
from workloads.p2_energy_dispatch.from_gold import job_from_row, market_signal_from_row
from workloads.p2_energy_dispatch.generate_energy_scenario import (
    EnergyScenario,
    generate_energy_scenario,
)

__all__ = [
    "EnergyPlanExplainer",
    "EnergyScenario",
    "Job",
    "PlanExplanation",
    "build_energy_plan",
    "co2_savings_pct",
    "cost_savings_pct",
    "energy_savings_pct",
    "generate_energy_scenario",
    "job_from_row",
    "market_signal_from_row",
    "optimize_dispatch",
]
