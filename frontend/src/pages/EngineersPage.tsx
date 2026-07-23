import React, { useMemo } from "react";
import { Container, Title, Text, Box } from "@mantine/core";
import { useEngineers } from "../hooks/analyticsHooks";
import DataGrid from "../components/DataGrid";
import { ColDef } from "ag-grid-community";
import { CatalogItem } from "../types";

export default function EngineersPage(): React.JSX.Element {
  const { data, isLoading } = useEngineers(1, 100);

  const columnDefs = useMemo<ColDef<CatalogItem>[]>(
    () => [
      {
        field: "id",
        headerName: "ID del Ingeniero",
        sortable: true,
        filter: true,
        flex: 1,
      },
      {
        field: "name",
        headerName: "Nombre Completo",
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
        <Title order={1}>Ingenieros</Title>
        <Text size="sm" c="dimmed">
          Catálogo completo de ingenieros de soporte y respuesta de
          ciberseguridad activos
        </Text>
      </Box>

      <DataGrid
        title="Listado de Personal Técnico"
        subtitle="Sincronizado desde el sistema maestro"
        columnDefs={columnDefs}
        rowData={data?.data}
        loading={isLoading}
      />
    </Container>
  );
}
