"""Adapters: medallion Gold-mart rows -> P2 dispatch inputs.

The Fabric Gold marts use mixed column casing (snake_case from the medallion pivot, PascalCase
from Spark). These helpers normalize a row dict to the P2 contract/dataclass shape so the notebook
can score directly off `gold_market_signals` (medallion-derived) and `gold_energy_jobs`.
"""

from __future__ import annotations

import re
from typing import Any

from novasteel_core.models import MarketSignal, Origin

from workloads.p2_energy_dispatch.dispatch_model import Job

_CAMEL = re.compile(r"(?<!^)(?=[A-Z])")


def _snake(key: str) -> str:
    """PascalCase/camelCase/snake_case -> snake_case (e.g. AssetId->asset_id, jobId->job_id)."""
    return _CAMEL.sub("_", key).lower()


def _normalize(row: dict[str, Any]) -> dict[str, Any]:
    return {_snake(k): v for k, v in row.items() if v is not None}


def market_signal_from_row(row: dict[str, Any]) -> MarketSignal:
    """Map a `gold_market_signals` row to a MarketSignal (extra columns ignored)."""
    d = _normalize(row)
    return MarketSignal.model_validate({
        "market": d["market"],
        "timestamp": d["timestamp"],
        "spot_price_eur_mwh": float(d["spot_price_eur_mwh"]),
        "grid_carbon_grams_per_kwh": float(d["grid_carbon_grams_per_kwh"]),
    })


def job_from_row(row: dict[str, Any]) -> Job:
    """Map a `gold_energy_jobs` row (production planning) to a dispatch Job."""
    d = _normalize(row)
    origin = d.get("origin", Origin.Synthetic.value)
    return Job(
        job_id=str(d["job_id"]),
        furnace_id=str(d["furnace_id"]),
        site=str(d["site"]),
        tons=float(d["tons"]),
        production_mwh=float(d["production_mwh"]),
        duration_slots=int(d["duration_slots"]),
        ready_slot=int(d["ready_slot"]),
        deadline_slot=int(d["deadline_slot"]),
        origin=Origin(origin) if not isinstance(origin, Origin) else origin,
    )
