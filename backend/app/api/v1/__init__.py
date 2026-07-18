from fastapi import APIRouter

from app.api.v1.health import router as health_router

v1_router = APIRouter()

# Include resource-scoped routers under /v1
v1_router.include_router(health_router, tags=["Health"])
