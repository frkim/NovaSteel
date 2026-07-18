from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from workloads.content_safety import AllowAll, BlockAll, ContentSafetyChecker, default_checker  # noqa: E402
from workloads.p2_energy_dispatch.dispatch_model import build_energy_plan  # noqa: E402
from workloads.p2_energy_dispatch.explainer import EnergyPlanExplainer  # noqa: E402
from workloads.p2_energy_dispatch.generate_energy_scenario import generate_energy_scenario  # noqa: E402
from workloads.p3_quality.explainer import QualityExplainer  # noqa: E402
from workloads.p3_quality.generate_quality_scenario import generate_quality_scenario  # noqa: E402
from workloads.p3_quality.quality_model import score_batch  # noqa: E402
from workloads.p4_knowledge_capture.assistant import KnowledgeAssistant  # noqa: E402
from workloads.p4_knowledge_capture.knowledge_library import load_library  # noqa: E402


class FakeChat:
    def __init__(self, response: str) -> None:
        self.response = response

    def complete(self, system: str, user: str) -> str:
        return self.response


def test_checkers_satisfy_protocol_and_defaults() -> None:
    assert isinstance(AllowAll(), ContentSafetyChecker)
    assert isinstance(BlockAll(), ContentSafetyChecker)
    assert AllowAll().is_safe("anything") is True
    assert BlockAll().is_safe("anything") is False
    assert isinstance(default_checker(), ContentSafetyChecker)  # AllowAll when no endpoint env


def test_p2_explainer_withholds_when_content_safety_blocks() -> None:
    s = generate_energy_scenario()
    plan = build_energy_plan(s.jobs, s.market, base_time=s.base_time)
    exp = EnergyPlanExplainer(FakeChat("some text"), content_safety=BlockAll()).explain(plan)
    assert exp.declined
    assert exp.content_safety_passed is False
    assert "Content Safety" in exp.text


def test_p3_explainer_withholds_when_content_safety_blocks() -> None:
    a = next(x for x in score_batch(generate_quality_scenario()) if x.at_risk and x.recoverable)
    exp = QualityExplainer(FakeChat("some text"), content_safety=BlockAll()).explain(a)
    assert exp.declined
    assert exp.content_safety_passed is False


def test_p4_assistant_withholds_when_content_safety_blocks() -> None:
    a = KnowledgeAssistant(FakeChat("Reline when RUL < 21 days [S1]."), load_library(),
                           content_safety=BlockAll())
    ans = a.ask("When should we reline the blast furnace lining?")
    assert ans.declined
    assert ans.recommendation is None


def test_p4_assistant_publishes_when_content_safety_allows() -> None:
    a = KnowledgeAssistant(FakeChat("Reline when RUL < 21 days [S1]."), load_library(),
                           content_safety=AllowAll())
    ans = a.ask("When should we reline the blast furnace lining?")
    assert not ans.declined
    assert ans.recommendation is not None
    assert ans.recommendation.content_safety_passed is True
