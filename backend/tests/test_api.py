# هذا الملف يحتوي على اختبارات بسيطة لمسارات Backend.

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# يختبر أن مسار الصحة يعمل.
def test_health_check() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


# يختبر تحليل البريد الإلكتروني.
def test_analyze_email() -> None:
    response = client.post(
        "/api/v1/analyze/email",
        json={"subject": "Verify now", "body": "Click this link to verify your account."},
    )

    data = response.json()
    assert response.status_code == 200
    assert data["input_type"] == "email"
    assert 0 <= data["risk_score"] <= 100
    assert data["reasons"]


# يختبر تحليل الرابط.
def test_analyze_url() -> None:
    response = client.post("/api/v1/analyze/url", json={"url": "https://example.com/login"})

    data = response.json()
    assert response.status_code == 200
    assert data["input_type"] == "url"
    assert 0 <= data["risk_score"] <= 100


# يختبر تحليل النص.
def test_analyze_text() -> None:
    response = client.post(
        "/api/v1/analyze/text",
        json={"text": "Your account will be locked unless you act now."},
    )

    data = response.json()
    assert response.status_code == 200
    assert data["input_type"] == "text"
    assert 0 <= data["risk_score"] <= 100


# يختبر أخطاء التحقق عند إرسال بيانات غير صحيحة.
def test_validation_error() -> None:
    response = client.post("/api/v1/analyze/text", json={"text": ""})

    assert response.status_code == 422
    assert response.json()["detail"] == "Validation error"
    assert "errors" in response.json()


# يختبر رفض النص الذي يحتوي على مسافات فقط.
def test_validation_error_for_whitespace_text() -> None:
    response = client.post("/api/v1/analyze/text", json={"text": "     "})

    assert response.status_code == 422
    assert response.json()["detail"] == "Validation error"


# يختبر رفض جسم البريد الذي يحتوي على مسافات فقط.
def test_validation_error_for_whitespace_email_body() -> None:
    response = client.post("/api/v1/analyze/email", json={"subject": "Hello", "body": "   "})

    assert response.status_code == 422
    assert response.json()["detail"] == "Validation error"


# يختبر أن OpenAPI يحتوي فقط على مسارات المشروع الحالي.
def test_openapi_paths_match_project_api() -> None:
    schema = client.get("/openapi.json").json()

    assert schema["info"]["title"] == "Phishing Email Detector API"
    assert set(schema["paths"].keys()) == {
        "/api/v1/health",
        "/api/v1/analyze/email",
        "/api/v1/analyze/url",
        "/api/v1/analyze/text",
    }
