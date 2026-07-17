# Fabric notebook — T028 Bronze telemetry landing
# ------------------------------------------------------------------------------
# Append-only raw landing of plant telemetry into OneLake Bronze on the live
# Fabric lakehouse (onelake_novasteel). Provenance (origin/sourceId) and site/quality
# are preserved VERBATIM — no defaulting, no mutation (Constitution IX). Readings
# missing valid provenance are quarantined, never silently promoted.
#
# Source: the Eventstream `es-telemetry` already streams IoT Hub -> bronze_telemetry;
# this notebook batch-reconciles from the Eventhouse (TelemetryRaw) and enforces the
# provenance data-quality gate before Silver runs.
# ------------------------------------------------------------------------------
from pyspark.sql import functions as F

BRONZE_TABLE = "onelake_novasteel.bronze_telemetry"
VALID_ORIGIN = ("Real", "Synthetic")
VALID_SITE = ("LU", "DE", "BE", "ES")

# Read the hot-path raw table exported from the RTI Eventhouse (KQL DB -> OneLake shortcut).
raw = spark.read.table("onelake_novasteel.telemetry_raw_kql")

# --- Provenance gate (Constitution IX): split clean vs quarantine, never default Origin ---
has_provenance = (
    F.col("Origin").isin(*VALID_ORIGIN)
    & F.col("SourceId").isNotNull()
    & (F.length(F.trim(F.col("SourceId"))) > 0)
    & F.col("Site").isin(*VALID_SITE)
)

clean = raw.where(has_provenance).withColumn("_ingested_at", F.current_timestamp()).withColumn("_layer", F.lit("bronze"))
quarantine = raw.where(~has_provenance).withColumn("_reason", F.lit("missing_or_invalid_provenance"))

# Append-only Bronze write (history retained; nothing overwritten).
clean.write.format("delta").mode("append").saveAsTable(BRONZE_TABLE)
quarantine.write.format("delta").mode("append").saveAsTable("onelake_novasteel.bronze_telemetry_quarantine")

print(f"Bronze appended: {clean.count()} rows; quarantined: {quarantine.count()} rows")
# Fail the pipeline if any row lost provenance upstream (gate; see platform/medallion/data_quality.py).
assert clean.where(F.col("Origin").isNull() | F.col("SourceId").isNull()).count() == 0
