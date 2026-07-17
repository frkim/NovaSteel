"""Physics-informed linear RUL estimator for furnace-lining degradation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
from uuid import NAMESPACE_URL, uuid5

from novasteel_core.models import (
    EvidenceItem,
    Origin,
    Pillar,
    Prediction,
    PredictionKind,
    PredictionStatus,
    TelemetryReading,
)

from .physics_features import (
    DEFAULT_HEAT_FLUX_FAILURE_THRESHOLD,
    FurnaceFeatureRecord,
    extract_features,
)

MODEL_VERSION = "rul-linear-v1"
STANDARD_REVIEW_PATH = "MaintenanceReview"
EXPEDITED_REVIEW_PATH = "ExpeditedMaintenanceReview"
MIN_ADVANCE_WARNING_DAYS = 21.0
DEFAULT_MONITORING_HORIZON_DAYS = 45.0
MIN_WEAR_RATE_PER_DAY = 0.2
MIN_OBSERVED_DAYS = 10.0


@dataclass(frozen=True)
class RulAssessment:
    prediction: Prediction
    features: FurnaceFeatureRecord
    escalated: bool
    review_path: str
    priority: str
    escalation_reason: str | None = None


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def _prediction_id(features: FurnaceFeatureRecord, ttf_days: float) -> str:
    key = f"{MODEL_VERSION}:{features.site}:{features.asset_id}:{features.window_end.isoformat()}:{ttf_days:.3f}"
    return str(uuid5(NAMESPACE_URL, key))


def _confidence(features: FurnaceFeatureRecord) -> float:
    window_days = max((features.window_end - features.window_start).total_seconds() / 86_400.0, 0.0)
    window_factor = _clamp(window_days / 30.0)
    slope_factor = _clamp(features.heat_flux_slope_per_day / 1.0)
    confidence = 0.15 + 0.60 * features.heat_flux_r_squared + 0.15 * window_factor + 0.10 * slope_factor
    return round(_clamp(confidence), 4)


def _evidence(features: FurnaceFeatureRecord, ttf_days: float) -> list[EvidenceItem]:
    evidence = [
        EvidenceItem(
            metric="HeatFlux",
            value=float(features.current_heat_flux or 0.0),
            weight=0.55,
            note="Current lining heat flux compared with the physics failure threshold.",
        ),
        EvidenceItem(
            metric="HeatFluxWearRate",
            value=features.heat_flux_slope_per_day,
            weight=0.30,
            note="Linear wear-rate slope in kW/m2 per day from the observed window.",
        ),
        EvidenceItem(
            metric="NormalizedHealthIndex",
            value=features.normalized_health_index,
            weight=0.10,
            note="0 means threshold reached; 1 means healthy baseline.",
        ),
        EvidenceItem(
            metric="ProjectedTimeToFailureDays",
            value=ttf_days,
            weight=0.05,
            note="Extrapolated days until the heat-flux failure threshold is reached.",
        ),
    ]
    if features.current_thermocouple_temp is not None:
        evidence.append(EvidenceItem(
            metric="ThermocoupleTempSlope",
            value=features.thermocouple_slope_per_day,
            weight=0.05,
            note="Thermal signature corroboration from thermocouple trend.",
        ))
    return evidence


def score_rul(
    readings: Iterable[TelemetryReading],
    *,
    failure_threshold: float = DEFAULT_HEAT_FLUX_FAILURE_THRESHOLD,
    monitoring_horizon_days: float = DEFAULT_MONITORING_HORIZON_DAYS,
) -> RulAssessment | None:
    """Score a reading window and raise a prediction only for actionable degradation.

    The estimator fits a linear heat-flux trend, extrapolates time to the physics
    failure threshold, suppresses healthy/non-actionable windows, and flags cases
    under the 21-day target for expedited human review. It never actuates equipment.
    """
    window = list(readings)
    if not window:
        return None
    features = extract_features(window, heat_flux_failure_threshold=failure_threshold)
    observed_days = (features.window_end - features.window_start).total_seconds() / 86_400.0
    if observed_days < MIN_OBSERVED_DAYS:
        return None
    if features.current_heat_flux is None or features.heat_flux_slope_per_day < MIN_WEAR_RATE_PER_DAY:
        return None

    remaining = failure_threshold - features.current_heat_flux
    if remaining <= 0:
        return None
    ttf_days = round(remaining / features.heat_flux_slope_per_day, 6)
    if ttf_days <= 0 or ttf_days > monitoring_horizon_days:
        return None

    escalated = ttf_days < MIN_ADVANCE_WARNING_DAYS
    prediction = Prediction(
        prediction_id=_prediction_id(features, ttf_days),
        pillar=Pillar.Maintenance,
        site=features.site,
        asset_id=features.asset_id,
        heat_id=None,
        kind=PredictionKind.LiningFailureRisk,
        time_to_failure_days=ttf_days,
        predicted_at=features.window_end,
        confidence=_confidence(features),
        evidence=_evidence(features, ttf_days),
        model_version=MODEL_VERSION,
        input_window_ref=features.input_window_ref,
        origin=Origin.Synthetic if features.origin == Origin.Synthetic else Origin.Real,
        status=PredictionStatus.Raised,
    )
    return RulAssessment(
        prediction=prediction,
        features=features,
        escalated=escalated,
        review_path=EXPEDITED_REVIEW_PATH if escalated else STANDARD_REVIEW_PATH,
        priority="High" if escalated else "Standard",
        escalation_reason=(
            f"Projected lead time {ttf_days:.1f} days is below the 21-day target."
            if escalated else None
        ),
    )
