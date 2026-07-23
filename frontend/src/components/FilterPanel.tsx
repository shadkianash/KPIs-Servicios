import React from "react";
import { useSearchParams } from "react-router-dom";
import {
  Card,
  Group,
  Select,
  TextInput,
  Button,
  Stack,
  Text,
  Collapse,
} from "@mantine/core";
import {
  useClients,
  useTechnologies,
  useEngineers,
  useTeams,
} from "../hooks/analyticsHooks";

export default function FilterPanel(): React.JSX.Element {
  const [searchParams, setSearchParams] = useSearchParams();
  const [filtersOpen, setFiltersOpen] = React.useState<boolean>(true);

  // Retrieve current active filters from URL query parameters
  const startDate = searchParams.get("startDate") || "";
  const endDate = searchParams.get("endDate") || "";
  const clientId = searchParams.get("clientId") || "";
  const technologyId = searchParams.get("technologyId") || "";
  const engineerId = searchParams.get("engineerId") || "";
  const teamId = searchParams.get("teamId") || "";

  // Query actual metadata dropdown catalogs via our React Query hooks
  const { data: clientsData, isLoading: loadingClients } = useClients(1, 100);
  const { data: technologiesData, isLoading: loadingTechs } = useTechnologies(
    1,
    100
  );
  const { data: engineersData, isLoading: loadingEngineers } = useEngineers(
    1,
    100
  );
  const { data: teamsData, isLoading: loadingTeams } = useTeams(1, 100);

  // Convert API structures to Mantine Select options format
  const clientOptions = (clientsData?.data || []).map((x) => ({
    value: x.id,
    label: x.name,
  }));
  const techOptions = (technologiesData?.data || []).map((x) => ({
    value: x.id,
    label: x.name,
  }));
  const engOptions = (engineersData?.data || []).map((x) => ({
    value: x.id,
    label: x.name,
  }));
  const teamOptions = (teamsData?.data || []).map((x) => ({
    value: x.id,
    label: x.name,
  }));

  // Dynamic filter updater helper
  const updateFilter = (key: string, value: string | null) => {
    const nextParams = new URLSearchParams(searchParams);
    if (value) {
      nextParams.set(key, value);
    } else {
      nextParams.delete(key);
    }
    // Reset to page 1 on filter modification to avoid out-of-bounds pages
    nextParams.set("page", "1");
    setSearchParams(nextParams);
  };

  // Reset all filters
  const resetFilters = () => {
    const nextParams = new URLSearchParams();
    nextParams.set("page", "1");
    nextParams.set("pageSize", "50");
    setSearchParams(nextParams);
  };

  const hasActiveFilters =
    startDate || endDate || clientId || technologyId || engineerId || teamId;

  return (
    <Card shadow="sm" radius="md" withBorder p="md" mb="md">
      <Group
        justify="space-between"
        align="center"
        style={{ cursor: "pointer" }}
        onClick={() => setFiltersOpen(!filtersOpen)}
      >
        <Group gap="xs">
          <span style={{ fontSize: "18px" }}>🔍</span>
          <Text size="sm" fw={700}>
            Filtros Avanzados de Datos{" "}
            {hasActiveFilters && (
              <span style={{ color: "var(--mantine-color-blue-filled)" }}>
                (Activos)
              </span>
            )}
          </Text>
        </Group>
        <Button size="xs" variant="subtle">
          {filtersOpen ? "Contraer ▲" : "Expandir ▼"}
        </Button>
      </Group>

      <Collapse in={filtersOpen}>
        <Stack gap="sm" mt="md">
          <Group grow align="flex-end" gap="sm">
            {/* Date Range Inputs */}
            <TextInput
              label="Fecha Desde"
              placeholder="YYYY-MM-DD"
              type="date"
              value={startDate}
              onChange={(e) =>
                updateFilter("startDate", e.target.value || null)
              }
            />
            <TextInput
              label="Fecha Hasta"
              placeholder="YYYY-MM-DD"
              type="date"
              value={endDate}
              onChange={(e) => updateFilter("endDate", e.target.value || null)}
            />
          </Group>

          <Group grow align="flex-end" gap="sm">
            {/* Entity Catalogs Select Dropdowns */}
            <Select
              label="Cliente"
              placeholder={
                loadingClients ? "Cargando..." : "Seleccionar cliente"
              }
              data={clientOptions}
              value={clientId || null}
              onChange={(val) => updateFilter("clientId", val)}
              clearable
              searchable
              disabled={loadingClients}
            />
            <Select
              label="Tecnología"
              placeholder={
                loadingTechs ? "Cargando..." : "Seleccionar tecnología"
              }
              data={techOptions}
              value={technologyId || null}
              onChange={(val) => updateFilter("technologyId", val)}
              clearable
              searchable
              disabled={loadingTechs}
            />
          </Group>

          <Group grow align="flex-end" gap="sm">
            <Select
              label="Ingeniero"
              placeholder={
                loadingEngineers ? "Cargando..." : "Seleccionar ingeniero"
              }
              data={engOptions}
              value={engineerId || null}
              onChange={(val) => updateFilter("engineerId", val)}
              clearable
              searchable
              disabled={loadingEngineers}
            />
            <Select
              label="Equipo"
              placeholder={loadingTeams ? "Cargando..." : "Seleccionar equipo"}
              data={teamOptions}
              value={teamId || null}
              onChange={(val) => updateFilter("teamId", val)}
              clearable
              searchable
              disabled={loadingTeams}
            />
          </Group>

          {hasActiveFilters && (
            <Group justify="flex-end" mt="xs">
              <Button
                size="xs"
                color="red"
                variant="light"
                onClick={resetFilters}
              >
                Limpiar Filtros
              </Button>
            </Group>
          )}
        </Stack>
      </Collapse>
    </Card>
  );
}
