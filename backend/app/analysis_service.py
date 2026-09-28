"""Integration of URL features, the email model, and type-specific policies."""
from __future__ import annotations
import sys
from functools import lru_cache
from pathlib import Path
from .risk_policy import apply_email_risk_policy, score_text_analysis, score_url_analysis

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ML_DIR = PROJECT_ROOT / "src" / "ml"
URL_DIR = PROJECT_ROOT / "notebooks" / "url_analysis"
for path in (ML_DIR, URL_DIR):
    if str(path) not in sys.path: sys.path.insert(0, str(path))

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
    if input_type == "url":
        score, reasons = score_url_analysis(url_analysis)
        model_flagged = False
    elif input_type == "text":
        score, reasons = score_text_analysis(text, url_analysis)
        model_flagged = False
    else:
        prediction = predict_from_analysis(sender=sender, subject=subject, body=text, url_analysis_result=url_analysis)
        score, reasons = apply_email_risk_policy(prediction["risk_score"], combined_text, url_analysis)
        model_flagged = prediction["label"] == 1
    classification = "Phishing" if model_flagged or score >= 50 else "Legitimate"
    if classification == "Phishing":
        score = max(score, 50.0)
        if not reasons: reasons = ["Machine-learning model detected phishing language patterns"]
    elif not reasons:
        reasons = ["No strong phishing indicators were detected"]
    return {"input_type": input_type, "classification": classification, "risk_score": round(score, 2), "reasons": reasons}
