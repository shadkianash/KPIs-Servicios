# Coding Rules & Quality Standards

To maintain exceptional code quality and facilitate autonomous assistance from AI agents, the following rules are strictly enforced.

---

## 1. General Rules

- **English Only**: All variable names, class names, file names, comments, docstrings, commits, and logs must be in **English**.
- **No Inline Disables Without Comments**: Never disable a linter rule (e.g., `# noqa` or `/* eslint-disable */`) without including a detailed comment explaining *why* it is necessary.
- **Strict Typing**: No using `Any` in Python, or `any` in TypeScript, unless absolutely unavoidable (and documented).

---

## 2. Python Coding Rules (Backend)

- **Use Ruff**: All formatting must follow Ruff rules.
- **Type Annotations**: All functions must have complete type signatures for inputs and return values.
  ```python
  # Good
  def calculate_sla_compliance(completed: int, total: int) -> float:
      if total == 0:
          return 0.0
      return (completed / total) * 100.0
  ```
- **Pydantic Models**: Always use Pydantic v2 schemas for request validation and response serialization. Ensure fields are annotated with descriptive `Field` attributes.
- **Async Handling**: Write asynchronous FastAPI endpoints using `async def` only when dealing with non-blocking I/O operations. Use synchronous functions when interacting with synchronous database engines.

---

## 3. TypeScript & React Rules (Frontend)

- **Functional Components**: Use React functional components with explicit TypeScript typings (`React.FC` or return type `JSX.Element`).
- **Strict Forms**: Always bind React Hook Form with Zod validation schemas. Do not parse raw object payloads.
- **State Partitioning**: Keep global client state (Zustand) extremely clean. Do not store server data in Zustand; use TanStack Query instead.
- **ECharts Wrapper**: Wrap Apache ECharts inside dedicated React components to handle resize, theme changes, and clean lifecycle destruction.

---

## 4. DB & Query Rules
- **No Raw SQL**: Always use SQLAlchemy 2.x unified Select query patterns.
- **Eager Loading**: Prevent `N+1` select problems by using explicit `joinedload` or `selectinload` for relationships.
- **Migrations**: Every DB schema change must have a corresponding, well-labeled Alembic migration file.

---

## 5. Polars Best Practices
- Avoid converting Polars DataFrames to Pandas.
- Use Polars lazy execution API (`lazy()`) and finalize with `.collect()` to maximize multithreading capability.
- Use explicit column typing when loading CSV datasets.
