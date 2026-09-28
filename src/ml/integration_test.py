"""Backward-compatible command-line smoke test; no import-time execution."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(PROJECT_ROOT / "src" / "ml"), str(PROJECT_ROOT / "notebooks" / "url_analysis")]


def main() -> None:
    from myprojectai import analyze_single_email
    from predict import predict_from_analysis

    sender = "support@example.com"
    subject = "Urgent: Verify your account"
    body = "Your account is suspended. Verify your password at http://192.168.1.10/login"
    analysis = analyze_single_email(sender, body)
    result = predict_from_analysis(sender, subject, body, analysis)
    if result["prediction"] != "Phishing":
        raise AssertionError(f"Regression: obvious phishing was not flagged: {result}")
    print(result)


if __name__ == "__main__":
    main()
