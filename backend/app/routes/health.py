# هذا الملف يحتوي على مسار فحص حالة Backend.

from fastapi import APIRouter, status

from ..core.config import APP_NAME, APP_VERSION
from ..schemas.analysis import HealthResponse
from ..services.analysis_service import ensure_ready

router = APIRouter(prefix="/api/v1", tags=["System"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Check backend health",
    description="Returns a simple response to confirm that the backend is running.",
)
# يرجع حالة تشغيل Backend.
def health_check() -> HealthResponse:
    ensure_ready()
    return HealthResponse(status="ok", service=APP_NAME, version=APP_VERSION)

