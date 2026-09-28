"""Train, calibrate, validate, evaluate, and atomically publish the final model."""

from __future__ import annotations

import json

import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.frozen import FrozenEstimator
from sklearn.metrics import (
    accuracy_score, average_precision_score, brier_score_loss, confusion_matrix,
    f1_score, log_loss, precision_recall_curve, precision_score, recall_score,
    roc_auc_score,
)
from sklearn.svm import LinearSVC

from model_artifact import build_metadata, publish_bundle
from prepare_features import RANDOM_STATE, prepare_features


def choose_threshold(y_true, probabilities, minimum_precision: float = 0.95) -> float:
    """Maximize recall subject to a validation precision requirement."""
    precision, recall, thresholds = precision_recall_curve(y_true, probabilities)
    candidates = []
    for index, threshold in enumerate(thresholds):
        if precision[index] >= minimum_precision:
            candidates.append((recall[index], precision[index], -threshold, threshold))
    if not candidates:
        f1 = 2 * precision[:-1] * recall[:-1] / np.maximum(precision[:-1] + recall[:-1], 1e-12)
        return float(thresholds[int(np.argmax(f1))])
    return float(max(candidates)[3])


def evaluate(y_true, probabilities, threshold: float) -> dict:
    predicted = (probabilities >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, predicted, labels=[0, 1]).ravel()
    return {
        "rows": int(len(y_true)),
        "threshold": round(float(threshold), 6),
        "accuracy": float(accuracy_score(y_true, predicted)),
        "precision": float(precision_score(y_true, predicted, zero_division=0)),
        "recall": float(recall_score(y_true, predicted, zero_division=0)),
        "f1": float(f1_score(y_true, predicted, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, probabilities)),
        "average_precision": float(average_precision_score(y_true, probabilities)),
        "brier_score": float(brier_score_loss(y_true, probabilities)),
        "log_loss": float(log_loss(y_true, probabilities)),
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
    }


def train_and_publish() -> dict:
    data = prepare_features()
    base_model = LinearSVC(random_state=RANDOM_STATE, max_iter=5000)
    base_model.fit(data["X_train"], data["y_train"])

    # Calibration sees only its dedicated sender-disjoint partition.
    model = CalibratedClassifierCV(FrozenEstimator(base_model), method="sigmoid")
    model.fit(data["X_calibration"], data["y_calibration"])

    validation_probability = model.predict_proba(data["X_validation"])[:, 1]
    threshold = choose_threshold(data["y_validation"], validation_probability)
    validation_metrics = evaluate(data["y_validation"], validation_probability, threshold)

    # Test is touched only after fitting, calibration, and threshold selection.
    test_probability = model.predict_proba(data["X_test"])[:, 1]
    test_metrics = evaluate(data["y_test"], test_probability, threshold)
    metadata = build_metadata(data["numeric_features"], threshold)
    report = {
        "metadata": metadata,
        "partition_rows": {name: len(frame) for name, frame in data["frames"].items()},
        "validation": validation_metrics,
        "test": test_metrics,
    }
    bundle = {
        "model": model,
        "tfidf": data["tfidf"],
        "scaler": data["scaler"],
        "numeric_features": data["numeric_features"],
        "threshold": threshold,
        "metadata": metadata,
    }
    publish_bundle(bundle, report)
    print(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    train_and_publish()
