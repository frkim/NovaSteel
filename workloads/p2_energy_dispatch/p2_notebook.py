# Fabric notebook wrapper for P2 energy-dispatch scheduling.
#
# This file is intentionally Spark-light for local py_compile. In Fabric, bind
# ``spark`` to the lakehouse session, read the Gold energy jobs + market-signal tables,
# run the tested heuristic dispatch, and write a contract-shaped EnergyPlan (Proposed)
# for an energy manager to approve or adjust. Decision-support only — no grid/furnace
# actuation, and synthetic provenance is preserved (Constitution I/IX).

from __future__ import annotations

import json

from workloads.p2_energy_dispatch.dispatch_model import build_energy_plan
from workloads.p2_energy_dispatch.from_gold import job_from_row, market_signal_from_row

GOLD_ENERGY_JOBS_TABLE = "gold_energy_jobs"
GOLD_MARKET_TABLE = "gold_market_signals"
ENERGY_PLAN_TABLE = "p2_energy_plans"


def _flatten_plan(plan) -> dict:
    """Flatten an EnergyPlan to a Spark/Power BI-friendly row (+ full contract JSON payload).

    A flat, non-null schema avoids Spark's nested/all-null inference limits; the complete
    contract object is preserved verbatim in ``payload_json`` for lineage and drill-through.
    """
    d = plan.model_dump(by_alias=True, mode="json")
    bc = d["baselineComparison"]
    return {
        "energy_plan_id": d["energyPlanId"],
        "site": d["site"],
        "status": d["status"],
        "solver": d["solver"],
        "origin": d["origin"],
        "expected_energy_per_ton": float(d["expectedEnergyPerTon"]),
        "baseline_energy_per_ton": float(bc["baselineEnergyPerTon"]),
        "expected_co2_per_ton": float(d["expectedCo2PerTon"]),
        "baseline_co2_per_ton": float(bc["baselineCo2PerTon"]),
        "expected_cost_eur": float(d["expectedCostEur"]),
        "baseline_cost_eur": float(bc["baselineCostEur"]),
        "scheduled_job_count": len(d["scheduledJobs"]),
        "deadline_breaches": json.dumps(d["deadlineBreaches"]),
        "payload_json": json.dumps(d),
    }


def dispatch_gold_energy(spark_session, base_time) -> int:  # pragma: no cover - Fabric wrapper
    """Build EnergyPlan rows per site from Gold energy jobs + medallion market signals."""
    market_rows = (
        spark_session.table(GOLD_MARKET_TABLE)
        .orderBy("timestamp")
        .collect()
    )
    market = [market_signal_from_row(r.asDict(recursive=True)) for r in market_rows]

    job_rows = spark_session.table(GOLD_ENERGY_JOBS_TABLE).collect()
    jobs_by_site: dict[str, list] = {}
    for r in job_rows:
        job = job_from_row(r.asDict(recursive=True))
        jobs_by_site.setdefault(job.site, []).append(job)

    plans = []
    for site, jobs in jobs_by_site.items():
        plan = build_energy_plan(jobs, market, base_time=base_time, site=site)
        plans.append(_flatten_plan(plan))

    if plans:
        (spark_session.createDataFrame(plans).write.mode("overwrite")
         .option("overwriteSchema", "true").saveAsTable(ENERGY_PLAN_TABLE))
    return len(plans)


# Fabric usage:
# from datetime import datetime, timezone
# emitted = dispatch_gold_energy(spark, datetime.now(timezone.utc))
# display({"p2EnergyPlansEmitted": emitted})
