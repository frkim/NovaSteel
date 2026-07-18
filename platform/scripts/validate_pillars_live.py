"""Live pillar validation on Fabric (P1/P2/P3) — bump to >=F4 first.

Builds + uploads the novasteel wheels to OneLake, then reuses the existing (lakehouse-bound)
`p1_rul_scoring` notebook as a runner: it sets the notebook body per pillar, runs it on live
Spark and reports. P2/P3 materialize their synthetic Gold source marts (Constitution IX:
synthetic-origin, kept separate) and write flattened result tables.

Env: FABRIC_TOKEN (https://api.fabric.microsoft.com), ONELAKE_TOKEN (https://storage.azure.com).
"""

from __future__ import annotations

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
LAKEHOUSE = "6ca48905-6b17-42da-9458-0caaa0e5fb3c"
RUNNER_NB = "a878518d-3eb2-4c37-a5f0-20188a11c3cf"  # p1_rul_scoring (reused as runner)
DIST = REPO / "dist"
WHEELS = ["novasteel_core-0.1.0-py3-none-any.whl", "novasteel_workloads-0.1.0-py3-none-any.whl"]
ONELAKE = "https://onelake.dfs.fabric.microsoft.com"
NB = f"https://api.fabric.microsoft.com/v1/workspaces/{WS}/notebooks"
ITEMS = f"https://api.fabric.microsoft.com/v1/workspaces/{WS}/items"

FAB = {"Authorization": f"Bearer {os.environ['FABRIC_TOKEN']}", "Content-Type": "application/json"}
LAKE_DEP = {
    "kernel_info": {"name": "synapse_pyspark"},
    "dependencies": {"lakehouse": {
        "default_lakehouse": LAKEHOUSE,
        "default_lakehouse_name": "onelake_novasteel",
        "default_lakehouse_workspace_id": WS,
        "known_lakehouses": [{"id": LAKEHOUSE}],
    }},
}


def build_wheels() -> None:
    DIST.mkdir(exist_ok=True)
    for target in [REPO / "libs" / "novasteel_core", REPO]:
        subprocess.run([sys.executable, "-m", "build", "--wheel", str(target), "--outdir", str(DIST)], check=True)


def _all_wheel_files() -> list[pathlib.Path]:
    files = list(DIST.glob("*.whl")) + list((DIST / "fabric_wheels").glob("*.whl"))
    return sorted(files, key=lambda p: p.name)


def clear_remote_wheels() -> None:
    h = {"Authorization": f"Bearer {os.environ['ONELAKE_TOKEN']}"}
    url = f"{ONELAKE}/{WS}/{LAKEHOUSE}/Files/wheels?recursive=true"
    r = requests.delete(url, headers=h)
    print(f"  cleared Files/wheels ({r.status_code})", flush=True)


def upload_wheels() -> str:
    h = {"Authorization": f"Bearer {os.environ['ONELAKE_TOKEN']}"}
    for f in _all_wheel_files():
        data = f.read_bytes()
        base = f"{ONELAKE}/{WS}/{LAKEHOUSE}/Files/wheels/{f.name}"
        requests.put(f"{base}?resource=file", headers=h).raise_for_status()
        requests.patch(f"{base}?action=append&position=0",
                       headers={**h, "Content-Type": "application/octet-stream"}, data=data).raise_for_status()
        requests.patch(f"{base}?action=flush&position={len(data)}", headers=h).raise_for_status()
        print(f"  uploaded Files/wheels/{f.name} ({len(data)} bytes)", flush=True)
    return "/lakehouse/default/Files/wheels"


def _poll(url):
    while True:
        time.sleep(4)
        o = requests.get(url, headers=FAB).json()
        if o.get("status") not in ("Running", "NotStarted"):
            return o


def _lro(resp):
    if resp.status_code == 200:
        return "Succeeded", (resp.json() if resp.text else None)
    loc = resp.headers.get("Location")
    o = _poll(loc)
    if o.get("status") == "Succeeded":
        r = requests.get(loc + "/result", headers=FAB)
        return "Succeeded", (r.json() if r.text else None)
    return o.get("status", "Failed"), o


def _make_py(cells: list[str]) -> str:
    meta = "\n".join("# META " + l for l in json.dumps(LAKE_DEP, indent=2).split("\n"))
    out = ["# Fabric notebook source", "", "# METADATA ********************", "", meta, ""]
    for cell in cells:
        out += ["# CELL ********************", "", cell, ""]
    return "\n".join(out)


def set_body(cells: list[str]) -> None:
    r = requests.post(f"{NB}/{RUNNER_NB}/getDefinition", headers=FAB, data="{}")
    status, res = _lro(r)
    if status != "Succeeded":
        raise RuntimeError(f"getDefinition failed: {json.dumps(res)[:300]}")
    new_parts = []
    for p in res["definition"]["parts"]:
        if p["path"] == ".schedules":
            continue
        if p["path"].endswith(".py"):
            payload = base64.b64encode(_make_py(cells).encode("utf-8")).decode("ascii")
            new_parts.append({"path": p["path"], "payload": payload, "payloadType": "InlineBase64"})
        else:
            new_parts.append({"path": p["path"], "payload": p["payload"], "payloadType": p["payloadType"]})
    u = requests.post(f"{NB}/{RUNNER_NB}/updateDefinition?updateMetadata=true", headers=FAB,
                      data=json.dumps({"definition": {"parts": new_parts}}))
    status, res = _lro(u)
    if status != "Succeeded":
        raise RuntimeError(f"updateDefinition failed: {json.dumps(res)[:500]}")


def run() -> str:
    resp = requests.post(f"{ITEMS}/{RUNNER_NB}/jobs/instances?jobType=RunNotebook", headers=FAB, data="{}")
    loc = resp.headers["Location"]
    deadline = time.time() + 600
    while time.time() < deadline:
        time.sleep(15)
        j = requests.get(loc, headers=FAB).json()
        if j["status"] not in ("NotStarted", "InProgress", "Running"):
            if j.get("failureReason"):
                print("   failureReason:", json.dumps(j["failureReason"])[:400])
            return j["status"]
    return "Timeout"


def lakehouse_tables() -> list[str]:
    r = requests.get(f"https://api.fabric.microsoft.com/v1/workspaces/{WS}/lakehouses/{LAKEHOUSE}/tables",
                     headers=FAB).json()
    return sorted(t["name"] for t in r.get("data", []))


INSTALL = (
    "import glob, subprocess, sys, importlib\n"
    "wheels = sorted(glob.glob('/lakehouse/default/Files/wheels/*.whl'))\n"
    "subprocess.run([sys.executable, '-m', 'pip', 'install', '--no-deps', *wheels], check=True)\n"
    "importlib.invalidate_caches()"
)


def _wrap(name: str, code: str, ok_expr: str) -> str:
    indented = "\n".join("    " + l for l in code.split("\n"))
    return (
        "import traceback\n"
        f"_p = '/lakehouse/default/Files/val_{name}.txt'\n"
        "try:\n"
        f"{indented}\n"
        f"    _r = {ok_expr}\n"
        "except Exception:\n"
        "    _r = traceback.format_exc()\n"
        "open(_p, 'w').write(str(_r))\n"
        "print(str(_r)[:800])"
    )


_P1_CODE = (
    "from workloads.p1_predictive_maintenance.rul_notebook import score_gold_furnace_features\n"
    "n = score_gold_furnace_features(spark)"
)
_P2_CODE = (
    "import json\n"
    "from workloads.p2_energy_dispatch.generate_energy_scenario import generate_energy_scenario\n"
    "from workloads.p2_energy_dispatch.dispatch_model import build_energy_plan, baseline_dispatch, optimize_dispatch, energy_savings_pct, co2_savings_pct\n"
    "s = generate_energy_scenario()\n"
    "market_rows = [m.model_dump(by_alias=True, mode='json') for m in s.market]\n"
    "job_rows = [{'jobId':j.job_id,'furnaceId':j.furnace_id,'site':j.site,'tons':j.tons,'productionMwh':j.production_mwh,'durationSlots':j.duration_slots,'readySlot':j.ready_slot,'deadlineSlot':j.deadline_slot,'origin':j.origin.value} for j in s.jobs]\n"
    "spark.createDataFrame(market_rows).write.mode('overwrite').option('overwriteSchema','true').saveAsTable('gold_market_signals')\n"
    "spark.createDataFrame(job_rows).write.mode('overwrite').option('overwriteSchema','true').saveAsTable('gold_energy_jobs')\n"
    "plan = build_energy_plan(s.jobs, s.market, base_time=s.base_time)\n"
    "row = plan.model_dump(by_alias=True, mode='json')\n"
    "b = baseline_dispatch(s.jobs, s.market); o = optimize_dispatch(s.jobs, s.market)\n"
    "summary = {'energyPlanId':row['energyPlanId'],'site':row['site'],'status':row['status'],'expectedEnergyPerTon':float(row['expectedEnergyPerTon']),'baselineEnergyPerTon':float(row['baselineComparison']['baselineEnergyPerTon']),'expectedCo2PerTon':float(row['expectedCo2PerTon']),'baselineCo2PerTon':float(row['baselineComparison']['baselineCo2PerTon']),'origin':row['origin'],'planJson':json.dumps(row)}\n"
    "spark.createDataFrame([summary]).write.mode('overwrite').option('overwriteSchema','true').saveAsTable('p2_energy_plans')"
)
_P3_CODE = (
    "import json\n"
    "from workloads.p3_quality.generate_quality_scenario import generate_quality_scenario\n"
    "from workloads.p3_quality.quality_model import score_batch, spc_drift_prediction, baseline_yield, recommended_yield\n"
    "heats = generate_quality_scenario()\n"
    "heat_rows = [{'heatId':h.heat_id,'site':h.site,'gradeTarget':h.grade_target,'sequence':h.sequence,'tappingTempC':h.tapping_temp_c,'sulfurPct':h.sulfur_pct,'inclusionIndex':h.inclusion_index,'actualHighGrade':h.actual_high_grade,'origin':h.origin.value} for h in heats]\n"
    "spark.createDataFrame(heat_rows).write.mode('overwrite').option('overwriteSchema','true').saveAsTable('gold_quality_features')\n"
    "a = score_batch(heats)\n"
    "preds = [{'predictionId':x.prediction.prediction_id,'heatId':x.prediction.heat_id,'kind':x.prediction.kind.value,'confidence':x.prediction.confidence,'predictedHighGrade':x.predicted_high_grade,'actualHighGrade':x.actual_high_grade,'json':json.dumps(x.prediction.model_dump(by_alias=True,mode='json'))} for x in a]\n"
    "spark.createDataFrame(preds).write.mode('overwrite').option('overwriteSchema','true').saveAsTable('p3_quality_predictions')\n"
    "recs = [{'recommendationId':x.recommendation.recommendation_id,'heatId':x.prediction.heat_id,'summary':x.recommendation.summary,'status':x.recommendation.status.value,'json':json.dumps(x.recommendation.model_dump(by_alias=True,mode='json'))} for x in a if x.recommendation]\n"
    "recs and spark.createDataFrame(recs).write.mode('overwrite').option('overwriteSchema','true').saveAsTable('p3_quality_recommendations')\n"
    "d = spc_drift_prediction(heats)\n"
    "d is not None and spark.createDataFrame([{'predictionId':d.prediction_id,'heatId':d.heat_id,'kind':d.kind.value,'json':json.dumps(d.model_dump(by_alias=True,mode='json'))}]).write.mode('overwrite').option('overwriteSchema','true').saveAsTable('p3_spc_drift')"
)

PILLARS = {
    "P1": [INSTALL, _wrap("P1", _P1_CODE, "f'P1_PREDICTIONS_EMITTED={n}'")],
    "P2": [INSTALL, _wrap("P2", _P2_CODE, "f'P2_ENERGY_SAVINGS_PCT={energy_savings_pct(b,o)} P2_CO2_SAVINGS_PCT={co2_savings_pct(b,o)}'")],
    "P3": [INSTALL, _wrap("P3", _P3_CODE, "f'P3_BASELINE_YIELD={baseline_yield(a)} P3_RECOMMENDED_YIELD={recommended_yield(a)} P3_SPC_DRIFT={(d.heat_id if d else None)}'")],
}


def _read_val(name: str) -> str:
    h = {"Authorization": f"Bearer {os.environ['ONELAKE_TOKEN']}"}
    url = f"{ONELAKE}/{WS}/{LAKEHOUSE}/Files/val_{name}.txt"
    r = requests.get(url, headers=h)
    return r.text if r.status_code == 200 else f"(no log: {r.status_code})"


def main() -> int:
    skip_deploy = "--skip-deploy" in sys.argv
    if not skip_deploy:
        print("Building wheels ...", flush=True)
        build_wheels()
        print("Clearing + uploading wheels to OneLake ...", flush=True)
        clear_remote_wheels()
        upload_wheels()
    else:
        print("Skipping wheel build/upload (using wheels already in OneLake).", flush=True)

    results = {}
    only = [a for a in sys.argv[1:] if a in PILLARS]
    run_names = only if only else list(PILLARS.keys())
    for name in run_names:
        cells = PILLARS[name]
        print(f"=== {name}: set body + run ===", flush=True)
        set_body(cells)
        status = run()
        time.sleep(3)
        val = _read_val(name)
        results[name] = {"status": status, "result": val.strip()[:400]}
        print(f"=== {name}: {status} :: {val.strip()[:300]} ===", flush=True)

    print("Lakehouse tables:", lakehouse_tables(), flush=True)
    print("RESULTS", json.dumps(results, indent=2))
    return 0 if all(v["status"] == "Completed" for v in results.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
