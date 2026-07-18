# Zustand Client State Stores

This directory manages global client-side UI and application states using Zustand.

## Core Directives
- Use Zustand strictly for localized client state (e.g. sidebar toggle status, active filters state, modal visibility).
- **Do not cache API response payloads in Zustand.** All server state metrics must be handled via TanStack Query hooks to allow automated refetching, invalidation, and request garbage collection.
