# Fabric notebook wrapper for the frozen KPI baseline (Phase 7).
#
# Spark-light for local py_compile. In Fabric, bind ``spark`` to the default lakehouse, read
# the Gold real-KPI mart (synthetic marts are excluded — Constitution IX), compute a frozen,
# normalized trailing-12-month baseline per site and write it to ``gold_kpi_baseline``. This
# baseline is the stable reference every executive dashboard compares live KPIs against.

from __future__ import annotations

from datetime import date

from kpi.kpi_baseline import ProductionRecord, compute_baseline

GOLD_REAL_KPI_TABLE = "gold_kpi_real"
BASELINE_TABLE = "gold_kpi_baseline"


def compute_frozen_baseline(spark_session, as_of: date, months: int = 12) -> int:  # pragma: no cover
    """Compute and persist the frozen KPI baseline per site from the real KPI mart."""
    rows = spark_session.table(GOLD_REAL_KPI_TABLE).collect()
    records = [ProductionRecord(**r.asDict(recursive=True)) for r in rows]
    sites = sorted({r.site for r in records})

    baselines = []
    for site in sites:
        try:
            baseline = compute_baseline(records, site=site, as_of=as_of, months=months)
        except ValueError:
            continue  # no in-window production for this site; skip rather than fabricate
        baselines.append(baseline.to_dict())

    if baselines:
        spark_session.createDataFrame(baselines).write.mode("overwrite").option(
            "overwriteSchema", "true"
        ).saveAsTable(BASELINE_TABLE)
    return len(baselines)


# Fabric usage (after %pip install of the novasteel wheels):
# from datetime import date
# n = compute_frozen_baseline(spark, date.today())
# display({"kpiBaselinesFrozen": n})
