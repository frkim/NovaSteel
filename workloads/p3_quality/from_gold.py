"""Adapters: medallion Gold-mart rows -> P3 quality inputs.

Maps a `gold_quality_features` row (Site/AssetId/Timestamp + tapping_temp_c/sulfur_pct/
inclusion_index) to the `Heat` dataclass the quality model scores, deriving the fields the raw
telemetry does not carry (a stable heat id, grade target, sequence). ``actual_high_grade`` is the
spec-evaluated *expected* outcome for demo/linkage; in production it is back-filled from lab QA.
"""

from __future__ import annotations

import re
from typing import Any

from novasteel_core.models import Origin

from workloads.p3_quality.generate_quality_scenario import GRADE_TARGET, Heat, _is_high_grade

_CAMEL = re.compile(r"(?<!^)(?=[A-Z])")


def _snake(key: str) -> str:
    return _CAMEL.sub("_", key).lower()


def _normalize(row: dict[str, Any]) -> dict[str, Any]:
    return {_snake(k): v for k, v in row.items() if v is not None}


def heat_from_row(row: dict[str, Any], *, sequence: int, grade_target: str = GRADE_TARGET) -> Heat:
    """Map a `gold_quality_features` row to a Heat, deriving id/grade/sequence."""
    d = _normalize(row)
    site = str(d["site"])
    asset_id = str(d.get("asset_id", "UNK"))
    ts = d["timestamp"]
    ts_key = ts.isoformat() if hasattr(ts, "isoformat") else str(ts)
    tapping = float(d["tapping_temp_c"])
    sulfur = float(d["sulfur_pct"])
    inclusion = float(d["inclusion_index"])
    origin = d.get("origin", Origin.Synthetic.value)
    return Heat(
        heat_id=f"HEAT-{site}-{asset_id}-{ts_key}",
        site=site,
        grade_target=grade_target,
        sequence=sequence,
        tapping_temp_c=tapping,
        sulfur_pct=sulfur,
        inclusion_index=inclusion,
        actual_high_grade=_is_high_grade(sulfur, inclusion, tapping),
        origin=Origin(origin) if not isinstance(origin, Origin) else origin,
    )


def heats_from_rows(rows: list[dict[str, Any]], *, grade_target: str = GRADE_TARGET) -> list[Heat]:
    """Map rows to Heats, assigning a stable per-(site) sequence ordered by timestamp."""
    def _ts(r: dict[str, Any]):
        d = _normalize(r)
        t = d["timestamp"]
        return t.isoformat() if hasattr(t, "isoformat") else str(t)

    ordered = sorted(rows, key=lambda r: (str(_normalize(r).get("site")), _ts(r)))
    seq_by_site: dict[str, int] = {}
    heats: list[Heat] = []
    for r in ordered:
        site = str(_normalize(r).get("site"))
        seq = seq_by_site.get(site, 0)
        seq_by_site[site] = seq + 1
        heats.append(heat_from_row(r, sequence=seq, grade_target=grade_target))
    return heats
