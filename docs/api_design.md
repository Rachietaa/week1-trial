# API design (Week 5)

Team: Trial team

## 1. Where do the 164 features come from?

Our model was trained on 164 features. About 40 of them summarize many rows of the six child
tables: an applicant's credits at other lenders, earlier applications at Home Credit, monthly
card balances, instalment payments. A request to /predict is about one applicant, and whoever
calls the API (the loan screen) knows the application form, not summaries of hundreds of
rows held in six other systems. So the caller cannot send them.

A service could get them in two ways:

- **Compute them at request time:** read the applicant's rows from each child table and run
  our Week 2 aggregations for that one person. Always current, but slow (six lookups per
  request) and complex, and the serving code would have to stay exactly the same as the
  training code; if the two ever differ, the model silently receives different numbers than
  it was trained on (training-serving skew).
- **Precompute them:** run the same Week 2 pipeline once, keep one finished row per applicant,
  and look it up by id at request time. Fast and guaranteed identical to training, but only as
  fresh as the last time the table was rebuilt.

## 2. What we chose, and why

A feature store, keyed by SK_ID_CURR. `python run.py export` builds it from the same feature
table and the same cleaning (`clean_application`) the model was trained on, and writes it next
to the model; the service loads both once, at startup. A request contains the applicant's id
and, optionally, updated amounts from the form (income, loan amount, yearly repayment, each
above 0). Updated amounts replace the stored values, and the four ratio features are
recomputed with the Week 2 formulas (a test checks they match `add_ratio_features`), because a
new income with the old credit-to-income ratio would describe an applicant who cannot exist.
The row is a copy: the store itself never changes, since every request shares it.

For this project it is the right choice: one fixed dataset, a model that changes rarely, and
an answer in about 9 ms on a laptop.

## 3. What can go wrong

- **An applicant who is not in the store** (a new customer): the service answers 404 and names
  the id; it never guesses. A real lender would compute the new applicant's features first.
- **A store that does not match the model:** both come from the same `export`, with the model's
  version and feature list in model_info.json, and the service uses that feature list in that
  order. Registering a new model means exporting (and uploading) both again, together.
- **Stale history:** a credit opened after the store was built is invisible until the next
  rebuild. Acceptable here; a lender would rebuild it nightly.
- **Small changes may not move the score:** our model is calibrated with isotonic regression,
  a step function, so a different income can land on the same step (see the example below).
  That is expected, not a bug.

## 4. Example requests

Valid:

    POST /predict {"SK_ID_CURR": 100021}
    200 {"SK_ID_CURR": 100021, "probability": 0.0670, "decision": "approve",
         "threshold": 0.07, "model_version": "1"}

Valid, with an updated income (the ratios are recomputed; here the calibrated score stays on
the same step):

    POST /predict {"SK_ID_CURR": 100021, "AMT_INCOME_TOTAL": 30000}
    200 {"SK_ID_CURR": 100021, "probability": 0.0670, "decision": "approve", ...}

Invalid:

    POST /predict {"SK_ID_CURR": 100021, "AMT_INCOME_TOTAL": -5}
    422 {"detail": [{"type": "greater_than", "loc": ["body", "AMT_INCOME_TOTAL"],
         "msg": "Input should be greater than 0", "input": -5}]}

Unknown applicant:

    POST /predict {"SK_ID_CURR": 1}
    404 {"detail": "applicant 1 is not in the feature store"}
