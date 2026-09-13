# هذا الملف يحتوي على نماذج البيانات المستخدمة في Requests وResponses.

from typing import Any, Literal

from pydantic import BaseModel, Field, HttpUrl, field_validator


class ErrorResponse(BaseModel):
    detail: str = Field(..., examples=["Request body is invalid."])


class ValidationErrorResponse(BaseModel):
    detail: str = Field(..., examples=["Validation error"])
    errors: list[dict[str, Any]] = Field(
        ...,
        examples=[
            [
                {
                    "type": "string_too_short",
                    "loc": ["body", "text"],
                    "msg": "String should have at least 1 character",
                    "input": "",
                }
            ]
        ],
    )


class HealthResponse(BaseModel):
    status: str = Field(..., examples=["ok"])
    service: str = Field(..., examples=["Phishing Email Detector API"])
    version: str = Field(..., examples=["1.0.0"])


class EmailAnalysisRequest(BaseModel):
    subject: str | None = Field(
        default=None,
        examples=["Account verification required"],
        description="Optional email subject.",
    )
    body: str = Field(
        ...,
        min_length=1,
        examples=["Please verify your account by clicking the link."],
        description="Email body text. It cannot be empty.",
    )

    # يرفض نص البريد إذا كان فارغًا بعد إزالة المسافات.
    @field_validator("body")
    @classmethod
    def validate_body(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Email body cannot be empty.")
        return value

    # ينظف عنوان البريد الاختياري من المسافات الزائدة.
    @field_validator("subject")
    @classmethod
    def clean_subject(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None


class URLAnalysisRequest(BaseModel):
    url: HttpUrl = Field(
        ...,
        examples=["https://example.com/login"],
        description="A single URL to analyze.",
    )


class TextAnalysisRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        examples=["Your account will be locked unless you verify it now."],
        description="Plain text to analyze. It cannot be empty.",
    )

    # يرفض النص إذا كان فارغًا بعد إزالة المسافات.
    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Text cannot be empty.")
        return value


class AnalysisResponse(BaseModel):
    input_type: Literal["email", "url", "text"] = Field(..., examples=["email"])
    classification: Literal["Phishing", "Legitimate"] = Field(..., examples=["Phishing"])
    risk_score: int = Field(..., ge=0, le=100, examples=[85])
    reasons: list[str] = Field(
        ...,
        examples=[["Mock indicator: suspicious language placeholder"]],
    )
