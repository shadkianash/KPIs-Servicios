# Cyber Services Analytics Platform (CSAP) - Project Profile

## 1. Overview
The **Cyber Services Analytics Platform (CSAP)** is a purpose-built, high-performance analytics system for cybersecurity services teams. It delivers insights on capacity, backlog, SLA compliance, productivity, and future operational trends.

## 2. Key Objectives & Boundaries
- **Strict Analytical Scope**: CSAP is **not** an ITSM system and **does not** manage tickets. It operates downstream from ticketing platforms.
- **Data Ingestion**: Processes daily Archer CSV exports. It must handle raw tabular data reliably, perform schema validations, and calculate business-critical KPIs.
- **Extensibility**: Architected with decoupled data loaders to support future native APIs and integrations (such as Jira, ServiceNow, etc.) without altering the underlying domain models or metric calculation engines.
- **Audience**: Designed for executive management, security services leaders, and operations analysts.

## 3. Key Concepts & Definitions
- **SLA Compliance**: Target completion versus actual completion metrics.
- **Backlog & Aging**: Analysis of open tickets and their idle durations.
- **Capacity & Productivity**: Metrics analyzing team performance, workload distributions, and bottleneck detection.

## 4. Operational Guardrails
- Maintain modular boundary separation between data ingestion, computation, database persistence, and API exposure.
- Strictly adhere to Python 3.13 and React/TypeScript best practices as detailed in `.ai/RULES.md` and `.ai/STACK.md`.
