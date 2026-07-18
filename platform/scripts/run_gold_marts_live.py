"""Eventhouse-backed live validation of the P2/P3 Gold marts.

Ingests new-metric telemetry (grid tariff + tap chemistry) into the live Eventhouse
`TelemetryRaw`, pushes the updated `gold_marts` notebook, runs Bronze -> Silver -> Gold on
Spark, and verifies `gold_market_signals` + `gold_quality_features` populate from the
eventhouse-backed shortcut. Requires >=F4.

Env: FABRIC_TOKEN, ONELAKE_TOKEN, KUSTO_TOKEN (token for the eventhouse cluster).
"""

from __future__ import annotations

import base64
import importlib.util
import json
import os
import pathlib
import time
from datetime import datetime, timedelta, timezone

import requests

REPO = pathlib.Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("vpl", REPO / "platform" / "scripts" / "validate_pillars_live.py")
vpl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vpl)  # reuse FAB headers, LAKE_DEP, _lro, run, _make_py, lakehouse_tables

KUSTO = "https://trd-ambx6f52vhyf6840ak.z1.kusto.fabric.microsoft.com"
DB = "novasteel_rti"
GOLD_MARTS_NB = "1afc497c-cdc1-4247-a07c-995188310a04"
BRONZE_NB = "feba84cf-6434-4b2f-acd9-b08f5e849fff"
SILVER_NB = "3c2d16f1-a0d9-46fc-8e99-57b2494a6ad3"
WS = vpl.WS
LAKEHOUSE = vpl.LAKEHOUSE
ONELAKE = vpl.ONELAKE


def _kusto(path: str, csl: str) -> dict:
    h = {"Authorization": f"Bearer {os.environ['KUSTO_TOKEN']}", "Content-Type": "application/json"}
    r = requests.post(f"{KUSTO}/v1/rest/{path}", headers=h, data=json.dumps({"db": DB, "csl": csl}), timeout=120)
    r.raise_for_status()
    return r.json()


def ingest_new_metrics() -> int:
    """Ingest a deterministic batch of P2 tariff + P3 quality readings into TelemetryRaw."""
    now = datetime.now(timezone.utc).replace(microsecond=0)
    rows = []
    # P2 market signals for two sites over 5 minutes (diurnal-ish values).
    for site, spot, carbon in (("LU", 42.0, 175.0), ("DE", 61.0, 255.0)):
        for i in range(5):
            ts = (now - timedelta(minutes=5 - i)).strftime("%Y-%m-%dT%H:%M:%SZ")
            for metric, value, unit in (("SpotPriceEurMwh", spot + i, "EUR/MWh"),
                                        ("GridCarbonGPerKwh", carbon + i, "gCO2/kWh")):
                rows.append(f'{site}-UTL1,Utility,{site},{metric},{value},{unit},{ts},Good,Synthetic,'
                            f'sim:{site}-UTL1,{ts},sim-{site}-UTL1,gold-marts-live')
    # P3 quality features for two furnaces over 5 heats (in-spec DP800).
    for site in ("LU", "DE"):
        for i in range(5):
            ts = (now - timedelta(minutes=5 - i)).strftime("%Y-%m-%dT%H:%M:%SZ")
            for metric, value, unit in (("TappingTemp", 1650.0 + i, "C"),
                                        ("SulfurPct", 0.007, "%"),
                                        ("InclusionIndex", 1.4, "idx")):
                rows.append(f'{site}-BF1,BlastFurnace,{site},{metric},{value},{unit},{ts},Good,Synthetic,'
                            f'sim:{site}-BF1,{ts},sim-{site}-BF1,gold-marts-live')
    csl = ".ingest inline into table TelemetryRaw <|\n" + "\n".join(rows)
    _kusto("mgmt", csl)
    return len(rows)


def push_notebook(nb_id: str, source_path: pathlib.Path) -> None:
    """Replace a deployed notebook's body with the repo .py source (single cell), keeping the
    lakehouse binding."""
    src = source_path.read_text(encoding="utf-8")
    cells = [src]
    r = requests.post(f"{vpl.NB}/{nb_id}/getDefinition", headers=vpl.FAB, data="{}")
    status, res = vpl._lro(r)
    if status != "Succeeded":
        raise RuntimeError(f"getDefinition failed: {json.dumps(res)[:300]}")
    new_parts = []
    for p in res["definition"]["parts"]:
        if p["path"] == ".schedules":
            continue
        if p["path"].endswith(".py"):
            payload = base64.b64encode(vpl._make_py(cells).encode("utf-8")).decode("ascii")
            new_parts.append({"path": p["path"], "payload": payload, "payloadType": "InlineBase64"})
        else:
            new_parts.append({"path": p["path"], "payload": p["payload"], "payloadType": p["payloadType"]})
    u = requests.post(f"{vpl.NB}/{nb_id}/updateDefinition?updateMetadata=true", headers=vpl.FAB,
                      data=json.dumps({"definition": {"parts": new_parts}}))
    status, res = vpl._lro(u)
    if status != "Succeeded":
        raise RuntimeError(f"updateDefinition failed: {json.dumps(res)[:400]}")


def run_nb(nb_id: str, name: str) -> str:
    vpl.RUNNER_NB = nb_id  # run() uses module global RUNNER_NB
    status = vpl.run()
    print(f"  {name}: {status}", flush=True)
    return status


def main() -> int:
    print("Ingesting new-metric batch into eventhouse TelemetryRaw ...", flush=True)
    n = ingest_new_metrics()
    print(f"  ingested {n} rows", flush=True)

    print("Pushing updated gold_marts notebook ...", flush=True)
    push_notebook(GOLD_MARTS_NB, REPO / "platform" / "medallion" / "gold_marts.py")

    print("Waiting for OneLake mirroring (shortcut latency ~5 min) ...", flush=True)
    time.sleep(360)

    print("Running medallion Bronze -> Silver -> Gold ...", flush=True)
    run_nb(BRONZE_NB, "bronze")
    run_nb(SILVER_NB, "silver")
    gold_status = run_nb(GOLD_MARTS_NB, "gold_marts")

    tables = vpl.lakehouse_tables()
    print("Lakehouse tables:", tables, flush=True)
    ok = ("gold_market_signals" in tables) and ("gold_quality_features" in tables) and gold_status == "Completed"
    print("RESULT", "OK" if ok else "INCOMPLETE", flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
