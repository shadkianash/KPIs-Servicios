import React, { useMemo } from "react";
import { Container, Title, Text, Box } from "@mantine/core";
import { useExecutions } from "../hooks/analyticsHooks";
import DataGrid from "../components/DataGrid";
import { ColDef } from "ag-grid-community";
import { KPIExecution } from "../types";

export default function ExecutionsPage(): React.JSX.Element {
  const { data, isLoading } = useExecutions(1, 100);

  const columnDefs = useMemo<ColDef<KPIExecution>[]>(
    () => [
      {
        field: "execution_id",
        headerName: "ID de Ejecución",
        sortable: true,
        filter: true,
        flex: 1.5,
        valueFormatter: (params) =>
          params.value ? `${params.value.substring(0, 8)}...` : "",
      },
      {
        field: "execution_status",
        headerName: "Estado",
        sortable: true,
        filter: true,
        flex: 1,
        cellRenderer: (params: { value: string }) => {
          const color =
            params.value === "COMPLETED"
              ? "green"
              : params.value === "FAILED"
                ? "red"
                : "blue";
          return `<span style="color: ${color}; font-weight: bold;">${params.value}</span>`;
        },
      },
      {
        field: "started_at",
        headerName: "Fecha Inicio",
        sortable: true,
        filter: true,
        flex: 1.5,
        valueFormatter: (params) =>
          params.value ? new Date(params.value).toLocaleString("es-ES") : "",
      },
      {
        field: "processed_tickets",
        headerName: "Tickets",
        sortable: true,
        filter: true,
        flex: 1,
      },
      {
        field: "duration_ms",
        headerName: "Duración (ms)",
        sortable: true,
        filter: true,
        flex: 1,
      },
    ],
    []
  );

  return (
    <Container fluid>
      <Box mb="md">
        <Title order={1}>Ejecuciones</Title>
        <Text size="sm" c="dimmed">
          Bitácora completa y auditoría de trabajos de agregación y cálculo del
          motor analítico
        </Text>
      </Box>

      <DataGrid
        title="Historial de Trabajos del Motor"
        subtitle="Registro de ejecuciones y volúmenes calculados"
        columnDefs={columnDefs}
        rowData={data?.data}
        loading={isLoading}
      />
    </Container>
  );
}
