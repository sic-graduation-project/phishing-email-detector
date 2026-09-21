"""Integration layer for URL analysis, NLP preprocessing, and ML inference."""

from functools import lru_cache
from pathlib import Path
import sys
from typing import Any, Callable

from app.schemas.analysis import AnalysisResponse


PROJECT_ROOT = Path(__file__).resolve().parents[3]
ML_DIR = PROJECT_ROOT / "src" / "ml"
URL_ANALYSIS_DIR = PROJECT_ROOT / "src" / "url_analysis"

# The team modules are scripts rather than installed packages. Register their
# directories in one place so the API reuses the original trained pipeline.
for module_dir in (ML_DIR, URL_ANALYSIS_DIR):
    module_path = str(module_dir)
    if module_path not in sys.path:
        sys.path.insert(0, module_path)


@lru_cache(maxsize=1)
def _load_pipeline() -> tuple[Callable[..., dict[str, Any]], Callable[..., dict[str, Any]]]:
    """Load model artifacts and the URL analyzer once per API process."""
    from analyzer import analyze_single_email
    from predict import predict_from_analysis

    return analyze_single_email, predict_from_analysis


def _reason_list(result: dict[str, Any]) -> list[str]:
    reasons = list(result.get("risk_indicators", []))
    if reasons:
        return reasons
    if result["prediction"] == "Phishing":
        return ["The trained model detected phishing-like language or structure"]
    return ["No strong phishing indicators were detected"]


def _analyze_with_email_model(
    *, input_type: str, sender: str, subject: str, body: str
) -> AnalysisResponse:
    analyze_single_email, predict_from_analysis = _load_pipeline()
    url_result = analyze_single_email(sender, body)
    result = predict_from_analysis(
        sender=sender,
        subject=subject,
        body=body,
        url_analysis_result=url_result,
    )
    return AnalysisResponse(
        input_type=input_type,
        classification=result["prediction"],
        risk_score=result["risk_score"],
        reasons=_reason_list(result),
    )


def analyze_email(sender: str | None, subject: str | None, body: str) -> AnalysisResponse:
    return _analyze_with_email_model(
        input_type="email",
        sender=sender or "",
        subject=subject or "",
        body=body,
    )


def analyze_url(url: str) -> AnalysisResponse:
    analyze_single_email, _ = _load_pipeline()
    url_result = analyze_single_email("", url)
    features = url_result["features"]

    # The trained model classifies complete emails; it must not receive a URL
    # as if it were an email body. Score standalone URLs only from URL-specific
    # features. The capped additive score is deliberately explainable and keeps
    # a clean HTTPS URL at zero risk.
    reasons = list(url_result["risk_indicators"])
    risk_score = (
        features["has_ip_url"] * 40
        + features["has_shortened_url"] * 30
        + features["has_at_in_url"] * 25
        + features["has_suspicious_url_word"] * 20
        + features["has_suspicious_characters"] * 15
        + features["has_http"] * 15
        + (15 if features["max_subdomain_count"] >= 3 else 0)
        + (15 if features["url_parameter_count"] >= 5 else 0)
    )
    if features["max_url_length"] >= 100:
        risk_score += 10
        reasons.append("URL is unusually long")
    risk_score = min(100, risk_score)

    return AnalysisResponse(
        input_type="url",
        classification="Phishing" if risk_score >= 50 else "Legitimate",
        risk_score=float(risk_score),
        reasons=reasons or ["No suspicious URL indicators were detected"],
    )


def analyze_text(text: str) -> AnalysisResponse:
    return _analyze_with_email_model(input_type="text", sender="", subject="", body=text)
