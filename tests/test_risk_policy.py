from backend.app.risk_policy import apply_risk_policy


def analysis(**features):
    indicators = [name for name, value in features.items() if value]
    return {"features": features, "risk_indicators": indicators, "indicator_count": len(indicators)}


def test_ip_login_url_cannot_be_marked_safe():
    score, reasons = apply_risk_policy(
        26.34,
        "URGENT: account suspended. Verify your password at http://192.168.1.10/login",
        analysis(has_ip_url=1, has_http=1, has_suspicious_url_word=1),
    )
    assert score >= 82
    assert reasons


def test_social_engineering_text_cannot_be_marked_safe():
    score, reasons = apply_risk_policy(
        10,
        "Urgent: your account is locked. Verify your password immediately.",
        analysis(),
    )
    assert score >= 72
    assert any("urgent language" in reason for reason in reasons)


def test_benign_text_keeps_model_score():
    score, reasons = apply_risk_policy(8.85, "Hello, the meeting is tomorrow.", analysis())
    assert score == 8.85
    assert reasons == []
