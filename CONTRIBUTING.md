# Contributing Guidelines

Welcome to the **Cyber Services Analytics Platform (CSAP)**! We are excited to have you contribute. This document outlines the standards, workflows, and quality practices expected from all developers (human and AI agents alike) working on this codebase.

---

## 1. Core Principles

- **Architecture over Speed**: We prioritize structured, modular, and extensible code. Take your time to build according to specifications.
- **Legibility over Complexity**: Write code that is easy to read, self-explanatory, and well-commented (in English).
- **Maintainability over Short Code**: Avoid overly concise "clever" solutions. Prefer descriptive variable names, clear separations of concern, and explicit typing.

---

## 2. Branching Strategy

We use a standard Git Flow branching model:

- `main`: Production-ready, stable code.
- `develop`: Primary integration branch for active development.
- Feature Branches: Created from `develop` and merged back via Pull Requests.
  - Naming convention: `feature/short-description` or `bugfix/issue-id`.

---

## 3. Pull Request Process

1. **Create Branch**: Check out a new branch from `develop`.
2. **Implement**: Add code and accompanying tests (Pytest for backend, Vitest/Playwright for frontend).
3. **Format & Lint**: Run quality checks locally.
4. **Draft PR**: Open a PR with the required structural sections:
   - Summary
   - Repository Structure
   - Documentation Created / Modified
   - Decisions Made
   - Assumptions
   - Future Recommendations
5. **Review**: Obtain approval from a tech lead before merging into `develop`.

---

## 4. Coding Standards & Tooling

To maintain a highly consistent codebase, we enforce strict linting and styling tools.

### Backend (Python 3.13)
- **Linter & Formatter**: [Ruff](https://github.com/astral-sh/ruff)
  - Ensure all python code follows PEP 8 standards.
- **Type Checking**: [MyPy](http://mypy-lang.org/)
  - Strict type hints are mandatory on all functions, classes, and variable declarations.
- **Testing**: [Pytest](https://docs.pytest.org/)
  - Write unit and integration tests under `backend/tests/`.

### Frontend (React / TypeScript)
- **Linter**: [ESLint](https://eslint.org/)
- **Formatter**: [Prettier](https://prettier.io/)
- **State Management**: Zustand
- **Query Handling**: TanStack Query (React Query)
- **Validation**: Zod (for forms and API data parsing)
- **Testing**: Vitest for component testing, Playwright for end-to-end integration flows.

---

## 5. Documentation Requirements

- **Language**: All code comments, Git commit messages, Pull Requests, and documentation must be in **English**.
- **Inline Comments**: Explain *why* something is done, not *what* it does (the code should make *what* it does clear).
- **Markdown**: Use semantic Markdown elements, tables, and code snippets when updating technical documentation.

---

Thank you for contributing to the long-term success of CSAP!
