"""Evaluation metrics for a default-probability model.

Accuracy is misleading when only about 8 percent of applicants default, so we use
ranking metrics that look at the scores themselves.
"""

from __future__ import annotations

import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score, roc_curve

ArrayLike = np.ndarray | list


# PROVIDED
def roc_auc(y_true: ArrayLike, y_score: ArrayLike) -> float:
    """Area under the ROC curve.

    It is the chance that a random defaulter scores above a random non-defaulter.
    """
    return float(roc_auc_score(y_true, y_score))


# PROVIDED
def pr_auc(y_true: ArrayLike, y_score: ArrayLike) -> float:
    """Area under the precision-recall curve (average precision). Its floor is the default rate."""
    return float(average_precision_score(y_true, y_score))


# TODO(student)  [reference solution]
def ks_statistic(y_true: ArrayLike, y_score: ArrayLike) -> float:
    """Kolmogorov-Smirnov (KS) statistic between the scores of the two classes.

    Reference solution: at each threshold, TPR is the share of defaulters above it and
    FPR the share of non-defaulters above it, so max(TPR - FPR) is the largest gap
    between the two cumulative score distributions.
    """
    fpr, tpr, _ = roc_curve(y_true, y_score)
    return float(np.max(tpr - fpr))


# TODO(student)  [reference solution]
def evaluate(y_true: ArrayLike, y_score: ArrayLike) -> dict[str, float]:
    """Compute every validation metric we report: ROC-AUC, PR-AUC, and KS."""
    return {
        "roc_auc": roc_auc(y_true, y_score),
        "pr_auc": pr_auc(y_true, y_score),
        "ks": ks_statistic(y_true, y_score),
    }
