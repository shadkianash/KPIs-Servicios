from fastapi import APIRouter

from app.api.v1.analytics.schemas.envelope import ResponseEnvelope

router = APIRouter()


@router.get(
    "/analytics/health",
    response_model=ResponseEnvelope[dict[str, str]],
    summary="Analytics engine status",
    description="Returns the status of the KPI analytics calculation and engine.",
)
async def get_analytics_health() -> ResponseEnvelope[dict[str, str]]:
    """Exposes health status of the Analytics system."""
    return ResponseEnvelope(
        success=True,
        data={
            "status": "active",
            "engine_version": "1.0.0",
            "calculation_version": "1.0.0",
        },
    )
