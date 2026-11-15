# Feature dictionary

Team: Trial team

| Feature | Source table | Meaning | How it was built |
|---|---|---|---|
| BUREAU_COUNT | bureau | How many credits other lenders report for the applicant, open or closed. | Count of the applicant's bureau rows. 0 if no bureau record (filled in the join). |
| BUREAU_AMT_CREDIT_SUM_MEAN | bureau | Typical size of the applicant's credits elsewhere. | Mean of AMT_CREDIT_SUM per applicant. Missing if no bureau record. |
| BUREAU_AMT_CREDIT_SUM_MAX | bureau | Largest credit the applicant has held elsewhere. | Max of AMT_CREDIT_SUM. Missing if no bureau record. |
| BUREAU_AMT_DEBT_MEAN | bureau | Typical debt still owed on credits elsewhere. | Mean of AMT_CREDIT_SUM_DEBT, ignoring missing values. Missing if none reported. |
| BUREAU_AMT_OVERDUE_SUM | bureau | Total amount currently overdue at other lenders. | Sum of AMT_CREDIT_SUM_OVERDUE. Missing if no bureau record. |
| BUREAU_DAYS_OVERDUE_MAX | bureau | Worst current lateness at another lender, in days. | Max of CREDIT_DAY_OVERDUE. Missing if no bureau record. |
| BUREAU_DAYS_CREDIT_MAX | bureau | How recently the applicant last took credit elsewhere (closer to 0 = more recent). | Max of DAYS_CREDIT (negative days before this application). |
| BUREAU_ACTIVE_COUNT | bureau | Credits still open at other lenders. | Count of rows with CREDIT_ACTIVE = Active. 0 if none. |
| BUREAU_CLOSED_COUNT | bureau | Credits already closed at other lenders. | Count of rows with CREDIT_ACTIVE = Closed. 0 if none. |
| PREV_COUNT | previous_application | How often the applicant applied to Home Credit before. | Count of previous_application rows. 0 if none. |
| PREV_APPROVED_RATE | previous_application | Share of earlier applications Home Credit approved. | Mean of (NAME_CONTRACT_STATUS = Approved). Missing if no earlier applications. |
| PREV_REFUSED_RATE | previous_application | Share of earlier applications Home Credit refused. | Mean of (NAME_CONTRACT_STATUS = Refused). Missing if no earlier applications. |
| PREV_AMT_APPLICATION_MEAN | previous_application | Typical amount the applicant asked for before. | Mean of AMT_APPLICATION. |
| PREV_AMT_CREDIT_MEAN | previous_application | Typical amount Home Credit offered before. | Mean of AMT_CREDIT. |
| PREV_DAYS_DECISION_MAX | previous_application | How recently the applicant last applied. | Max of DAYS_DECISION. |
| PREV_DAYS_TERMINATION_MEAN | previous_application | Typical time since earlier loans ended. | Mean of DAYS_TERMINATION after replacing the 365243 'no date' code with missing. |
| PREV_LAST_STATUS | previous_application | Outcome of the most recent earlier application (text). | NAME_CONTRACT_STATUS of the row with the largest DAYS_DECISION; ties broken by the larger SK_ID_PREV. |
| BB_CREDIT_COUNT | bureau_balance | Bureau credits that have a monthly payment history. | Stage 1 per SK_ID_BUREAU, stage 2 count per applicant via bureau. 0 if none. |
| BB_MONTHS_COUNT | bureau_balance | Months of bureau payment history. | Sum over the applicant's credits of their monthly rows. 0 if none. |
| BB_LATE_MONTHS_COUNT | bureau_balance | Months the applicant was late on a bureau credit. | Months with STATUS 1-5, summed over credits. 0 if none. |
| BB_LATE_SHARE | bureau_balance | Share of bureau months paid late. | BB_LATE_MONTHS_COUNT / BB_MONTHS_COUNT (pooled over months, not averaged per credit). |
| BB_WORST_STATUS | bureau_balance | Worst lateness grade ever reported (0 = on time, 5 = 120+ days or written off). | Max numeric STATUS; C and X ignored. Missing if only C/X months. |
| POS_LOAN_COUNT | POS_CASH_balance | Earlier point-of-sale or cash loans at Home Credit. | Distinct SK_ID_PREV per applicant. 0 if none. |
| POS_MONTHS_COUNT | POS_CASH_balance | Months of history on those loans. | Count of monthly rows. 0 if none. |
| POS_DPD_MAX | POS_CASH_balance | Worst days past due in any month. | Max of SK_DPD. |
| POS_DPD_MEAN | POS_CASH_balance | Average days past due per month. | Mean of SK_DPD. |
| POS_LATE_SHARE | POS_CASH_balance | Share of months with any lateness. | Mean of (SK_DPD > 0) over months. |
| POS_COMPLETED_SHARE | POS_CASH_balance | Share of those loans the applicant finished. | Per loan: any month with status Completed; then the mean over loans. |
| INST_COUNT | installments_payments | Payment records on earlier loans. | Count of rows, including the few with no payment recorded. 0 if none. |
| INST_LATE_SHARE | installments_payments | Share of payments made after the due date. | Mean of (DAYS_ENTRY_PAYMENT > DAYS_INSTALMENT) over rows with a recorded payment. |
| INST_DAYS_LATE_MAX | installments_payments | Most days any payment was late. | Max of (DAYS_ENTRY_PAYMENT - DAYS_INSTALMENT) clipped at 0, over recorded payments. |
| INST_UNDERPAID_SHARE | installments_payments | Share of payments smaller than the amount due. | Mean of (AMT_PAYMENT < AMT_INSTALMENT) over recorded payments. |
| INST_PAYMENT_DIFF_MEAN | installments_payments | Whether the applicant tends to pay more or less than due. | Mean of AMT_PAYMENT - AMT_INSTALMENT over recorded payments. |
| CC_MONTHS_COUNT | credit_card_balance | Months of Home Credit card history. | Count of card-month rows. 0 if none. |
| CC_BALANCE_MEAN | credit_card_balance | Typical balance carried on the card. | Mean of AMT_BALANCE (can be slightly negative when overpaid). |
| CC_UTILIZATION_MEAN | credit_card_balance | How much of the limit the applicant typically uses. | Mean of AMT_BALANCE / AMT_CREDIT_LIMIT_ACTUAL, skipping months with a 0 limit. |
| CC_UTILIZATION_MAX | credit_card_balance | Highest share of the limit ever used. | Max of the same ratio, skipping 0-limit months. Missing if no month has a limit. |
| CC_DRAWINGS_MEAN | credit_card_balance | Typical money taken from the card per month. | Mean of AMT_DRAWINGS_CURRENT. |
| CC_DPD_MAX | credit_card_balance | Worst days past due on the card. | Max of SK_DPD. |
| CREDIT_INCOME_RATIO | application_train | Loan size in years of income. | AMT_CREDIT / AMT_INCOME_TOTAL; missing if income is 0 or missing. |
| ANNUITY_INCOME_RATIO | application_train | Share of yearly income that goes to repayments. | AMT_ANNUITY / AMT_INCOME_TOTAL; missing if either is missing or income is 0. |
| CREDIT_GOODS_RATIO | application_train | Borrowing compared with the price of what is bought (above 1 = borrowing extra). | AMT_CREDIT / AMT_GOODS_PRICE; missing if goods price is 0 or missing. |
| ANNUITY_CREDIT_RATIO | application_train | Yearly repayment as a share of the loan (rough inverse of its length). | AMT_ANNUITY / AMT_CREDIT. |
