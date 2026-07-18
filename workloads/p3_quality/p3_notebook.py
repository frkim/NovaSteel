# Fabric notebook wrapper for P3 quality prediction & SPC.
#
# This file is intentionally Spark-light for local py_compile. In Fabric, bind ``spark`` to
# the lakehouse session, read Gold quality features per heat, predict grade outcomes, raise
# SPC-drift signals, and write contract-shaped Prediction + Recommendation rows for a
# metallurgist to review. Decision-support only — no automatic process change (Constitution I),
# and synthetic provenance is preserved (Constitution IX).

from __future__ import annotations

import json

from workloads.p3_quality.from_gold import heats_from_rows
from workloads.p3_quality.quality_model import score_batch, spc_drift_prediction

GOLD_QUALITY_TABLE = "gold_quality_features"
PREDICTION_TABLE = "p3_quality_predictions"
RECOMMENDATION_TABLE = "p3_quality_recommendations"
SPC_TABLE = "p3_spc_drift"


def _flatten_prediction(pred) -> dict:
    d = pred.model_dump(by_alias=True, mode="json")
    return {
        "prediction_id": d["predictionId"],
        "heat_id": d.get("heatId") or "",
        "site": d["site"],
        "kind": d["kind"],
        "confidence": float(d["confidence"]),
        "model_version": d["modelVersion"],
        "status": d["status"],
        "origin": d["origin"],
        "payload_json": json.dumps(d),
    }


def _flatten_recommendation(rec) -> dict:
    d = rec.model_dump(by_alias=True, mode="json")
    return {
        "recommendation_id": d["recommendationId"],
        "heat_id": d.get("relatedHeatId") or "",
        "site": d["site"],
        "summary": d["summary"],
        "status": d["status"],
        "content_safety_passed": bool(d["contentSafetyPassed"]),
        "payload_json": json.dumps(d),
    }


def _write(spark_session, rows, table):  # pragma: no cover - Fabric wrapper
    if rows:
        (spark_session.createDataFrame(rows).write.mode("overwrite")
         .option("overwriteSchema", "true").saveAsTable(table))


def score_gold_quality(spark_session) -> dict:  # pragma: no cover - Fabric wrapper
    """Score medallion-derived Gold quality features; write predictions, recs and SPC drift.

    Writes flat, non-null rows (+ full contract JSON in ``payload_json``) so Spark schema
    inference is robust and the tables are Power BI Direct Lake friendly.
    """
    rows = spark_session.table(GOLD_QUALITY_TABLE).collect()
    heats = heats_from_rows([r.asDict(recursive=True) for r in rows])

    assessments = score_batch(heats)
    predictions = [_flatten_prediction(a.prediction) for a in assessments]
    recommendations = [_flatten_recommendation(a.recommendation) for a in assessments if a.recommendation]

    _write(spark_session, predictions, PREDICTION_TABLE)
    _write(spark_session, recommendations, RECOMMENDATION_TABLE)

    drift = spc_drift_prediction(heats, metric="tapping_temp_c")
    _write(spark_session, [_flatten_prediction(drift)] if drift is not None else [], SPC_TABLE)

    return {
        "predictions": len(predictions),
        "recommendations": len(recommendations),
        "spcDrift": 0 if drift is None else 1,
    }


# Fabric usage:
# counts = score_gold_quality(spark)
# display(counts)
