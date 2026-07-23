import React, { useMemo } from "react";
import { Container, Title, Text, Box } from "@mantine/core";
import { useClients } from "../hooks/analyticsHooks";
import DataGrid from "../components/DataGrid";
import { ColDef } from "ag-grid-community";
import { CatalogItem } from "../types";

export default function ClientsPage(): React.JSX.Element {
  const { data, isLoading } = useClients(1, 100);

  const columnDefs = useMemo<ColDef<CatalogItem>[]>(
    () => [
      {
        field: "id",
        headerName: "ID de Cliente",
        sortable: true,
        filter: true,
        flex: 1,
      },
      {
        field: "name",
        headerName: "Razón Social / Nombre",
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
        <Title order={1}>Clientes</Title>
        <Text size="sm" c="dimmed">
          Catálogo completo de clientes y corporativos con soporte contratado
          activo
        </Text>
      </Box>

      <DataGrid
        title="Listado de Clientes"
        subtitle="Entidades con monitoreo y escalado activo"
        columnDefs={columnDefs}
        rowData={data?.data}
        loading={isLoading}
      />
    </Container>
  );
}
