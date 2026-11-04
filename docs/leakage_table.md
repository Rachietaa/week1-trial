<!-- PROVIDED template. Copy it to docs/leakage_table.md and fill that copy in:
       cp docs/leakage_table_template.md docs/leakage_table.md      (Windows: copy ...)
     For each feature, answer Yes or No in the third column and give your reason in the fourth.
     Replace every "?" and every "TODO(student)". Keep the table format: python run.py check
     reads it. Add a row for every feature you create, including ones you add yourself. -->

# Leakage table

Team: Sample team (instructor example)

**The question for every feature:** at the moment an applicant submits this application,
before we decide, would we already know this value?

If the answer is No, the feature **leaks**: it carries information from the future (often from
the outcome itself). A leaking feature makes validation scores look great and then fails in
real use, because the value does not exist yet when the decision is made.

**How to check, not guess:** the `DAYS_*` and `MONTHS_*` columns count days or months
**relative to this application** (negative = before it). Look at the largest value of each
time column a feature is built from. If it is above 0, part of that feature describes the
future. One look at `df["COL"].max()` is better than an opinion.

## Features you built (and the worked example)

| Feature | Source table | Known at application time? | Why / how you checked |
|---|---|---|---|
| BUREAU_COUNT | bureau | Yes | The bureau report is pulled when the application arrives. Every DAYS_CREDIT in our sample is negative (max -2), so all counted credits were opened before this application. |
| BUREAU_ACTIVE_COUNT | bureau | Yes | CREDIT_ACTIVE is the status on the bureau report at application time; DAYS_CREDIT_UPDATE max is 0, so no record was updated after the application. |
| BUREAU_CLOSED_COUNT | bureau | Yes | Same report. DAYS_ENDDATE_FACT (actual close date) has max 0: every closure happened on or before the application day. |
| BUREAU_AMT_CREDIT_SUM_MEAN | bureau | Yes | Credit amounts are fixed when each credit is opened, and all opened before the application (DAYS_CREDIT max -2). |
| BUREAU_AMT_CREDIT_SUM_MAX | bureau | Yes | As above. |
| BUREAU_AMT_DEBT_MEAN | bureau | Yes | Debt outstanding as reported on the bureau report at application time (DAYS_CREDIT_UPDATE max 0). |
| BUREAU_AMT_OVERDUE_SUM | bureau | Yes | Current overdue amount on the report at application time. |
| BUREAU_DAYS_OVERDUE_MAX | bureau | Yes | Current days overdue on the report at application time. |
| BUREAU_DAYS_CREDIT_MAX | bureau | Yes | Max -2: the newest credit opened 2 days before the application. Note DAYS_CREDIT_ENDDATE is positive for 8,446 rows, but that is the *scheduled* end date in the contract, known in advance; we do not use it anyway. |
| PREV_COUNT | previous_application | Yes | Every DAYS_DECISION is negative (max -2): all earlier applications were decided before this one. |
| PREV_APPROVED_RATE | previous_application | Yes | Decisions already made (DAYS_DECISION max -2). |
| PREV_REFUSED_RATE | previous_application | Yes | As above. |
| PREV_AMT_APPLICATION_MEAN | previous_application | Yes | Amounts were set when those earlier applications were made. |
| PREV_AMT_CREDIT_MEAN | previous_application | Yes | As above. |
| PREV_DAYS_DECISION_MAX | previous_application | Yes | Max -2, so it is in the past. |
| PREV_DAYS_TERMINATION_MEAN | previous_application | Yes | After replacing 365243 with NaN, no DAYS_TERMINATION is above 0 in our sample. Without that replacement the column "looks" 1,000 years in the future: a good example of checking the max. |
| PREV_LAST_STATUS | previous_application | Yes | The status of the most recent earlier decision, made at least 2 days before this application. |
| BB_CREDIT_COUNT | bureau_balance | Yes | MONTHS_BALANCE ranges from -95 to 0: nothing after the application month. |
| BB_MONTHS_COUNT | bureau_balance | Yes | As above. |
| BB_LATE_MONTHS_COUNT | bureau_balance | Yes | Monthly statuses up to the application month (max 0). |
| BB_LATE_SHARE | bureau_balance | Yes | As above. |
| BB_WORST_STATUS | bureau_balance | Yes | As above. |
| POS_LOAN_COUNT | POS_CASH_balance | Yes | MONTHS_BALANCE max is -1: only months before the application. |
| POS_MONTHS_COUNT | POS_CASH_balance | Yes | As above. |
| POS_DPD_MAX | POS_CASH_balance | Yes | As above. |
| POS_DPD_MEAN | POS_CASH_balance | Yes | As above. |
| POS_LATE_SHARE | POS_CASH_balance | Yes | As above. |
| POS_COMPLETED_SHARE | POS_CASH_balance | Yes | Status in months before the application (max -1). |

## Application columns worth a second look

These already sit in `application_train` and went into your Week 1 baseline. Some are less
obvious than they look. Find each one in `HomeCredit_columns_description.csv` (in your
download) before you answer.

| Feature | Source table | Known at application time? | Why / how you checked |
|---|---|---|---|
| TARGET | application_train | No | It is the outcome: whether the client later had payment difficulties. Using it as a feature is the most direct leak possible. |
| EXT_SOURCE_2 | application_train | Yes | Caveat: it is an external score that exists at application time, but we do not know how or when the provider computed it. If it were refreshed after the loan was issued it would leak. Its high importance is a reason to ask the provider, not to relax. |
| DEF_30_CNT_SOCIAL_CIRCLE | application_train | Yes | Only if it was observed at application time, which the column description does not say. It is also a fairness concern: it judges the applicant by other people's defaults. |
| AMT_REQ_CREDIT_BUREAU_HOUR | application_train | Yes | Enquiries in the hour before the application, so known. But it probably includes the enquiry made for this very application, so it partly measures our own process, not the applicant. |
| DAYS_LAST_PHONE_CHANGE | application_train | Yes | Max is 0: the change happened on or before the application day. |

## Beyond single columns

Leakage can also come from **how** a feature is computed, not only from which column it uses.
In two or three sentences: name one way your feature code could leak even if every column
above is a Yes, and how your code avoids it.

Leakage can also come from how a feature is computed. Filling missing values or scaling with statistics from all 5,000 applicants would let validation applicants influence training; target encoding a category with TARGET means, or picking features by validation AUC, would leak too. Our aggregations only use each applicant's own rows (never TARGET or another applicant), and every fitted step (imputer, scaler, encoder, model) lives inside the sklearn Pipeline, fitted on the train split only.
