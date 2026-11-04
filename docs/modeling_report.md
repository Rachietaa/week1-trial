# Modeling report (Week 3)

Team: Trial team

## 1. The production model

HistGradientBoostingClassifier with the settings of Optuna trial 28 (best of 30, CV AUC
0.750): learning_rate 0.010, max_iter 250, max_leaf_nodes 12, min_samples_leaf 122,
l2_regularization 0.003, max_features 0.51. That means many small, cautious trees with large
leaves, the direction our Monday variations pointed (hgb_regularized, 0.739). It uses all
164 features of our Week 2 feature table, is calibrated with isotonic regression, and
rejects applicants whose calibrated score is at least 0.070. Registered as
`models:/credit-risk@staging`, version 1.

## 2. Production model against the decision tree

| | Production model | tree_tuned |
|---|---|---|
| Validation ROC-AUC [95% CI] | 0.758 [0.707, 0.810] | 0.703 [0.645, 0.756] |
| CV ROC-AUC (train split) | 0.743 ± 0.023 | 0.697 ± 0.010 |
| Latency p95, one applicant (ms) | 7.0 (p50 6.0) | 2.6 |
| Model size (KB) | 492 | 18 |
| Features | 164 | 164 |
| Explainability | 250 trees of up to 12 leaves: needs SHAP or permutation importance | one tree of depth 5: can be printed and read |

On the validation split the production model is 0.055 AUC better, with a paired 95%
interval of [-0.002, +0.114]: almost, but not quite, entirely above 0. With only 81 defaults
in validation we cannot claim the difference is certain from validation alone. The
cross-validated AUCs on 4,000 training applicants point the same way (0.743 against 0.697,
about two fold standard deviations), which is our main evidence.

What we give up: the tree is almost three times faster, 27 times smaller, and a loan officer
can follow its five questions. Speed and size hardly matter here: 7 ms per applicant and
under half a megabyte are small for a web service. Explainability does matter, because a
lender must be able to tell a rejected applicant why; we will need SHAP explanations
(Week 6) to close that gap. We choose boosting because ranking risk better is the model's
job, and its other costs are affordable.

## 3. The decision threshold

We reject when the calibrated score is at least 0.070. Our Week 1 costs are 10 units for
approving someone who defaults and 1 unit for rejecting someone who would have repaid, so a
missed default is ten times worse. The break-even probability is 1 / (1 + 10) = 0.091, far
below 0.5; our threshold is a little lower than that, which means it rejects slightly more
cautiously.

The threshold was chosen on out-of-fold scores of the training split (each applicant scored
by a model that never saw them), never on the validation split: choosing it there would fit
the threshold to those 1,000 applicants and make their cost look better than it is.

On the validation split our rule costs 0.545 units per applicant, against 0.782 at a
threshold of 0.5 and 0.810 when approving everyone: about 30% cheaper. The price is that it
rejects 28.5% of applicants, a business decision the lender has to accept; a "refer to an
analyst" band between approve and reject would soften it.

## 4. Calibration

Isotonic calibration did not help our model: the Brier score went from 0.0689 to 0.0706 (a
little worse), and the average predicted probability moved from 0.078 to 0.083 against a real
default rate of 0.081. The reliability plot (`reports/figures/reliability.png`) shows both
curves close to the diagonal. Boosting trained on log loss already gives roughly calibrated
probabilities, and an isotonic map learned from about 320 defaults adds a little noise. We
keep calibration in the pipeline anyway: it costs nothing at prediction time, and it would
matter for a model that is not calibrated (for example one trained with undersampling,
whose scores come out far too high). Next we would try sigmoid calibration.

## 5. Limitations and risks

- Only 81 defaults in validation: every validation AUC carries about ±0.05, and the
  difference between our two models is not certain on validation alone.
- The Optuna search and the threshold used the same 4,000 training applicants, so the CV
  numbers are slightly optimistic.
- The costs are the same for every applicant; in reality a default costs in proportion to the
  loan amount.
- CODE_GENDER and age (DAYS_BIRTH) are among the features. Both are sensitive (our Week 1
  problem statement) and must be checked for fairness in Week 6.
- The data has no dates, so we cannot test whether the model keeps working on later
  applicants.
