# Fabric notebook wrapper for P1 predictive furnace-lining maintenance.
#
# Spark-light for local py_compile. In Fabric this runs against the default lakehouse
# (bare table names resolve once a default lakehouse is bound — see
# platform/scripts/bind_medallion_lakehouse.py). It reads Silver telemetry (TelemetryReading
# shaped), builds per-asset windows, scores the tested RUL model and appends contract-shaped
# Prediction rows for human review. Synthetic provenance is preserved and predictions are
# decision-support only (no actuation) — Constitution I/IX.

from __future__ import annotations

from novasteel_core.models import TelemetryReading

from workloads.p1_predictive_maintenance.rul_model import score_rul

SILVER_TABLE = "silver_telemetry"
PREDICTION_TABLE = "p1_predictions"

# Silver columns that are optional for scoring; supply safe defaults if a column is absent.
_DEFAULTS = {"assetType": "Furnace", "unit": "", "quality": "Good", "sourceId": "", "origin": "Real"}


def _to_reading(row_dict: dict) -> TelemetryReading:
    payload = {**_DEFAULTS, **{k: v for k, v in row_dict.items() if v is not None}}
    return TelemetryReading.model_validate(payload)


def score_gold_furnace_features(spark_session) -> int:  # pragma: no cover - Fabric wrapper
    """Score furnace windows from Silver telemetry and append Prediction rows."""
    rows = spark_session.table(SILVER_TABLE).collect()
    windows: dict[str, list[TelemetryReading]] = {}
    for row in rows:
        reading = _to_reading(row.asDict(recursive=True))
        key = f"{reading.site}:{reading.asset_id}"
        windows.setdefault(key, []).append(reading)

    predictions = []
    for readings in windows.values():
        assessment = score_rul(readings)
        if assessment is not None:
            predictions.append(assessment.prediction.model_dump(by_alias=True, mode="json"))

    if predictions:
        spark_session.createDataFrame(predictions).write.mode("append").saveAsTable(PREDICTION_TABLE)
    return len(predictions)


# Fabric usage (after %pip install of the novasteel wheels):
# emitted_count = score_gold_furnace_features(spark)
# display({"p1PredictionsEmitted": emitted_count})
