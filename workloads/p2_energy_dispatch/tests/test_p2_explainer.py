from __future__ import annotations

from workloads.p2_energy_dispatch.dispatch_model import baseline_dispatch, build_energy_plan, optimize_dispatch
from workloads.p2_energy_dispatch.explainer import INSUFFICIENT, EnergyPlanExplainer, PlanExplanation
from workloads.p2_energy_dispatch.generate_energy_scenario import generate_energy_scenario


class FakeChat:
    def __init__(self, response: str) -> None:
        self.response = response
        self.calls: list[tuple[str, str]] = []

    def complete(self, system: str, user: str) -> str:  # matches ChatClient protocol
        self.calls.append((system, user))
        return self.response


def _plan():
    s = generate_energy_scenario()
    return s, build_energy_plan(s.jobs, s.market, base_time=s.base_time)


def test_grounded_explanation_carries_evidence_and_uncertainty() -> None:
    s, plan = _plan()
    chat = FakeChat("Overnight batching cuts warm-ups and shifts load to low-carbon hours.")
    exp = EnergyPlanExplainer(chat).explain(
        plan, baseline=baseline_dispatch(s.jobs, s.market), optimized=optimize_dispatch(s.jobs, s.market))

    assert isinstance(exp, PlanExplanation)
    assert not exp.declined
    assert exp.text
    # Evidence is the model's OWN numbers (grounding) — not fabricated by the LLM.
    assert exp.evidence["energySavingsPct"] >= 14.0
    assert exp.evidence["co2SavingsPct"] >= 22.0
    assert exp.uncertainty  # uncertainty is always stated (Principle VI)
    assert exp.content_safety_passed is True
    # The prompt only ever contained the grounded FACTS.
    assert "Energy saving vs baseline" in chat.calls[0][1]


def test_explainer_declines_on_insufficient_token() -> None:
    _, plan = _plan()
    exp = EnergyPlanExplainer(FakeChat(INSUFFICIENT)).explain(plan)
    assert exp.declined
    assert exp.evidence  # evidence still surfaced for the reviewer


def test_explainer_derives_savings_from_plan_when_no_dispatch_results() -> None:
    _, plan = _plan()
    exp = EnergyPlanExplainer(FakeChat("ok")).explain(plan)
    assert not exp.declined
    assert exp.evidence["energySavingsPct"] > 0
