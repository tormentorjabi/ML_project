from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd
import yaml  # type: ignore[import-untyped]

import mlflow
from src.data.download_from_s3 import download_file
from src.data.upload_to_s3 import upload_file
from src.models.train_model import (TrainingConfig, log_metrics_to_mlflow,
                                    save_model, train_regressor)


@dataclass
class DatasetConfig:
    bucket: str
    key: str
    local_path: str
    target: str


@dataclass
class ExperimentSettings:
    name: str
    tracking_uri: str
    s3_bucket: str
    run_name: Optional[str] = None
    test_size: float = 0.2
    random_state: int = 42


def load_yaml_config(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        result = yaml.safe_load(file)
        if not isinstance(result, dict):
            raise ValueError("YAML config must be a dictionary")
        return result


def _build_run_name(settings: ExperimentSettings, params: Dict[str, object]) -> str:
    if settings.run_name:
        return settings.run_name
    param_fragment = "-".join(f"{key}={value}" for key, value in sorted(params.items()))
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    return f"{settings.name}-{param_fragment}-{timestamp}"


def execute_experiment(config_raw: Dict[str, Any]) -> None:
    data_cfg = DatasetConfig(**config_raw["data"])
    experiment_cfg = ExperimentSettings(**config_raw["experiment"])
    model_params: Dict[str, object] = config_raw["model"].get("params", {})

    download_file(data_cfg.bucket, data_cfg.key, data_cfg.local_path)
    dataset = pd.read_csv(data_cfg.local_path)
    # Drop rows with any missing values before training to avoid NaN issues downstream
    dataset = dataset.dropna(axis=0)

    mlflow.set_tracking_uri(experiment_cfg.tracking_uri)  # type: ignore[attr-defined]
    mlflow.set_experiment(experiment_cfg.name)  # type: ignore[attr-defined]

    run_name = _build_run_name(experiment_cfg, model_params)
    with mlflow.start_run(run_name=run_name):  # type: ignore[attr-defined]
        train_cfg = TrainingConfig(
            target=data_cfg.target,
            test_size=experiment_cfg.test_size,
            random_state=experiment_cfg.random_state,
            model_params=model_params,
        )

        mlflow.log_params(model_params)  # type: ignore[attr-defined]
        mlflow.log_params(  # type: ignore[attr-defined]
            {
                "test_size": train_cfg.test_size,
                "random_state": train_cfg.random_state,
                "target": train_cfg.target,
                "dataset_key": data_cfg.key,
            }
        )

        model, metrics = train_regressor(dataset, train_cfg)
        log_metrics_to_mlflow(metrics)

        local_model_path = Path("models") / experiment_cfg.name / f"{run_name}.joblib"
        save_model(model, local_model_path)

        metrics_path = local_model_path.with_suffix(".metrics.json")
        metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

        # Artifacts are uploaded to S3; skip MLflow artifact upload to avoid server/API issues

        s3_key_prefix = f"{experiment_cfg.name}/{run_name}"
        upload_file(
            experiment_cfg.s3_bucket,
            f"{s3_key_prefix}/model.joblib",
            str(local_model_path),
        )
        upload_file(
            experiment_cfg.s3_bucket, f"{s3_key_prefix}/metrics.json", str(metrics_path)
        )


def run_single_experiment(config_path: Path) -> None:
    config_raw = load_yaml_config(config_path)
    execute_experiment(config_raw)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run single ML experiment and log to MLflow + S3"
    )
    parser.add_argument(
        "--config",
        required=True,
        type=Path,
        help="Path to YAML config with experiment setup",
    )
    args = parser.parse_args()

    run_single_experiment(args.config)


if __name__ == "__main__":
    main()
