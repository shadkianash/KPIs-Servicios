# Vite React TypeScript Frontend

This folder contains the complete modern web dashboard interface built on React, Vite, TypeScript, and Mantine.

---

## 1. Directory Structure

```text
frontend/
├── public/           # Static public assets (logos, icons, manifest files)
├── src/
│   ├── components/   # Pure UI and functional React components
│   ├── hooks/        # Custom React hooks (including queries)
│   ├── pages/        # Route page views (Dashboard, Ingestion, Reports)
│   ├── services/     # API client classes and networking integrations
│   ├── state/        # Global Zustand client state modules
│   ├── types/        # Core TypeScript interface definitions
│   └── main.tsx      # Main application bundle mountpoint
└── tests/            # Vitest unit/component tests and Playwright configs
```

---

## 2. Coding Guidelines
- **UI & Layout**: Strictly leverage Mantine UI library elements.
- **Charts & Visualizations**: Use custom components wrapping Apache ECharts.
- **Grids**: Use AG Grid Enterprise for dense list tables.
- **Forms**: Implement React Hook Form coupled with Zod validation.
- **Type Checking**: Strict TypeScript compiler options enabled. Avoid `any` types. Ensure ESLint and Prettier run with clean outputs before committing.
- **Server Cache**: Use TanStack Query to fetch, synchronize, and cache all API metrics. Avoid copying server metrics into Zustand state.
