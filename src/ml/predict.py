from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from scipy.sparse import csr_matrix, hstack

from feature_builder import URL_SENDER_FEATURES
from nlp_feature_builder import (
    NLP_NUMERIC_FEATURES,
    build_nlp_features,
)


# ============================================================
# Paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODELS_DIR = PROJECT_ROOT / "models"

MODEL_PATH = MODELS_DIR / "calibrated_linear_svc.pkl"
TFIDF_PATH = MODELS_DIR / "tfidf_vectorizer.pkl"
SCALER_PATH = MODELS_DIR / "numeric_scaler.pkl"
FEATURE_NAMES_PATH = MODELS_DIR / "numeric_feature_names.pkl"


# ============================================================
# Load saved ML artifacts once
# ============================================================

def load_artifacts():
    required_files = [
        MODEL_PATH,
        TFIDF_PATH,
        SCALER_PATH,
        FEATURE_NAMES_PATH,
    ]

    missing_files = [
        path
        for path in required_files
        if not path.exists()
    ]

    if missing_files:
        raise FileNotFoundError(
            "Missing ML artifact(s): "
            + ", ".join(str(path) for path in missing_files)
        )

    model = joblib.load(MODEL_PATH)
    tfidf = joblib.load(TFIDF_PATH)
    scaler = joblib.load(SCALER_PATH)
    numeric_feature_names = joblib.load(
        FEATURE_NAMES_PATH
    )

    return (
        model,
        tfidf,
        scaler,
        numeric_feature_names,
    )


MODEL, TFIDF, SCALER, NUMERIC_FEATURE_NAMES = (
    load_artifacts()
)


# ============================================================
# Input validation
# ============================================================

def validate_url_sender_features(
    url_sender_features: dict[str, Any],
) -> None:
    missing = [
        feature
        for feature in URL_SENDER_FEATURES
        if feature not in url_sender_features
    ]

    if missing:
        raise ValueError(
            "Missing URL/Sender ML features: "
            f"{missing}"
        )


# ============================================================
# Build features for one new email
# ============================================================

def prepare_single_email(
    sender: str,
    subject: str,
    body: str,
    url_sender_features: dict[str, Any],
):
    validate_url_sender_features(
        url_sender_features
    )

    # --------------------------------------------------------
    # Build one-row DataFrame for NLP extraction
    # --------------------------------------------------------

    email_df = pd.DataFrame(
        [
            {
                "email_id": 0,
                "sender": sender or "",
                "subject": subject or "",
                "body": body or "",
                "label": 0,
            }
        ]
    )

    nlp_df = build_nlp_features(
        email_df
    )

    clean_body = nlp_df.loc[
        0,
        "clean_body",
    ]

    # --------------------------------------------------------
    # TF-IDF
    #
    # IMPORTANT:
    # transform only.
    # Never fit on a new email.
    # --------------------------------------------------------

    text_features = TFIDF.transform(
        [clean_body]
    )

    # --------------------------------------------------------
    # Combine 15 URL/Sender + 8 NLP numeric features
    # in exactly the same order used during training.
    # --------------------------------------------------------

    feature_values = {}

    for feature in URL_SENDER_FEATURES:
        feature_values[feature] = (
            url_sender_features[feature]
        )

    for feature in NLP_NUMERIC_FEATURES:
        feature_values[feature] = (
            nlp_df.loc[0, feature]
        )

    # Validate saved feature order
    missing_numeric = [
        feature
        for feature in NUMERIC_FEATURE_NAMES
        if feature not in feature_values
    ]

    if missing_numeric:
        raise ValueError(
            "Could not build numeric features: "
            f"{missing_numeric}"
        )

    numeric_row = [
        feature_values[feature]
        for feature in NUMERIC_FEATURE_NAMES
    ]

    numeric_df = pd.DataFrame(
        [numeric_row],
        columns=NUMERIC_FEATURE_NAMES,
        dtype=float,
    )

    # --------------------------------------------------------
    # Apply TRAINED scaler.
    # transform only.
    # --------------------------------------------------------

    numeric_scaled = SCALER.transform(
        numeric_df
    )

    numeric_sparse = csr_matrix(
        numeric_scaled
    )

    # --------------------------------------------------------
    # Final 10,023-feature vector
    # --------------------------------------------------------

    X = hstack(
        [
            text_features,
            numeric_sparse,
        ]
    ).tocsr()

    expected_features = (
        len(TFIDF.vocabulary_)
        + len(NUMERIC_FEATURE_NAMES)
    )

    if X.shape[1] != expected_features:
        raise ValueError(
            f"Unexpected feature count. "
            f"Expected {expected_features}, "
            f"got {X.shape[1]}."
        )

    return X


# ============================================================
# Prediction
# ============================================================

def predict_email(
    sender: str,
    subject: str,
    body: str,
    url_sender_features: dict[str, Any],
) -> dict[str, Any]:

    X = prepare_single_email(
        sender=sender,
        subject=subject,
        body=body,
        url_sender_features=url_sender_features,
    )

    probability = float(
        MODEL.predict_proba(X)[0, 1]
    )

    predicted_label = int(
        probability >= 0.5
    )

    prediction = (
        "Phishing"
        if predicted_label == 1
        else "Legitimate"
    )

    risk_score = round(
        probability * 100,
        2,
    )

    return {
        "label": predicted_label,
        "prediction": prediction,
        "risk_score": risk_score,
        "phishing_probability": probability,
    }

def predict_from_analysis(
    sender: str,
    subject: str,
    body: str,
    url_analysis_result: dict[str, Any],
) -> dict[str, Any]:

    if "features" not in url_analysis_result:
        raise ValueError(
            "url_analysis_result must contain 'features'."
        )

    ml_result = predict_email(
        sender=sender,
        subject=subject,
        body=body,
        url_sender_features=url_analysis_result["features"],
    )

    return {
        **ml_result,
        "risk_indicators": url_analysis_result.get(
            "risk_indicators", []
        ),
        "indicator_count": url_analysis_result.get(
            "indicator_count", 0
        ),
        "sender_domain": url_analysis_result.get(
            "sender_domain", ""
        ),
        "extracted_urls": url_analysis_result.get(
            "extracted_urls", []
        ),
        "domain_mismatch": url_analysis_result.get(
            "domain_mismatch", 0
        ),
    }

# ============================================================
# Local test
# ============================================================

def main():
    print("=" * 60)
    print("ML SINGLE EMAIL PREDICTION TEST")
    print("=" * 60)

    # Temporary test values.
    # Later these 15 values will come directly from
    # Ryan's analyze_single_email(sender, body).

    test_url_sender_features = {
        "url_count": 1,
        "max_url_length": 30,
        "has_https": 0,
        "has_http": 1,
        "has_at_in_url": 0,
        "has_shortened_url": 0,
        "has_ip_url": 1,
        "max_subdomain_count": 0,
        "url_parameter_count": 0,
        "has_suspicious_characters": 0,
        "has_suspicious_url_word": 1,
        "sender_email_length": 19,
        "sender_domain_length": 11,
        "sender_local_part_length": 7,
        "sender_has_display_name": 0,
    }

    result = predict_email(
        sender="support@example.com",
        subject="Urgent: Verify your account",
        body=(
            "Your account has been suspended. "
            "Please verify your password immediately at "
            "http://192.168.1.10/login"
        ),
        url_sender_features=test_url_sender_features,
    )

    print("\nPrediction result:")

    for key, value in result.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()