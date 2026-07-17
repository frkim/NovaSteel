"""Deterministic synthetic furnace-lining degradation telemetry."""

from __future__ import annotations

import math
import random
from datetime import datetime, timedelta, timezone
from typing import Iterable

from novasteel_core.models import Origin, TelemetryReading

HEAT_FLUX_BASE = 80.0
HEAT_FLUX_FAILURE_THRESHOLD = 160.0
THERMOCOUPLE_BASE = 1180.0
THERMOCOUPLE_FAILURE = 1420.0


def _utc_start(start: datetime | None) -> datetime:
    if start is None:
        return datetime(2026, 1, 1, tzinfo=timezone.utc)
    return start if start.tzinfo else start.replace(tzinfo=timezone.utc)


def generate_degrading_furnace(
    *,
    asset_id: str = "LU-BF1",
    site: str = "LU",
    asset_type: str = "BlastFurnace",
    horizon_days: int = 60,
    failure_day: int = 60,
    seed: int = 7,
    start: datetime | None = None,
) -> list[TelemetryReading]:
    """Create daily synthetic readings whose heat-flux reaches failure at ``failure_day``.

    Heat flux is linear and monotonic so replayed lead-time tests are stable. The
    companion thermocouple and vibration channels include deterministic mild noise.
    All readings are explicitly synthetic with ``source_id='sim:<asset_id>'``.
    """
    if failure_day <= 0:
        raise ValueError("failure_day must be positive")
    if horizon_days < 0:
        raise ValueError("horizon_days must be non-negative")

    rng = random.Random(seed)
    start_at = _utc_start(start)
    source_id = f"sim:{asset_id}"
    readings: list[TelemetryReading] = []
    previous_temp = THERMOCOUPLE_BASE

    for day in range(horizon_days + 1):
        timestamp = start_at + timedelta(days=day)
        progress = min(day / failure_day, 1.0)
        heat_flux = HEAT_FLUX_BASE + (HEAT_FLUX_FAILURE_THRESHOLD - HEAT_FLUX_BASE) * progress

        target_temp = THERMOCOUPLE_BASE + (THERMOCOUPLE_FAILURE - THERMOCOUPLE_BASE) * progress
        noisy_temp = target_temp + 1.8 * math.sin(day * 0.37 + seed) + rng.uniform(-0.6, 0.6)
        thermocouple_temp = max(previous_temp + 0.05, noisy_temp) if day else noisy_temp
        previous_temp = thermocouple_temp

        vibration = 2.0 + 0.06 * math.sin(day * 0.21 + seed) + rng.uniform(-0.02, 0.02)

        readings.extend([
            TelemetryReading(
                asset_id=asset_id,
                asset_type=asset_type,
                site=site,
                metric="HeatFlux",
                value=round(heat_flux, 6),
                unit="kW/m2",
                timestamp=timestamp,
                quality="Good",
                origin=Origin.Synthetic,
                source_id=source_id,
            ),
            TelemetryReading(
                asset_id=asset_id,
                asset_type=asset_type,
                site=site,
                metric="ThermocoupleTemp",
                value=round(thermocouple_temp, 6),
                unit="degC",
                timestamp=timestamp,
                quality="Good",
                origin=Origin.Synthetic,
                source_id=source_id,
            ),
            TelemetryReading(
                asset_id=asset_id,
                asset_type=asset_type,
                site=site,
                metric="Vibration",
                value=round(vibration, 6),
                unit="mm/s",
                timestamp=timestamp,
                quality="Good",
                origin=Origin.Synthetic,
                source_id=source_id,
            ),
        ])
    return readings


def generate_healthy_furnace(
    *,
    asset_id: str = "LU-BF1",
    site: str = "LU",
    asset_type: str = "BlastFurnace",
    horizon_days: int = 60,
    seed: int = 11,
    start: datetime | None = None,
) -> list[TelemetryReading]:
    """Create a synthetic non-degrading furnace series for anti-alarm-fatigue tests."""
    rng = random.Random(seed)
    start_at = _utc_start(start)
    source_id = f"sim:{asset_id}"
    readings: list[TelemetryReading] = []
    for day in range(horizon_days + 1):
        timestamp = start_at + timedelta(days=day)
        heat_flux = HEAT_FLUX_BASE + 1.2 * math.sin(day * 0.19) + rng.uniform(-0.25, 0.25)
        thermocouple_temp = THERMOCOUPLE_BASE + 2.5 * math.sin(day * 0.23) + rng.uniform(-0.7, 0.7)
        vibration = 2.0 + 0.04 * math.sin(day * 0.27) + rng.uniform(-0.02, 0.02)
        for metric, value, unit in (
            ("HeatFlux", heat_flux, "kW/m2"),
            ("ThermocoupleTemp", thermocouple_temp, "degC"),
            ("Vibration", vibration, "mm/s"),
        ):
            readings.append(TelemetryReading(
                asset_id=asset_id,
                asset_type=asset_type,
                site=site,
                metric=metric,
                value=round(value, 6),
                unit=unit,
                timestamp=timestamp,
                quality="Good",
                origin=Origin.Synthetic,
                source_id=source_id,
            ))
    return readings


def readings_up_to(readings: Iterable[TelemetryReading], day: int) -> list[TelemetryReading]:
    """Return readings from the first timestamp through ``day`` inclusive."""
    ordered = sorted(readings, key=lambda r: r.timestamp)
    if not ordered:
        return []
    start = ordered[0].timestamp
    cutoff = start + timedelta(days=day)
    return [r for r in ordered if r.timestamp <= cutoff]


def replay_degrading_until_day(
    *,
    up_to_day: int,
    failure_day: int = 60,
    horizon_days: int = 60,
    seed: int = 7,
) -> list[TelemetryReading]:
    """Generate and truncate the deterministic degrading-furnace scenario."""
    return readings_up_to(
        generate_degrading_furnace(horizon_days=horizon_days, failure_day=failure_day, seed=seed),
        up_to_day,
    )
