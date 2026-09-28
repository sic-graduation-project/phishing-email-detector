"""FastAPI application entry point."""

import os

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .core.config import APP_DESCRIPTION, APP_NAME, APP_VERSION, get_cors_origins
from .rate_limit import SlidingWindowLimiter
from .routes.analysis import router as analysis_router
from .routes.health import router as health_router

tags_metadata = [
    {"name": "System", "description": "Backend status and health endpoints."},
    {"name": "Email Analysis", "description": "Analyze email subject and body."},
    {"name": "URL Analysis", "description": "Analyze a single URL."},
    {"name": "Text Analysis", "description": "Analyze plain text content."},
]

app = FastAPI(
    title=APP_NAME,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

_analysis_limiter = SlidingWindowLimiter(
    int(os.getenv("ANALYSIS_RATE_LIMIT_PER_MINUTE", "60"))
)


@app.middleware("http")
async def limit_analysis_requests(request: Request, call_next):
    """Apply a per-client sliding-window limit to public analysis routes."""
    if request.url.path.startswith("/api/v1/analyze/"):
        client = request.client.host if request.client else "unknown"
        if not _analysis_limiter.allow(client):
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many analysis requests. Please try again shortly."},
                headers={"Retry-After": "60"},
            )
    return await call_next(request)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder({"detail": "Validation error", "errors": exc.errors()}),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


app.include_router(health_router)
app.include_router(analysis_router)
