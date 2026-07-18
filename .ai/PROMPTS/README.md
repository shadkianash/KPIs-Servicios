# AI Prompts Guide

This folder (`.ai/PROMPTS/`) is dedicated to storing structured prompt templates that speed up common operations, ensuring highly uniform outputs when human developers prompt LLM agents to write code for the CSAP repository.

---

## Recommended Prompt Templates

### 1. Ingestion / Data Loader Prompts
To build or extend data connectors (e.g., migrating from CSV to a API connector), use a prompt that enforces the decoupled interface:
> *"Implement a new service connector for [Jira/ServiceNow] following the Abstract Data Loader pattern defined in `.ai/ARCHITECTURE.md`. It must parse raw JSON payloads, map them to our internal `TicketIngestSchema` (Pydantic), and leverage Polars for data type enforcement before passing the frame to the Calculation Engine. Ensure strict typing is applied throughout and write tests simulating network failures."*

### 2. Metric Calculations (Polars)
To expand or add new operational calculations (such as ticket resolution trends), prompt:
> *"Write a pure, database-independent calculation module in Python 3.13 utilizing Polars. The function must accept a Polars DataFrame conforming to the schema in `.ai/DOMAIN.md` and calculate [Metric Name]. Keep this logic completely decoupled from database connections or FastAPI routing. Write accompanying Pytests to verify accuracy with mock edge-case DataFrames."*

### 3. Frontend Component Prompts
To request modular components that utilize our layout rules:
> *"Create a React TypeScript component using Mantine components and Apache ECharts to visualize [KPI Trend]. Fetch the required dataset using TanStack Query from the `/api/v1/kpis/[endpoint]` endpoint. Ensure state is kept local or in query cache (do not pollute global Zustand). Bind the component to handle resizing smoothly."*
