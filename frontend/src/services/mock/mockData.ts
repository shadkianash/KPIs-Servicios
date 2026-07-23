import {
  CatalogItem,
  DailySnapshot,
  KPIExecution,
  MonthlySnapshot,
} from "../../types";

export const mockClients: CatalogItem[] = [
  { id: "c1", name: "Banco del Norte" },
  { id: "c2", name: "Aseguradora Global" },
  { id: "c3", name: "Telecomunicaciones Patria" },
  { id: "c4", name: "Energía del Sur" },
  { id: "c5", name: "Logística Express" },
];

export const mockTechnologies: CatalogItem[] = [
  { id: "t1", name: "Firewalls Fortinet" },
  { id: "t2", name: "CrowdStrike Falcon EDR" },
  { id: "t3", name: "SIEM Splunk" },
  { id: "t4", name: "AWS Cloud Security" },
  { id: "t5", name: "Azure Sentinel" },
];

export const mockEngineers: CatalogItem[] = [
  { id: "e1", name: "Alejandro Gómez" },
  { id: "e2", name: "Beatriz Rodríguez" },
  { id: "e3", name: "Carlos Mendoza" },
  { id: "e4", name: "Diana Martínez" },
  { id: "e5", name: "Eduardo Silva" },
];

export const mockTeams: CatalogItem[] = [
  { id: "g1", name: "SOC Nivel 1" },
  { id: "g2", name: "SOC Nivel 2" },
  { id: "g3", name: "Respuesta a Incidentes" },
  { id: "g4", name: "Gestión de Vulnerabilidades" },
];

export const mockExecutions: KPIExecution[] = [
  {
    execution_id: "6a2f8b50-3bfd-4299-8802-123456789001",
    started_at: "2026-03-05T01:00:00Z",
    finished_at: "2026-03-05T01:00:12.450Z",
    duration_ms: 12450,
    execution_status: "COMPLETED",
    calculation_version: "1.0.0",
    engine_version: "1.0.0",
    processed_tickets: 450,
    processed_time_entries: 320,
    generated_daily_snapshots: 45,
    generated_monthly_snapshots: 12,
    correlation_id: "corr-20260305-010000",
    warnings: [],
    errors: [],
  },
  {
    execution_id: "6a2f8b50-3bfd-4299-8802-123456789002",
    started_at: "2026-03-04T01:00:00Z",
    finished_at: "2026-03-04T01:00:11.200Z",
    duration_ms: 11200,
    execution_status: "COMPLETED",
    calculation_version: "1.0.0",
    engine_version: "1.0.0",
    processed_tickets: 440,
    processed_time_entries: 310,
    generated_daily_snapshots: 45,
    generated_monthly_snapshots: 12,
    correlation_id: "corr-20260304-010000",
    warnings: ["Some tickets had missing SLA targets; fallbacks applied."],
    errors: [],
  },
  {
    execution_id: "6a2f8b50-3bfd-4299-8802-123456789003",
    started_at: "2026-03-03T01:00:00Z",
    finished_at: "2026-03-03T01:00:02.500Z",
    duration_ms: 2500,
    execution_status: "FAILED",
    calculation_version: "1.0.0",
    engine_version: "1.0.0",
    processed_tickets: 0,
    processed_time_entries: 0,
    generated_daily_snapshots: 0,
    generated_monthly_snapshots: 0,
    correlation_id: "corr-20260303-010000",
    warnings: [],
    errors: ["Failed to connect to CSV export directory. No file found."],
  },
];

// Helper to generate trend snapshots
export const generateMockDailySnapshots = (): DailySnapshot[] => {
  const snapshots: DailySnapshot[] = [];
  const baseExecutionId = "6a2f8b50-3bfd-4299-8802-123456789001";

  // 30 days of data for multiple dimensions (global, clients, engineers, teams)
  for (let i = 30; i >= 0; i--) {
    const d = new Date();
    d.setDate(d.getDate() - i);
    const dateStr = d.toISOString().split("T")[0];

    // 1. Global
    snapshots.push({
      id: `ds-global-${i}`,
      snapshot_date: dateStr,
      aggregation_level: "global",
      snapshot_version: "1.0.0",
      execution_id: baseExecutionId,
      metrics: {
        tickets_assigned: 50 + Math.floor(Math.sin(i) * 10),
        tickets_closed: 45 + Math.floor(Math.cos(i) * 8),
        worked_hours: 180 + Math.floor(Math.sin(i / 2) * 20),
        avg_hours_per_ticket: 4.2 + Math.cos(i) * 0.5,
        avg_response_time_hours: 1.5 + Math.sin(i) * 0.3,
        avg_resolution_time_hours: 24.5 + Math.cos(i / 2) * 3,
        open_backlog: 120 + i * 2 - Math.floor(Math.sin(i) * 15),
        reopened_backlog: 5 + (i % 3),
        sla_compliance_rate: 94.5 + Math.sin(i / 5) * 3,
      },
    });

    // 2. Client c1
    snapshots.push({
      id: `ds-c1-${i}`,
      snapshot_date: dateStr,
      aggregation_level: "client",
      client_id: "c1",
      snapshot_version: "1.0.0",
      execution_id: baseExecutionId,
      metrics: {
        tickets_assigned: 15 + Math.floor(Math.sin(i) * 3),
        tickets_closed: 12 + Math.floor(Math.cos(i) * 2),
        worked_hours: 45 + Math.floor(Math.sin(i) * 5),
        avg_hours_per_ticket: 3.8,
        open_backlog: 30 + Math.floor(i * 0.5),
        sla_compliance_rate: 92.1 + Math.sin(i / 4) * 4,
      },
    });

    // 3. Engineer e1
    snapshots.push({
      id: `ds-e1-${i}`,
      snapshot_date: dateStr,
      aggregation_level: "engineer",
      engineer_id: "e1",
      snapshot_version: "1.0.0",
      execution_id: baseExecutionId,
      metrics: {
        tickets_assigned: 6 + (i % 3),
        tickets_closed: 5 + (i % 2),
        worked_hours: 24 + (i % 4) * 2,
        avg_hours_per_ticket: 4.5,
        open_backlog: 10 + Math.floor(i * 0.1),
        sla_compliance_rate: 96.0 + Math.sin(i / 3) * 2,
      },
    });
  }
  return snapshots;
};

export const generateMockMonthlySnapshots = (): MonthlySnapshot[] => {
  const snapshots: MonthlySnapshot[] = [];
  const baseExecutionId = "6a2f8b50-3bfd-4299-8802-123456789001";
  const months = [
    { year: 2025, month: 11 },
    { year: 2025, month: 12 },
    { year: 2026, month: 1 },
    { year: 2026, month: 2 },
    { year: 2026, month: 3 },
  ];

  months.forEach(({ year, month }, idx) => {
    // 1. Global
    snapshots.push({
      id: `ms-global-${year}-${month}`,
      year,
      month,
      aggregation_level: "global",
      snapshot_version: "1.0.0",
      execution_id: baseExecutionId,
      metrics: {
        tickets_assigned: 1200 + idx * 100,
        tickets_closed: 1150 + idx * 95,
        worked_hours: 4500 + idx * 300,
        avg_hours_per_ticket: 3.9,
        avg_response_time_hours: 1.4,
        avg_resolution_time_hours: 22.1,
        open_backlog: 140 - idx * 5,
        reopened_backlog: 25 + (idx % 2) * 5,
        sla_compliance_rate: 93.2 + idx * 0.6,
      },
    });

    // 2. Client c1
    snapshots.push({
      id: `ms-c1-${year}-${month}`,
      year,
      month,
      aggregation_level: "client",
      client_id: "c1",
      snapshot_version: "1.0.0",
      execution_id: baseExecutionId,
      metrics: {
        tickets_assigned: 320 + idx * 25,
        tickets_closed: 305 + idx * 22,
        worked_hours: 1200 + idx * 80,
        avg_hours_per_ticket: 3.8,
        open_backlog: 45 - idx * 2,
        sla_compliance_rate: 91.5 + idx * 0.8,
      },
    });

    // 3. Client c2
    snapshots.push({
      id: `ms-c2-${year}-${month}`,
      year,
      month,
      aggregation_level: "client",
      client_id: "c2",
      snapshot_version: "1.0.0",
      execution_id: baseExecutionId,
      metrics: {
        tickets_assigned: 280 + idx * 15,
        tickets_closed: 270 + idx * 12,
        worked_hours: 1050 + idx * 50,
        avg_hours_per_ticket: 4.1,
        open_backlog: 38 - idx,
        sla_compliance_rate: 94.2 + idx * 0.4,
      },
    });

    // 4. Team g1
    snapshots.push({
      id: `ms-g1-${year}-${month}`,
      year,
      month,
      aggregation_level: "team",
      team_id: "g1",
      snapshot_version: "1.0.0",
      execution_id: baseExecutionId,
      metrics: {
        tickets_assigned: 400 + idx * 30,
        tickets_closed: 385 + idx * 28,
        worked_hours: 1550 + idx * 90,
        avg_hours_per_ticket: 3.5,
        open_backlog: 50 - idx * 3,
        sla_compliance_rate: 95.1 + idx * 0.5,
      },
    });
  });

  return snapshots;
};
