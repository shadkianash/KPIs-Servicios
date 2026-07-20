import logging
import sys

from app.config.settings import get_settings
from app.core.context import get_correlation_id, get_request_id

# Load settings singleton
settings = get_settings()


class StructuredFormatter(logging.Formatter):
    """Custom logging Formatter that injects request-scoped trace IDs dynamically."""

    def format(self, record: logging.LogRecord) -> str:
        # Fetch request_id and correlation_id safely from async ContextVars
        record.request_id = get_request_id() or "N/A"
        record.correlation_id = get_correlation_id() or "N/A"
        return super().format(record)


def setup_logging() -> None:
    """Configure centralized structured console logging."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    root_logger = logging.getLogger()
    # Remove existing handlers
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    console_handler = logging.StreamHandler(sys.stdout)

    # Custom format including Request-ID and Correlation-ID
    log_format = (
        "%(asctime)s [%(levelname)s] "
        "[ReqId: %(request_id)s] [CorrId: %(correlation_id)s] "
        "%(name)s: %(message)s"
    )

    formatter = StructuredFormatter(log_format)
    console_handler.setFormatter(formatter)

    root_logger.addHandler(console_handler)
    root_logger.setLevel(log_level)

    # Clean up and suppress verbose third party logging
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
