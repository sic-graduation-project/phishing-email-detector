# هذا الملف يحتوي على مسارات API الخاصة بتحليل البريد والرابط والنص.

from fastapi import APIRouter, status

from app.schemas.analysis import (
    AnalysisResponse,
    EmailAnalysisRequest,
    ErrorResponse,
    TextAnalysisRequest,
    URLAnalysisRequest,
    ValidationErrorResponse,
)
from app.services.analysis_service import analyze_email, analyze_text, analyze_url

router = APIRouter(prefix="/api/v1/analyze")

ERROR_RESPONSES = {
    422: {"model": ValidationErrorResponse, "description": "Validation error"},
    500: {"model": ErrorResponse, "description": "Internal server error"},
}


@router.post(
    "/email",
    response_model=AnalysisResponse,
    status_code=status.HTTP_200_OK,
    tags=["Email Analysis"],
    summary="Analyze an email",
    description="Analyzes an email using URL/sender features, NLP, and the trained ML model.",
    responses=ERROR_RESPONSES,
)
# يستقبل البريد الإلكتروني ويمرره إلى طبقة الخدمات.
def analyze_email_endpoint(payload: EmailAnalysisRequest) -> AnalysisResponse:
    return analyze_email(sender=payload.sender, subject=payload.subject, body=payload.body)


@router.post(
    "/url",
    response_model=AnalysisResponse,
    status_code=status.HTTP_200_OK,
    tags=["URL Analysis"],
    summary="Analyze a URL",
    description="Analyzes a single URL using explainable URL-specific risk indicators.",
    responses=ERROR_RESPONSES,
)
# يستقبل الرابط ويمرره إلى طبقة الخدمات.
def analyze_url_endpoint(payload: URLAnalysisRequest) -> AnalysisResponse:
    return analyze_url(url=str(payload.url))


@router.post(
    "/text",
    response_model=AnalysisResponse,
    status_code=status.HTTP_200_OK,
    tags=["Text Analysis"],
    summary="Analyze plain text",
    description="Analyzes plain text using NLP and the trained ML model.",
    responses=ERROR_RESPONSES,
)
# يستقبل النص ويمرره إلى طبقة الخدمات.
def analyze_text_endpoint(payload: TextAnalysisRequest) -> AnalysisResponse:
    return analyze_text(text=payload.text)
