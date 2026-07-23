from fastapi import APIRouter

from app.api.v1.analytics.routers.drilldown import router as drilldown_router
from app.api.v1.analytics.routers.health import router as analytics_health_router
from app.api.v1.analytics.routers.kpi_executions import router as kpi_executions_router
from app.api.v1.analytics.routers.metadata import router as metadata_router
from app.api.v1.analytics.routers.snapshots import router as snapshots_router
from app.api.v1.health import router as health_router

v1_router = APIRouter()

# Include resource-scoped routers under /v1 with correct tags and stable URL structures
v1_router.include_router(health_router, tags=["Health"])
v1_router.include_router(analytics_health_router, tags=["Analytics Health"])
v1_router.include_router(metadata_router, tags=["Metadata"])
v1_router.include_router(kpi_executions_router, tags=["KPI Executions"])
v1_router.include_router(snapshots_router, tags=["KPI Snapshots"])
v1_router.include_router(drilldown_router, tags=["Drilldown"])
