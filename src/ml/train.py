from pathlib import Path

import joblib

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
    roc_auc_score,
)

from prepare_features import prepare_features


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODELS_DIR = PROJECT_ROOT / "models"


def train_logistic_regression():
    print("=" * 60)
    print("PHISHING EMAIL ML TRAINING")
    print("=" * 60)

    # --------------------------------------------------------
    # Prepare features
    # --------------------------------------------------------

    data = prepare_features()

    X_train = data["X_train"]
    X_test = data["X_test"]
    y_train = data["y_train"]
    y_test = data["y_test"]

    print("\n" + "=" * 60)
    print("TRAINING LOGISTIC REGRESSION")
    print("=" * 60)

    model = LogisticRegression(
        max_iter=2000,
        random_state=42,
        solver="liblinear",
    )

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

    print("\n" + "=" * 60)
    print("LOGISTIC REGRESSION RESULTS")
    print("=" * 60)

    print(f"Accuracy : {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1 Score : {f1:.4f}")
    print(f"ROC-AUC  : {roc_auc:.4f}")

    print("\nConfusion Matrix:")
    print(matrix)

    tn, fp, fn, tp = matrix.ravel()

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
    # Save model
    # --------------------------------------------------------

    MODELS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    model_path = (
        MODELS_DIR
        / "logistic_regression.pkl"
    )

    joblib.dump(
        model,
        model_path,
    )

    print(
        "\nModel saved to:"
    )

    print(model_path)

    return {
        "model": model,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "roc_auc": roc_auc,
        "confusion_matrix": matrix,
    }


if __name__ == "__main__":
    train_logistic_regression()