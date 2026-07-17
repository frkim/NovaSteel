"""P3 quality-outcome prediction + SPC drift (Constitution I/VI, SC-004).

Predicts, per heat, whether an automotive-grade coil will meet spec from its process
features, links predicted-vs-actual outcomes, and proposes a *reviewable* corrective
adjustment for recoverable excursions. Also raises SPC-drift signals from control charts.
All outputs are decision-support: a metallurgist reviews and approves; nothing is actuated.
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import NAMESPACE_URL, uuid5

from novasteel_core.models import (
    EvidenceItem,
    Origin,
    Pillar,
    Prediction,
    PredictionKind,
    PredictionStatus,
    Recommendation,
    RecommendationPillar,
    RecommendationStatus,
)

from workloads.p3_quality.generate_quality_scenario import (
    GRADE_TARGET,
    INCLUSION_MAX,
    SULFUR_MAX_PCT,
    TAPPING_MAX_C,
    TAPPING_MIN_C,
    Heat,
    heat_timestamp,
)
from workloads.p3_quality.spc import ControlLimits, control_limits, first_drift

MODEL_VERSION = "quality-rules-v1"
SPC_MODEL_VERSION = "spc-we-v1"
CORRECTABLE_TEMP_MARGIN_C = 20.0  # temperature excursions beyond this are non-recoverable in-run
SEVERE_INCLUSION = 3.5  # inclusion cleanliness beyond this has no reviewable in-run fix


@dataclass(frozen=True)
class QualityAssessment:
    prediction: Prediction
    predicted_high_grade: bool
    actual_high_grade: bool
    at_risk: bool
    recoverable: bool
    recommendation: Recommendation | None


def _violations(heat: Heat) -> list[str]:
    v: list[str] = []
    if heat.sulfur_pct > SULFUR_MAX_PCT:
        v.append("sulfur")
    if heat.inclusion_index > INCLUSION_MAX:
        v.append("inclusion")
    if not (TAPPING_MIN_C <= heat.tapping_temp_c <= TAPPING_MAX_C):
        v.append("tapping_temp")
    return v


def _temp_recoverable(heat: Heat) -> bool:
    if TAPPING_MIN_C <= heat.tapping_temp_c <= TAPPING_MAX_C:
        return True
    if heat.tapping_temp_c > TAPPING_MAX_C:
        return heat.tapping_temp_c - TAPPING_MAX_C <= CORRECTABLE_TEMP_MARGIN_C
    return TAPPING_MIN_C - heat.tapping_temp_c <= CORRECTABLE_TEMP_MARGIN_C


def _confidence(heat: Heat) -> float:
    """Higher when process margins to every spec limit are comfortable."""
    m_sulfur = (SULFUR_MAX_PCT - heat.sulfur_pct) / SULFUR_MAX_PCT
    m_incl = (INCLUSION_MAX - heat.inclusion_index) / INCLUSION_MAX
    band = (TAPPING_MAX_C - TAPPING_MIN_C) / 2.0
    center = (TAPPING_MAX_C + TAPPING_MIN_C) / 2.0
    m_temp = (band - abs(heat.tapping_temp_c - center)) / band
    margin = min(m_sulfur, m_incl, m_temp)
    return round(max(0.05, min(0.99, 0.5 + 0.5 * margin)), 4)


def _evidence(heat: Heat) -> list[EvidenceItem]:
    return [
        EvidenceItem(metric="SulfurPct", value=heat.sulfur_pct, weight=0.4,
                     note=f"Spec max {SULFUR_MAX_PCT:.3f}%."),
        EvidenceItem(metric="InclusionIndex", value=heat.inclusion_index, weight=0.35,
                     note=f"Spec max {INCLUSION_MAX:.1f}."),
        EvidenceItem(metric="TappingTempC", value=heat.tapping_temp_c, weight=0.25,
                     note=f"Spec band {TAPPING_MIN_C:.0f}-{TAPPING_MAX_C:.0f} C."),
    ]


def _recommendation(heat: Heat, violations: list[str]) -> Recommendation:
    actions = {
        "sulfur": "extend ladle desulphurization to bring S below 0.010%",
        "inclusion": "increase soft-stirring time to lower the inclusion index below 2.0",
        "tapping_temp": "adjust tapping temperature back into the 1630-1670 C band",
    }
    steps = "; ".join(actions[v] for v in violations)
    return Recommendation(
        recommendation_id=str(uuid5(NAMESPACE_URL, f"rec:{heat.heat_id}")),
        pillar=RecommendationPillar.Quality,
        site=heat.site,
        related_heat_id=heat.heat_id,
        summary=f"At-risk for {GRADE_TARGET}: {steps}.",
        rationale=(
            "Predicted out-of-spec on "
            + ", ".join(violations)
            + "; the listed adjustment historically restores high-grade outcome. "
            "Proposed for metallurgist review — no automatic process change."
        ),
        expected_impact={"gradeRecovery": GRADE_TARGET, "violations": violations},
        content_safety_passed=True,
        status=RecommendationStatus.Proposed,  # human-in-the-loop (Constitution I)
    )


def predict_heat(heat: Heat) -> QualityAssessment:
    """Predict the high-grade outcome and, for recoverable excursions, propose a fix."""
    violations = _violations(heat)
    predicted_high_grade = not violations
    at_risk = not predicted_high_grade
    recoverable = at_risk and _temp_recoverable(heat) and heat.inclusion_index <= SEVERE_INCLUSION

    prediction = Prediction(
        prediction_id=str(uuid5(NAMESPACE_URL, f"pred:{MODEL_VERSION}:{heat.heat_id}")),
        pillar=Pillar.Quality,
        site=heat.site,
        asset_id=None,
        heat_id=heat.heat_id,
        kind=PredictionKind.QualityOutcome,
        time_to_failure_days=None,
        predicted_at=heat_timestamp(heat),
        confidence=_confidence(heat),
        evidence=_evidence(heat),
        model_version=MODEL_VERSION,
        input_window_ref=f"gold_quality_features/{heat.site}/{heat.heat_id}",
        origin=Origin.Synthetic if heat.origin == Origin.Synthetic else Origin.Real,
        status=PredictionStatus.Raised,
    )
    recommendation = _recommendation(heat, violations) if recoverable else None
    return QualityAssessment(
        prediction=prediction,
        predicted_high_grade=predicted_high_grade,
        actual_high_grade=heat.actual_high_grade,
        at_risk=at_risk,
        recoverable=recoverable,
        recommendation=recommendation,
    )


def score_batch(heats: list[Heat]) -> list[QualityAssessment]:
    return [predict_heat(h) for h in heats]


def baseline_yield(assessments: list[QualityAssessment]) -> float:
    """High-grade fraction with NO intervention (actual outcomes)."""
    if not assessments:
        return 0.0
    return sum(1 for a in assessments if a.actual_high_grade) / len(assessments)


def recommended_yield(assessments: list[QualityAssessment]) -> float:
    """High-grade fraction if every recoverable at-risk heat's approved fix is applied."""
    if not assessments:
        return 0.0
    recovered = sum(1 for a in assessments if a.actual_high_grade or a.recoverable)
    return recovered / len(assessments)


def yield_uplift(assessments: list[QualityAssessment]) -> float:
    """Absolute high-grade yield improvement (percentage points, 0-1 scale)."""
    return round(recommended_yield(assessments) - baseline_yield(assessments), 6)


def spc_drift_prediction(
    heats: list[Heat],
    *,
    metric: str = "tapping_temp_c",
    in_control_count: int = 10,
    site: str | None = None,
) -> Prediction | None:
    """Raise an SPC-drift Prediction if the metric leaves statistical control."""
    if len(heats) <= in_control_count:
        return None
    series = [getattr(h, metric) for h in heats]
    limits: ControlLimits = control_limits(series[:in_control_count])
    drift = first_drift(series, limits)
    if drift is None:
        return None
    heat = heats[drift.index]
    site = site or heat.site
    return Prediction(
        prediction_id=str(uuid5(NAMESPACE_URL, f"spc:{SPC_MODEL_VERSION}:{heat.heat_id}:{metric}")),
        pillar=Pillar.Quality,
        site=site,
        asset_id=None,
        heat_id=heat.heat_id,
        kind=PredictionKind.SpcDrift,
        time_to_failure_days=None,
        predicted_at=heat_timestamp(heat),
        confidence=0.9,
        evidence=[
            EvidenceItem(metric=metric, value=round(drift.value, 3), weight=1.0,
                         note=f"{drift.rule} violation; UCL={limits.ucl:.2f}, mean={limits.mean:.2f}."),
        ],
        model_version=SPC_MODEL_VERSION,
        input_window_ref=f"gold_quality_features/{site}/spc/{metric}",
        origin=Origin.Synthetic if heat.origin == Origin.Synthetic else Origin.Real,
        status=PredictionStatus.Raised,
    )
