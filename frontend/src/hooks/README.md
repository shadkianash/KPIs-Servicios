# Custom React Hooks

This folder contains reusable, stateful React Hooks.

## Guidelines
- Write hooks to isolate complex browser behaviors (e.g. `useDebounce`, `useThemeSwitcher`).
- Include TanStack Query implementations (e.g. `useKpisQuery`, `useIngestionStatus`) to cleanly separate query lifecycles, retries, and data fetching definitions from standard presentation layers.
