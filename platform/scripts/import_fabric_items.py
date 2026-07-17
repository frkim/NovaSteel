"""Import NovaSteel notebooks (and stub eventstream/data-pipeline items) into a live
Fabric workspace via the Fabric REST API.

Auth: pass a Fabric bearer token via the NS_FABRIC_TOKEN env var (a service-principal
token that is a workspace/capacity admin, or an interactive admin token). Workspace id
via NS_FABRIC_WORKSPACE.

Usage:
  $env:NS_FABRIC_TOKEN = (Get-Content sptoken.txt)
  $env:NS_FABRIC_WORKSPACE = '<workspace-guid>'
  python platform/scripts/import_fabric_items.py
"""

from __future__ import annotations

import base64
import json
import os
import pathlib
import time
import urllib.error
import urllib.request

FABRIC = "https://api.fabric.microsoft.com/v1"
REPO = pathlib.Path(__file__).resolve().parents[2]

# (source .py, Fabric notebook display name)
NOTEBOOKS = [
    ("platform/medallion/bronze_telemetry.py", "bronze_telemetry"),
    ("platform/medallion/silver_telemetry.py", "silver_telemetry"),
    ("platform/medallion/gold_marts.py", "gold_marts"),
    ("workloads/p1_predictive_maintenance/rul_notebook.py", "p1_rul_scoring"),
]


def _headers() -> dict[str, str]:
    tok = os.environ["NS_FABRIC_TOKEN"].strip()
    return {"Authorization": f"Bearer {tok}", "Content-Type": "application/json"}


def _py_to_ipynb_b64(py_path: pathlib.Path) -> str:
    """Wrap a .py script into a minimal Fabric PySpark .ipynb and base64-encode it."""
    source = py_path.read_text(encoding="utf-8").splitlines(keepends=True)
    nb = {
        "cells": [{
            "cell_type": "code",
            "source": source,
            "metadata": {},
            "outputs": [],
            "execution_count": None,
        }],
        "metadata": {
            "language_info": {"name": "python"},
            "kernelspec": {"name": "synapse_pyspark", "display_name": "Synapse PySpark"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    raw = json.dumps(nb).encode("utf-8")
    return base64.b64encode(raw).decode("ascii")


def _post(url: str, body: dict) -> tuple[int, dict, str]:
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"),
                                headers=_headers(), method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            txt = resp.read().decode("utf-8")
            return resp.status, (json.loads(txt) if txt else {}), resp.headers.get("Location", "")
    except urllib.error.HTTPError as e:
        return e.code, {"error": e.read().decode("utf-8")}, ""


def _wait_lro(location: str) -> None:
    if not location:
        return
    for _ in range(30):
        req = urllib.request.Request(location, headers=_headers(), method="GET")
        with urllib.request.urlopen(req) as resp:
            st = json.loads(resp.read().decode("utf-8")).get("status")
        if st in ("Succeeded", "Completed", "Failed"):
            return
        time.sleep(5)


def import_notebook(ws: str, py_rel: str, name: str) -> None:
    body = {
        "displayName": name,
        "definition": {
            "format": "ipynb",
            "parts": [{
                "path": "notebook-content.ipynb",
                "payload": _py_to_ipynb_b64(REPO / py_rel),
                "payloadType": "InlineBase64",
            }],
        },
    }
    code, resp, loc = _post(f"{FABRIC}/workspaces/{ws}/notebooks", body)
    if code in (200, 201):
        print(f"  notebook '{name}' created ({resp.get('id','?')})")
    elif code == 202:
        _wait_lro(loc)
        print(f"  notebook '{name}' created (async)")
    else:
        print(f"  notebook '{name}' FAILED [{code}]: {resp.get('error')}")


def create_item(ws: str, item_type: str, name: str) -> None:
    code, resp, loc = _post(f"{FABRIC}/workspaces/{ws}/{item_type}", {"displayName": name})
    if code in (200, 201):
        print(f"  {item_type[:-1]} '{name}' created ({resp.get('id','?')})")
    elif code == 202:
        _wait_lro(loc)
        print(f"  {item_type[:-1]} '{name}' created (async)")
    else:
        print(f"  {item_type[:-1]} '{name}' FAILED [{code}]: {resp.get('error')}")


def main() -> int:
    ws = os.environ["NS_FABRIC_WORKSPACE"].strip()
    print(f"Importing items into workspace {ws} ...")
    print("Notebooks:")
    for rel, name in NOTEBOOKS:
        import_notebook(ws, rel, name)
    print("Streaming / pipeline items (topology + source binding configured in-portal):")
    create_item(ws, "eventstreams", "es_telemetry")
    create_item(ws, "dataPipelines", "df_mes_erp_eam")
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
