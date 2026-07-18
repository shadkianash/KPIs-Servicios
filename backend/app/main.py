import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.v1 import v1_router
from app.config.settings import get_settings
from app.core.logging import setup_logging
from app.exceptions.handlers import register_exception_handlers
from app.middleware.trace import TraceAndTimingMiddleware

# Initialize centralized structured logs
setup_logging()
logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    """App startup and shutdown lifecycle event hooks."""
    logger.info(
        f"Starting service: {settings.PROJECT_NAME} in environment: {settings.ENV}"
    )
    yield
    logger.info(f"Stopping service: {settings.PROJECT_NAME}")


app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# 1. Trusted Host Security Middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS,
)

# 2. CORS configurations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Custom request tracking and execution timer middleware
app.add_middleware(TraceAndTimingMiddleware)

# 4. GZip Response Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Register centralized exception handlers
register_exception_handlers(app)

# Include v1 API Routers
app.include_router(v1_router, prefix=settings.API_V1_STR)


# Backward-compatible endpoints matching Phase 0.2
@app.get("/health")
@app.get("/api/health")
def health_check() -> dict[str, str]:
    """Exposes simple healthcheck state."""
    return {
        "status": "ok",
        "service": "KPIs Servicios API",
        "version": "0.1.0",
    }
