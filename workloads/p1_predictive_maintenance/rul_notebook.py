# Fabric notebook wrapper for P1 predictive furnace-lining maintenance.
#
# This file is intentionally Spark-light for local py_compile. In Fabric, bind
# ``spark`` to the lakehouse session, read Gold furnace features from
# ``onelake_novasteel.gold_furnace_features``, score the RUL model, and write
# contract-shaped Prediction rows for human review. Synthetic provenance must be
# preserved and predictions remain decision-support only (no actuation).

from __future__ import annotations

from novasteel_core.models import TelemetryReading

from workloads.p1_predictive_maintenance.rul_model import score_rul

GOLD_FEATURE_TABLE = "onelake_novasteel.gold_furnace_features"
PREDICTION_TABLE = "onelake_novasteel.p1_predictions"


def score_gold_furnace_features(spark_session) -> int:  # pragma: no cover - Fabric wrapper
    """Score Gold furnace feature windows in Fabric and append Prediction rows."""
    rows = spark_session.table(GOLD_FEATURE_TABLE).collect()
    windows: dict[str, list[TelemetryReading]] = {}
    for row in rows:
        reading = TelemetryReading.model_validate(row.asDict(recursive=True))
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


# Fabric usage:
# emitted_count = score_gold_furnace_features(spark)
# display({"p1PredictionsEmitted": emitted_count})
