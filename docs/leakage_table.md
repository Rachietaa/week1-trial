# Leakage table

Team: Trial team

**The question for every feature:** at the moment an applicant submits this application,
before we decide, would we already know this value?

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
| INST_COUNT | installments_payments | Yes | DAYS_INSTALMENT and DAYS_ENTRY_PAYMENT both have max -2: every payment was due and made before the application. |
| INST_LATE_SHARE | installments_payments | Yes | Built only from payments made before the application (DAYS_ENTRY_PAYMENT max -2). |
| INST_DAYS_LATE_MAX | installments_payments | Yes | As above. |
| INST_UNDERPAID_SHARE | installments_payments | Yes | Amounts due and paid before the application. |
| INST_PAYMENT_DIFF_MEAN | installments_payments | Yes | As above. |
| CC_MONTHS_COUNT | credit_card_balance | Yes | MONTHS_BALANCE max is -1: only months before the application. |
| CC_BALANCE_MEAN | credit_card_balance | Yes | As above. |
| CC_UTILIZATION_MEAN | credit_card_balance | Yes | Balance and limit from months before the application. |
| CC_UTILIZATION_MAX | credit_card_balance | Yes | As above. |
| CC_DRAWINGS_MEAN | credit_card_balance | Yes | As above. |
| CC_DPD_MAX | credit_card_balance | Yes | As above. |
| CREDIT_INCOME_RATIO | application_train | Yes | Both amounts are on the application form itself. |
| ANNUITY_INCOME_RATIO | application_train | Yes | Annuity and income are on the application. |
| CREDIT_GOODS_RATIO | application_train | Yes | Credit and goods price are on the application. |
| ANNUITY_CREDIT_RATIO | application_train | Yes | Both from the application. |

## Application columns worth a second look

| Feature | Source table | Known at application time? | Why / how you checked |
|---|---|---|---|
| TARGET | application_train | No | It is the outcome: whether the client later had payment difficulties. Using it as a feature is the most direct leak possible. |
| EXT_SOURCE_2 | application_train | Yes, with a caveat | A normalized score from an external source, so it exists at application time. But we do not know how or when the provider computed it; if it were refreshed after the loan was issued it would leak. In a real project: ask the provider. Its high importance is a reason to be suspicious, not reassured. |
| DEF_30_CNT_SOCIAL_CIRCLE | application_train | Unclear (Yes if computed at application) | "How many people in the client's social surroundings defaulted on 30 DPD." Depends on when it was observed. It is also a fairness question: it judges people by others' behavior. |
| AMT_REQ_CREDIT_BUREAU_HOUR | application_train | Yes, but read it carefully | Bureau enquiries in the hour before the application. Likely includes the enquiry made *for this application*, so it partly measures the process, not the person. |
| DAYS_LAST_PHONE_CHANGE | application_train | Yes | Max is 0: the change happened on or before the application day. |

## Beyond single columns

Leakage can also come from how a feature is computed. Examples: filling missing values or
scaling with statistics computed over all 5,000 applicants (that lets validation applicants
influence training), target encoding a category with TARGET means over all applicants, or
choosing features by looking at validation AUC. Our aggregations only use each applicant's own
rows, so they cannot see another applicant's data or any TARGET; all fitting (imputer, scaler,
encoder, model) happens inside the sklearn Pipeline on the train split only.
