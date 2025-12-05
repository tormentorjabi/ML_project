from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

import joblib
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline


def load_model(path: Path) -> Pipeline:
    if not path.exists():
        raise FileNotFoundError(f"Model file not found: {path}")
    return joblib.load(path)


def predict(
    model: Pipeline, data: pd.DataFrame, columns: Iterable[str] | None = None
) -> pd.Series | np.ndarray[Any, Any]:
    features = data if columns is None else data[list(columns)]
    return model.predict(features)
