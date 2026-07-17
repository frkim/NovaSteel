"""Deterministic synthetic energy-dispatch scenario (market curve + flexible heats).

Produces an hourly market curve with a realistic diurnal shape (cheap, low-carbon at
night; expensive, carbon-intensive at midday) and a set of flexible furnace heats whose
charge is ready at staggered times but whose deadlines leave slack for load-shifting.
All data is explicitly synthetic (Constitution IX).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from novasteel_core.models import MarketSignal, Origin

from workloads.p2_energy_dispatch.dispatch_model import Job

BASE_TIME = datetime(2026, 3, 2, 0, 0, tzinfo=timezone.utc)  # a Monday 00:00 UTC
MARKET = "EU-Central"


def _day_factor(hour_of_day: int) -> float:
    """0 at deep night, ~1 at the midday demand peak (hour 13)."""
    if 6 <= hour_of_day <= 20:
        return round(math.sin(math.pi * (hour_of_day - 6) / 14.0), 6)
    return 0.05


@dataclass(frozen=True)
class EnergyScenario:
    base_time: datetime
    horizon_hours: int
    market: list[MarketSignal]
    jobs: list[Job]

    def slot_time(self, slot: int) -> datetime:
        return self.base_time + timedelta(hours=slot)


def generate_market_curve(horizon_hours: int = 48) -> list[MarketSignal]:
    """Hourly spot price (EUR/MWh) and grid carbon (g/kWh) with a diurnal shape."""
    signals: list[MarketSignal] = []
    for slot in range(horizon_hours):
        factor = _day_factor(slot % 24)
        signals.append(MarketSignal(
            market=MARKET,
            timestamp=BASE_TIME + timedelta(hours=slot),
            spot_price_eur_mwh=round(35.0 + 75.0 * factor, 4),
            grid_carbon_grams_per_kwh=round(150.0 + 320.0 * factor, 4),
        ))
    return signals


def generate_energy_scenario(
    *,
    site: str = "LU",
    furnace_id: str = "LU-EAF1",
    horizon_hours: int = 48,
    heats: int = 4,
    tons_per_heat: float = 150.0,
    production_mwh: float = 20.0,
    duration_slots: int = 2,
    ready_step_slots: int = 6,
    first_ready_slot: int = 4,
    deadline_slot: int = 47,
) -> EnergyScenario:
    """Build a deterministic scenario with ``heats`` flexible heats on one EAF.

    Charges become ready every ``ready_step_slots`` hours; each heat must finish by
    ``deadline_slot`` — leaving enough slack for the optimizer to defer/batch the heats
    into the overnight low-carbon trough.
    """
    jobs = [
        Job(
            job_id=f"HEAT-{site}-{i + 1:02d}",
            furnace_id=furnace_id,
            site=site,
            tons=tons_per_heat,
            production_mwh=production_mwh,
            duration_slots=duration_slots,
            ready_slot=first_ready_slot + i * ready_step_slots,
            deadline_slot=deadline_slot,
            origin=Origin.Synthetic,
        )
        for i in range(heats)
    ]
    return EnergyScenario(
        base_time=BASE_TIME,
        horizon_hours=horizon_hours,
        market=generate_market_curve(horizon_hours),
        jobs=jobs,
    )
