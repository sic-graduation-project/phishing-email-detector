# هذا الملف يتأكد أن Swagger static يخص مشروع Phishing فقط.

from pathlib import Path

from scripts.generate_static_swagger import generate_static_swagger


BACKEND_DIR = Path(__file__).resolve().parents[1]
STATIC_SWAGGER_FILE = BACKEND_DIR / "swagger-static" / "index.html"


# يولد Swagger static ويتأكد من عدم وجود بيانات مشروع آخر.
def test_static_swagger_matches_phishing_project() -> None:
    generate_static_swagger()

    content = STATIC_SWAGGER_FILE.read_text(encoding="utf-8")

    forbidden_terms = ["Waraqa", "ProcessPaperRequest", "ChatRequest", "/internal/v1/"]
    required_terms = [
        "Phishing Email Detector",
        "/api/v1/health",
        "/api/v1/analyze/email",
        "/api/v1/analyze/url",
        "/api/v1/analyze/text",
        "supportedSubmitMethods: []",
    ]

    for term in forbidden_terms:
        assert term not in content

    for term in required_terms:
        assert term in content
