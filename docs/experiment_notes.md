# Experiment notes (Week 3)

Team: Trial team

## Setup

Every run below trained on the same rows: the train split of our feature table (4,000
applicants, 323 defaults), compared with 5-fold stratified cross-validation, data_version
851fead5a421 (from `python run.py check`). Exported table: `reports/mlflow_runs.csv`.

## Results

| Run | What changed from hgb_default | CV AUC ± std | Train AUC | Valid AUC [95% CI] |
|---|---|---|---|---|
| baseline_lr | (logistic regression, Week 1 pipeline) | 0.723 ± 0.032 | 0.845 | 0.727 [0.666, 0.783] |
| tree_unlimited | (decision tree, no limits) | 0.543 ± 0.013 | 1.000 | 0.549 [0.508, 0.599] |
| tree_tuned | (decision tree, max_depth 5, min_samples_leaf 50) | 0.697 ± 0.010 | 0.782 | 0.703 [0.645, 0.756] |
| hgb_default | nothing | 0.725 ± 0.039 | 1.000 | 0.697 [0.636, 0.760] |
| hgb_balanced | class_weight=balanced | 0.713 ± 0.045 | 1.000 | 0.726 [0.666, 0.783] |
| hgb_undersample | 3 non-defaulters per defaulter | 0.722 ± 0.025 | 0.999 | 0.755 [0.697, 0.809] |
| hgb_l2 | l2_regularization 1.0 | 0.732 ± 0.033 | 1.000 | 0.745 [0.697, 0.796] |
| hgb_leaf100 | min_samples_leaf 100 | 0.722 ± 0.024 | 1.000 | 0.756 [0.705, 0.807] |
| hgb_leaves8 | max_leaf_nodes 8 | 0.723 ± 0.041 | 0.985 | 0.732 [0.677, 0.790] |
| hgb_regularized | learning_rate 0.03, 300 trees, 8 leaves, leaf 100, l2 1.0 | 0.739 ± 0.020 | 0.957 | 0.757 [0.704, 0.809] |

## Overfitting

tree_unlimited scores 1.000 on its own training rows but only 0.543 in cross-validation,
barely better than guessing: with no limits it memorized the training applicants. The grid
chose max_depth 5 and min_samples_leaf 50 (CV 0.697), which fits the training rows much
less (0.782) and generalizes far better. Default boosting also reaches train AUC 1.000, so it
overfits too, just less.

## What helped and what did not

No single change beat the noise: the one-setting variations land between 0.713 and 0.732,
all within one standard deviation (about 0.03) of hgb_default's 0.725. Class weights and
undersampling did not raise the AUC at all. Combining the regularizing settings in
hgb_regularized gave the best CV AUC (0.739), the smallest spread (0.020), and the smallest
train/CV gap, beating baseline_lr by 0.016, still less than one standard deviation.
Validation AUCs move much more (0.697 to 0.757) than CV AUCs, which is why we compare by CV.
Next we would search these settings together with Optuna.
