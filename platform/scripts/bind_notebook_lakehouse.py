"""Attach the default lakehouse to the medallion notebooks and update them in-place.

Scheduled Fabric notebooks need a default lakehouse bound in their .ipynb metadata so
`spark.read.table("<lakehouse>.<table>")` / `saveAsTable(...)` resolve. This rebuilds each
medallion notebook from its .py source WITH the lakehouse dependency and PATCHes the existing
Fabric notebook item via updateDefinition (no duplicates).

Env:
  NS_FABRIC_TOKEN     Fabric bearer token (workspace admin)
  NS_FABRIC_WORKSPACE workspace id
  NS_LAKEHOUSE_ID     default lakehouse item id
  NS_LAKEHOUSE_NAME   default lakehouse name (default: onelake_novasteel)
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

NOTEBOOKS = [
    ("platform/medallion/bronze_telemetry.py", "bronze_telemetry"),
    ("platform/medallion/silver_telemetry.py", "silver_telemetry"),
    ("platform/medallion/gold_marts.py", "gold_marts"),
]


def _headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {os.environ['NS_FABRIC_TOKEN'].strip()}", "Content-Type": "application/json"}


def _ipynb_b64(py_path: pathlib.Path, lakehouse_id: str, lakehouse_name: str, ws: str) -> str:
    nb = {
        "cells": [{
            "cell_type": "code",
            "source": py_path.read_text(encoding="utf-8").splitlines(keepends=True),
            "metadata": {}, "outputs": [], "execution_count": None,
        }],
        "metadata": {
            "language_info": {"name": "python"},
            "kernelspec": {"name": "synapse_pyspark", "display_name": "Synapse PySpark"},
            # Binding the default lakehouse makes table names resolve at run time.
            "dependencies": {
                "lakehouse": {
                    "default_lakehouse": lakehouse_id,
                    "default_lakehouse_name": lakehouse_name,
                    "default_lakehouse_workspace_id": ws,
                }
            },
        },
        "nbformat": 4, "nbformat_minor": 5,
    }
    return base64.b64encode(json.dumps(nb).encode("utf-8")).decode("ascii")


def _api(method: str, url: str, body: dict | None = None) -> tuple[int, dict, str]:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=_headers(), method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            txt = resp.read().decode("utf-8")
            return resp.status, (json.loads(txt) if txt else {}), resp.headers.get("Location", "")
    except urllib.error.HTTPError as e:
        return e.code, {"error": e.read().decode("utf-8")}, ""


def _find_notebook_id(ws: str, name: str) -> str | None:
    _, body, _ = _api("GET", f"{FABRIC}/workspaces/{ws}/items?type=Notebook")
    for item in body.get("value", []):
        if item.get("displayName") == name:
            return item["id"]
    return None


def main() -> int:
    ws = os.environ["NS_FABRIC_WORKSPACE"].strip()
    lh_id = os.environ["NS_LAKEHOUSE_ID"].strip()
    lh_name = os.environ.get("NS_LAKEHOUSE_NAME", "onelake_novasteel").strip()
    for rel, name in NOTEBOOKS:
        nb_id = _find_notebook_id(ws, name)
        if not nb_id:
            print(f"  {name}: NOT FOUND")
            continue
        payload = _ipynb_b64(REPO / rel, lh_id, lh_name, ws)
        body = {"definition": {"parts": [{"path": "notebook-content.ipynb", "payload": payload, "payloadType": "InlineBase64"}]}}
        code, resp, loc = _api("POST", f"{FABRIC}/workspaces/{ws}/items/{nb_id}/updateDefinition", body)
        if code in (200, 201):
            print(f"  {name}: updated (lakehouse bound)")
        elif code == 202:
            for _ in range(30):
                s, b, _ = _api("GET", loc)
                if b.get("status") in ("Succeeded", "Completed", "Failed"):
                    break
                time.sleep(4)
            print(f"  {name}: updated async (lakehouse bound)")
        else:
            print(f"  {name}: FAILED [{code}] {resp.get('error')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
