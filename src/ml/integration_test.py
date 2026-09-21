import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(PROJECT_ROOT / "src" / "ml")
)

sys.path.insert(
    0,
    str(PROJECT_ROOT / "notebooks" / "url_analysis")
)

from predict import predict_from_analysis
from myprojectai import analyze_single_email


sender = "support@example.com"
subject = "Urgent: Verify your account"

body = """
Your account has been suspended.
Please verify your password immediately at:
http://192.168.1.10/login
"""

url_analysis_result = analyze_single_email(
    sender,
    body,
)

final_result = predict_from_analysis(
    sender=sender,
    subject=subject,
    body=body,
    url_analysis_result=url_analysis_result,
)

print("\n" + "=" * 60)
print("FINAL INTEGRATION RESULT")
print("=" * 60)

for key, value in final_result.items():
    print(f"{key}: {value}")