"""Deterministic unit tests for the knowledge assistant (no Azure calls).

Uses a fake ChatClient so grounding/citation/decline behaviour is verified without
touching gpt-5. A separate live smoke test (`live_smoke.py`) exercises real gpt-5.
"""

from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))

from novasteel_core.models import RecommendationPillar, RecommendationStatus  # noqa: E402
from workloads.p4_knowledge_capture.assistant import INSUFFICIENT, KnowledgeAssistant  # noqa: E402
from workloads.p4_knowledge_capture.knowledge_library import load_library  # noqa: E402

FURNACE_Q = "When should we reline the blast furnace lining?"


class FakeChat:
    def __init__(self, response: str) -> None:
        self.response = response
        self.calls: list[tuple[str, str]] = []

    def complete(self, system: str, user: str) -> str:  # matches ChatClient protocol
        self.calls.append((system, user))
        return self.response


def _assistant(response: str) -> tuple[KnowledgeAssistant, FakeChat]:
    chat = FakeChat(response)
    return KnowledgeAssistant(chat, load_library()), chat


def test_grounded_answer_has_citations_and_is_proposed() -> None:
    a, chat = _assistant("Reline when the RUL model forecasts failure within 21 days [S1].")
    ans = a.ask(FURNACE_Q)
    assert not ans.declined
    assert ans.recommendation is not None
    rec = ans.recommendation
    assert rec.pillar == RecommendationPillar.Knowledge
    assert rec.status == RecommendationStatus.Proposed          # human-in-the-loop gate
    assert rec.citations and rec.citations[0].source_id == "SOP-FURNACE-RELINE-014"
    assert rec.content_safety_passed is True
    assert ans.used_sources == ["SOP-FURNACE-RELINE-014"]
    assert len(chat.calls) == 1                                  # model was consulted


def test_ungrounded_question_declines_without_calling_model() -> None:
    a, chat = _assistant("should never be returned")
    ans = a.ask("What is the capital of France?")
    assert ans.declined
    assert ans.recommendation is None
    assert chat.calls == []                                      # no retrieval -> no fabrication


def test_model_insufficient_context_declines() -> None:
    a, _ = _assistant(INSUFFICIENT)
    ans = a.ask(FURNACE_Q)
    assert ans.declined and ans.recommendation is None


def test_answer_without_citations_is_rejected() -> None:
    a, _ = _assistant("Just reline it whenever.")               # no [S#] tags
    ans = a.ask(FURNACE_Q)
    assert ans.declined and ans.recommendation is None


def test_citation_index_maps_to_correct_source() -> None:
    a, _ = _assistant("Move heats to low-price windows [S1].")
    ans = a.ask("How do we schedule energy intensive heats around electricity price?")
    assert not ans.declined
    assert ans.recommendation.citations[0].source_id == "SOP-ENERGY-DISPATCH-007"
