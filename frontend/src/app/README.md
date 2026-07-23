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

---

## 2. Core Routing Specification
Vite-based code-splitting is enforced using `React.lazy` and `React.Suspense` configurations. Routes are declared inside `src/App.tsx`:

- `/`: Core Executive Dashboard (`DashboardPage`)
- `/engineers`: soporte de Ingenieros (`EngineersPage`)
- `/clients`: soporte de Clientes (`ClientsPage`)
- `/technologies`: soporte de Tecnologías (`TechnologiesPage`)
- `/teams`: colas de Equipos (`TeamsPage`)
- `/executions`: bitácoras de Ejecuciones (`ExecutionsPage`)
- `/settings`: placeholder de Configuración (`SettingsPage`)
- `/not-found`: error de página (`NotFoundPage`)

All unregistered routes automatically fallback-redirect to `/not-found`.

---

## 3. State Management Policy
To maintain absolute separation of concerns, the state is split cleanly into two layers:

### A. Client UI State (Zustand)
Global frontend behaviors (such as active light/dark/system themes, sidebar collapsible toggles, active dashboard selection tabs) reside in `src/stores/uiStore.ts`.

### B. Server State (TanStack Query)
Calculated KPIs, historical daily/monthly snapshots, catalog lists, and execution logs must never be duplicated in global client stores. They are cached and managed using standard React Query hooks (`useDailySnapshots`, `useExecutions`, etc.).

---

## 4. API Integration & Mock Failover Layer
All REST hooks query the FastAPI backend (`baseURL` resolved via relative Vite proxy `/api`). If the API is offline, empty, or returns a failing payload during initial deployments, hooks automatically trigger failover-resolution through the dedicated mock service layer (`src/services/mock/`):

```text
+----------------------+      +----------------------+
|  React Query Hook    | ---> | FastAPI REST Backend |
+----------------------+      +----------------------+
          |                              |
          v (Offline / Error)            v (Active)
+----------------------+      +----------------------+
|  Mock Service Layer  |      |   Real JSON Payload  |
+----------------------+      +----------------------+
```

---

## 5. Chart Strategy (Apache ECharts)
- Standard Line, Bar, Pie, and Area charts are wrapped inside the reusable, stateless `EChartCard` wrapper component (`src/components/EChartCard.tsx`).
- Responsive auto-resizing is handled dynamically via native `ResizeObserver` instances.
- Theme switching triggers instant repaint using ECharts' built-in Dark Mode scheme on active color scheme modifications.

---

## 6. Grid Strategy (AG Grid Community)
Tabular analytical datasets are presented using the stateless `DataGrid` component (`src/components/DataGrid.tsx`):
- Standard features: Multi-column sorting, column filtering, pagination page select, and resizing are enabled.
- Skin: Themes automatically toggle between `ag-theme-alpine` and `ag-theme-alpine-dark` depending on the user's active theme preference.
