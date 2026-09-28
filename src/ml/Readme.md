# Machine-learning pipeline

The production classifier combines body TF-IDF, URL features, and numeric NLP
features. Sender-derived features are retained for analysis but excluded from
the model because the deployed URL/text endpoints and current email form do not
provide a reliable sender.

## Leakage-safe experiment design

`prepare_features.py` deterministically assigns every sender to one of ten
stratified group folds and creates four non-overlapping partitions:

| Partition | Purpose | Rows |
|---|---|---:|
| Train | Fit TF-IDF, scaler, and LinearSVC | 23,490 |
| Calibration | Fit sigmoid probability calibration only | 3,915 |
| Validation | Select the decision threshold | 3,915 |
| Test | One final evaluation after all choices | 7,834 |

The production threshold maximizes validation recall while requiring at least
95% validation precision. It is stored inside the model bundle rather than
being hard-coded at 0.5.

## Verified final test result

These figures come from `models/evaluation_report.json`, generated on
2026-09-28 using scikit-learn 1.9.1:

| Metric | Result |
|---|---:|
| Accuracy | 99.07% |
| Precision | 98.55% |
| Recall | 99.79% |
| F1 | 99.17% |
| ROC-AUC | 99.94% |
| Average precision | 99.94% |
| Brier score | 0.00391 |
| Log loss | 0.01772 |
| False positives | 64 |
| False negatives | 9 |

These are in-dataset sender-disjoint results, not a guarantee of performance
on future attacks. External and time-based validation remains necessary before
making broader accuracy claims.

## Artifacts

The only production artifact is:

```text
models/phishing_model_bundle.joblib
```

It atomically contains the calibrated model, TF-IDF vectorizer, numeric scaler,
feature order, selected threshold, dataset SHA-256 fingerprints, source commit,
schema version, and scikit-learn version. Inference refuses to load an
incomplete bundle or a bundle created with a different scikit-learn version.
The older individual `.pkl` files are legacy artifacts and are not loaded.

## Commands

```powershell
# Train, calibrate, select threshold, evaluate once, and publish atomically
python src/ml/calibrated_svc.py

# Compare candidate models on validation only (never the final test set)
python src/ml/compare_models.py

# Verify sender and exact-body separation using the real production split
python src/ml/check_data_leakage.py

# Evaluate the locked model on a separately sourced labeled dataset
python src/ml/evaluate_external.py path/to/external_emails.csv

# Run prediction regression
python src/ml/integration_test.py

# Run automated tests
python -m pytest -q
```

Do not report new test metrics after repeatedly inspecting or tuning against the
test partition. If model choices change after viewing it, create a new locked
test dataset—preferably newer and from independent sources.

External evaluation input must contain `sender`, `subject`, `body`, and `label`
columns. The evaluator never retrains or modifies the production bundle.
