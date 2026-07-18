# API Routers and Controllers

This directory contains the FastAPI routing layer, organized by resource boundaries.

## Purpose
- Map HTTP endpoints to appropriate Python controller/service functions.
- Enforce API contract constraints using Pydantic validation schemas.
- Route request handling based on API versioning (e.g., `/v1/`).

## Architecture Rule
- **No business logic or SQL queries should reside directly within the routers.**
- Routers should parse incoming requests, execute authorization guards, call services from `app/services/`, and return serialized Pydantic responses.
