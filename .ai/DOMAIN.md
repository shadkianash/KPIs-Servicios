# Domain Model & Glossary

This document maps out the logical business domain of the Cyber Services Analytics Platform (CSAP). It serves as a single source of truth for both human engineers and AI agents.

---

## 1. Core Domain Context

CSAP calculates performance and workflow indicators for cybersecurity service teams. The primary input is tabular logs representing ticket entries extracted from **Archer**.

---

## 2. Key Entities & Definitions

- **Service Ticket**: A single, granular request or operational task recorded in Archer (e.g., Incident analysis, vulnerability assessment, firewall review).
- **Service Desk Team**: The team or queue owning the ticket.
- **SLA (Service Level Agreement)**: The target duration allowed to resolve or close a ticket, typically defined in days or hours.
- **SLA Status**:
  - `Met`: Resolved within the SLA window.
  - `Breached`: Exceeded the SLA resolution window.
  - `Exempt`: Marked as excluded from standard SLA calculation (e.g., due to external dependencies).
- **State**: The current phase of a ticket (e.g., `New`, `In Progress`, `Pending Client`, `Closed`, `Cancelled`).
- **Backlog**: Active, non-resolved service tickets currently assigned to a queue.
- **Aging**: The duration of time a ticket has spent in the Backlog since creation.
- **Capacity**: The volume of service tickets a team can successfully complete over a set time window.
- **Productivity**: Inflow of tickets vs. Outflow (completion rate), analyzed per team or individual resource.

---

## 3. Metrics & Calculations Guide

### SLA Compliance Rate (%)
$$\text{SLA Compliance} = \left( \frac{\text{Tickets Resolving SLA Met}}{\text{Total SLA-Eligible Resolved Tickets}} \right) \times 100$$

### Backlog Aging Categories
We classify backlog tickets into aging buckets:
- `0 - 15 days`
- `16 - 30 days`
- `31 - 60 days`
- `60+ days`

### Backlog Growth Index
$$\text{Growth Index} = \frac{\text{New Incoming Tickets}}{\text{Resolved Tickets}}$$
- Index $> 1.0$: Backlog is accumulating.
- Index $< 1.0$: Backlog is shrinking.
