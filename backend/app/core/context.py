from contextvars import ContextVar

# Safe request-scoped trace context variables
request_id_ctx_var: ContextVar[str | None] = ContextVar("request_id", default=None)
correlation_id_ctx_var: ContextVar[str | None] = ContextVar(
    "correlation_id", default=None
)


def get_request_id() -> str:
    """Retrieve current request ID, defaulting to an empty string."""
    return request_id_ctx_var.get() or ""


def get_correlation_id() -> str:
    """Retrieve current correlation ID, defaulting to an empty string."""
    return correlation_id_ctx_var.get() or ""
