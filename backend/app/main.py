# هذا الملف ينشئ تطبيق FastAPI ويربط المسارات والإعدادات.

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import APP_DESCRIPTION, APP_NAME, APP_VERSION, get_cors_origins
from app.routes.analysis import router as analysis_router
from app.routes.health import router as health_router

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
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
# يرجع أخطاء التحقق بشكل بسيط ومفهوم.
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder({"detail": "Validation error", "errors": exc.errors()}),
    )


@app.exception_handler(Exception)
# يرجع خطأ عام بدون كشف تفاصيل حساسة.
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


app.include_router(health_router)
app.include_router(analysis_router)
