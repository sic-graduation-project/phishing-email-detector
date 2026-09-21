# هذا الملف يحتوي على إعدادات Backend القادمة من Environment Variables.

import os

from dotenv import load_dotenv

load_dotenv()


# تقرأ قائمة روابط Frontend المسموح بها أثناء التطوير.
def get_cors_origins() -> list[str]:
    origins = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    )
    return [origin.strip() for origin in origins.split(",") if origin.strip()]


APP_NAME = os.getenv("APP_NAME", "Phishing Email Detector API")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
APP_DESCRIPTION = """
Backend API for the Nexus team graduation project.

The API combines NLP, URL/sender analysis, and the trained machine-learning
model to classify email, URL, and text input.
"""
