from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

import mlflow
from src.features.build_features import (build_preprocess_pipeline,
                                         split_columns)


@dataclass
class TrainingConfig:
    target: str
    test_size: float = 0.2
    random_state: int = 42
    model_params: Dict[str, object] | None = None


def _init_model(params: Dict[str, object] | None) -> RandomForestRegressor:
    defaults = {
        "n_estimators": 200,
        "max_depth": None,
        "n_jobs": -1,
        "random_state": 42,
    }
    merged = {**defaults, **(params or {})}
    return RandomForestRegressor(**merged)


def train_regressor(
    data: pd.DataFrame, config: TrainingConfig
) -> Tuple[Pipeline, Dict[str, float]]:
    """
    Train regression model on provided dataframe.

    Returns fitted sklearn Pipeline and metrics dict.
    """
    if config.target not in data.columns:
        raise ValueError(f"Target column '{config.target}' missing in data")

    data_clean = data.copy()
    # Coerce target to numeric, then drop any rows containing NaN across all columns
    data_clean[config.target] = pd.to_numeric(
        data_clean[config.target], errors="coerce"
    )
    data_clean = data_clean.dropna(axis=0)
    if data_clean.empty:
        raise ValueError("Dataset is empty after dropping rows with NaN")

    X = data_clean.drop(columns=[config.target])
    y = data_clean[config.target].to_numpy(dtype=float, copy=True)

    numeric_cols, categorical_cols = split_columns(X)
    preprocess = build_preprocess_pipeline(numeric_cols, categorical_cols)

    model = _init_model(config.model_params)
    pipeline = Pipeline(steps=[("preprocess", preprocess), ("model", model)])

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=config.test_size, random_state=config.random_state
    )
    pipeline.fit(X_train, y_train)

    predictions = pipeline.predict(X_val)
    mse = mean_squared_error(y_val, predictions)
    metrics = {
        "mae": mean_absolute_error(y_val, predictions),
        "rmse": float(np.sqrt(mse)),
        "r2": r2_score(y_val, predictions),
    }
    return pipeline, metrics


def save_model(model: Pipeline, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)


def log_metrics_to_mlflow(metrics: Dict[str, float]) -> None:
    for key, value in metrics.items():
        mlflow.log_metric(key, value)  # type: ignore[attr-defined]
