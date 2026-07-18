# Database Session Management

This folder contains SQLAlchemy session bindings, transactional decorators, and connection initializers.

## Purpose
- Establish the asynchronous and synchronous connection engines for PostgreSQL.
- Export dependency functions for FastAPI router dependency injection (e.g. `get_db_session`).
- Declare the SQLAlchemy declarative base metadata classes.
