# Technology Stack Specification

This document defines the strict, approved technology stack for the CSAP repository. No alternative libraries or packages should be proposed.

---

## 1. Backend

| Technology / Library | Version | Purpose |
| :--- | :--- | :--- |
| **Python** | 3.13 | Core programming language |
| **FastAPI** | Latest (0.115+) | REST API Framework |
| **SQLAlchemy** | 2.x | Database ORM |
| **Alembic** | Latest (1.13+) | Database migrations management |
| **Pydantic** | v2 | Data validation and settings |
| **PostgreSQL** | Latest (16+) | Primary transactional & analytical store |
| **Redis** | Latest (7+) | Cache and rate-limiting store |
| **Polars** | Latest (1.x+) | Fast dataframe library for high-speed CSV parsing and KPI calculations |
| **Pytest** | Latest | Testing framework |

---

## 2. Frontend

| Technology / Library | Version | Purpose |
| :--- | :--- | :--- |
| **React** | Latest (18/19) | Frontend library |
| **TypeScript** | Latest (5.x) | Static typing |
| **Vite** | Latest (5/6) | Build tool and dev server |
| **Mantine** | Latest (7.x) | Core component library and design system |
| **AG Grid Enterprise** | Latest | High-performance interactive data tables (license acquired later) |
| **Apache ECharts** | Latest | Interactive charts, dashboards, and visual analytics |
| **TanStack Query** | Latest (v5) | Server-state management and caching |
| **Zustand** | Latest | Lightweight global client state management |
| **React Hook Form** | Latest | Form handling and validation binding |
| **Zod** | Latest (v3) | Schema-based validation for forms and API responses |
| **Vitest** | Latest | Frontend unit and component testing |
| **Playwright** | Latest | E2E functional browser integration testing |

---

## 3. Infrastructure

- **Docker**: Used to containerize frontend, backend, database, and cache services.
- **Docker Compose**: Orchestrates multi-container development and staging setups.
- **Nginx**: Serves as a reverse proxy, load balancer, and static file server for frontend builds.

---

## 4. Code Quality & Formatting

The following tools are strictly required. Code that does not comply with these configurations will fail CI/CD:
- **Ruff**: Super-fast Python linter and formatter.
- **MyPy**: Strict static type checking for Python.
- **ESLint**: Standard JS/TS linter.
- **Prettier**: Opinionated code formatter for TS/TSX/CSS/JSON.
