# Problem statement

Team: Trial team

## 1. Who uses the model, and for what decision?

Loan officers and the automated application workflow at a consumer lender. When an
application arrives, the model estimates the probability that the applicant will have
payment difficulties. That score drives the first decision on the application, before
any money is lent. Without a model, officers judge each file by hand, which is slow and
inconsistent between officers.

## 2. The options

- **Approve** when the predicted risk is below a low threshold.
- **Refer** to a credit analyst when the risk is between the two thresholds. A referral costs
  analyst time, so the refer band should be narrow.
- **Reject** when the risk is above a high threshold.

## 3. The cost of approving someone who defaults

Example figure: 10 cost units per approved applicant who defaults (lost principal and
collection costs). Replace this with the task-card number.

## 4. The cost of rejecting someone who would have repaid

Example figure: 1 cost unit per good applicant rejected (lost interest margin). A missed
default costs 10 times as much as a lost good customer, so the approval threshold should
sit well below 0.5: we accept rejecting several good customers to avoid one default.

## 5. Success metrics, and why

- **ROC-AUC**: how well the scores rank defaulters above non-defaulters, regardless of threshold.
- **PR-AUC**: how precise the high-risk end is. Its floor is the default rate (about 0.08),
  so it shows progress that ROC-AUC can hide when positives are rare.
- **KS**: the largest gap between the score distributions of the two classes, a standard
  credit-scoring measure.
- **Expected cost** at the chosen threshold, using the costs above: this is what the business
  actually pays.

Accuracy is a poor choice: predicting "no default" for everyone is 92% accurate and useless.
Baseline on the fixed split: ROC-AUC 0.710, PR-AUC 0.169, KS 0.356 (81 defaults in validation,
so expect a few points of noise).

## 6. Risks and sensitive features

CODE_GENDER and DAYS_BIRTH (age) are sensitive. Occupation, income type (for example
pensioners), family status, and region can act as proxies for them. Wrongly rejected
applicants lose access to credit; wrongly approved applicants can end up in debt they
cannot repay.

## 7. Assumptions

- The historical TARGET reflects what would happen to future applicants.
- The two costs are constant per applicant (in reality they depend on the loan amount).
- The 5,000-applicant sample represents the full population. If the costs were very
  different from 10:1, the threshold, and possibly the metric we optimize, would change most.
