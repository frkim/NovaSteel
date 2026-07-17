"""Physics-informed furnace-lining feature extraction."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

from novasteel_core.models import Origin, TelemetryReading

DEFAULT_HEAT_FLUX_FAILURE_THRESHOLD = 160.0
DEFAULT_HEAT_FLUX_HEALTHY_BASELINE = 80.0


@dataclass(frozen=True)
class LinearFit:
    slope_per_day: float
    intercept: float
    r_squared: float


@dataclass(frozen=True)
class FurnaceFeatureRecord:
    asset_id: str
    site: str
    origin: Origin
    source_ids: tuple[str, ...]
    window_start: datetime
    window_end: datetime
    current_heat_flux: float | None
    heat_flux_slope_per_day: float
    heat_flux_r_squared: float
    heat_flux_acceleration_per_day2: float
    current_thermocouple_temp: float | None
    thermocouple_slope_per_day: float
    vibration_level: float | None
    normalized_health_index: float
    input_window_ref: str


def _days_since_start(readings: list[TelemetryReading]) -> list[float]:
    start = readings[0].timestamp
    return [(r.timestamp - start).total_seconds() / 86_400.0 for r in readings]


def linear_fit(xs: list[float], ys: list[float]) -> LinearFit:
    """Least-squares linear fit without external dependencies."""
    if len(xs) != len(ys):
        raise ValueError("xs and ys must be the same length")
    if len(xs) < 2:
        return LinearFit(0.0, ys[0] if ys else 0.0, 0.0)
    x_mean = sum(xs) / len(xs)
    y_mean = sum(ys) / len(ys)
    denom = sum((x - x_mean) ** 2 for x in xs)
    if denom == 0:
        return LinearFit(0.0, y_mean, 0.0)
    slope = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys)) / denom
    intercept = y_mean - slope * x_mean
    ss_tot = sum((y - y_mean) ** 2 for y in ys)
    ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(xs, ys))
    r_squared = 1.0 if ss_tot == 0 else max(0.0, min(1.0, 1.0 - ss_res / ss_tot))
    return LinearFit(slope, intercept, r_squared)


def _metric_rows(readings: Iterable[TelemetryReading], metric: str) -> list[TelemetryReading]:
    return sorted((r for r in readings if r.metric == metric), key=lambda r: r.timestamp)


def _metric_fit(readings: list[TelemetryReading]) -> LinearFit:
    if not readings:
        return LinearFit(0.0, 0.0, 0.0)
    return linear_fit(_days_since_start(readings), [r.value for r in readings])


def _recent_acceleration(readings: list[TelemetryReading]) -> float:
    if len(readings) < 6:
        return 0.0
    midpoint = len(readings) // 2
    early = readings[:midpoint]
    late = readings[midpoint:]
    return _metric_fit(late).slope_per_day - _metric_fit(early).slope_per_day


def _origin_for(readings: Iterable[TelemetryReading]) -> Origin:
    return Origin.Synthetic if any(r.origin == Origin.Synthetic for r in readings) else Origin.Real


def extract_features(
    readings: Iterable[TelemetryReading],
    *,
    heat_flux_failure_threshold: float = DEFAULT_HEAT_FLUX_FAILURE_THRESHOLD,
    heat_flux_healthy_baseline: float = DEFAULT_HEAT_FLUX_HEALTHY_BASELINE,
) -> FurnaceFeatureRecord:
    """Extract current wear, slope, acceleration and health index from a reading window."""
    window = sorted(list(readings), key=lambda r: r.timestamp)
    if not window:
        raise ValueError("at least one telemetry reading is required")

    heat = _metric_rows(window, "HeatFlux")
    temp = _metric_rows(window, "ThermocoupleTemp")
    vibration = _metric_rows(window, "Vibration")
    heat_fit = _metric_fit(heat)
    temp_fit = _metric_fit(temp)
    current_heat = heat[-1].value if heat else None
    current_temp = temp[-1].value if temp else None
    current_vibration = vibration[-1].value if vibration else None

    if current_heat is None:
        health_index = 1.0
    else:
        span = max(heat_flux_failure_threshold - heat_flux_healthy_baseline, 1.0)
        health_index = (heat_flux_failure_threshold - current_heat) / span
        health_index = max(0.0, min(1.0, health_index))

    asset_id = window[0].asset_id
    site = window[0].site
    source_ids = tuple(sorted({r.source_id for r in window if r.source_id}))
    input_window_ref = (
        f"onelake_novasteel.gold_furnace_features/{site}/{asset_id}/"
        f"{window[0].timestamp.date().isoformat()}_{window[-1].timestamp.date().isoformat()}"
    )
    return FurnaceFeatureRecord(
        asset_id=asset_id,
        site=site,
        origin=_origin_for(window),
        source_ids=source_ids,
        window_start=window[0].timestamp,
        window_end=window[-1].timestamp,
        current_heat_flux=current_heat,
        heat_flux_slope_per_day=heat_fit.slope_per_day,
        heat_flux_r_squared=heat_fit.r_squared,
        heat_flux_acceleration_per_day2=_recent_acceleration(heat),
        current_thermocouple_temp=current_temp,
        thermocouple_slope_per_day=temp_fit.slope_per_day,
        vibration_level=current_vibration,
        normalized_health_index=health_index,
        input_window_ref=input_window_ref,
    )
