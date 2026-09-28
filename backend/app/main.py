import os
from typing import Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, HttpUrl, field_validator

from .analysis_service import analyze, ensure_ready


def _cors_origins() -> list[str]:
    configured = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    return [origin.strip() for origin in configured.split(",") if origin.strip()]

app = FastAPI(title="Nexus Phishing Detector API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class EmailRequest(BaseModel):
    subject: str | None = Field(default=None, max_length=200)
    body: str = Field(min_length=1, max_length=5000)

    @field_validator("body")
    @classmethod
    def body_is_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Email body cannot be blank")
        return value.strip()


class TextRequest(BaseModel):
    text: str = Field(min_length=1, max_length=5000)

    @field_validator("text")
    @classmethod
    def text_is_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Text cannot be blank")
        return value.strip()


class URLRequest(BaseModel):
    url: HttpUrl


class AnalysisResponse(BaseModel):
    input_type: Literal["email", "url", "text"]
    classification: Literal["Phishing", "Legitimate"]
    risk_score: float = Field(ge=0, le=100)
    reasons: list[str]


@app.get("/api/v1/health")
def health() -> dict[str, str]:
    ensure_ready()
    return {"status": "ok", "service": "Nexus Phishing Detector API"}


@app.post("/api/v1/analyze/email", response_model=AnalysisResponse)
def analyze_email(payload: EmailRequest) -> dict:
    return analyze("email", payload.body, payload.subject or "")


@app.post("/api/v1/analyze/text", response_model=AnalysisResponse)
def analyze_text(payload: TextRequest) -> dict:
    return analyze("text", payload.text)


@app.post("/api/v1/analyze/url", response_model=AnalysisResponse)
def analyze_url(payload: URLRequest) -> dict:
    return analyze("url", str(payload.url))
