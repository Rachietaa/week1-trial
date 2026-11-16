# Data card: Home Credit Default Risk (Week 1 sample)

## 1. Source and license terms

Kaggle competition "Home Credit Default Risk" (home-credit-default-risk), published by Home
Credit Group. Use is governed by the competition rules, which every user accepts before
downloading. Each person downloads their own copy, and the data is not redistributed: `data/`
is in .gitignore, so no raw or sampled rows are committed.

## 2. What each table holds

| Table | One row is... | Links by |
|---|---|---|
| application_train | one applicant's current application, with TARGET | SK_ID_CURR |
| bureau | one credit at another institution, reported to the credit bureau | SK_ID_CURR, SK_ID_BUREAU |
| bureau_balance | one month of status for a bureau credit | SK_ID_BUREAU (no SK_ID_CURR) |
| previous_application | one earlier application at Home Credit | SK_ID_CURR, SK_ID_PREV |
| POS_CASH_balance | one month of a previous point-of-sale or cash loan | SK_ID_CURR, SK_ID_PREV |
| installments_payments | one installment (due and paid) on a previous credit | SK_ID_CURR, SK_ID_PREV |
| credit_card_balance | one month of a previous credit card | SK_ID_CURR, SK_ID_PREV |

## 3. Full size versus sample size

| Table | Full rows | Sample rows | MB as loaded | MB after shrinking |
|---|---:|---:|---:|---:|
| application_train | 307,511 | 5,000 | 8.7 | 1.6 |
| bureau | 1,716,428 | 23,680 | 7.1 | 1.2 |
| bureau_balance | 27,299,925 | 231,091 | 16.3 | 1.3 |
| previous_application | 1,670,214 | 23,009 | 26.2 | 2.0 |
| POS_CASH_balance | 10,001,358 | 138,350 | 15.7 | 2.9 |
| installments_payments | 13,605,401 | 186,311 | 11.4 | 5.3 |
| credit_card_balance | 3,840,312 | 50,668 | 11.6 | 3.8 |

The sample takes 5,000 whole applicants, stratified on TARGET with a fixed seed, plus every
row they have in the other tables. Sampling rows at random would break the links: an
applicant could keep their application but lose half their payment history. About 15% of
child-table rows belong to applicants in application_test, which is why the sample has
fewer child rows than 5,000/307,511 of each full table.

## 4. Target definition and class balance

TARGET = 1 means the client had payment difficulties on this loan. Default rate: 8.07% in the
full data, 8.08% in the sample (404 defaults), 8.08% in train (323 of 4,000), and 8.10% in
validation (81 of 1,000). The split is stratified so both parts have the same base rate and
the metrics are comparable.

## 5. Known issues

- application_train is 25% missing cells overall; many housing columns are more than half empty.
- DAYS_EMPLOYED = 365243 (about 1,000 years) is a placeholder. All 897 such applicants in the
  sample are pensioners.
- DAYS_* columns are negative days before the application date (DAYS_BIRTH = -12000 is about 33 years).
- Some flag columns (for example FLAG_MOBIL) are constant in the sample.
- CODE_GENDER contains a rare "XNA" value in the full data.

## 6. Sensitive columns

CODE_GENDER and DAYS_BIRTH directly; NAME_FAMILY_STATUS, CNT_CHILDREN, NAME_INCOME_TYPE,
OCCUPATION_TYPE, and region columns can act as proxies. The baseline uses them as they are;
we will decide how to handle them before relying on the model.

## 7. Limitations of a small sample

Only 81 defaults in validation, so ROC-AUC and KS can move by a few points from chance
alone. Rare categories (for example some occupation types with fewer than 10 applicants)
give unreliable rates and may be missing entirely from the training split.
