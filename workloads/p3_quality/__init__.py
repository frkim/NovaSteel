"""P3 quality workload (Constitution I/VI, SC-004).

Predicts automotive-grade coil outcomes per heat, links predicted-vs-actual, proposes
reviewable corrective adjustments for recoverable excursions, and raises SPC-drift signals.
Decision-support only — a metallurgist reviews and approves; nothing is actuated.
"""

from workloads.p3_quality.decision_service import (
    audit_quality_prediction,
    record_quality_decision,
)
from workloads.p3_quality.explainer import QualityExplainer, RootCauseExplanation
from workloads.p3_quality.generate_quality_scenario import (
    Heat,
    generate_quality_scenario,
)
from workloads.p3_quality.quality_model import (
    MODEL_VERSION,
    QualityAssessment,
    baseline_yield,
    predict_heat,
    recommended_yield,
    score_batch,
    spc_drift_prediction,
    yield_uplift,
)
from workloads.p3_quality.spc import ControlLimits, control_limits, detect_drift, first_drift

__all__ = [
    "ControlLimits",
    "Heat",
    "MODEL_VERSION",
    "QualityAssessment",
    "QualityExplainer",
    "RootCauseExplanation",
    "audit_quality_prediction",
    "baseline_yield",
    "control_limits",
    "detect_drift",
    "first_drift",
    "generate_quality_scenario",
    "predict_heat",
    "recommended_yield",
    "record_quality_decision",
    "score_batch",
    "spc_drift_prediction",
    "yield_uplift",
]
