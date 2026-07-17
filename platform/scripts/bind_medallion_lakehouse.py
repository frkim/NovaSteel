"""Bind the default lakehouse into medallion notebook definitions (native .py format)
so on-demand / scheduled Spark runs resolve partial-namespace table names
(spark.read.table / saveAsTable) without an interactive portal attach.

Fabric .py notebooks store item metadata in a leading `# META` comment block; we
parse that JSON, inject metadata.dependencies.lakehouse (matching the interactively
attached bronze notebook), and push it back via the items updateDefinition API.

Usage:  python bind_medallion_lakehouse.py <notebookId> [<notebookId> ...]
Requires FABRIC_TOKEN env var (token for https://api.fabric.microsoft.com).
"""
import base64
import json
import os
import sys
import time

import requests

WS = "9a005c2a-169c-4cd7-af65-7f097bd0c5b8"
BASE = f"https://api.fabric.microsoft.com/v1/workspaces/{WS}/notebooks"
LAKE_DEP = {
    "default_lakehouse": "6ca48905-6b17-42da-9458-0caaa0e5fb3c",
    "default_lakehouse_name": "onelake_novasteel",
    "default_lakehouse_workspace_id": WS,
    "known_lakehouses": [{"id": "6ca48905-6b17-42da-9458-0caaa0e5fb3c"}],
}

TOKEN = os.environ["FABRIC_TOKEN"]
H = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
META_PREFIX = "# META "


def _poll(op_url):
    while True:
        time.sleep(4)
        o = requests.get(op_url, headers=H).json()
        if o.get("status") not in ("Running", "NotStarted"):
            return o


def _lro(resp):
    if resp.status_code == 200:
        return "Succeeded", (resp.json() if resp.text else None)
    loc = resp.headers.get("Location")
    o = _poll(loc)
    if o.get("status") == "Succeeded":
        res = requests.get(loc + "/result", headers=H)
        return "Succeeded", (res.json() if res.text else None)
    return o.get("status", "Failed"), o


def _meta_block(meta: dict) -> list:
    """Render a Fabric `# METADATA` comment block for the given metadata dict."""
    body = [META_PREFIX + l for l in json.dumps(meta, indent=2).split("\n")]
    return ["# METADATA ********************", ""] + body


def _inject_dependency(py_text: str) -> str:
    """Ensure the notebook has a default-lakehouse binding in its `# META` block,
    and repair any stale `onelake_novasteel.` schema prefix on table names."""
    # Repair broken schema-qualified table refs (lakehouse name is not a schema).
    py_text = py_text.replace("onelake_novasteel.", "")

    lines = py_text.split("\n")
    meta_idx = [i for i, ln in enumerate(lines) if ln.startswith("# META")]

    if meta_idx:  # existing block -> merge dependency in
        start, end = meta_idx[0], meta_idx[-1]
        json_lines = [
            ln[len(META_PREFIX):] if ln.startswith(META_PREFIX) else ln[len("# META"):]
            for ln in lines[start:end + 1]
        ]
        meta = json.loads("\n".join(json_lines))
        meta.setdefault("dependencies", {})["lakehouse"] = LAKE_DEP
        # widen replacement to swallow the "# METADATA ***" header + trailing blank
        hdr = next((i for i in range(start, -1, -1) if lines[i].startswith("# METADATA")), start)
        tail = end + 1
        if tail < len(lines) and lines[tail].strip() == "":
            tail += 1
        new = _meta_block(meta) + [""]
        return "\n".join(lines[:hdr] + new + lines[tail:])

    # No metadata block: insert one right after the source header.
    meta = {"kernel_info": {"name": "synapse_pyspark"}, "dependencies": {"lakehouse": LAKE_DEP}}
    hdr_idx = next((i for i, ln in enumerate(lines) if ln.startswith("# Fabric notebook source")), 0)
    block = [""] + _meta_block(meta) + [""]
    return "\n".join(lines[:hdr_idx + 1] + block + lines[hdr_idx + 1:])


def bind(nb_id):
    print(f"=== {nb_id}: getDefinition (native) ===", flush=True)
    r = requests.post(f"{BASE}/{nb_id}/getDefinition", headers=H, data="{}")
    status, res = _lro(r)
    if status != "Succeeded":
        print(f"  getDefinition FAILED: {json.dumps(res)[:500]}")
        return False
    parts = res["definition"]["parts"]

    new_parts = []
    for p in parts:
        if p["path"] == ".schedules":
            continue  # read-only; excluded from updateDefinition
        if p["path"].endswith(".py"):
            py = base64.b64decode(p["payload"]).decode("utf-8")
            py = _inject_dependency(py)
            payload = base64.b64encode(py.encode("utf-8")).decode("ascii")
            new_parts.append({"path": p["path"], "payload": payload, "payloadType": "InlineBase64"})
        else:
            new_parts.append({"path": p["path"], "payload": p["payload"], "payloadType": p["payloadType"]})

    body = json.dumps({"definition": {"parts": new_parts}})
    print(f"=== {nb_id}: updateDefinition ({len(new_parts)} parts) ===", flush=True)
    u = requests.post(f"{BASE}/{nb_id}/updateDefinition?updateMetadata=true", headers=H, data=body)
    status, res = _lro(u)
    if status != "Succeeded":
        print(f"  updateDefinition FAILED: {json.dumps(res)[:800]}")
        return False
    print("  OK -> default lakehouse bound")
    return True


if __name__ == "__main__":
    ok = all(bind(x) for x in sys.argv[1:])
    sys.exit(0 if ok else 1)
