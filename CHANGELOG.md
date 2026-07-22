# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-03-05

### Added
- **Frontend Dependencies**: Added `zustand`, `@tanstack/react-query`, and `zod` to the React TS project.
- **Testing Dependencies**: Added `@playwright/test` for browser and E2E integration testing to `frontend/package.json`.
- **Docker Compose Ports**: Exposed FastAPI Backend directly on port 8000 in `infra/docker-compose.yml`.

### Fixed
- **TypeScript Compilation**: Fixed multiple TS compilation errors including missing type definitions, unused imports, implicit `any` bindings, and environment variables declarations in Vite.
- **Python Formatting**: Resolved line-length formatting issues in backend tests via Ruff.
- **Frontend Formatting**: Ran prettier and resolved layout/formatting issues in frontend files.

## [0.1.0] - 2026-03-05

### Added
- **Repository Structure**: Created a professional and scalable workspace containing `backend/`, `frontend/`, `infra/`, `docs/`, and `.ai/` directories.
- **Root Files**: Initialized base repository configurations, including a comprehensive `.gitignore`, `LICENSE` (MIT), `CHANGELOG.md`, and `CONTRIBUTING.md`.
- **Global Documentation**: Added root `README.md` introducing the Cyber Services Analytics Platform (CSAP), its business objectives, core architecture, and complete technology stack.
- **AI Agent Context**: Initialized the `.ai/` directory containing detailed instructional metadata (`PROJECT.md`, `ARCHITECTURE.md`, `STACK.md`, `RULES.md`, `DOMAIN.md`, `CONSTITUTION.md`, `IMPLEMENTATION_PLAN.md`, `CURRENT_STATE.md`, `NEXT_TASK.md`, `REVIEW_CHECKLIST.md`, and a prompts guide).
- **Technical Docs**: Established `docs/` subdirectories for `architecture`, `api`, `database`, and `runbooks`, each populated with professional instructional templates.
- **Folder Scaffolding**: Added modular directory layouts with descriptive `README.md` guidelines for the React/TypeScript frontend, FastAPI/Python backend, and Docker/Nginx infrastructure.
