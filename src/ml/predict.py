"""Inference using the atomically versioned production model bundle."""

from __future__ import annotations

from typing import Any

import pandas as pd
from scipy.sparse import csr_matrix, hstack

from model_artifact import load_bundle
from nlp_feature_builder import NLP_NUMERIC_FEATURES, build_nlp_features

BUNDLE = load_bundle()
MODEL = BUNDLE["model"]
TFIDF = BUNDLE["tfidf"]
SCALER = BUNDLE["scaler"]
NUMERIC_FEATURE_NAMES = BUNDLE["numeric_features"]
DECISION_THRESHOLD = float(BUNDLE["threshold"])


def prepare_single_email(
    sender: str,
    subject: str,
    body: str,
    url_sender_features: dict[str, Any],
):
    email_df = pd.DataFrame([{
        "email_id": 0,
        "sender": sender or "",
        "subject": subject or "",
        "body": body or "",
        "label": 0,
    }])
    nlp_df = build_nlp_features(email_df)
    feature_values = dict(url_sender_features)
    for feature in NLP_NUMERIC_FEATURES:
        feature_values[feature] = nlp_df.loc[0, feature]

    missing = [name for name in NUMERIC_FEATURE_NAMES if name not in feature_values]
    if missing:
        raise ValueError(f"Missing production model features: {missing}")
    numeric_df = pd.DataFrame(
        [[feature_values[name] for name in NUMERIC_FEATURE_NAMES]],
        columns=NUMERIC_FEATURE_NAMES,
        dtype=float,
    )
    text_features = TFIDF.transform([nlp_df.loc[0, "clean_body"]])
    numeric_features = csr_matrix(SCALER.transform(numeric_df))
    matrix = hstack([text_features, numeric_features]).tocsr()
    if matrix.shape[1] != MODEL.n_features_in_:
        raise ValueError("Inference feature count does not match the bundled model.")
    return matrix


def predict_email(
    sender: str,
    subject: str,
    body: str,
    url_sender_features: dict[str, Any],
) -> dict[str, Any]:
    matrix = prepare_single_email(sender, subject, body, url_sender_features)
    probability = float(MODEL.predict_proba(matrix)[0, 1])
    predicted_label = int(probability >= DECISION_THRESHOLD)
    return {
        "label": predicted_label,
        "prediction": "Phishing" if predicted_label else "Legitimate",
        "risk_score": round(probability * 100, 2),
        "phishing_probability": probability,
        "decision_threshold": DECISION_THRESHOLD,
    }


def predict_from_analysis(
    sender: str,
    subject: str,
    body: str,
    url_analysis_result: dict[str, Any],
) -> dict[str, Any]:
    if "features" not in url_analysis_result:
        raise ValueError("url_analysis_result must contain 'features'.")
    ml_result = predict_email(sender, subject, body, url_analysis_result["features"])
    return {
        **ml_result,
        "risk_indicators": url_analysis_result.get("risk_indicators", []),
        "indicator_count": url_analysis_result.get("indicator_count", 0),
        "sender_domain": url_analysis_result.get("sender_domain", ""),
        "extracted_urls": url_analysis_result.get("extracted_urls", []),
        "domain_mismatch": url_analysis_result.get("domain_mismatch", 0),
    }
