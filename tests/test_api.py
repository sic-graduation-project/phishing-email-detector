from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_obvious_phishing_text_is_flagged():
    response = client.post(
        "/api/v1/analyze/text",
        json={
            "text": "URGENT: Your account is suspended. Verify your password now at "
            "http://192.168.1.10/login"
        },
    )
    assert response.status_code == 200
    result = response.json()
    assert result["classification"] == "Phishing"
    assert result["risk_score"] >= 80
    assert result["reasons"]


def test_suspicious_url_is_flagged():
    response = client.post(
        "/api/v1/analyze/url",
        json={"url": "https://paypal-login-security.example.com/verify?account=1"},
    )
    assert response.status_code == 200
    assert response.json()["classification"] == "Phishing"


def test_benign_text_stays_legitimate():
    response = client.post(
        "/api/v1/analyze/text",
        json={"text": "Hello, the project meeting is tomorrow at ten."},
    )
    assert response.status_code == 200
    assert response.json()["classification"] == "Legitimate"


def test_blank_text_and_non_http_url_are_rejected():
    assert client.post("/api/v1/analyze/text", json={"text": "   "}).status_code == 422
    assert client.post("/api/v1/analyze/url", json={"url": "javascript:alert(1)"}).status_code == 422
