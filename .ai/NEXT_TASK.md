# Next Development Task

This document explicitly defines the immediate next task to be completed by the next developer or AI agent.

---

## Task ID: CSAP-001
**Title**: Initialize Development Environment and Local Docker Containers

### Objectives
1. Configure `backend/pyproject.toml` or `backend/requirements.txt` with FastAPI, SQLAlchemy 2.x, Alembic, Pydantic v2, PostgreSQL, Redis, and Polars.
2. Configure `frontend/package.json` with React, Vite, TypeScript, Mantine, Zustand, TanStack Query, and Zod.
3. Configure `infra/docker-compose.yml` to orchestrate:
   - `postgres:16-alpine`
   - `redis:7-alpine`
   - `backend` (built from `backend/Dockerfile`)
   - `frontend` (built from `frontend/Dockerfile` in development mode)
4. Setup `infra/nginx/nginx.conf` to act as reverse proxy forwarding `/api` to the backend container and `/` to the frontend.
5. Verify that the Docker ecosystem boots cleanly via `docker compose up --build`.

### Verification Criteria
- [ ] Running `docker compose ps` shows all 4 containers in `Up` state.
- [ ] Navigating to `http://localhost:8000/docs` opens the FastAPI Swagger documentation.
- [ ] Navigating to `http://localhost:5173` or port configured via Nginx opens the Vite React starter page.
- [ ] Ruff and ESLint checks can be run inside their respective workspaces and pass with zero errors.
