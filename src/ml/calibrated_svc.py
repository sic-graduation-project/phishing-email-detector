from pathlib import Path

import joblib

from sklearn.calibration import CalibratedClassifierCV
from sklearn.svm import LinearSVC
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)

from prepare_features import prepare_features


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODELS_DIR = PROJECT_ROOT / "models"


def main():
    print("=" * 70)
    print("CALIBRATED LINEAR SVC")
    print("=" * 70)

    data = prepare_features()

    X_train = data["X_train"]
    X_test = data["X_test"]
    y_train = data["y_train"]
    y_test = data["y_test"]

    # --------------------------------------------------------
    # Base classifier
    # --------------------------------------------------------

    base_model = LinearSVC(
        random_state=42,
        max_iter=5000,
    )

    # --------------------------------------------------------
    # Probability calibration
    #
    # Calibration is performed using cross-validation
    # on TRAINING data only.
    # --------------------------------------------------------

    model = CalibratedClassifierCV(
        estimator=base_model,
        method="sigmoid",
        cv=5,
    )

    print("\nTraining calibrated Linear SVC...")

    model.fit(X_train, y_train)

    print("Training completed.")

    # --------------------------------------------------------
    # Predictions
    # --------------------------------------------------------

    y_pred = model.predict(X_test)

    y_probability = model.predict_proba(
        X_test
    )[:, 1]

    # --------------------------------------------------------
    # Evaluation
    # --------------------------------------------------------

    accuracy = accuracy_score(
        y_test,
        y_pred,
    )

    precision = precision_score(
        y_test,
        y_pred,
        pos_label=1,
    )

    recall = recall_score(
        y_test,
        y_pred,
        pos_label=1,
    )

    f1 = f1_score(
        y_test,
        y_pred,
        pos_label=1,
    )

    roc_auc = roc_auc_score(
        y_test,
        y_probability,
    )

    matrix = confusion_matrix(
        y_test,
        y_pred,
    )

    tn, fp, fn, tp = matrix.ravel()

    print("\n" + "=" * 70)
    print("CALIBRATED LINEAR SVC RESULTS")
    print("=" * 70)

    print(f"Accuracy : {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1 Score : {f1:.4f}")
    print(f"ROC-AUC  : {roc_auc:.4f}")

    print("\nConfusion Matrix:")
    print(matrix)

    print("\nConfusion Matrix Details:")
    print(f"True Negatives : {tn}")
    print(f"False Positives: {fp}")
    print(f"False Negatives: {fn}")
    print(f"True Positives : {tp}")

    print("\nClassification Report:")
    print(
        classification_report(
            y_test,
            y_pred,
            target_names=[
                "Legitimate",
                "Phishing",
            ],
            digits=4,
        )
    )

    # --------------------------------------------------------
    # Risk score examples
    # --------------------------------------------------------

    print("\nRisk Score Examples:")

    for index in range(10):
        actual = y_test[index]
        predicted = y_pred[index]
        risk_score = y_probability[index] * 100

        print(
            f"Email {index + 1:>2}: "
            f"Actual={actual} | "
            f"Predicted={predicted} | "
            f"Risk={risk_score:.2f}%"
        )

    # --------------------------------------------------------
    # Save model
    # --------------------------------------------------------

    MODELS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    model_path = (
        MODELS_DIR
        / "calibrated_linear_svc.pkl"
    )

    joblib.dump(
        model,
        model_path,
    )

    print("\nModel saved to:")
    print(model_path)


if __name__ == "__main__":
    main()