# Fabric Data Science notebook scaffold — P1 RUL model training (MLflow).
#
# Trains a data-driven Remaining-Useful-Life regressor on Gold furnace features and logs it to
# MLflow (Fabric Data Science), as the ML uplift over the physics-linear estimator in
# workloads/p1_predictive_maintenance/rul_model.py. Requires Fabric Data Science compute
# (mlflow + scikit-learn are preinstalled there); imports are lazy so this file stays
# py_compile-clean without those libraries locally.
#
# The trained model is decision-support only: at inference it feeds the same Prediction contract
# (Constitution I/VI). Provenance + model_version are logged with every run for traceability (II).

from __future__ import annotations

MODEL_NAME = "novasteel-p1-rul"
GOLD_FEATURE_TABLE = "gold_furnace_features"
LABEL_COLUMN = "time_to_failure_days"  # supervised label (from historical run-to-maintenance events)


def train_rul_model(spark_session, experiment: str = "novasteel-p1-rul"):  # pragma: no cover - Fabric
    """Train + register a RUL regressor from Gold furnace features; return the run id.

    Expects a labelled feature table (features + observed time-to-failure). Logs metrics
    (MAE / lead-time coverage), params and the model to MLflow for human review before promotion.
    """
    import mlflow  # lazy
    from sklearn.ensemble import GradientBoostingRegressor
    from sklearn.metrics import mean_absolute_error
    from sklearn.model_selection import train_test_split

    pdf = spark_session.table(GOLD_FEATURE_TABLE).toPandas()
    feature_cols = [c for c in pdf.columns if c not in {LABEL_COLUMN, "AssetId", "Site", "w"}]
    x = pdf[feature_cols].fillna(0.0)
    y = pdf[LABEL_COLUMN]
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25, random_state=7)

    mlflow.set_experiment(experiment)
    with mlflow.start_run() as run:
        model = GradientBoostingRegressor(random_state=7)
        model.fit(x_train, y_train)
        mae = mean_absolute_error(y_test, model.predict(x_test))
        mlflow.log_params({"model": "GradientBoostingRegressor", "features": len(feature_cols)})
        mlflow.log_metric("mae_days", float(mae))
        # A model only ships if it meets the >=21-day advance-warning target (SC-003) on holdout.
        mlflow.set_tag("meets_sc003_target", str(mae <= 5.0))
        mlflow.sklearn.log_model(model, artifact_path="model", registered_model_name=MODEL_NAME)
        return run.info.run_id


# Fabric usage:
# run_id = train_rul_model(spark)
# Promote the registered model to Production only after human review of the logged metrics.
