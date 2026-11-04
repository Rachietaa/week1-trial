"""Joining per-applicant feature tables onto the application table.

The application table has exactly one row per applicant, and so must the result. A join that
silently adds rows (because a child table was not aggregated) or drops rows (because of an
inner join) still runs without an error, and the model then trains on the wrong data. The
functions here make that mistake fail loudly instead.
"""

from __future__ import annotations

import pandas as pd

# PROVIDED: a feature whose name ends with this is a count, so "no records" means 0.
COUNT_SUFFIX = "_COUNT"


# TODO(student)
def assert_one_row_per_applicant(
    df: pd.DataFrame, expected_ids: pd.Series, id_col: str = "SK_ID_CURR"
) -> None:
    """Raise a ValueError unless ``df`` has exactly one row for each id in ``expected_ids``.

    Student version: duplicates first, then the row count, then the exact set of ids (a
    duplicated id plus a missing id keeps the count equal, so the count alone is not enough).
    """
    ids = df[id_col]
    n_dup = int(ids.duplicated().sum())
    if n_dup:
        raise ValueError(f"{n_dup:,} applicant ids appear more than once "
                         f"({len(df):,} rows for {ids.nunique():,} applicants)")
    if len(df) != len(expected_ids):
        raise ValueError(f"{len(df):,} rows for {len(expected_ids):,} applicants")
    missing = set(expected_ids) - set(ids)
    extra = set(ids) - set(expected_ids)
    if missing or extra:
        raise ValueError(f"{len(missing):,} applicants missing and {len(extra):,} unexpected")


# TODO(student)
def join_features(
    app: pd.DataFrame, feature_tables: dict[str, pd.DataFrame], id_col: str = "SK_ID_CURR"
) -> pd.DataFrame:
    """Left-join each per-applicant feature table onto the application table.

    Student version: check each table before joining, left-join so nobody is dropped, fill
    counts with 0, then check the result.
    """
    out = app.copy()
    for name, table in feature_tables.items():
        n_dup = int(table[id_col].duplicated().sum())
        if n_dup:
            raise ValueError(f"feature table '{name}' has {n_dup:,} duplicated {id_col} values; "
                             f"aggregate it to one row per applicant before joining")
        clash = [c for c in table.columns if c != id_col and c in out.columns]
        if clash:
            raise ValueError(f"feature table '{name}' repeats existing columns {clash}")

        # how="left" keeps applicants with no history; validate= double-checks the keys.
        out = out.merge(table, on=id_col, how="left", validate="one_to_one")
        # No records means zero of them, so counts become 0. Averages stay missing: an
        # average of nothing is unknown, not 0.
        counts = [c for c in table.columns if c.endswith(COUNT_SUFFIX)]
        out[counts] = out[counts].fillna(0)

    assert_one_row_per_applicant(out, app[id_col], id_col)
    return out
