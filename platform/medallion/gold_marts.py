# Fabric notebook — T030 Gold marts (features + KPIs)
# ------------------------------------------------------------------------------
# Silver -> Gold: feature tables + KPI marts for Power BI (Direct Lake). Synthetic
# data (origin='Synthetic') is bucketed into a separate `data_class` and is EXCLUDED
# from every real KPI, and clearly labelled — it can never masquerade as real in a
# dashboard or a KPI baseline (Constitution IX). Mirrors the tested logic in
# platform/medallion/transforms.py::to_gold_kpi.
# ------------------------------------------------------------------------------
from pyspark.sql import functions as F

silver = spark.read.table("silver_telemetry")

# Explicit provenance class on every Gold row.
classed = silver.withColumn(
    "data_class",
    F.when(F.col("Origin") == "Synthetic", F.lit("synthetic")).otherwise(F.lit("real")),
)

kpi = (
    classed.groupBy("Site", "Metric", "data_class")
    .agg(
        F.count("*").alias("count"),
        F.avg("Value").alias("avg_value"),
        F.min("Value").alias("min_value"),
        F.max("Value").alias("max_value"),
        (F.sum(F.when(F.col("Quality") == "Good", 1).otherwise(0)) / F.count("*")).alias("good_ratio"),
        F.sum(F.col("is_stale").cast("int")).alias("stale_count"),
        F.collect_set("SourceId").alias("source_ids"),
    )
)

# Real KPI mart — the ONLY table dashboards/KPI baselines read for real metrics.
kpi_real = kpi.where(F.col("data_class") == "real")
kpi_real.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(
    "gold_kpi_real"
)

# Synthetic mart kept separate for demo/validation only, explicitly labelled.
kpi.where(F.col("data_class") == "synthetic").write.format("delta").mode("overwrite").option(
    "overwriteSchema", "true"
).saveAsTable("gold_kpi_synthetic")

# Physics-informed furnace feature table for the P1 RUL model (real only).
furnace_features = (
    classed.where((F.col("AssetType") == "BlastFurnace") & (F.col("data_class") == "real"))
    .groupBy("AssetId", "Site", F.window("Timestamp", "1 hour").alias("w"))
    .pivot("Metric", ["ThermocoupleTemp", "HeatFlux", "Vibration"])
    .agg(F.avg("Value"))
)
furnace_features.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(
    "gold_furnace_features"
)

# Gate: no synthetic source may appear in the real KPI mart (Constitution IX).
leak = kpi_real.where(F.array_contains(F.expr("transform(source_ids, s -> startswith(s, 'sim:'))"), True))
assert leak.count() == 0, "synthetic source leaked into real KPI mart"
print("Gold marts written: gold_kpi_real, gold_kpi_synthetic, gold_furnace_features")
