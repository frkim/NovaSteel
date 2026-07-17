"""Execute P1 furnace-RUL scoring against LIVE Gold features in the Fabric eventhouse.

Flow: ingest a deterministic degrading-furnace series into the live Eventhouse
`TelemetryRaw`, query it back (the live Gold feature source), run the tested RUL model,
and emit a Prediction with a >=21-day advance warning. Proves P1 scoring end-to-end on
the live F8 platform.

Env:
  NS_KUSTO_URI    Eventhouse query service URI (https://trd-...kusto.fabric.microsoft.com)
  NS_KUSTO_DB     KQL database name (novasteel_rti)
  NS_KUSTO_TOKEN  Bearer token for the cluster (az account get-access-token --resource <uri>)

Run:  python workloads/p1_predictive_maintenance/run_p1_live.py
"""

from __future__ import annotations

import json
import os
import pathlib
import sys
import urllib.request

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from novasteel_core.models import Origin, TelemetryReading  # noqa: E402
from workloads.p1_predictive_maintenance.generate_degrading_furnace import (  # noqa: E402
    generate_degrading_furnace,
    readings_up_to,
)
from workloads.p1_predictive_maintenance.rul_model import score_rul  # noqa: E402

ASSET = "LU-BF9"  # isolated demo asset in the live eventhouse


def _kusto(endpoint: str, path: str, body: dict) -> dict:
    req = urllib.request.Request(
        f"{os.environ['NS_KUSTO_URI']}/v1/rest/{path}",
        data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": f"Bearer {os.environ['NS_KUSTO_TOKEN']}",
                 "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _ingest(readings: list[TelemetryReading]) -> None:
    db = os.environ["NS_KUSTO_DB"]
    rows = []
    for r in readings:
        ts = r.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
        rows.append(",".join([
            r.asset_id, r.asset_type, r.site, r.metric, f"{r.value}", r.unit, ts,
            r.quality, r.origin.value, r.source_id, ts, f"sim-{r.asset_id}",
            f"degrading-furnace-{r.asset_id}",
        ]))
    csl = ".ingest inline into table TelemetryRaw <|\n" + "\n".join(rows)
    _kusto(os.environ["NS_KUSTO_URI"], "mgmt", {"db": db, "csl": csl})


def _query_live_features() -> list[TelemetryReading]:
    db = os.environ["NS_KUSTO_DB"]
    csl = (f"TelemetryRaw | where AssetId == '{ASSET}' "
           "| project AssetId, AssetType, Site, Metric, Value, Unit, Timestamp, Quality, Origin, SourceId "
           "| order by Timestamp asc")
    res = _kusto(os.environ["NS_KUSTO_URI"], "query", {"db": db, "csl": csl})
    table = res["Tables"][0]
    cols = [c["ColumnName"] for c in table["Columns"]]
    out: list[TelemetryReading] = []
    for row in table["Rows"]:
        rec = dict(zip(cols, row))
        out.append(TelemetryReading.model_validate({
            "assetId": rec["AssetId"], "assetType": rec["AssetType"], "site": rec["Site"],
            "metric": rec["Metric"], "value": float(rec["Value"]), "unit": rec["Unit"],
            "timestamp": rec["Timestamp"], "quality": rec["Quality"],
            "origin": rec["Origin"], "sourceId": rec["SourceId"],
        }))
    return out


def main() -> int:
    # Deterministic degrading furnace failing at day 60; replay up to day 39 (>=21d before).
    series = generate_degrading_furnace(asset_id=ASSET, site="LU", failure_day=60, horizon_days=60, seed=7)
    replay = readings_up_to(series, 39)
    print(f"Ingesting {len(replay)} synthetic readings for {ASSET} into live eventhouse ...")
    _ingest(replay)

    live = _query_live_features()
    print(f"Queried {len(live)} readings back from the live eventhouse (Gold feature source).")
    assert live and all(r.origin == Origin.Synthetic for r in live), "provenance must be Synthetic"

    assessment = score_rul(live)
    assert assessment is not None, "expected a furnace-lining prediction from live features"
    p = assessment.prediction
    print("\n=== P1 RUL Prediction (scored on LIVE Fabric eventhouse features) ===")
    print(f"  kind               : {p.kind.value}")
    print(f"  site/asset         : {p.site}/{p.asset_id}")
    print(f"  timeToFailureDays  : {p.time_to_failure_days:.1f}  (>=21 required)")
    print(f"  confidence         : {p.confidence:.3f}")
    print(f"  modelVersion       : {p.model_version}")
    print(f"  origin             : {p.origin.value}")
    print(f"  evidence           : {[e.metric for e in p.evidence]}")
    print(f"  escalated          : {assessment.escalated}")
    assert p.time_to_failure_days is not None and p.time_to_failure_days >= 21, "must warn >=21 days ahead"
    print("\nLIVE P1 OK: >=21-day furnace-lining warning produced from live eventhouse features (SC-003).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
