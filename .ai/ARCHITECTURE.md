# Architecture Overview

This document details the architectural patterns and boundaries established for the **Cyber Services Analytics Platform (CSAP)**.

---

## 1. High-Level Architecture Pattern

CSAP utilizes a modular, decoupled architecture where ingestion, processing, persistence, and presentation are kept separate.

```text
+-----------------------+      +-----------------------+      +-----------------------+
|  Archer CSV Exports   | ---> | Ingestion / Loader    | ---> | Polars Processing     |
|                       |      | (Extensible Interface)|      | Engine (KPI Calculus) |
+-----------------------+      +-----------------------+      +-----------------------+
                                                                          |
                                                                          v
+-----------------------+      +-----------------------+      +-----------------------+
| React / TypeScript    | <--- | FastAPI (REST Endp.)  | <--- | Database (Postgres)   |
| Frontend (Mantine)    |      | (Pydantic / SQLAlch)  |      | / Cache (Redis)       |
+-----------------------+      +-----------------------+      +-----------------------+
```

---

## 2. Core Architectural Principles

1. **Decoupled Data Loader Pattern**:
   - Data Ingestion is decoupled from the main metric calculus.
   - Loaders must implement a common interface. The default loader ingests Daily CSV files from Archer, but future loaders (Jira, ServiceNow APIs) must be pluggable with zero impact on the analytical engine.
2. **Stateless Core Processing**:
   - The KPI calculation engine is stateless and utilizes **Polars** for high-volume, multi-threaded dataframe manipulation.
3. **Repository Pattern for DB Access**:
   - Databases access is abstracted using the Repository Pattern via SQLAlchemy 2.x to separate business models from persistence mechanics.
4. **Thin Controllers / Clean APIs**:
   - FastAPI endpoints should focus only on request validation (Pydantic v2), calling backend services, and returning formatted models. No business or processing logic lives directly in routers.
5. **Uni-directional Frontend State Flow**:
   - React application uses TanStack Query for server state cache and Zustand for clean, global client state. No prop-drilling or messy synchronization allowed.

---

## 3. Data Flow
1. **Ingestion**: CSV exported from Archer is fed into the loader.
2. **Transformation & Calculation**: Polars processes raw tables, enforces data typing, computes KPI vectors, and outputs structured models.
3. **Storage**: Data is written into PostgreSQL via SQLAlchemy.
4. **API Delivery**: FastAPI fetches metrics, leveraging Redis to cache heavy analytical calculations.
5. **Visualization**: Frontend queries FastAPI, handles local state, and visualizes interactive trends using Apache ECharts and AG Grid.
