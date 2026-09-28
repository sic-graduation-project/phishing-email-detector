"""Integration of URL features, NLP/ML prediction, and the safety policy."""

from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path

from .risk_policy import apply_risk_policy

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ML_DIR = PROJECT_ROOT / "src" / "ml"
URL_DIR = PROJECT_ROOT / "notebooks" / "url_analysis"
for path in (ML_DIR, URL_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


@lru_cache(maxsize=1)
def _components():
    from myprojectai import analyze_single_email
    from predict import predict_from_analysis

    return analyze_single_email, predict_from_analysis


def ensure_ready() -> None:
    """Load model artifacts so readiness fails if deployment is incomplete."""
    _components()


def analyze(input_type: str, text: str, subject: str = "", sender: str = "") -> dict:
    analyze_single_email, predict_from_analysis = _components()
    combined_text = f"{subject}\n{text}".strip()
    url_analysis = analyze_single_email(sender, combined_text)
    prediction = predict_from_analysis(
        sender=sender,
        subject=subject,
        body=text,
        url_analysis_result=url_analysis,
    )
    score, reasons = apply_risk_policy(prediction["risk_score"], combined_text, url_analysis)
    # Respect the threshold selected on the validation partition. The heuristic
    # policy may additionally promote a high-confidence indicator to phishing.
    classification = "Phishing" if prediction["label"] == 1 or score >= 50 else "Legitimate"
    if not reasons:
        reasons = ["No strong phishing indicators were detected"]
    return {
        "input_type": input_type,
        "classification": classification,
        "risk_score": score,
        "reasons": reasons,
    }
