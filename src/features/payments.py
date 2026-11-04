"""Repayment behavior at Home Credit: installment payments and credit card months.

installments_payments has one row per payment made (or due) on an earlier loan: when it was
due (DAYS_INSTALMENT), when it was paid (DAYS_ENTRY_PAYMENT), what was due (AMT_INSTALMENT),
and what was paid (AMT_PAYMENT). credit_card_balance has one row per card per month. Both
carry SK_ID_CURR, so each groups by applicant directly.

These tables answer the lender's favorite question: does this person pay on time? Follow the
pattern of ``aggregate_bureau`` in src/features/bureau.py.
"""

from __future__ import annotations

import pandas as pd

from src.features.common import (  # noqa: F401  (helpers for you to use)
    count_where,
    require_columns,
    safe_divide,
    share_where,
)

# PROVIDED
INSTALLMENTS_COLUMNS = [
    "SK_ID_CURR", "SK_ID_PREV", "DAYS_INSTALMENT", "DAYS_ENTRY_PAYMENT", "AMT_INSTALMENT",
    "AMT_PAYMENT",
]
INSTALLMENTS_FEATURES = [
    "INST_COUNT", "INST_LATE_SHARE", "INST_DAYS_LATE_MAX", "INST_UNDERPAID_SHARE",
    "INST_PAYMENT_DIFF_MEAN",
]
CREDIT_CARD_COLUMNS = [
    "SK_ID_CURR", "SK_ID_PREV", "MONTHS_BALANCE", "AMT_BALANCE", "AMT_CREDIT_LIMIT_ACTUAL",
    "AMT_DRAWINGS_CURRENT", "SK_DPD",
]
CREDIT_CARD_FEATURES = [
    "CC_MONTHS_COUNT", "CC_BALANCE_MEAN", "CC_UTILIZATION_MEAN", "CC_UTILIZATION_MAX",
    "CC_DRAWINGS_MEAN", "CC_DPD_MAX",
]


# TODO(student)
def aggregate_installments(
    installments: pd.DataFrame, id_col: str = "SK_ID_CURR"
) -> pd.DataFrame:
    """Summarize each applicant's payment history on earlier loans into one row.

    Args:
        installments: The installments_payments table, one row per payment.
        id_col: The applicant id column.

    Returns:
        One row per applicant that appears in ``installments``, with ``id_col`` and exactly
        these columns (``INSTALLMENTS_FEATURES``):

        - INST_COUNT: payment rows
        - INST_LATE_SHARE: share of payments made after the due date
          (DAYS_ENTRY_PAYMENT > DAYS_INSTALMENT)
        - INST_DAYS_LATE_MAX: the most days any payment was late; 0 if never late
        - INST_UNDERPAID_SHARE: share of payments smaller than the amount due
          (AMT_PAYMENT < AMT_INSTALMENT)
        - INST_PAYMENT_DIFF_MEAN: average of AMT_PAYMENT - AMT_INSTALMENT (negative means the
          applicant tends to pay less than due)

        Rows with no payment recorded (DAYS_ENTRY_PAYMENT or AMT_PAYMENT missing) are left out
        of the two shares, the late maximum, and the average, but still count in INST_COUNT.

    Hints:
        - Both DAYS_* columns count days before this application (negative), so "later" means
          a larger number.
        - A comparison with NaN gives False, which would quietly count a missing payment as
          "on time". Make the missing rows NaN before taking a share, so they drop out.
        - ``share_where`` uses every row as the denominator. Here you need a different one.
    """
    require_columns(installments, INSTALLMENTS_COLUMNS, "installments_payments")

    # A payment that was never made has no entry date or no amount. Turn its per-row values
    # into NaN, so the shares, the maximum and the average skip it instead of calling it
    # "on time". It still counts as a row in INST_COUNT.
    paid = installments["DAYS_ENTRY_PAYMENT"].notna() & installments["AMT_PAYMENT"].notna()
    days_late = installments["DAYS_ENTRY_PAYMENT"] - installments["DAYS_INSTALMENT"]
    rows = installments.assign(
        IS_LATE=days_late.gt(0).astype(float).where(paid),
        DAYS_LATE=days_late.clip(lower=0).where(paid),  # on time or early counts as 0 days
        IS_UNDERPAID=installments["AMT_PAYMENT"].lt(installments["AMT_INSTALMENT"])
                                                .astype(float).where(paid),
        PAYMENT_DIFF=(installments["AMT_PAYMENT"] - installments["AMT_INSTALMENT"]).where(paid),
    )

    # The mean of a 0/1 column that skips NaN is a share over the paid rows only.
    out = rows.groupby(id_col).agg(
        INST_COUNT=("SK_ID_PREV", "size"),
        INST_LATE_SHARE=("IS_LATE", "mean"),
        INST_DAYS_LATE_MAX=("DAYS_LATE", "max"),
        INST_UNDERPAID_SHARE=("IS_UNDERPAID", "mean"),
        INST_PAYMENT_DIFF_MEAN=("PAYMENT_DIFF", "mean"),
    )
    return out.reset_index()[[id_col, *INSTALLMENTS_FEATURES]]


# TODO(student)
def aggregate_credit_card(
    credit_card: pd.DataFrame, id_col: str = "SK_ID_CURR"
) -> pd.DataFrame:
    """Summarize each applicant's monthly credit card history into one row.

    Args:
        credit_card: The credit_card_balance table, one row per card (SK_ID_PREV) per month.
        id_col: The applicant id column.

    Returns:
        One row per applicant that appears in ``credit_card``, with ``id_col`` and exactly
        these columns (``CREDIT_CARD_FEATURES``):

        - CC_MONTHS_COUNT: card-month rows
        - CC_BALANCE_MEAN: average AMT_BALANCE
        - CC_UTILIZATION_MEAN / _MAX: average and largest AMT_BALANCE / AMT_CREDIT_LIMIT_ACTUAL
          over the months whose limit is above 0; NaN if no month has a limit
        - CC_DRAWINGS_MEAN: average AMT_DRAWINGS_CURRENT (money taken from the card that month)
        - CC_DPD_MAX: the largest SK_DPD (days past due) in any month

    Hints:
        - In our sample about 1 in 5 card months has a limit of 0. ``safe_divide`` gives NaN
          there instead of inf, and pandas' mean and max skip NaN.
        - A balance can be slightly negative (the customer overpaid). Keep it.
    """
    require_columns(credit_card, CREDIT_CARD_COLUMNS, "credit_card_balance")

    # Utilization only means something when there is a limit: safe_divide gives NaN for a
    # limit of 0, and .where drops any (unexpected) negative limit too.
    limit = credit_card["AMT_CREDIT_LIMIT_ACTUAL"]
    cards = credit_card.assign(
        UTILIZATION=safe_divide(credit_card["AMT_BALANCE"], limit.where(limit > 0)),
    )

    out = cards.groupby(id_col).agg(
        CC_MONTHS_COUNT=("SK_ID_PREV", "size"),
        CC_BALANCE_MEAN=("AMT_BALANCE", "mean"),
        CC_UTILIZATION_MEAN=("UTILIZATION", "mean"),
        CC_UTILIZATION_MAX=("UTILIZATION", "max"),
        CC_DRAWINGS_MEAN=("AMT_DRAWINGS_CURRENT", "mean"),
        CC_DPD_MAX=("SK_DPD", "max"),
    )
    return out.reset_index()[[id_col, *CREDIT_CARD_FEATURES]]
