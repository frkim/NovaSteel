"""Train the P1 RUL regressor + P3 quality classifier on Fabric (MLflow), proving the ML-uplift
pipeline end-to-end. Labelled training data is generated inline from the deterministic scenario
generators (ground truth), so the pipeline runs without waiting on real run-to-failure / lab-QA
labels. Requires >=F4. Reuses validate_pillars_live plumbing (wheels install, notebook run)."""

from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import time

import requests

REPO = pathlib.Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("vpl", REPO / "platform" / "scripts" / "validate_pillars_live.py")
vpl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vpl)

TRAIN_CODE = (
    "import mlflow\n"
    "from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor\n"
    "from sklearn.model_selection import train_test_split\n"
    "from sklearn.metrics import f1_score, mean_absolute_error\n"
    "from workloads.p3_quality.generate_quality_scenario import generate_quality_scenario\n"
    "from workloads.p1_predictive_maintenance.generate_degrading_furnace import generate_degrading_furnace, readings_up_to\n"
    "from workloads.p1_predictive_maintenance.physics_features import extract_features\n"
    # ---- P3 quality classifier ----
    "heats = []\n"
    "for seed in range(1, 9):\n"
    "    heats += generate_quality_scenario(seed=seed)\n"
    "X3 = [[h.tapping_temp_c, h.sulfur_pct, h.inclusion_index] for h in heats]\n"
    "y3 = [int(h.actual_high_grade) for h in heats]\n"
    "x3tr, x3te, y3tr, y3te = train_test_split(X3, y3, test_size=0.25, random_state=7, stratify=y3)\n"
    "mlflow.set_experiment('novasteel-p3-quality')\n"
    "with mlflow.start_run() as r3:\n"
    "    m3 = GradientBoostingClassifier(random_state=7).fit(x3tr, y3tr)\n"
    "    f1 = f1_score(y3te, m3.predict(x3te))\n"
    "    mlflow.log_metric('f1', float(f1))\n"
    "    mlflow.sklearn.log_model(m3, artifact_path='model', registered_model_name='novasteel-p3-quality')\n"
    "    p3_run = r3.info.run_id\n"
    # ---- P1 RUL regressor ----
    "rows = []\n"
    "for seed in range(1, 12):\n"
    "    for fd in (40, 50, 60, 70):\n"
    "        series = generate_degrading_furnace(failure_day=fd, horizon_days=fd, seed=seed)\n"
    "        for day in range(15, fd):\n"
    "            f = extract_features(readings_up_to(series, day))\n"
    "            rows.append(((f.current_heat_flux or 0.0), f.heat_flux_slope_per_day, f.heat_flux_r_squared, f.normalized_health_index, float(fd - day)))\n"
    "X1 = [[a, b, c, d] for (a, b, c, d, _) in rows]\n"
    "y1 = [t for (_, _, _, _, t) in rows]\n"
    "x1tr, x1te, y1tr, y1te = train_test_split(X1, y1, test_size=0.25, random_state=7)\n"
    "mlflow.set_experiment('novasteel-p1-rul')\n"
    "with mlflow.start_run() as r1:\n"
    "    m1 = GradientBoostingRegressor(random_state=7).fit(x1tr, y1tr)\n"
    "    mae = mean_absolute_error(y1te, m1.predict(x1te))\n"
    "    mlflow.log_metric('mae_days', float(mae))\n"
    "    mlflow.sklearn.log_model(m1, artifact_path='model', registered_model_name='novasteel-p1-rul')\n"
    "    p1_run = r1.info.run_id\n"
)


def main() -> int:
    print("Rebuild + upload wheels ...", flush=True)
    vpl.build_wheels()
    vpl.clear_remote_wheels()
    vpl.upload_wheels()

    cells = [vpl.INSTALL, vpl._wrap("ML", TRAIN_CODE,
             "f'P3_F1={f1:.3f} P3_RUN={p3_run} P1_MAE_DAYS={mae:.2f} P1_RUN={p1_run} P1_SAMPLES={len(rows)}'")]
    print("=== training on Fabric ===", flush=True)
    vpl.set_body(cells)
    status = vpl.run()
    time.sleep(3)
    print(f"status={status}", flush=True)
    print(vpl._read_val("ML").strip()[:600])
    return 0 if status == "Completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
