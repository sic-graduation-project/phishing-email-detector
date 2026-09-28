import time

from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)

from prepare_features import prepare_features


def evaluate_model(
    name,
    model,
    X_train,
    X_test,
    y_train,
    y_test,
):
    print("\n" + "=" * 70)
    print(f"TRAINING: {name}")
    print("=" * 70)

    start_time = time.time()

    model.fit(X_train, y_train)

    training_time = time.time() - start_time

    y_pred = model.predict(X_test)

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

    matrix = confusion_matrix(
        y_test,
        y_pred,
    )

    tn, fp, fn, tp = matrix.ravel()

    result = {
        "Model": name,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1": f1,
        "False Positives": fp,
        "False Negatives": fn,
        "Training Time": training_time,
    }

    print(f"Accuracy : {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1 Score : {f1:.4f}")

    print("\nConfusion Matrix:")
    print(matrix)

    print("\nErrors:")
    print(f"False Positives: {fp}")
    print(f"False Negatives: {fn}")

    print(
        f"\nTraining Time: "
        f"{training_time:.2f} seconds"
    )

    return result


def main():
    print("=" * 70)
    print("PHISHING MODEL COMPARISON")
    print("=" * 70)

    data = prepare_features()

    X_train = data["X_train"]
    # Model comparison uses validation only. The final test set remains locked.
    X_test = data["X_validation"]
    y_train = data["y_train"]
    y_test = data["y_validation"]

    models = [
        (
            "Logistic Regression",
            LogisticRegression(
                max_iter=2000,
                random_state=42,
                solver="liblinear",
            ),
        ),
        (
            "Linear SVC",
            LinearSVC(
                random_state=42,
                max_iter=5000,
            ),
        ),
        (
            "Multinomial Naive Bayes",
            MultinomialNB(),
        ),
    ]

    results = []

    for name, model in models:
        result = evaluate_model(
            name,
            model,
            X_train,
            X_test,
            y_train,
            y_test,
        )

        results.append(result)

    print("\n" + "=" * 70)
    print("MODEL COMPARISON SUMMARY")
    print("=" * 70)

    header = (
        f"{'Model':<28}"
        f"{'Acc':>8}"
        f"{'Prec':>8}"
        f"{'Recall':>8}"
        f"{'F1':>8}"
        f"{'FP':>7}"
        f"{'FN':>7}"
        f"{'Time':>10}"
    )

    print(header)
    print("-" * len(header))

    for result in results:
        print(
            f"{result['Model']:<28}"
            f"{result['Accuracy']:>8.4f}"
            f"{result['Precision']:>8.4f}"
            f"{result['Recall']:>8.4f}"
            f"{result['F1']:>8.4f}"
            f"{result['False Positives']:>7}"
            f"{result['False Negatives']:>7}"
            f"{result['Training Time']:>9.2f}s"
        )


if __name__ == "__main__":
    main()
