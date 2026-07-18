import logging
import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.context import correlation_id_ctx_var, request_id_ctx_var

logger = logging.getLogger(__name__)


class TraceAndTimingMiddleware(BaseHTTPMiddleware):
    """Middleware capturing Request-ID and Correlation-ID."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        start_time = time.perf_counter()

        # Capture or generate Request ID
        req_id_header = request.headers.get("X-Request-ID")
        req_id = req_id_header if req_id_header else str(uuid.uuid4())

        # Capture or generate Correlation ID
        corr_id_header = request.headers.get("X-Correlation-ID")
        corr_id = corr_id_header if corr_id_header else req_id

        # Bind tracing ContextVars for the duration of the request task
        req_token = request_id_ctx_var.set(req_id)
        corr_token = correlation_id_ctx_var.set(corr_id)

        try:
            response = await call_next(request)
        except Exception:
            # Clean context vars even in exception blocks
            request_id_ctx_var.reset(req_token)
            correlation_id_ctx_var.reset(corr_token)
            raise

        # Calculate processing duration
        duration = time.perf_counter() - start_time
        logger.info(
            f"Processed: {request.method} {request.url.path} "
            f"-> Status {response.status_code} in {duration:.4f}s"
        )

        # Attach identifiers to the response headers
        response.headers["X-Request-ID"] = req_id
        response.headers["X-Correlation-ID"] = corr_id

        # Clean tracing tokens
        request_id_ctx_var.reset(req_token)
        correlation_id_ctx_var.reset(corr_token)

        return response
