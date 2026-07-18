# Fabric Data Science notebook scaffold — P3 quality classifier training (MLflow).
#
# Trains a data-driven high-grade classifier on Gold quality features + lab QA outcomes and logs
# it to MLflow (Fabric Data Science), as the ML uplift over the rules-based estimator in
# workloads/p3_quality/quality_model.py. Requires Fabric Data Science compute; imports are lazy
# so this file stays py_compile-clean locally.
#
# Decision-support only: at inference the model feeds the same Prediction/Recommendation
# contracts and outputs remain Raised/Proposed for metallurgist review (Constitution I/VI).

from __future__ import annotations

MODEL_NAME = "novasteel-p3-quality"
GOLD_QUALITY_TABLE = "gold_quality_features"
LABEL_COLUMN = "actual_high_grade"  # back-filled from lab QA once results are in


def train_quality_model(spark_session, experiment: str = "/NovaSteel/P3-Quality"):  # pragma: no cover - Fabric
    """Train + register a high-grade classifier from Gold quality features; return the run id."""
    import mlflow  # lazy
    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.metrics import f1_score, precision_score, recall_score
    from sklearn.model_selection import train_test_split

    pdf = spark_session.table(GOLD_QUALITY_TABLE).toPandas()
    feature_cols = ["tapping_temp_c", "sulfur_pct", "inclusion_index"]
    x = pdf[feature_cols].fillna(0.0)
    y = pdf[LABEL_COLUMN].astype(int)
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25, random_state=7, stratify=y)

    mlflow.set_experiment(experiment)
    with mlflow.start_run() as run:
        model = GradientBoostingClassifier(random_state=7)
        model.fit(x_train, y_train)
        pred = model.predict(x_test)
        mlflow.log_params({"model": "GradientBoostingClassifier", "features": feature_cols})
        mlflow.log_metric("precision", float(precision_score(y_test, pred, zero_division=0)))
        mlflow.log_metric("recall", float(recall_score(y_test, pred, zero_division=0)))
        mlflow.log_metric("f1", float(f1_score(y_test, pred, zero_division=0)))
        mlflow.sklearn.log_model(model, artifact_path="model", registered_model_name=MODEL_NAME)
        return run.info.run_id


# Fabric usage:
# run_id = train_quality_model(spark)
# Promote to Production only after human review; keep predicted-vs-actual linkage for evaluation.
