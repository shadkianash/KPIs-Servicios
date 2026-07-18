# API Services and Fetching Clients

This directory manages the core API networking client instances.

## Purpose
- Establish an Axios or Fetch client instance customized with baseline authentication headers, interceptors, and default response mappings.
- Model physical networking calls (e.g. `apiClient.get('/v1/kpis/sla')`) into clean, asynchronous functions.
- Keep network connections isolated, avoiding manual fetch routines inside components.
