# AI Code Review Checklist

This checklist must be executed by any AI agent prior to submitting a Pull Request.

---

## 1. Architectural Integrity
- [ ] Ensure that code additions do not blend business calculations directly into FastAPI routers.
- [ ] Confirm that database queries are abstracted behind service/repository functions.
- [ ] Verify that no third-party libraries have been added to the codebase unless they are explicitly permitted in `.ai/STACK.md`.
- [ ] Ensure the Data Loader implementation retains a separate interface, ensuring that the main system calculations do not couple with the Archer CSV file structure.

## 2. Quality & Validation
- [ ] All Python functions have 100% complete type signatures (no `Any`).
- [ ] All TypeScript interfaces are fully typed (no `any`).
- [ ] No temporary debugging files, print statements, or `console.log` statements are left in production paths.
- [ ] Every API response is strictly parsed/validated via Pydantic (backend) and Zod (frontend).

## 3. Formatting & Standards
- [ ] Python: Run `ruff check .` and `ruff format . --check` to ensure there are no compliance issues.
- [ ] Python: Run `mypy .` to verify no static typing errors exist.
- [ ] Frontend: Run `npm run lint` and `npm run format:check` (or respective bun/yarn commands).
- [ ] All new files contain headers and are thoroughly documented in English.

## 4. Documentation
- [ ] If any domain concept was altered, the change is reflected in `.ai/DOMAIN.md` and `docs/`.
- [ ] The `CHANGELOG.md` is updated following standard SemVer and Keep a Changelog practices.
