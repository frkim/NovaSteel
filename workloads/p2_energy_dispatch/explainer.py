"""P2 GenAI explainer — grounded natural-language rationale for an energy plan (Principle VI).

Turns a contract-shaped ``EnergyPlan`` into an operator-facing explanation that is grounded
ONLY in the plan's own numbers, states its uncertainty, and passes Content Safety. The model
is instructed to decline rather than fabricate. The explanation is advisory: the plan stays
``Proposed`` and an energy manager still approves/adjusts it (Principle I).

The ``ChatClient`` protocol is injectable, so this is unit-tested with a deterministic fake and
can run live against the deployed Foundry model
(``workloads.p4_knowledge_capture.foundry_client.FoundryClient`` satisfies the protocol).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from novasteel_core.models import EnergyPlan, Solver

from workloads.content_safety import AllowAll, ContentSafetyChecker
from workloads.p2_energy_dispatch.dispatch_model import (
    DispatchResult,
    co2_savings_pct,
    energy_savings_pct,
)

INSUFFICIENT = "INSUFFICIENT_CONTEXT"

SYSTEM_PROMPT = (
    "You are the NovaSteel energy-dispatch explainer. Explain the proposed energy plan to an "
    "energy manager using ONLY the FACTS provided. Do not invent numbers, prices or emissions. "
    "State the expected savings, the key trade-offs, and the plan's UNCERTAINTY. If the FACTS are "
    f"insufficient to explain the plan, reply with exactly this token and nothing else: {INSUFFICIENT}. "
    "Be concise, operational, and never instruct anyone to actuate equipment automatically."
)


class ChatClient(Protocol):
    def complete(self, system: str, user: str) -> str: ...


@dataclass
class PlanExplanation:
    energy_plan_id: str
    declined: bool
    text: str | None = None
    evidence: dict[str, float] = field(default_factory=dict)
    uncertainty: str = ""
    content_safety_passed: bool = True


def _uncertainty(plan: EnergyPlan) -> str:
    parts = []
    if plan.solver == Solver.Heuristic:
        parts.append("Heuristic solver: feasible and near-optimal, not a proven global optimum.")
    else:
        parts.append("MILP solver: optimal for the modelled constraints.")
    if plan.deadline_breaches:
        parts.append(
            f"{len(plan.deadline_breaches)} furnace(s) could not be batched feasibly "
            f"({', '.join(plan.deadline_breaches)}); those fell back to the baseline placement."
        )
    parts.append("Savings assume the forecast spot-price and grid-carbon curve holds.")
    return " ".join(parts)


def _facts(plan: EnergyPlan, energy_savings: float, co2_savings: float) -> str:
    bc = plan.baseline_comparison
    return (
        f"Site: {plan.site}\n"
        f"Scheduled heats: {len(plan.scheduled_jobs)}\n"
        f"Solver: {plan.solver.value}\n"
        f"Expected energy/ton: {plan.expected_energy_per_ton:.4f} MWh (baseline {bc.baseline_energy_per_ton:.4f})\n"
        f"Expected CO2/ton: {plan.expected_co2_per_ton:.2f} kg (baseline {bc.baseline_co2_per_ton:.2f})\n"
        f"Expected cost: EUR {plan.expected_cost_eur:.2f} (baseline EUR {bc.baseline_cost_eur:.2f})\n"
        f"Energy saving vs baseline: {energy_savings:.2f}%\n"
        f"CO2 saving vs baseline: {co2_savings:.2f}%\n"
        f"Deadline breaches: {plan.deadline_breaches or 'none'}"
    )


class EnergyPlanExplainer:
    def __init__(self, chat: ChatClient, content_safety: ContentSafetyChecker | None = None) -> None:
        self._chat = chat
        self._safety = content_safety or AllowAll()

    def explain(
        self,
        plan: EnergyPlan,
        *,
        baseline: DispatchResult | None = None,
        optimized: DispatchResult | None = None,
    ) -> PlanExplanation:
        # Prefer exact savings from the dispatch results; else derive from the plan's per-ton values.
        if baseline is not None and optimized is not None:
            energy_savings = energy_savings_pct(baseline, optimized)
            co2_savings = co2_savings_pct(baseline, optimized)
        else:
            bc = plan.baseline_comparison
            energy_savings = _pct(bc.baseline_energy_per_ton, plan.expected_energy_per_ton)
            co2_savings = _pct(bc.baseline_co2_per_ton, plan.expected_co2_per_ton)

        evidence = {
            "energySavingsPct": round(energy_savings, 4),
            "co2SavingsPct": round(co2_savings, 4),
            "expectedEnergyPerTon": plan.expected_energy_per_ton,
            "baselineEnergyPerTon": plan.baseline_comparison.baseline_energy_per_ton,
        }
        answer = self._chat.complete(SYSTEM_PROMPT, _facts(plan, energy_savings, co2_savings)).strip()
        if not answer or INSUFFICIENT in answer:
            return PlanExplanation(plan.energy_plan_id, declined=True,
                                   text="Model reported insufficient grounded context; declined.",
                                   evidence=evidence, uncertainty=_uncertainty(plan))
        safe = self._safety.is_safe(answer)
        if not safe:
            # Content Safety blocked the generation — never surface it (Constitution VI).
            return PlanExplanation(plan.energy_plan_id, declined=True,
                                   text="Generated explanation failed Content Safety; withheld.",
                                   evidence=evidence, uncertainty=_uncertainty(plan),
                                   content_safety_passed=False)
        return PlanExplanation(
            energy_plan_id=plan.energy_plan_id,
            declined=False,
            text=answer,
            evidence=evidence,
            uncertainty=_uncertainty(plan),
            content_safety_passed=True,
        )


def _pct(before: float, after: float) -> float:
    return 0.0 if before <= 0 else round((before - after) / before * 100.0, 4)
