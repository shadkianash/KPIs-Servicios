# TypeScript Type Declarations

This directory houses global type models, interfaces, and custom type definitions.

## Directives
- Declare interfaces mirroring backend FastAPI entities (e.g. `Ticket`, `Team`, `KpiReport`).
- Establish TypeScript unions for status flags (e.g., `SlaStatus = 'MET' | 'BREACHED' | 'EXEMPT'`).
- Prevent repeating type schemas across pages and components by importing definitions from this centralized module.
