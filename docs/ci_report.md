# CI and the quality gate (Week 4)

Team: Trial team

## The pipeline

Cloud Build project: `project-8e7951a2-cb46-497d-99b`. Trigger: `pr-checks`, on pull
requests to `main`, running as the service account `cloud-build-ci` (role: Logs Writer).
Branch protection on `main` requires a pull request and the check
`pr-checks (project-8e7951a2-cb46-497d-99b)`.

| Step | What it runs | Why it is there |
|---|---|---|
| install | `pip install -r requirements.txt` | the same packages as on our laptops, on a fresh machine every time |
| lint | `python -m ruff check .` | style errors and real bugs (unused names, undefined variables) before anything runs |
| test | `python -m pytest -q` | the unit tests and every earlier week's tests run; the data and model tests skip, because the Kaggle data is never in GitHub and so never on the build machine |
| gate | `python -m scripts.quality_gate` | blocks a change that makes the model worse, or whose metrics do not belong to its code |

A green build takes about 3 minutes, almost all of it the install step.

## Gate thresholds, and why

Our registered model (version 1): validation AUC 0.758, expected cost 0.545 per applicant at
its threshold 0.070. Approving everyone costs 0.810.

- **min_auc** = 0.70. Our Week 1 logistic regression on the application table alone reached
  0.710, so a model below 0.70 is worse than the simplest thing we built and must not ship.
  It is a floor, not a target: every reasonable boosting model clears it.
- **max_cost** = 0.70. Our model costs 0.545 per applicant; approving everyone costs 0.810. A
  model above 0.70 would save less than 14% compared with having no model at all, which is not
  worth the risk of running one.
- **max_auc_drop** = 0.02. The gate compares the model this commit would ship with the one we
  registered. Rebuilding the same code and data gives exactly the same AUC (fixed seed and
  split), so any drop comes from a change. 0.02 leaves room for small trade-offs (for example
  a simpler, faster model) but blocks a real loss. Dropping the EXT_SOURCE scores, for
  example, gives 0.705: above the floor, so only this rule would stop it.
- **allow_failing_model_tests** = 0. Every model test must pass or be a documented known
  failure (xfail, with its finding in docs/test_findings.md). Our three known failures
  (weekday, gender, income) are documented; a new, unexplained failure blocks the merge.

## Evidence

- A green Cloud Build run on a pull request (#1, "CI pipeline and quality gate", merged):
  https://console.cloud.google.com/cloud-build/builds/a68555d7-9885-4cb9-9307-a67ccd7ffca1?project=424758227832
- A red run, and what made it red (#2, "Small change without new metrics"):
  https://console.cloud.google.com/cloud-build/builds/732dac53-fdd7-4386-a60f-25f17c774cc8?project=424758227832
  We added one line to `src/models.py` (a comment) and pushed it without running
  `python run.py evaluate`. Install, lint, and test passed; the gate failed with:
  "stale metrics: the code or config changed after reports/gate_metrics.json was written
  (1e193886c3b90aeb != 7763de4307e40c9a). Run python run.py evaluate and commit the new file."
  Even a harmless-looking change must come with metrics measured on the new code.
- How the red pull request was handled: GitHub greyed out the merge button because the
  required check failed, so it could not be merged by accident. We closed it without merging;
  the change was only to show the gate working.
