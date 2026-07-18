from __future__ import annotations

from workloads.p3_quality.explainer import INSUFFICIENT, QualityExplainer, RootCauseExplanation
from workloads.p3_quality.generate_quality_scenario import generate_quality_scenario
from workloads.p3_quality.quality_model import score_batch


class FakeChat:
    def __init__(self, response: str) -> None:
        self.response = response
        self.calls: list[tuple[str, str]] = []

    def complete(self, system: str, user: str) -> str:  # matches ChatClient protocol
        self.calls.append((system, user))
        return self.response


def _at_risk_assessment():
    return next(a for a in score_batch(generate_quality_scenario()) if a.at_risk and a.recoverable)


def test_root_cause_explanation_is_grounded_in_evidence() -> None:
    a = _at_risk_assessment()
    chat = FakeChat("Sulphur is above the 0.010% limit; extend desulphurization to recover grade.")
    exp = QualityExplainer(chat).explain(a)

    assert isinstance(exp, RootCauseExplanation)
    assert not exp.declined
    assert exp.heat_id == a.prediction.heat_id
    assert exp.drivers == [e.metric for e in a.prediction.evidence]
    assert exp.confidence == a.prediction.confidence
    assert exp.uncertainty
    assert exp.content_safety_passed is True
    # The prompt was grounded on the heat's actual evidence metrics.
    assert "SulfurPct" in chat.calls[0][1]
    # A recoverable heat's corrective action is offered to the model as grounding.
    assert "Recommended corrective action" in chat.calls[0][1]


def test_explainer_declines_on_insufficient_token() -> None:
    a = _at_risk_assessment()
    exp = QualityExplainer(FakeChat(INSUFFICIENT)).explain(a)
    assert exp.declined
    assert exp.drivers  # evidence drivers still surfaced


def test_non_recoverable_heat_uncertainty_flags_reroute() -> None:
    a = next(x for x in score_batch(generate_quality_scenario()) if x.at_risk and not x.recoverable)
    exp = QualityExplainer(FakeChat("Severe inclusion; cannot recover in-run.")).explain(a)
    assert "lower grade" in exp.uncertainty.lower()
