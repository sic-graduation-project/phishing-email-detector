"""Integration layer for URL analysis, NLP preprocessing, and ML inference."""

from functools import lru_cache
from pathlib import Path
import sys
from typing import Any, Callable

from ..risk_policy import apply_email_risk_policy, score_text_analysis, score_url_analysis
from ..schemas.analysis import AnalysisResponse


PROJECT_ROOT = Path(__file__).resolve().parents[3]
ML_DIR = PROJECT_ROOT / "src" / "ml"
URL_ANALYSIS_DIR = PROJECT_ROOT / "src" / "url_analysis"

for module_dir in (ML_DIR, URL_ANALYSIS_DIR):
    module_path = str(module_dir)
    if module_path not in sys.path:
        sys.path.insert(0, module_path)


@lru_cache(maxsize=1)
def _load_pipeline() -> tuple[Callable[..., dict[str, Any]], Callable[..., dict[str, Any]]]:
    """Load the production bundle and URL analyzer once per API process."""
    from analyzer import analyze_single_email
    from predict import predict_from_analysis

    return analyze_single_email, predict_from_analysis


def ensure_ready() -> None:
    """Fail readiness when the URL analyzer or model bundle cannot load."""
    _load_pipeline()


def _response(
    *, input_type: str, score: float, reasons: list[str], model_flagged: bool = False
) -> AnalysisResponse:
    classification = "Phishing" if model_flagged or score >= 50 else "Legitimate"
    if classification == "Phishing":
        score = max(score, 50.0)
        if not reasons:
            reasons = ["Machine-learning model detected phishing language patterns"]
    elif not reasons:
        reasons = ["No strong phishing indicators were detected"]
    return AnalysisResponse(
        input_type=input_type,
        classification=classification,
        risk_score=round(score, 2),
        reasons=reasons,
    )


def analyze_email(sender: str | None, subject: str | None, body: str) -> AnalysisResponse:
    analyze_single_email, predict_from_analysis = _load_pipeline()
    clean_sender = sender or ""
    clean_subject = subject or ""
    combined_text = f"{clean_subject}\n{body}".strip()
    url_result = analyze_single_email(clean_sender, combined_text)
    prediction = predict_from_analysis(
        sender=clean_sender,
        subject=clean_subject,
        body=body,
        url_analysis_result=url_result,
    )
    score, reasons = apply_email_risk_policy(
        prediction["risk_score"], combined_text, url_result
    )
    return _response(
        input_type="email",
        score=score,
        reasons=reasons,
        model_flagged=prediction["label"] == 1,
    )


def analyze_url(url: str) -> AnalysisResponse:
    analyze_single_email, _ = _load_pipeline()
    url_result = analyze_single_email("", url)
    score, reasons = score_url_analysis(url_result)
    return _response(input_type="url", score=score, reasons=reasons)


def analyze_text(text: str) -> AnalysisResponse:
    analyze_single_email, _ = _load_pipeline()
    url_result = analyze_single_email("", text)
    score, reasons = score_text_analysis(text, url_result)
    return _response(input_type="text", score=score, reasons=reasons)
