"""Package the NovaSteel workloads and make a Fabric notebook run them end-to-end.

Steps:
1. Build the ``novasteel-core`` and ``novasteel-workloads`` wheels.
2. Upload both wheels to the lakehouse ``Files/wheels/`` via the OneLake DFS API.
3. Inject a ``%pip install`` cell + a scoring-call cell into a target notebook so a
   scheduled/on-demand run installs the wheels and actually invokes the tested model.

Because Fabric Spark needs >=F4 (F2 rejects Spark with HTTP 430), this is designed for the
"bump -> run -> drop" batch pattern. Uploading the wheels works on any capacity; only the
notebook *execution* needs F4.

Env:
  FABRIC_TOKEN    token for https://api.fabric.microsoft.com  (az account get-access-token --resource https://api.fabric.microsoft.com)
  ONELAKE_TOKEN   token for https://storage.azure.com          (az account get-access-token --resource https://storage.azure.com)

Usage:
  python platform/scripts/deploy_workload_wheels.py <notebookId> \
      --call "from workloads.p1_predictive_maintenance.rul_notebook import score_gold_furnace_features; display({'p1PredictionsEmitted': score_gold_furnace_features(spark)})"
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import pathlib
import subprocess
import sys
import time

import requests

REPO = pathlib.Path(__file__).resolve().parents[2]
WS = "9a005c2a-169c-4cd7-af65-7f097bd0c5b8"
LAKEHOUSE = "6ca48905-6b17-42da-9458-0caaa0e5fb3c"  # onelake_novasteel
LAKEHOUSE_SUFFIXED = f"{LAKEHOUSE}"
DIST = REPO / "dist"
WHEELS = ["novasteel_core-0.1.0-py3-none-any.whl", "novasteel_workloads-0.1.0-py3-none-any.whl"]
ONELAKE = "https://onelake.dfs.fabric.microsoft.com"
FABRIC = f"https://api.fabric.microsoft.com/v1/workspaces/{WS}/notebooks"


def build_wheels() -> None:
    DIST.mkdir(exist_ok=True)
    for target in [REPO / "libs" / "novasteel_core", REPO]:
        subprocess.run([sys.executable, "-m", "build", "--wheel", str(target), "--outdir", str(DIST)], check=True)


def upload_wheels() -> str:
    token = os.environ["ONELAKE_TOKEN"]
    h = {"Authorization": f"Bearer {token}"}
    for name in WHEELS:
        data = (DIST / name).read_bytes()
        base = f"{ONELAKE}/{WS}/{LAKEHOUSE_SUFFIXED}/Files/wheels/{name}"
        requests.put(f"{base}?resource=file", headers=h).raise_for_status()
        requests.patch(f"{base}?action=append&position=0", headers={**h, "Content-Type": "application/octet-stream"}, data=data).raise_for_status()
        requests.patch(f"{base}?action=flush&position={len(data)}", headers=h).raise_for_status()
        print(f"  uploaded Files/wheels/{name} ({len(data)} bytes)")
    return "/lakehouse/default/Files/wheels/" + " /lakehouse/default/Files/wheels/".join(WHEELS)


def _poll(op_url, h):
    while True:
        time.sleep(4)
        o = requests.get(op_url, headers=h).json()
        if o.get("status") not in ("Running", "NotStarted"):
            return o


def _lro(resp, h):
    if resp.status_code == 200:
        return "Succeeded", (resp.json() if resp.text else None)
    loc = resp.headers.get("Location")
    o = _poll(loc, h)
    if o.get("status") == "Succeeded":
        r = requests.get(loc + "/result", headers=h)
        return "Succeeded", (r.json() if r.text else None)
    return o.get("status", "Failed"), o


def wire_notebook(nb_id: str, pip_paths: str, call_code: str) -> None:
    h = {"Authorization": f"Bearer {os.environ['FABRIC_TOKEN']}", "Content-Type": "application/json"}
    r = requests.post(f"{FABRIC}/{nb_id}/getDefinition", headers=h, data="{}")
    status, res = _lro(r, h)
    if status != "Succeeded":
        raise RuntimeError(f"getDefinition failed: {json.dumps(res)[:400]}")

    parts = res["definition"]["parts"]
    new_parts = []
    for p in parts:
        if p["path"] == ".schedules":
            continue
        if p["path"].endswith(".py"):
            py = base64.b64decode(p["payload"]).decode("utf-8")
            py = _inject_cells(py, pip_paths, call_code)
            payload = base64.b64encode(py.encode("utf-8")).decode("ascii")
            new_parts.append({"path": p["path"], "payload": payload, "payloadType": "InlineBase64"})
        else:
            new_parts.append({"path": p["path"], "payload": p["payload"], "payloadType": p["payloadType"]})

    body = json.dumps({"definition": {"parts": new_parts}})
    u = requests.post(f"{FABRIC}/{nb_id}/updateDefinition?updateMetadata=true", headers=h, data=body)
    status, res = _lro(u, h)
    if status != "Succeeded":
        raise RuntimeError(f"updateDefinition failed: {json.dumps(res)[:600]}")
    print("  notebook wired: %pip install + scoring call injected")


_INSTALL_MARK = "# NOVASTEEL_WHEELS_INSTALL"
_CALL_MARK = "# NOVASTEEL_SCORING_CALL"


def _inject_cells(py: str, pip_paths: str, call_code: str) -> str:
    lines = py.split("\n")
    # Find the first "# CELL" marker; insert an install cell before it.
    cell_idx = next((i for i, ln in enumerate(lines) if ln.startswith("# CELL")), len(lines))
    install_cell = [
        "# CELL ********************",
        "",
        _INSTALL_MARK,
        f"%pip install {pip_paths}",
        "",
    ]
    call_cell = [
        "",
        "# CELL ********************",
        "",
        _CALL_MARK,
        call_code,
        "",
    ]
    # Avoid duplicating on re-runs.
    if _INSTALL_MARK not in py:
        lines = lines[:cell_idx] + install_cell + lines[cell_idx:]
    if _CALL_MARK not in py:
        lines = lines + call_cell
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("notebook_id")
    ap.add_argument("--call", required=True, help="Python to invoke the scoring wrapper in Fabric")
    ap.add_argument("--skip-build", action="store_true")
    args = ap.parse_args()

    if not args.skip_build:
        print("Building wheels ...")
        build_wheels()
    print("Uploading wheels to OneLake ...")
    pip_paths = upload_wheels()
    print("Wiring notebook ...")
    wire_notebook(args.notebook_id, pip_paths, args.call)
    print("Done. Bump the capacity to >=F4 and run the notebook to score.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
