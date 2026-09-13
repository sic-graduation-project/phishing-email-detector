# هذا الملف يحتوي على إعدادات Backend القادمة من Environment Variables.

import os

from dotenv import load_dotenv

load_dotenv()


# تقرأ قائمة روابط Frontend المسموح بها أثناء التطوير.
def get_cors_origins() -> list[str]:
    origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
    return [origin.strip() for origin in origins.split(",") if origin.strip()]


APP_NAME = os.getenv("APP_NAME", "Phishing Email Detector API")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
APP_DESCRIPTION = """
Backend API for the Nexus team graduation project.

The current analysis logic is a clear mock placeholder until the final NLP,
URL/Sender Analysis, and Machine Learning components are connected.
"""
