# Abstract Data Ingestion Loaders

This directory contains the pluggable data loader architecture.

## Purpose
- Define the base class/protocol interface for all ingestion sources.
- House the **Archer CSV Data Loader**, responsible for parsing daily CSV logs.
- Decouple the structure of incoming raw datasets from the database model storage layer, allowing future API-based loaders (e.g., Jira, ServiceNow) to be added with minimal codebase impact.
