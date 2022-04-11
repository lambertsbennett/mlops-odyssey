from random import random, randint
from sklearn.ensemble import RandomForestRegressor
import os

import mlflow
import mlflow.sklearn

mlflow.set_tracking_uri('http://localhost:5000')

mlflow.set_experiment("test2")

with mlflow.start_run(run_name="YOUR_RUN_NAME") as run:
    params = {"n_estimators": 5, "random_state": 42}
    sk_learn_rfr = RandomForestRegressor(**params)

    # Log parameters and metrics using the MLflow APIs
    mlflow.log_params(params)
    mlflow.log_param("param_1", randint(0, 100))
    mlflow.log_metrics({"metric_1": random(), "metric_2": random() + 1})

    os.environ["AWS_ACCESS_KEY_ID"] = "admin"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "dYzac5sD8R"
    os.environ['MLFLOW_S3_ENDPOINT_URL'] = 'http://localhost:9000'

    # Log the sklearn model and register as version 1
    mlflow.sklearn.log_model(
        sk_model=sk_learn_rfr,
        artifact_path="artifacts",
        registered_model_name="sk-learn-random-forest-reg-model"
    )