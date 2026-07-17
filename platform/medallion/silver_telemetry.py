# Fabric notebook — T029 Silver telemetry (conform + freshness)
# ------------------------------------------------------------------------------
# Bronze -> Silver: dedup, conform, compute freshness/quality flags, partition by
# site+date. Provenance (origin/sourceId/site/quality) is carried through unchanged
# (Constitution IX). Stale telemetry is downgraded to Suspect so it is never presented
# as current (FR-022, Constitution VI). Mirrors the tested logic in
# platform/medallion/transforms.py::to_silver.
# ------------------------------------------------------------------------------
from pyspark.sql import functions as F, Window

STALE_AFTER_SECONDS = 900  # 15 min

bronze = spark.read.table("onelake_novasteel.bronze_telemetry")

# Dedup: keep the latest ingested row per (asset, metric, timestamp).
w = Window.partitionBy("AssetId", "Metric", "Timestamp").orderBy(F.col("_ingested_at").desc())
deduped = (
    bronze.withColumn("_rn", F.row_number().over(w)).where(F.col("_rn") == 1).drop("_rn")
)

silver = (
    deduped
    .withColumn("freshness_seconds", F.col("_ingested_at").cast("long") - F.col("Timestamp").cast("long"))
    .withColumn("is_stale", F.col("freshness_seconds") > F.lit(STALE_AFTER_SECONDS))
    .withColumn(
        "Quality",
        F.when(F.col("is_stale") & (F.col("Quality") == "Good"), F.lit("Suspect")).otherwise(F.col("Quality")),
    )
    .withColumn("partition", F.concat_ws("/", F.col("Site"), F.to_date("Timestamp")))
    .withColumn("_layer", F.lit("silver"))
)

# Provenance columns are never dropped or altered here.
for col in ("Origin", "SourceId", "Site", "Quality"):
    assert col in silver.columns, f"provenance column {col} lost in Silver"

(
    silver.write.format("delta")
    .mode("overwrite")
    .partitionBy("Site")
    .option("overwriteSchema", "true")
    .saveAsTable("onelake_novasteel.silver_telemetry")
)
print(f"Silver rows: {silver.count()}")
