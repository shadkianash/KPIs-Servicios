# Infrastructure Configurations

This folder manages configuration layouts, files, and templates for containerizing and running CSAP.

---

## 1. Subdirectory Contents

- `nginx/`:
  - `nginx.conf`: Routing configs managing reverse proxies, forwarding `/api` paths to backend FastAPI, and other requests to static React builds.
  - `logs/`: Directory mapping runtime request logs.
- `docker-compose.yml`: Multi-service compose orchestrator initializing the postgres, redis, backend, and frontend containers synchronously.

---

## 2. Docker Best Practices
- Keep image layers lean utilizing Alpine base images where possible.
- Run production images as non-root users to satisfy cybersecurity compliance policies.
- Ensure state persistence (Postgres, Redis caches, and ingested CSV store files) are strictly bound to isolated Docker volumes mapped outside the containers.
