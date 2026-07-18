# Stage 1: Build the virtual environment
FROM python:3.13-slim AS builder

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy dependency configuration files and lock files
COPY pyproject.toml uv.lock ./

# Install dependencies into the default .venv directory
RUN uv sync --no-install-project --no-dev

# Stage 2: Production-ready runtime
FROM python:3.13-slim AS runner

# Create non-root system user
RUN groupadd -g 10001 appuser && \
    useradd -u 10001 -g appuser -d /app -s /sbin/nologin appuser

# Set working directory
WORKDIR /app

# Copy virtual environment and source code
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv
COPY --chown=appuser:appuser app /app/app
COPY --chown=appuser:appuser migrations /app/migrations
COPY --chown=appuser:appuser alembic.ini /app/alembic.ini

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Use non-root user
USER appuser

# Expose FastAPI port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=3)" || exit 1

# Start the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
