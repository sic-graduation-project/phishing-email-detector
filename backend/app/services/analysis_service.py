# هذا الملف يحتوي على منطق تحليل مؤقت حتى يتم ربط نموذج تعلم الآلة النهائي.

from app.schemas.analysis import AnalysisResponse


MOCK_REASONS = [
    "Mock indicator: final ML model is not connected yet",
    "Mock indicator: temporary backend response for API integration",
]


# تنشئ نتيجة مؤقتة موحدة لكل أنواع التحليل.
def _build_mock_response(input_type: str, risk_score: int) -> AnalysisResponse:
    classification = "Phishing" if risk_score >= 50 else "Legitimate"
    return AnalysisResponse(
        input_type=input_type,
        classification=classification,
        risk_score=risk_score,
        reasons=MOCK_REASONS,
    )


# تحلل بيانات البريد الإلكتروني وترجع النتيجة.
def analyze_email(subject: str | None, body: str) -> AnalysisResponse:
    return _build_mock_response(input_type="email", risk_score=85)


# تحلل الرابط وترجع النتيجة.
def analyze_url(url: str) -> AnalysisResponse:
    return _build_mock_response(input_type="url", risk_score=75)


# تحلل النص العادي وترجع النتيجة.
def analyze_text(text: str) -> AnalysisResponse:
    return _build_mock_response(input_type="text", risk_score=65)

