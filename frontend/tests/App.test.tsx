import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { MantineProvider } from "@mantine/core";
import App from "../src/App";

describe("App Bootstrap rendering", () => {
  it("renders 'KPIs Servicios' and 'Bootstrap completed successfully.'", () => {
    render(
      <MantineProvider>
        <App />
      </MantineProvider>
    );

    expect(screen.getByText("KPIs Servicios")).toBeInTheDocument();
    expect(screen.getByText("Bootstrap completed successfully.")).toBeInTheDocument();
  });
});
