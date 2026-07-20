from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def get_health() -> dict[str, str]:
    """Exposes versioned API health state."""
    return {
        "status": "ok",
        "service": "KPIs Servicios API",
        "version": "0.1.0",
    }
