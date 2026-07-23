import {
  CatalogItem,
  DailySnapshot,
  KPIExecution,
  MonthlySnapshot,
  ResponseEnvelope,
} from "../../types";
import {
  mockClients,
  mockTechnologies,
  mockEngineers,
  mockTeams,
  mockExecutions,
  generateMockDailySnapshots,
  generateMockMonthlySnapshots,
} from "./mockData";

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export const mockService = {
  async getClients(
    page = 1,
    pageSize = 50
  ): Promise<ResponseEnvelope<CatalogItem[]>> {
    await delay(150);
    const start = (page - 1) * pageSize;
    const end = start + pageSize;
    const items = mockClients.slice(start, end);
    return {
      success: true,
      data: items,
      pagination: {
        page,
        page_size: pageSize,
        total_records: mockClients.length,
        total_pages: Math.ceil(mockClients.length / pageSize),
      },
    };
  },

  async getTechnologies(
    page = 1,
    pageSize = 50
  ): Promise<ResponseEnvelope<CatalogItem[]>> {
    await delay(150);
    const start = (page - 1) * pageSize;
    const end = start + pageSize;
    const items = mockTechnologies.slice(start, end);
    return {
      success: true,
      data: items,
      pagination: {
        page,
        page_size: pageSize,
        total_records: mockTechnologies.length,
        total_pages: Math.ceil(mockTechnologies.length / pageSize),
      },
    };
  },

  async getEngineers(
    page = 1,
    pageSize = 50
  ): Promise<ResponseEnvelope<CatalogItem[]>> {
    await delay(150);
    const start = (page - 1) * pageSize;
    const end = start + pageSize;
    const items = mockEngineers.slice(start, end);
    return {
      success: true,
      data: items,
      pagination: {
        page,
        page_size: pageSize,
        total_records: mockEngineers.length,
        total_pages: Math.ceil(mockEngineers.length / pageSize),
      },
    };
  },

  async getTeams(
    page = 1,
    pageSize = 50
  ): Promise<ResponseEnvelope<CatalogItem[]>> {
    await delay(150);
    const start = (page - 1) * pageSize;
    const end = start + pageSize;
    const items = mockTeams.slice(start, end);
    return {
      success: true,
      data: items,
      pagination: {
        page,
        page_size: pageSize,
        total_records: mockTeams.length,
        total_pages: Math.ceil(mockTeams.length / pageSize),
      },
    };
  },

  async getExecutions(
    page = 1,
    pageSize = 50
  ): Promise<ResponseEnvelope<KPIExecution[]>> {
    await delay(200);
    const start = (page - 1) * pageSize;
    const end = start + pageSize;
    const items = mockExecutions.slice(start, end);
    return {
      success: true,
      data: items,
      pagination: {
        page,
        page_size: pageSize,
        total_records: mockExecutions.length,
        total_pages: Math.ceil(mockExecutions.length / pageSize),
      },
    };
  },

  async getExecutionDetail(
    id: string
  ): Promise<ResponseEnvelope<KPIExecution>> {
    await delay(100);
    const execution = mockExecutions.find((x) => x.execution_id === id);
    if (!execution) {
      throw new Error(`KPI Execution ${id} not found.`);
    }
    return {
      success: true,
      data: execution,
    };
  },

  async getDailySnapshots(
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
  ): Promise<ResponseEnvelope<DailySnapshot[]>> {
    await delay(250);
    let all = generateMockDailySnapshots();

    // Filtering logic
    if (filters.startDate) {
      all = all.filter((s) => s.snapshot_date >= filters.startDate!);
    }
    if (filters.endDate) {
      all = all.filter((s) => s.snapshot_date <= filters.endDate!);
    }
    if (filters.engineerId) {
      all = all.filter(
        (s) =>
          s.engineer_id === filters.engineerId ||
          s.aggregation_level === "global"
      );
    }
    if (filters.clientId) {
      all = all.filter(
        (s) =>
          s.client_id === filters.clientId || s.aggregation_level === "global"
      );
    }
    if (filters.teamId) {
      all = all.filter(
        (s) => s.team_id === filters.teamId || s.aggregation_level === "global"
      );
    }

    const start = (page - 1) * pageSize;
    const end = start + pageSize;
    const items = all.slice(start, end);

    return {
      success: true,
      data: items,
      pagination: {
        page,
        page_size: pageSize,
        total_records: all.length,
        total_pages: Math.ceil(all.length / pageSize),
      },
    };
  },

  async getMonthlySnapshots(
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
  ): Promise<ResponseEnvelope<MonthlySnapshot[]>> {
    await delay(250);
    let all = generateMockMonthlySnapshots();

    if (filters.year) {
      all = all.filter((s) => s.year === filters.year);
    }
    if (filters.month) {
      all = all.filter((s) => s.month === filters.month);
    }
    if (filters.clientId) {
      all = all.filter(
        (s) =>
          s.client_id === filters.clientId || s.aggregation_level === "global"
      );
    }
    if (filters.teamId) {
      all = all.filter(
        (s) => s.team_id === filters.teamId || s.aggregation_level === "global"
      );
    }

    const start = (page - 1) * pageSize;
    const end = start + pageSize;
    const items = all.slice(start, end);

    return {
      success: true,
      data: items,
      pagination: {
        page,
        page_size: pageSize,
        total_records: all.length,
        total_pages: Math.ceil(all.length / pageSize),
      },
    };
  },
};
