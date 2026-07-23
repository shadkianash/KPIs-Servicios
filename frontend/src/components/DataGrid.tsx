import React from "react";
import { AgGridReact } from "ag-grid-react";
import { ColDef } from "ag-grid-community";
import { Card, Text, Button, Group, Box, LoadingOverlay } from "@mantine/core";
import { useUIStore } from "../stores/uiStore";

// Import AG Grid styles
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";

interface DataGridProps<T = unknown> {
  title: string;
  subtitle?: string;
  columnDefs: ColDef<T>[];
  rowData: T[] | null | undefined;
  loading?: boolean;
  pagination?: boolean;
  paginationPageSize?: number;
}

export default function DataGrid({
  title,
  subtitle,
  columnDefs,
  rowData,
  loading = false,
  pagination = true,
  paginationPageSize = 10,
}: DataGridProps): React.JSX.Element {
  const themeMode = useUIStore((state) => state.themeMode);

  // Determine grid dark mode class
  const isDark =
    themeMode === "dark" ||
    (themeMode === "system" &&
      window.matchMedia("(prefers-color-scheme: dark)").matches);

  const gridThemeClass = isDark ? "ag-theme-alpine-dark" : "ag-theme-alpine";

  return (
    <Card shadow="sm" radius="md" withBorder style={{ position: "relative" }}>
      <LoadingOverlay
        visible={loading}
        zIndex={1000}
        overlayProps={{ radius: "sm", blur: 1 }}
      />

      <Group justify="space-between" align="center" mb="md">
        <Box>
          <Text size="md" fw={700}>
            {title}
          </Text>
          {subtitle && (
            <Text size="xs" c="dimmed">
              {subtitle}
            </Text>
          )}
        </Box>
        <Button
          size="xs"
          variant="outline"
          color="gray"
          disabled
          title="Función deshabilitada para esta fase"
        >
          📥 Exportar CSV
        </Button>
      </Group>

      <Box
        className={gridThemeClass}
        style={{
          height: "350px",
          width: "100%",
        }}
      >
        <AgGridReact
          columnDefs={columnDefs}
          rowData={rowData || []}
          pagination={pagination}
          paginationPageSize={paginationPageSize}
          paginationPageSizeSelector={[5, 10, 20, 50]}
          domLayout="normal"
          defaultColDef={{
            sortable: true,
            filter: true,
            resizable: true,
            flex: 1,
            minWidth: 100,
          }}
        />
      </Box>
    </Card>
  );
}
