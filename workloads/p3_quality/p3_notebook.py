# Fabric notebook wrapper for P3 quality prediction & SPC.
#
# This file is intentionally Spark-light for local py_compile. In Fabric, bind ``spark`` to
# the lakehouse session, read Gold quality features per heat, predict grade outcomes, raise
# SPC-drift signals, and write contract-shaped Prediction + Recommendation rows for a
# metallurgist to review. Decision-support only — no automatic process change (Constitution I),
# and synthetic provenance is preserved (Constitution IX).

from __future__ import annotations

from workloads.p3_quality.generate_quality_scenario import Heat
from workloads.p3_quality.quality_model import score_batch, spc_drift_prediction

GOLD_QUALITY_TABLE = "gold_quality_features"
PREDICTION_TABLE = "p3_quality_predictions"
RECOMMENDATION_TABLE = "p3_quality_recommendations"
SPC_TABLE = "p3_spc_drift"


def score_gold_quality(spark_session) -> dict:  # pragma: no cover - Fabric wrapper
    """Score Gold quality features and write predictions, recommendations and SPC drift."""
    rows = spark_session.table(GOLD_QUALITY_TABLE).orderBy("sequence").collect()
    heats = [Heat(**r.asDict(recursive=True)) for r in rows]

    assessments = score_batch(heats)
    predictions = [a.prediction.model_dump(by_alias=True, mode="json") for a in assessments]
    recommendations = [
        a.recommendation.model_dump(by_alias=True, mode="json")
        for a in assessments
        if a.recommendation is not None
    ]

    if predictions:
        spark_session.createDataFrame(predictions).write.mode("append").saveAsTable(PREDICTION_TABLE)
    if recommendations:
        spark_session.createDataFrame(recommendations).write.mode("append").saveAsTable(RECOMMENDATION_TABLE)

    drift = spc_drift_prediction(heats, metric="tapping_temp_c")
    if drift is not None:
        spark_session.createDataFrame(
            [drift.model_dump(by_alias=True, mode="json")]
        ).write.mode("append").saveAsTable(SPC_TABLE)

    return {
        "predictions": len(predictions),
        "recommendations": len(recommendations),
        "spcDrift": 0 if drift is None else 1,
    }


# Fabric usage:
# counts = score_gold_quality(spark)
# display(counts)
