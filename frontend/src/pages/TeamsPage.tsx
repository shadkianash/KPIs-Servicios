import React, { useMemo } from "react";
import { Container, Title, Text, Box } from "@mantine/core";
import { useTeams } from "../hooks/analyticsHooks";
import DataGrid from "../components/DataGrid";
import { ColDef } from "ag-grid-community";
import { CatalogItem } from "../types";

export default function TeamsPage(): React.JSX.Element {
  const { data, isLoading } = useTeams(1, 100);

  const columnDefs = useMemo<ColDef<CatalogItem>[]>(
    () => [
      {
        field: "id",
        headerName: "ID del Equipo",
        sortable: true,
        filter: true,
        flex: 1,
      },
      {
        field: "name",
        headerName: "Nombre del Equipo / Cola",
        sortable: true,
        filter: true,
        flex: 2,
      },
    ],
    []
  );

  return (
    <Container fluid>
      <Box mb="md">
        <Title order={1}>Equipos</Title>
        <Text size="sm" c="dimmed">
          Grupos resolutores, niveles de guardia y células del SOC registradas
        </Text>
      </Box>

      <DataGrid
        title="Listado de Equipos Resolutores"
        subtitle="Estructura operativa de las colas de servicio"
        columnDefs={columnDefs}
        rowData={data?.data}
        loading={isLoading}
      />
    </Container>
  );
}
