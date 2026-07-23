import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../services/apiClient";
import { mockService } from "../services/mock/mockService";
import {
  CatalogItem,
  DailySnapshot,
  KPIExecution,
  MonthlySnapshot,
  ResponseEnvelope,
} from "../types";

// Helper to check if we are in mock mode or API is failing
const fetchWithFallback = async <T>(
  apiCall: () => Promise<{ data: ResponseEnvelope<T> }>,
  mockCall: () => Promise<ResponseEnvelope<T>>,
  label: string
): Promise<ResponseEnvelope<T>> => {
  try {
    const res = await apiCall();
    if (res.data && res.data.success) {
      return res.data;
    }
    throw new Error(`API response success is false for ${label}`);
  } catch (err) {
    console.warn(
      `[API Fallback] Fetching '${label}' from API failed, falling back to Mock Service:`,
      err
    );
    return await mockCall();
  }
};

export const useClients = (page = 1, pageSize = 50) => {
  return useQuery({
    queryKey: ["clients", page, pageSize],
    queryFn: () =>
      fetchWithFallback(
        () =>
          apiClient.get<ResponseEnvelope<CatalogItem[]>>(
            `/metadata/clients?page=${page}&page_size=${pageSize}`
          ),
        () => mockService.getClients(page, pageSize),
        "clients"
      ),
  });
};

export const useTechnologies = (page = 1, pageSize = 50) => {
  return useQuery({
    queryKey: ["technologies", page, pageSize],
    queryFn: () =>
      fetchWithFallback(
        () =>
          apiClient.get<ResponseEnvelope<CatalogItem[]>>(
            `/metadata/technologies?page=${page}&page_size=${pageSize}`
          ),
        () => mockService.getTechnologies(page, pageSize),
        "technologies"
      ),
  });
};

export const useEngineers = (page = 1, pageSize = 50) => {
  return useQuery({
    queryKey: ["engineers", page, pageSize],
    queryFn: () =>
      fetchWithFallback(
        () =>
          apiClient.get<ResponseEnvelope<CatalogItem[]>>(
            `/metadata/engineers?page=${page}&page_size=${pageSize}`
          ),
        () => mockService.getEngineers(page, pageSize),
        "engineers"
      ),
  });
};

export const useTeams = (page = 1, pageSize = 50) => {
  return useQuery({
    queryKey: ["teams", page, pageSize],
    queryFn: () =>
      fetchWithFallback(
        () =>
          apiClient.get<ResponseEnvelope<CatalogItem[]>>(
            `/metadata/teams?page=${page}&page_size=${pageSize}`
          ),
        () => mockService.getTeams(page, pageSize),
        "teams"
      ),
  });
};

export const useExecutions = (page = 1, pageSize = 50) => {
  return useQuery({
    queryKey: ["executions", page, pageSize],
    queryFn: () =>
      fetchWithFallback(
        () =>
          apiClient.get<ResponseEnvelope<KPIExecution[]>>(
            `/kpi/executions?page=${page}&page_size=${pageSize}`
          ),
        () => mockService.getExecutions(page, pageSize),
        "executions"
      ),
  });
};

export const useDailySnapshots = (
  filters: {
    startDate?: string | null;
    endDate?: string | null;
    engineerId?: string | null;
    clientId?: string | null;
    technologyId?: string | null;
    teamId?: string | null;
  },
  page = 1,
  pageSize = 50
) => {
  return useQuery({
    queryKey: ["dailySnapshots", filters, page, pageSize],
    queryFn: () => {
      const params = new URLSearchParams();
      if (filters.startDate) params.append("start_date", filters.startDate);
      if (filters.endDate) params.append("end_date", filters.endDate);
      if (filters.engineerId) params.append("engineer_id", filters.engineerId);
      if (filters.clientId) params.append("client_id", filters.clientId);
      if (filters.technologyId)
        params.append("technology_id", filters.technologyId);
      if (filters.teamId) params.append("team_id", filters.teamId);
      params.append("page", String(page));
      params.append("page_size", String(pageSize));

      return fetchWithFallback(
        () =>
          apiClient.get<ResponseEnvelope<DailySnapshot[]>>(
            `/kpi/daily?${params.toString()}`
          ),
        () => mockService.getDailySnapshots(filters, page, pageSize),
        "dailySnapshots"
      );
    },
  });
};

export const useMonthlySnapshots = (
  filters: {
    year?: number | null;
    month?: number | null;
    engineerId?: string | null;
    clientId?: string | null;
    technologyId?: string | null;
    teamId?: string | null;
  },
  page = 1,
  pageSize = 50
) => {
  return useQuery({
    queryKey: ["monthlySnapshots", filters, page, pageSize],
    queryFn: () => {
      const params = new URLSearchParams();
      if (filters.year) params.append("year", String(filters.year));
      if (filters.month) params.append("month", String(filters.month));
      if (filters.engineerId) params.append("engineer_id", filters.engineerId);
      if (filters.clientId) params.append("client_id", filters.clientId);
      if (filters.technologyId)
        params.append("technology_id", filters.technologyId);
      if (filters.teamId) params.append("team_id", filters.teamId);
      params.append("page", String(page));
      params.append("page_size", String(pageSize));

      return fetchWithFallback(
        () =>
          apiClient.get<ResponseEnvelope<MonthlySnapshot[]>>(
            `/kpi/monthly?${params.toString()}`
          ),
        () => mockService.getMonthlySnapshots(filters, page, pageSize),
        "monthlySnapshots"
      );
    },
  });
};
