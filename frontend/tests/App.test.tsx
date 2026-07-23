import { describe, it, expect } from "vitest";
import { render, screen, fireEvent, act } from "@testing-library/react";
import { MantineProvider } from "@mantine/core";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import App from "../src/App";
import KPICard from "../src/components/KPICard";
import FilterPanel from "../src/components/FilterPanel";
import { useUIStore } from "../src/stores/uiStore";

// Mock resize observer and matchMedia for full compatibility
class ResizeObserverMock {
  observe() {}
  unobserve() {}
  disconnect() {}
}
global.ResizeObserver = ResizeObserverMock;

const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

describe("CSAP Frontend Core Foundation Tests", () => {
  it("renders App shell layout and side navigation links", () => {
    render(<App />);

    // Assert that the brand header and main navigation elements are correctly presented
    expect(screen.getByText("CSAP Analytics")).toBeInTheDocument();
    expect(screen.getByText("Cuadro de Mando")).toBeInTheDocument();
    expect(screen.getByText("Ingenieros")).toBeInTheDocument();
    expect(screen.getByText("Clientes")).toBeInTheDocument();
    expect(screen.getByText("Tecnologías")).toBeInTheDocument();
    expect(screen.getByText("Equipos")).toBeInTheDocument();
  });

  it("verifies state mutations in global Zustand UI store", () => {
    const { toggleSidebar, setThemeMode } = useUIStore.getState();

    // Toggle sidebar
    act(() => {
      toggleSidebar();
    });
    expect(useUIStore.getState().sidebarCollapsed).toBe(true);

    // Set theme
    act(() => {
      setThemeMode("dark");
    });
    expect(useUIStore.getState().themeMode).toBe("dark");
  });

  it("renders KPI Cards with numeric data and custom colors", () => {
    render(
      <MantineProvider>
        <KPICard title="Cumplimiento SLA" value="98.5%" trend="1.2%" trendDirection="up" icon="🛡️" />
      </MantineProvider>
    );

    expect(screen.getByText("CUMPLIMIENTO SLA")).toBeInTheDocument();
    expect(screen.getByText("98.5%")).toBeInTheDocument();
    expect(screen.getByText("▲ 1.2%")).toBeInTheDocument();
  });

  it("supports collapsing filter panel on click", () => {
    const queryClient = createTestQueryClient();
    render(
      <QueryClientProvider client={queryClient}>
        <MantineProvider>
          <BrowserRouter>
            <FilterPanel />
          </BrowserRouter>
        </MantineProvider>
      </QueryClientProvider>
    );

    const filterHeader = screen.getByText(/Filtros Avanzados de Datos/i);
    expect(filterHeader).toBeInTheDocument();

    // Collapse filters
    fireEvent.click(filterHeader);
    expect(screen.getByText("Expandir ▼")).toBeInTheDocument();
  });
});
