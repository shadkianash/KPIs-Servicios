# CSAP Frontend Architecture Manual

This document details the architectural layout, components hierarchy, routing rules, and state partitions of the **Cyber Services Analytics Platform (CSAP)** frontend.

---

## 1. System Directory Map
The frontend codebase is organized into isolated, thematic folders under `src/` to ensure high maintainability and decoupled modules:

- `src/app/`: Central architectural metadata, configurations, and core manuals.
- `src/components/`: Reusable, stateless presentational widgets (e.g., KPICards, EChartCard, DataGrid).
- `src/hooks/`: Stateful REST API consumer queries and filters (TanStack Query hooks).
- `src/layouts/`: Frame layout structures (AppLayout with collapsible side navbar and header).
- `src/pages/`: Isolated orchestrator page components (lazy loaded).
- `src/services/`: Low-level network connectors (`apiClient` and mock services).
- `src/stores/`: Zustand state modules restricted to local UI/UX settings.
- `src/theme/`: Mantine design systems.
- `src/types/`: Strict TypeScript interface models.
- `src/utils/`: Custom helpers (e.g., kpiEvaluator).

---

## 2. Core Routing & Drill-Down Specification
Vite-based code-splitting is enforced using `React.lazy` and `React.Suspense` configurations. Routes are declared inside `src/App.tsx`:

- `/`: Core Executive Dashboard (`DashboardPage`)
- `/engineers`: soporte de Ingenieros (`EngineersPage`)
- `/clients`: soporte de Clientes (`ClientsPage`)
- `/technologies`: soporte de Tecnologías (`TechnologiesPage`)
- `/teams`: colas de Equipos (`TeamsPage`)
- `/executions`: bitácoras de Ejecuciones (`ExecutionsPage`)
- `/settings`: placeholder de Configuración (`SettingsPage`)
- `/not-found`: error de página (`NotFoundPage`)

### Drill-down semantic paths:
- `/engineers/:engineerId` (or `/engineers/:engineerId/monthly` or `/engineers/:engineerId/daily`): Engineer performance drilldown sheet.
- `/clients/:clientId`: Client performance drilldown sheet.
- `/technologies/:technologyId`: Technology performance drilldown sheet.
- `/teams/:teamId`: Team performance drilldown sheet.
- `/executions/:executionId`: Operational KPI Execution detailed logs and audit sheet.

All unregistered routes automatically fallback-redirect to `/not-found`.

---

## 3. State Management Policy
To maintain absolute separation of concerns, the state is split cleanly into two layers:

### A. Client UI State (Zustand)
Global frontend behaviors (such as active light/dark/system themes, sidebar collapsible toggles, active dashboard selection tabs) reside in `src/stores/uiStore.ts`.

### B. Server State (TanStack Query)
Calculated KPIs, historical daily/monthly snapshots, catalog lists, and execution logs must never be duplicated in global client stores. They are cached and managed using standard React Query hooks (`useDailySnapshots`, `useExecutions`, etc.).

---

## 4. KPI Status Evaluation Framework (CSAP-007)
Métricas are evaluated dynamically using a configuration-driven policy framework located in `src/utils/kpiEvaluator.ts`. Each KPI defines:
- **target**: Target performance value.
- **warning**: Margin threshold triggering warnings.
- **critical**: Critical margin threshold.
- **direction**: `"higher-is-better"` (e.g. SLA) or `"lower-is-better"` (e.g. Response/Resolution times).

The presentational layer only consumes evaluated status tags (`success`, `warning`, `critical`, `neutral`), keeping business SLA logic fully isolated.

---

## 5. Grid Toolbar & Layout Persistence (CSAP-007)
We integrated `GridToolbar` into the custom `DataGrid` wrapper. Layout changes (column widths, pinning, order, visibility, active sorting, active filters) are automatically serialized and persisted inside `localStorage` under versioned keys matching the pattern:
`csap:grid:<grid-key>:v1`

---

## 6. Chart Strategy (Apache ECharts)
- Standard Line, Bar, Pie, and Area charts are wrapped inside the reusable, stateless `EChartCard` wrapper component (`src/components/EChartCard.tsx`).
- Responsive auto-resizing is handled dynamically via native `ResizeObserver` instances.
- Theme switching triggers instant repaint using ECharts' built-in Dark Mode scheme on active color scheme modifications.
