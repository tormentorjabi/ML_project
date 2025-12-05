from __future__ import annotations

from typing import Iterable, List, Tuple

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def split_columns(frame: pd.DataFrame) -> Tuple[List[str], List[str]]:
    """
    Split dataframe columns into numeric and categorical lists.
    This separation is reused across training/prediction pipelines.
    """
    numeric_cols = list(frame.select_dtypes(include=["number"]).columns)
    categorical_cols = [col for col in frame.columns if col not in numeric_cols]
    return numeric_cols, categorical_cols


def build_preprocess_pipeline(
    numeric_cols: Iterable[str], categorical_cols: Iterable[str]
) -> ColumnTransformer:
    """
    Build preprocessing pipeline:
    - numeric: median imputation + standardization
    - categorical: most frequent imputation + one-hot
    """
    numeric_processor = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_processor = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_processor, list(numeric_cols)),
            ("categorical", categorical_processor, list(categorical_cols)),
        ]
    )
