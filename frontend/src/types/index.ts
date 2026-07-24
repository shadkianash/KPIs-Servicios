export interface CatalogItem {
  id: string;
  name: string;
}

export interface PaginationInfo {
  page: number;
  page_size: number;
  total_records: number;
  total_pages: number;
}

export interface ResponseEnvelope<T> {
  success: boolean;
  data: T;
  pagination?: PaginationInfo;
}

export interface ErrorDetail {
  code: string;
  message: string;
  details?: unknown;
}

export interface ErrorEnvelope {
  success: boolean;
  error: ErrorDetail;
}

export interface KPIExecution {
  execution_id: string;
  started_at: string | null;
  finished_at: string | null;
  duration_ms: number | null;
  execution_status: "RUNNING" | "COMPLETED" | "FAILED";
  calculation_version: string;
  engine_version: string;
  processed_tickets: number;
  processed_time_entries: number;
  generated_daily_snapshots: number;
  generated_monthly_snapshots: number;
  correlation_id: string;
  warnings?: string[] | null;
  errors?: string[] | null;
}

export interface DailySnapshot {
  id: string;
  snapshot_date: string;
  aggregation_level: "global" | "client" | "engineer" | "technology" | "team";
  engineer_id?: string | null;
  client_id?: string | null;
  technology_id?: string | null;
  team_id?: string | null;
  snapshot_version: string;
  execution_id: string;
  metrics: Record<string, number>;
}

export interface MonthlySnapshot {
  id: string;
  year: number;
  month: number;
  aggregation_level: "global" | "client" | "engineer" | "technology" | "team";
  engineer_id?: string | null;
  client_id?: string | null;
  technology_id?: string | null;
  team_id?: string | null;
  snapshot_version: string;
  execution_id: string;
  metrics: Record<string, number>;
}

export interface FilterState {
  startDate: string | null;
  endDate: string | null;
  engineerId: string | null;
  clientId: string | null;
  technologyId: string | null;
  teamId: string | null;
  page: number;
  pageSize: number;
  sort: string | null;
  order: "asc" | "desc" | null;
}

// KPI status evaluation framework typing specs (CSAP-007)
export type KPIDirection = "higher-is-better" | "lower-is-better";
export type KPIStatus = "success" | "warning" | "critical" | "neutral";

export interface KPICardPolicy {
  id: string;
  name: string;
  target: number;
  warning: number;
  critical: number;
  direction: KPIDirection;
  unit: string;
}

export interface KPIEvaluationResult {
  status: KPIStatus;
  color: string;
  message: string;
}
