"""Home Credit's own history with the applicant: earlier applications and their loans.

previous_application has one row per earlier application at Home Credit, approved or not.
POS_CASH_balance has one row per month of each earlier point-of-sale or cash loan. Both carry
SK_ID_CURR, so each can be grouped by applicant directly.

Follow the pattern of ``aggregate_bureau`` in src/features/bureau.py.
"""

from __future__ import annotations

import pandas as pd

from src.features.common import (  # noqa: F401  (helpers for you to use)
    SENTINEL,
    count_where,
    replace_sentinel,
    require_columns,
    share_where,
)

# PROVIDED
PREVIOUS_COLUMNS = [
    "SK_ID_CURR", "SK_ID_PREV", "NAME_CONTRACT_STATUS", "AMT_APPLICATION", "AMT_CREDIT",
    "DAYS_DECISION", "DAYS_TERMINATION",
]
# Columns of previous_application that use SENTINEL for "no date".
PREVIOUS_DAY_COLUMNS = [
    "DAYS_FIRST_DRAWING", "DAYS_FIRST_DUE", "DAYS_LAST_DUE_1ST_VERSION", "DAYS_LAST_DUE",
    "DAYS_TERMINATION",
]
PREVIOUS_FEATURES = [
    "PREV_COUNT", "PREV_APPROVED_RATE", "PREV_REFUSED_RATE", "PREV_AMT_APPLICATION_MEAN",
    "PREV_AMT_CREDIT_MEAN", "PREV_DAYS_DECISION_MAX", "PREV_DAYS_TERMINATION_MEAN",
    "PREV_LAST_STATUS",
]
POS_CASH_COLUMNS = ["SK_ID_CURR", "SK_ID_PREV", "NAME_CONTRACT_STATUS", "SK_DPD"]
POS_CASH_FEATURES = [
    "POS_LOAN_COUNT", "POS_MONTHS_COUNT", "POS_DPD_MAX", "POS_DPD_MEAN", "POS_LATE_SHARE",
    "POS_COMPLETED_SHARE",
]


# TODO(student)
def aggregate_previous(previous: pd.DataFrame, id_col: str = "SK_ID_CURR") -> pd.DataFrame:
    """Summarize each applicant's earlier applications at Home Credit into one row.

    Student version: sentinel to NaN, named aggregation, two status shares, and the status of
    the most recent application (ties broken by the larger SK_ID_PREV).
    """
    require_columns(previous, PREVIOUS_COLUMNS, "previous_application")
    # 365243 means "no date"; left in, it would drag the DAYS_* averages ~1,000 years forward.
    prev = replace_sentinel(previous, PREVIOUS_DAY_COLUMNS)

    out = prev.groupby(id_col).agg(
        PREV_COUNT=("SK_ID_PREV", "count"),
        PREV_AMT_APPLICATION_MEAN=("AMT_APPLICATION", "mean"),
        PREV_AMT_CREDIT_MEAN=("AMT_CREDIT", "mean"),
        PREV_DAYS_DECISION_MAX=("DAYS_DECISION", "max"),
        PREV_DAYS_TERMINATION_MEAN=("DAYS_TERMINATION", "mean"),
    )
    keys, status = prev[id_col], prev["NAME_CONTRACT_STATUS"]
    out["PREV_APPROVED_RATE"] = share_where(status.eq("Approved"), keys)
    out["PREV_REFUSED_RATE"] = share_where(status.eq("Refused"), keys)

    # Most recent = largest DAYS_DECISION; on a tie, the larger SK_ID_PREV. Sorting by both
    # makes the answer the same every run, whatever order the rows arrive in.
    latest = (prev.sort_values([id_col, "DAYS_DECISION", "SK_ID_PREV"])
                  .drop_duplicates(id_col, keep="last")
                  .set_index(id_col)["NAME_CONTRACT_STATUS"])
    out["PREV_LAST_STATUS"] = latest.astype(object)
    return out.reset_index()


# TODO(student)  (carry-over: finish before the next class)
def aggregate_pos_cash(pos_cash: pd.DataFrame, id_col: str = "SK_ID_CURR") -> pd.DataFrame:
    """Summarize the monthly history of each applicant's earlier POS and cash loans.

    Args:
        pos_cash: The POS_CASH_balance table, one row per earlier loan (SK_ID_PREV) per month.
        id_col: The applicant id column.

    Returns:
        One row per applicant that appears in ``pos_cash``, with ``id_col`` and exactly these
        columns (``POS_CASH_FEATURES``):

        - POS_LOAN_COUNT: distinct earlier loans (SK_ID_PREV)
        - POS_MONTHS_COUNT: monthly records across those loans
        - POS_DPD_MAX / POS_DPD_MEAN: largest and average SK_DPD (days past due) in a month
        - POS_LATE_SHARE: share of months with SK_DPD above 0
        - POS_COMPLETED_SHARE: share of the applicant's loans with at least one month whose
          NAME_CONTRACT_STATUS is "Completed"

    Hints:
        - Most columns are a single groupby; POS_COMPLETED_SHARE is per loan first, then per
          applicant (the same two-stage idea as bureau_balance).
        - Watch the denominators: POS_LATE_SHARE is over months, POS_COMPLETED_SHARE over loans.
    """
    require_columns(pos_cash, POS_CASH_COLUMNS, "POS_CASH_balance")

    # Per-month summaries: one groupby by applicant.
    out = pos_cash.groupby(id_col).agg(
        POS_LOAN_COUNT=("SK_ID_PREV", "nunique"),
        POS_MONTHS_COUNT=("SK_ID_PREV", "size"),
        POS_DPD_MAX=("SK_DPD", "max"),
        POS_DPD_MEAN=("SK_DPD", "mean"),
    )
    keys = pos_cash[id_col]
    # Denominator: months.
    out["POS_LATE_SHARE"] = share_where(pos_cash["SK_DPD"].gt(0), keys)

    # Denominator: loans. Stage 1: did each loan ever reach "Completed"? Stage 2: the share of
    # the applicant's loans that did.
    completed = pos_cash["NAME_CONTRACT_STATUS"].eq("Completed")
    per_loan = completed.groupby([keys, pos_cash["SK_ID_PREV"]]).any()
    out["POS_COMPLETED_SHARE"] = per_loan.astype(float).groupby(level=id_col).mean()

    return out.reset_index()[[id_col, *POS_CASH_FEATURES]]
