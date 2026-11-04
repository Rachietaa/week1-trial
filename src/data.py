"""Loading the sampled tables and the fixed train/validation split."""

from __future__ import annotations

from typing import Any

import pandas as pd


# PROVIDED
def load_table(name: str, config: dict[str, Any]) -> pd.DataFrame:
    """Read one sampled table from data/sample/ with pandas' default type inference.

    Args:
        name: A table name from ``config["tables"]``, for example ``"bureau"``.
        config: The loaded config (see ``src.utils.load_config``).

    Returns:
        The table as a DataFrame.
    """
    if name not in config["tables"]:
        raise KeyError(f"Unknown table '{name}'. Known tables: {list(config['tables'])}")
    path = config["paths"]["sample_dir"] / config["tables"][name]
    if not path.exists():
        raise FileNotFoundError(f"{path} not found. Run `python run.py sample` first.")
    return pd.read_csv(path)


# PROVIDED
def load_application(config: dict[str, Any]) -> pd.DataFrame:
    """Return the sampled application_train table (one row per applicant)."""
    return load_table("application_train", config)


# TODO(student)  [reference solution]
def load_split(config: dict[str, Any]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split the sampled application table into train and validation rows.

    Reference solution: validates the split file, then selects rows by id.
    """
    id_col = config["id_col"]
    app = load_application(config)
    split = pd.read_csv(config["paths"]["split_file"], dtype={id_col: app[id_col].dtype})

    if split[id_col].duplicated().any():
        raise ValueError("split file lists some applicant ids more than once")
    bad_values = set(split["split"]) - {"train", "valid"}
    if bad_values:
        raise ValueError(f"split file has unknown split values: {sorted(bad_values)}")
    if set(split[id_col]) != set(app[id_col]):
        raise ValueError("split file ids do not match the applicants in the sample")

    train_ids = split.loc[split["split"] == "train", id_col]
    valid_ids = split.loc[split["split"] == "valid", id_col]
    train_df = app[app[id_col].isin(train_ids)].reset_index(drop=True)
    valid_df = app[app[id_col].isin(valid_ids)].reset_index(drop=True)
    return train_df, valid_df
