# Fabric notebook wrapper for P2 energy-dispatch scheduling.
#
# This file is intentionally Spark-light for local py_compile. In Fabric, bind
# ``spark`` to the lakehouse session, read the Gold energy jobs + market-signal tables,
# run the tested heuristic dispatch, and write a contract-shaped EnergyPlan (Proposed)
# for an energy manager to approve or adjust. Decision-support only — no grid/furnace
# actuation, and synthetic provenance is preserved (Constitution I/IX).

from __future__ import annotations

from novasteel_core.models import MarketSignal

from workloads.p2_energy_dispatch.dispatch_model import Job, build_energy_plan

GOLD_ENERGY_JOBS_TABLE = "gold_energy_jobs"
GOLD_MARKET_TABLE = "gold_market_signals"
ENERGY_PLAN_TABLE = "p2_energy_plans"


def dispatch_gold_energy(spark_session, base_time) -> int:  # pragma: no cover - Fabric wrapper
    """Build EnergyPlan rows per site from Gold energy jobs + market signals."""
    market_rows = (
        spark_session.table(GOLD_MARKET_TABLE)
        .orderBy("timestamp")
        .collect()
    )
    market = [MarketSignal.model_validate(r.asDict(recursive=True)) for r in market_rows]

    job_rows = spark_session.table(GOLD_ENERGY_JOBS_TABLE).collect()
    jobs_by_site: dict[str, list[Job]] = {}
    for r in job_rows:
        d = r.asDict(recursive=True)
        jobs_by_site.setdefault(d["site"], []).append(Job(**d))

    plans = []
    for site, jobs in jobs_by_site.items():
        plan = build_energy_plan(jobs, market, base_time=base_time, site=site)
        plans.append(plan.model_dump(by_alias=True, mode="json"))

    if plans:
        spark_session.createDataFrame(plans).write.mode("append").saveAsTable(ENERGY_PLAN_TABLE)
    return len(plans)


# Fabric usage:
# from datetime import datetime, timezone
# emitted = dispatch_gold_energy(spark, datetime.now(timezone.utc))
# display({"p2EnergyPlansEmitted": emitted})
