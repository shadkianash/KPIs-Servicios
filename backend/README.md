# FastAPI Backend Workspace

This folder hosts the complete FastAPI backend codebase. The application is structured using modular architecture separating the api routes, data ingestion engines, database models, and service classes.

---

## 1. Directory Structure

```text
backend/
├── app/
│   ├── api/          # API routers and endpoints separated by version
│   ├── core/         # Core config settings, security, and logging
│   ├── db/           # Session management and base DB model configurations
│   ├── models/       # SQLAlchemy relational database models
│   ├── schemas/      # Pydantic v2 schemas for request and response validation
│   ├── services/     # Pure business logic services, Polars calculation engine
│   └── loaders/      # Ingestion loader implementations (Archer CSV loader)
├── migrations/       # Alembic migrations history
└── tests/            # Pytest test suite (unit and integration tests)
```

---

## 2. Coding Guidelines
- **Python Version**: Strict Python 3.13.
- **Type Annotations**: Mandatory across all modules.
- **Code Quality**: Ensure Ruff linter and MyPy run cleanly prior to proposing any pull requests.
- **DB Operations**: All transactional database updates must occur within bounded SQLAlchemy sessions, utilizing standard Repository patterns inside `app/services/` or dedicated modules.
