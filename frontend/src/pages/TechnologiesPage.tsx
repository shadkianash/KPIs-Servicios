import React, { useMemo } from "react";
import { Container, Title, Text, Box } from "@mantine/core";
import { useTechnologies } from "../hooks/analyticsHooks";
import DataGrid from "../components/DataGrid";
import { ColDef } from "ag-grid-community";
import { CatalogItem } from "../types";

export default function TechnologiesPage(): React.JSX.Element {
  const { data, isLoading } = useTechnologies(1, 100);

  const columnDefs = useMemo<ColDef<CatalogItem>[]>(
    () => [
      {
        field: "id",
        headerName: "ID de Tecnología",
        sortable: true,
        filter: true,
        flex: 1,
      },
      {
        field: "name",
        headerName: "Solución de Seguridad",
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
        <Title order={1}>Tecnologías</Title>
        <Text size="sm" c="dimmed">
          Herramientas, EDRs, SIEMs y componentes bajo monitoreo operativo
          activo
        </Text>
      </Box>

      <DataGrid
        title="Catálogo Tecnológico"
        subtitle="Sistemas integrados en la consola de análisis"
        columnDefs={columnDefs}
        rowData={data?.data}
        loading={isLoading}
      />
    </Container>
  );
}
