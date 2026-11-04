# Test findings (Week 4)

Team: Trial team

| Kind | Tests | Passed | Failed | Known failures (xfail) | Skipped |
|---|---|---|---|---|---|
| Unit | 5 | 5 | 0 | 0 | 0 |
| Data | 5 | 5 | 0 | 0 | 0 |
| Model | 4 | 1 | 0 | 3 | 0 |

## Limits we chose, and why

- **Ages 18 to 70** (`test_value_ranges`): our sample spans 21.0 to 68.8 years and lending
  starts at 18, so an age outside 18-70 means DAYS_BIRTH was flipped or mis-read.
- **Income above 0**: the lowest income in the sample is 27,000; 0 or less is impossible.
- **Rates and shares between 0 and 1**: they are proportions; anything else is a bug in an
  aggregation (dividing by the wrong count).
- **EXT_SOURCE_2 missing for under 1%** (`test_missing_values`): it is missing for 0.24%.
  It is our strongest feature, so more missing values would quietly weaken the model.
- **Default rate 6% to 10%** (`test_default_rate`): the sample has 8.08%. A 5,000-applicant
  sample of an 8% rate almost never leaves 7.3%-8.8% by chance, so 6%-10% only fails if the
  sample or the labels really changed.
- **Minimum AUC 0.70** (`test_minimum_auc`, provided): our model scores 0.758; the Week 1
  baseline on the application table alone reached 0.710.
- **"No change" means at most 0.001** (weekday, income): far below anything that could move a
  decision at our threshold (0.070).
- **Gender: at most 0.01**: one hundredth of a probability can already move an applicant across
  the threshold.

## Findings

### test_application_weekday_does_not_change_the_score

- **What failed:** when every validation applicant is set to MONDAY, 21 of 1,000 scores move by
  more than 0.001 and 12 by more than 0.01; the largest change is 0.050 (0.094 if everyone is
  set to SUNDAY). 3 decisions flip between approve and reject.
- **Why:** WEEKDAY_APPR_PROCESS_START is one of our 164 features, and our tuned model (12
  leaves per tree, each tree on a random 51% of the features) uses it. In the training data the
  default rate by weekday ranges from 7.0% (Friday) to 9.4% (Tuesday), with only 248 Sunday
  applicants: that is chance, and the model learned it as if it were real.
- **Does it matter for the lender?** Yes: the day someone applies must not change their
  decision, and we could not explain such a decision to them.
- **Decision:** kept as a known failure (`xfail(strict=True)`) for now. The fix is to remove
  WEEKDAY_APPR_PROCESS_START (and, for the same reason, HOUR_APPR_PROCESS_START) from the
  features, retrain, and register the new model; we plan it before Week 5's deployment. When
  that model is registered this test will pass, `strict=True` will turn it red, and we remove
  the mark.

### test_gender_does_not_change_the_score

- **What failed:** 238 of 1,000 applicants' scores change by more than 0.01 when CODE_GENDER is
  switched between F and M; men score higher in 236 of them (by 0.008 on average). 28 decisions
  flip. The largest change is 0.500 to 1.000, a step in the isotonic calibration.
- **Why:** CODE_GENDER is one of the features, and men default more often in our data (10.6%
  against 6.8% for women), so the model learned to use it.
- **Does it matter for the lender?** Yes: gender is a protected attribute; a credit decision
  must not depend on it. Removing the column is not enough on its own, because other features
  (occupation, income type, car ownership) can stand in for gender.
- **Decision:** kept as a known failure (`xfail(strict=True)`) until the Week 6 fairness
  analysis tells us how removing gender changes the treatment of each group (and which other
  features act as proxies); then we retrain without it.

### test_higher_income_does_not_raise_risk

- **What failed:** with 50% more income (and the income ratios recomputed by `change_income`),
  50 of 1,000 applicants get riskier; the largest increase is 0.101, and 2 applicants would be
  newly rejected.
- **Why:** the increases come mostly from the ratio features: changing only
  ANNUITY_INCOME_RATIO makes 40 applicants riskier, only CREDIT_INCOME_RATIO 22, and even raw
  AMT_INCOME_TOTAL alone 17. For some ranges the model learned that a smaller loan compared with
  income means more risk, a pattern from noise in about 320 training defaults.
- **Does it matter for the lender?** Yes: reporting a higher income should never push an
  applicant toward rejection.
- **Decision:** kept as a known failure (`xfail(strict=True)`) for now. It is fixable:
  HistGradientBoosting's `monotonic_cst` can force the risk never to rise with income and never
  to fall as the two ratios rise. We will try it, compare the CV AUC, and register the
  constrained model if the AUC holds; then this test passes and we remove the mark.
