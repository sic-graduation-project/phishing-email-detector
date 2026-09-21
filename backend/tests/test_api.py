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
        json={
            "sender": "Support <support@example.com>",
            "subject": "Verify now",
            "body": "Click this link to verify your account.",
        },
    )

    data = response.json()
    assert response.status_code == 200
    assert data["input_type"] == "email"
    assert 0 <= data["risk_score"] <= 100
    assert data["reasons"]
    assert not any("Mock" in reason for reason in data["reasons"])


# يختبر تحليل الرابط.
def test_analyze_url() -> None:
    response = client.post("/api/v1/analyze/url", json={"url": "https://devanas.ly"})

    data = response.json()
    assert response.status_code == 200
    assert data["input_type"] == "url"
    assert data["classification"] == "Legitimate"
    assert data["risk_score"] == 0
    assert data["reasons"] == ["No suspicious URL indicators were detected"]


def test_analyze_suspicious_url() -> None:
    response = client.post(
        "/api/v1/analyze/url",
        json={"url": "http://192.168.1.10/login?verify=1"},
    )

    data = response.json()
    assert response.status_code == 200
    assert data["classification"] == "Phishing"
    assert data["risk_score"] >= 50
    assert "URL contains an IP address" in data["reasons"]
    assert "URL uses HTTP instead of HTTPS" in data["reasons"]


def test_analyze_shortened_suspicious_url() -> None:
    response = client.post(
        "/api/v1/analyze/url",
        json={"url": "https://bit.ly/verify-account"},
    )

    data = response.json()
    assert response.status_code == 200
    assert data["classification"] == "Phishing"
    assert data["risk_score"] == 50
    assert "URL uses a shortened URL service" in data["reasons"]


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
