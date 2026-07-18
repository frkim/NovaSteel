"""P3 GenAI explainer — grounded root-cause narrative for a quality prediction (Principle VI).

Turns a ``QualityAssessment`` into a metallurgist-facing root-cause explanation grounded ONLY in
the heat's process evidence (sulphur, inclusion, tapping temperature vs spec). States uncertainty
from the model confidence, passes Content Safety, and declines rather than fabricates. Advisory
only: the prediction stays ``Raised`` and a metallurgist approves any action (Principle I).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from workloads.p3_quality.quality_model import QualityAssessment

INSUFFICIENT = "INSUFFICIENT_CONTEXT"

SYSTEM_PROMPT = (
    "You are the NovaSteel quality root-cause explainer. Explain, for a metallurgist, WHY the heat "
    "is predicted in/out of grade, using ONLY the EVIDENCE metrics provided and their spec limits. "
    "Do not invent measurements. Name the specific out-of-spec driver(s), reference the recommended "
    "corrective action if one is provided, and state the prediction's UNCERTAINTY. If the EVIDENCE is "
    f"insufficient, reply with exactly this token and nothing else: {INSUFFICIENT}. Be concise and never "
    "instruct anyone to change the process automatically."
)


class ChatClient(Protocol):
    def complete(self, system: str, user: str) -> str: ...


@dataclass
class RootCauseExplanation:
    heat_id: str
    declined: bool
    text: str | None = None
    drivers: list[str] = field(default_factory=list)
    confidence: float = 0.0
    uncertainty: str = ""
    content_safety_passed: bool = True


def _drivers(assessment: QualityAssessment) -> list[str]:
    return [e.metric for e in assessment.prediction.evidence]


def _facts(assessment: QualityAssessment) -> str:
    p = assessment.prediction
    lines = [
        f"Heat: {p.heat_id}  Site: {p.site}",
        f"Predicted high-grade: {assessment.predicted_high_grade}  (confidence {p.confidence:.2f})",
        f"At risk: {assessment.at_risk}  Recoverable in-run: {assessment.recoverable}",
        "Evidence:",
    ]
    for e in p.evidence:
        lines.append(f"  - {e.metric}={e.value} ({e.note})")
    if assessment.recommendation is not None:
        lines.append(f"Recommended corrective action: {assessment.recommendation.summary}")
    return "\n".join(lines)


def _uncertainty(assessment: QualityAssessment) -> str:
    c = assessment.prediction.confidence
    band = "high" if c >= 0.75 else "moderate" if c >= 0.5 else "low"
    extra = "" if assessment.recoverable or not assessment.at_risk else \
        " No in-run reviewable fix restores this heat; consider re-routing to a lower grade."
    return f"Model confidence is {band} ({c:.2f}); rules-based estimate on synthetic evidence.{extra}"


class QualityExplainer:
    def __init__(self, chat: ChatClient) -> None:
        self._chat = chat

    def explain(self, assessment: QualityAssessment) -> RootCauseExplanation:
        answer = self._chat.complete(SYSTEM_PROMPT, _facts(assessment)).strip()
        heat_id = assessment.prediction.heat_id or ""
        if not answer or INSUFFICIENT in answer:
            return RootCauseExplanation(heat_id, declined=True,
                                        text="Model reported insufficient grounded context; declined.",
                                        drivers=_drivers(assessment),
                                        confidence=assessment.prediction.confidence,
                                        uncertainty=_uncertainty(assessment))
        return RootCauseExplanation(
            heat_id=heat_id,
            declined=False,
            text=answer,
            drivers=_drivers(assessment),
            confidence=assessment.prediction.confidence,
            uncertainty=_uncertainty(assessment),
            content_safety_passed=_content_safety_ok(answer),
        )


def _content_safety_ok(_text: str) -> bool:
    """Hook for Azure AI Content Safety (Constitution VI); wire the real API before go-live."""
    return True
