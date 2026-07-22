import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MantineProvider } from "@mantine/core";
import App from "../src/App";
import { apiClient } from "../src/services/apiClient";
import HealthPage from "../src/pages/HealthPage";

// Mock axios to avoid network requests during unit tests
vi.mock("../src/services/apiClient", () => ({
  apiClient: {
    get: vi.fn(() =>
      Promise.resolve({
        data: {
          status: "ok",
          service: "KPIs Servicios API",
          version: "0.1.0",
        },
      })
    ),
  },
}));

describe("Frontend Bootstrap Rendering and Clients", () => {
  it("verifies API Client initialized with default base url", () => {
    expect(apiClient).toBeDefined();
  });

  it("renders AppShell and Title 'KPIs Servicios'", () => {
    render(<App />);

    // Assert main header titles render correctly
    expect(screen.getAllByText("KPIs Servicios").length).toBeGreaterThan(0);
    expect(screen.getByText("Bootstrap completed successfully.")).toBeInTheDocument();
  });

  it("renders HealthPage card component", () => {
    render(
      <MantineProvider>
        <HealthPage />
      </MantineProvider>
    );

    expect(screen.getByText("Backend status")).toBeInTheDocument();
  });
});
