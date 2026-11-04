"""Logistic regression baseline on the application table.

Run it with ``python run.py baseline`` or ``python -m src.baseline``. It trains on the train
split only, scores the validation split, and writes reports/metrics.json.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.data import load_split
from src.metrics import evaluate
from src.utils import DEFAULT_CONFIG, load_config, set_seed

# PROVIDED
DAYS_EMPLOYED_SENTINEL = 365243
METRICS_KEYS = (
    "model", "roc_auc", "pr_auc", "ks", "n_train", "n_valid", "valid_default_rate", "seed",
)
MODEL_NAME = "logistic_regression"


# TODO(student)  [reference solution]
def clean_application(df: pd.DataFrame) -> pd.DataFrame:
    """Replace the DAYS_EMPLOYED sentinel with NaN and add the DAYS_EMPLOYED_ANOM flag."""
    out = df.copy()
    is_sentinel = out["DAYS_EMPLOYED"] == DAYS_EMPLOYED_SENTINEL
    out["DAYS_EMPLOYED_ANOM"] = is_sentinel.astype(int)
    out["DAYS_EMPLOYED"] = out["DAYS_EMPLOYED"].mask(is_sentinel, np.nan)
    return out


# TODO(student)  [reference solution]
def get_feature_columns(df: pd.DataFrame, config: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Split the model's input columns into numeric and categorical lists.

    The id and target columns are never features. Numbers and booleans count as numeric;
    everything else (text, category) counts as categorical.
    """
    excluded = {config["id_col"], config["target_col"]}
    candidates = [col for col in df.columns if col not in excluded]
    numeric = [
        col for col in candidates
        if pd.api.types.is_numeric_dtype(df[col]) or pd.api.types.is_bool_dtype(df[col])
    ]
    categorical = [col for col in candidates if col not in numeric]
    return numeric, categorical


# TODO(student)  [reference solution]
def build_preprocessor(numeric_cols: list[str], categorical_cols: list[str]) -> ColumnTransformer:
    """Median-impute and scale numbers; mode-impute and one-hot encode categories."""
    numeric = Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
    ])
    categorical = Pipeline([
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])
    return ColumnTransformer([
        ("num", numeric, numeric_cols),
        ("cat", categorical, categorical_cols),
    ])


# TODO(student)  [reference solution]
def build_model(config: dict[str, Any], preprocessor: ColumnTransformer) -> Pipeline:
    """Preprocessing followed by logistic regression, configured from config.yaml."""
    settings = config["baseline"]
    classifier = LogisticRegression(
        max_iter=settings["max_iter"],
        class_weight=settings["class_weight"],
        random_state=config["seed"],
    )
    return Pipeline([("preprocess", preprocessor), ("model", classifier)])


# TODO(student)  [reference solution]
def write_metrics(metrics: dict[str, float], extra: dict[str, Any], path: str | Path) -> None:
    """Merge metrics and extra, check the schema, and write indented JSON."""
    record = {**extra, **metrics}
    missing = [key for key in METRICS_KEYS if key not in record]
    if missing:
        raise ValueError(f"metrics are missing required keys: {missing}")
    record = {key: (value.item() if isinstance(value, np.generic) else value)
              for key, value in record.items()}
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2) + "\n")


# TODO(student)  [reference solution]
def run_baseline(config: dict[str, Any]) -> dict[str, Any]:
    """Train on the train split, evaluate on the validation split, and write metrics.json."""
    set_seed(config["seed"])
    target = config["target_col"]

    train_df, valid_df = load_split(config)
    train_df = clean_application(train_df)
    valid_df = clean_application(valid_df)

    numeric_cols, categorical_cols = get_feature_columns(train_df, config)
    features = numeric_cols + categorical_cols
    model = build_model(config, build_preprocessor(numeric_cols, categorical_cols))

    model.fit(train_df[features], train_df[target])  # fit on train only
    valid_scores = model.predict_proba(valid_df[features])[:, 1]

    metrics = evaluate(valid_df[target].to_numpy(), valid_scores)
    extra = {
        "model": MODEL_NAME,
        "n_train": len(train_df),
        "n_valid": len(valid_df),
        "valid_default_rate": float(valid_df[target].mean()),
        "seed": config["seed"],
    }
    write_metrics(metrics, extra, config["paths"]["metrics_file"])
    return {**extra, **metrics}


# PROVIDED
def main() -> None:
    """Command-line entry point: ``python -m src.baseline [--config PATH]``."""
    parser = argparse.ArgumentParser(description="Train and evaluate the baseline model.")
    parser.add_argument("--config", default=DEFAULT_CONFIG, help="path to config.yaml")
    args = parser.parse_args()

    config = load_config(args.config)
    results = run_baseline(config)
    print(json.dumps(results, indent=2))
    print(f"Wrote {config['paths']['metrics_file']}")


if __name__ == "__main__":
    main()
