"""Frozen KPI baseline computation (spec Phase 7 / KPI baseline; Constitution II/VI).

Computes a reproducible, normalized trailing-12-month baseline for the four executive KPIs
(energy/ton, CO2/ton, cost/ton, high-grade yield) per site. The result is *frozen*: it records
the exact window and as-of date so later performance is always compared against a stable,
auditable reference — never a moving target.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Iterable


@dataclass(frozen=True)
class ProductionRecord:
    """One normalized production observation (per heat or per day)."""

    timestamp: datetime
    site: str
    tons: float
    energy_mwh: float
    co2_kg: float
    cost_eur: float
    high_grade: bool


@dataclass(frozen=True)
class BaselineKpis:
    site: str
    as_of: date
    window_start: date
    window_end: date
    months: int
    sample_count: int
    total_tons: float
    energy_mwh_per_ton: float
    co2_kg_per_ton: float
    cost_eur_per_ton: float
    high_grade_yield: float
    frozen: bool = field(default=True)

    def to_dict(self) -> dict:
        return {
            "site": self.site,
            "asOf": self.as_of.isoformat(),
            "windowStart": self.window_start.isoformat(),
            "windowEnd": self.window_end.isoformat(),
            "months": self.months,
            "sampleCount": self.sample_count,
            "totalTons": round(self.total_tons, 6),
            "energyMwhPerTon": round(self.energy_mwh_per_ton, 6),
            "co2KgPerTon": round(self.co2_kg_per_ton, 6),
            "costEurPerTon": round(self.cost_eur_per_ton, 6),
            "highGradeYield": round(self.high_grade_yield, 6),
            "frozen": self.frozen,
        }


def _minus_months(d: date, months: int) -> date:
    """Return ``d`` shifted back ``months`` calendar months (clamped day-of-month)."""
    month_index = (d.year * 12 + (d.month - 1)) - months
    year, month0 = divmod(month_index, 12)
    month = month0 + 1
    # clamp day to the last valid day of the target month
    if month == 12:
        next_month_first = date(year + 1, 1, 1)
    else:
        next_month_first = date(year, month + 1, 1)
    last_day = (next_month_first - _one_day()).day
    return date(year, month, min(d.day, last_day))


def _one_day():
    from datetime import timedelta

    return timedelta(days=1)


def compute_baseline(
    records: Iterable[ProductionRecord],
    *,
    site: str,
    as_of: date,
    months: int = 12,
) -> BaselineKpis:
    """Compute the frozen, normalized baseline for ``site`` over the trailing ``months``.

    Only records for the site within ``(window_start, as_of]`` are included. Raises
    ``ValueError`` if no in-window production exists (a baseline must be grounded in data —
    Constitution VI: no fabricated metrics).
    """
    window_start = _minus_months(as_of, months)
    selected = [
        r for r in records
        if r.site == site and window_start < r.timestamp.date() <= as_of and r.tons > 0
    ]
    if not selected:
        raise ValueError(f"no production records for site {site} in the trailing {months} months")

    total_tons = sum(r.tons for r in selected)
    total_energy = sum(r.energy_mwh for r in selected)
    total_co2 = sum(r.co2_kg for r in selected)
    total_cost = sum(r.cost_eur for r in selected)
    high_grade_count = sum(1 for r in selected if r.high_grade)

    return BaselineKpis(
        site=site,
        as_of=as_of,
        window_start=window_start,
        window_end=as_of,
        months=months,
        sample_count=len(selected),
        total_tons=total_tons,
        energy_mwh_per_ton=total_energy / total_tons,
        co2_kg_per_ton=total_co2 / total_tons,
        cost_eur_per_ton=total_cost / total_tons,
        high_grade_yield=high_grade_count / len(selected),
    )


def improvement_vs_baseline(current_per_ton: float, baseline_per_ton: float) -> float:
    """Percent reduction of a lower-is-better KPI vs the frozen baseline (0 if baseline<=0)."""
    if baseline_per_ton <= 0:
        return 0.0
    return round((baseline_per_ton - current_per_ton) / baseline_per_ton * 100.0, 4)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)
