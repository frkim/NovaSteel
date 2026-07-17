"""Deterministic synthetic production history for KPI baseline tests (Constitution IX).

Generates ~13 months of daily production records so a trailing-12-month baseline has a full
window plus a few out-of-window days to prove the window boundary is enforced.
"""

from __future__ import annotations

import math
import random
from datetime import date, datetime, timedelta, timezone

from kpi.kpi_baseline import ProductionRecord

START = datetime(2025, 5, 1, 6, 0, tzinfo=timezone.utc)


def generate_history(*, site: str = "LU", days: int = 400, seed: int = 5) -> list[ProductionRecord]:
    """One record per day: fixed tonnage with mild deterministic variation in energy/CO2/cost."""
    rng = random.Random(seed)
    out: list[ProductionRecord] = []
    for i in range(days):
        ts = START + timedelta(days=i)
        tons = 150.0 + 5.0 * math.sin(i * 0.3)
        energy = tons * (0.62 + 0.02 * math.sin(i * 0.11)) + rng.uniform(-0.5, 0.5)
        co2 = energy * (300.0 + 20.0 * math.sin(i * 0.07))  # kg per MWh ~ carbon
        cost = energy * (55.0 + 5.0 * math.sin(i * 0.09))
        high_grade = (i % 5) != 0  # ~80% high-grade baseline
        out.append(ProductionRecord(
            timestamp=ts,
            site=site,
            tons=round(tons, 3),
            energy_mwh=round(energy, 4),
            co2_kg=round(co2, 3),
            cost_eur=round(cost, 3),
            high_grade=high_grade,
        ))
    return out


def default_as_of() -> date:
    """A stable as-of date well inside the generated range (trailing 12 months full)."""
    return date(2026, 5, 1)
