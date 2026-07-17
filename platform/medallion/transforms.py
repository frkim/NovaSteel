"""Provenance-preserving medallion transforms (Bronze -> Silver -> Gold).

This is the **Spark-free core** of the ingestion pipeline so the provenance and
data-quality gates (Constitution VIII/IX) run deterministically under pytest. The
Fabric notebooks (`bronze_telemetry.py`, `silver_telemetry.py`, `gold_marts.py`)
wrap these same functions over Spark DataFrames on the live OneLake lakehouse.

Guarantees enforced here:
- Constitution IX: `origin` + `sourceId` (and `site`/`quality`) are preserved verbatim
  Bronze -> Silver -> Gold, and synthetic data is NEVER counted in real KPIs.
- Constitution VI: missing/stale telemetry is flagged (reduced confidence), never
  silently presented as current.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable

from novasteel_core.models import Origin, TelemetryReading

# Identity/provenance columns that MUST survive every medallion layer (Constitution IX).
PROVENANCE_FIELDS: tuple[str, ...] = ("origin", "source_id", "site", "quality")

# Telemetry older than this (vs. the processing clock) is flagged stale (Constitution VI).
DEFAULT_STALE_AFTER_SECONDS = 900  # 15 minutes


def _as_reading(row: TelemetryReading | dict[str, Any]) -> TelemetryReading:
    return row if isinstance(row, TelemetryReading) else TelemetryReading.model_validate(row)


def _aware(ts: datetime) -> datetime:
    return ts if ts.tzinfo else ts.replace(tzinfo=timezone.utc)


def to_bronze(readings: Iterable[TelemetryReading | dict[str, Any]],
              ingested_at: datetime | None = None) -> list[dict[str, Any]]:
    """Append-only raw landing. Preserves every source field verbatim and stamps
    ingestion metadata. No filtering, no mutation of provenance (Constitution IX)."""
    ingested_at = _aware(ingested_at or datetime.now(timezone.utc))
    bronze: list[dict[str, Any]] = []
    for row in readings:
        r = _as_reading(row)
        rec = r.model_dump(by_alias=False)
        rec["ingested_at"] = ingested_at
        rec["_layer"] = "bronze"
        bronze.append(rec)
    return bronze


def to_silver(bronze_rows: Iterable[dict[str, Any]],
              now: datetime | None = None,
              stale_after_seconds: int = DEFAULT_STALE_AFTER_SECONDS) -> list[dict[str, Any]]:
    """Dedup, conform, and compute freshness/quality flags. Provenance preserved.

    - Dedup key: (asset_id, metric, timestamp) keeping the latest ingestion.
    - Adds `freshness_seconds`, `is_stale`, and `partition` (site + date) for Gold.
    - Downgrades `quality` to 'Suspect' when stale (reduced confidence, Constitution VI).
    """
    now = _aware(now or datetime.now(timezone.utc))
    latest: dict[tuple[str, str, datetime], dict[str, Any]] = {}
    for rec in bronze_rows:
        key = (rec["asset_id"], rec["metric"], _aware(rec["timestamp"]))
        prev = latest.get(key)
        if prev is None or _aware(rec.get("ingested_at", now)) >= _aware(prev.get("ingested_at", now)):
            latest[key] = rec

    silver: list[dict[str, Any]] = []
    for rec in latest.values():
        ts = _aware(rec["timestamp"])
        freshness = (now - ts).total_seconds()
        is_stale = freshness > stale_after_seconds
        out = dict(rec)
        # Provenance is copied through untouched.
        out["freshness_seconds"] = freshness
        out["is_stale"] = is_stale
        if is_stale and out.get("quality") == "Good":
            out["quality"] = "Suspect"
        out["partition"] = f"{rec['site']}/{ts.date().isoformat()}"
        out["_layer"] = "silver"
        silver.append(out)
    silver.sort(key=lambda r: (r["site"], r["asset_id"], r["metric"], _aware(r["timestamp"])))
    return silver


def to_gold_kpi(silver_rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Aggregate per (site, metric, data_class) KPI marts.

    Synthetic data (`origin == Synthetic`) is bucketed into a separate `data_class`
    and MUST NOT be aggregated into real KPIs (Constitution IX). Each mart row carries
    its `data_class` so dashboards/KPIs can exclude or clearly label synthetic data.
    """
    buckets: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for rec in silver_rows:
        data_class = "synthetic" if rec.get("origin") == Origin.Synthetic.value else "real"
        buckets.setdefault((rec["site"], rec["metric"], data_class), []).append(rec)

    marts: list[dict[str, Any]] = []
    for (site, metric, data_class), rows in sorted(buckets.items()):
        values = [r["value"] for r in rows]
        good = sum(1 for r in rows if r.get("quality") == "Good")
        marts.append({
            "site": site,
            "metric": metric,
            "data_class": data_class,          # 'real' | 'synthetic' (Constitution IX)
            "count": len(rows),
            "avg_value": sum(values) / len(values),
            "min_value": min(values),
            "max_value": max(values),
            "good_ratio": good / len(rows),
            "stale_count": sum(1 for r in rows if r.get("is_stale")),
            "source_ids": sorted({r.get("source_id", "") for r in rows}),
            "_layer": "gold",
        })
    return marts
