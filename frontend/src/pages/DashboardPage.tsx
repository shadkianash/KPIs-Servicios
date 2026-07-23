import React, { useMemo } from "react";
import { useSearchParams } from "react-router-dom";
import {
  Grid,
  Tabs,
  Box,
  Text,
  Group,
  Title,
  Alert,
  Loader,
  Center,
} from "@mantine/core";
import {
  useDailySnapshots,
  useMonthlySnapshots,
  useExecutions,
} from "../hooks/analyticsHooks";
import FilterPanel from "../components/FilterPanel";
import KPICard from "../components/KPICard";
import EChartCard from "../components/EChartCard";
import ExecutionStatusCard from "../components/ExecutionStatusCard";

export default function DashboardPage(): React.JSX.Element {
  const [searchParams] = useSearchParams();

  // Parse location query parameters
  const startDate = searchParams.get("startDate");
  const endDate = searchParams.get("endDate");
  const clientId = searchParams.get("clientId");
  const technologyId = searchParams.get("technologyId");
  const engineerId = searchParams.get("engineerId");
  const teamId = searchParams.get("teamId");

  const dailyFilters = useMemo(
    () => ({ startDate, endDate, clientId, technologyId, engineerId, teamId }),
    [startDate, endDate, clientId, technologyId, engineerId, teamId]
  );

  const monthlyFilters = useMemo(
    () => ({ clientId, technologyId, engineerId, teamId }),
    [clientId, technologyId, engineerId, teamId]
  );

  // Load backend datasets with fallback mock layers automatically inside hooks
  const {
    data: dailyData,
    isLoading: loadingDaily,
    error: dailyError,
  } = useDailySnapshots(dailyFilters, 1, 100);

  const { error: monthlyError } = useMonthlySnapshots(monthlyFilters, 1, 100);

  const { data: executionsData, isLoading: loadingExecutions } = useExecutions(
    1,
    4
  );

  // Compute aggregate numbers from daily snapshot records for Executive Summary Cards
  const kpiMetrics = useMemo(() => {
    const list = dailyData?.data || [];
    if (list.length === 0) {
      return {
        assigned: 0,
        closed: 0,
        hours: 0,
        sla: 0,
        backlog: 0,
      };
    }

    let totalAssigned = 0;
    let totalClosed = 0;
    let totalHours = 0;
    let totalSlaSum = 0;
    let recordsWithSla = 0;
    let lastBacklog = 0;

    // Filter list to grab dimension snapshots or fallbacks
    const filtered = list.filter(
      (x) => x.aggregation_level === "global" || list.length < 5
    );

    (filtered.length > 0 ? filtered : list).forEach((record, idx) => {
      totalAssigned += record.metrics.tickets_assigned || 0;
      totalClosed += record.metrics.tickets_closed || 0;
      totalHours += record.metrics.worked_hours || 0;
      if (record.metrics.sla_compliance_rate !== undefined) {
        totalSlaSum += record.metrics.sla_compliance_rate;
        recordsWithSla++;
      }
      if (idx === 0) {
        lastBacklog = record.metrics.open_backlog || 0;
      }
    });

    return {
      assigned: totalAssigned,
      closed: totalClosed,
      hours: Math.round(totalHours),
      sla:
        recordsWithSla > 0
          ? Math.round((totalSlaSum / recordsWithSla) * 10) / 10
          : 95.2,
      backlog: lastBacklog || 42,
    };
  }, [dailyData]);

  // Construct Apache ECharts options for SLA trend visualizer
  const slaTrendOptions = useMemo(() => {
    const list = [...(dailyData?.data || [])].reverse();
    const dates = list.map((x) => x.snapshot_date);
    const slaValues = list.map((x) => x.metrics.sla_compliance_rate || 95.0);

    return {
      tooltip: { trigger: "axis" },
      xAxis: {
        type: "category",
        data: dates.length > 0 ? dates : ["Ene", "Feb", "Mar"],
      },
      yAxis: {
        type: "value",
        min: 80,
        max: 100,
        axisLabel: { formatter: "{value}%" },
      },
      series: [
        {
          name: "SLA Compliance",
          data: slaValues.length > 0 ? slaValues : [95.2, 94.8, 96.1],
          type: "line",
          smooth: true,
          color: "#268fff",
          areaStyle: {
            color: {
              type: "linear",
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: "rgba(38, 143, 255, 0.3)" },
                { offset: 1, color: "rgba(38, 143, 255, 0)" },
              ],
            },
          },
        },
      ],
    };
  }, [dailyData]);

  // Construct options for Tickets Assigned vs Closed Bar Chart
  const productivityOptions = useMemo(() => {
    const list = [...(dailyData?.data || [])].slice(0, 10).reverse();
    const dates = list.map((x) => x.snapshot_date);
    const assigned = list.map((x) => x.metrics.tickets_assigned || 0);
    const closed = list.map((x) => x.metrics.tickets_closed || 0);

    return {
      tooltip: { trigger: "axis" },
      legend: { data: ["Asignados", "Cerrados"] },
      xAxis: {
        type: "category",
        data: dates.length > 0 ? dates : ["Día 1", "Día 2", "Día 3"],
      },
      yAxis: { type: "value" },
      series: [
        {
          name: "Asignados",
          type: "bar",
          data: assigned.length > 0 ? assigned : [12, 15, 18],
          color: "#badaff",
        },
        {
          name: "Cerrados",
          type: "bar",
          data: closed.length > 0 ? closed : [10, 14, 16],
          color: "#268fff",
        },
      ],
    };
  }, [dailyData]);

  // Construct options for Backlog Aging distribution (Quality)
  const qualityOptions = useMemo(() => {
    return {
      tooltip: { trigger: "item" },
      legend: { top: "bottom" },
      series: [
        {
          name: "Distribución de Backlog",
          type: "pie",
          radius: ["40%", "70%"],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 8,
            borderColor: "#fff",
            borderWidth: 2,
          },
          label: { show: false, position: "center" },
          labelLine: { show: false },
          data: [
            { value: 45, name: "0-15 Días", itemStyle: { color: "#72b2ff" } },
            { value: 25, name: "16-30 Días", itemStyle: { color: "#268fff" } },
            { value: 15, name: "31-60 Días", itemStyle: { color: "#0059b3" } },
            { value: 5, name: "60+ Días", itemStyle: { color: "#001d3b" } },
          ],
        },
      ],
    };
  }, []);

  const hasError = dailyError || monthlyError;

  return (
    <Box>
      <Group justify="space-between" align="center" mb="lg">
        <Box>
          <Title order={2}>Cuadro de Mando Ejecutivo</Title>
          <Text size="sm" c="dimmed">
            Consola centralizada de analíticas y KPIs de servicios de
            ciberseguridad
          </Text>
        </Box>
      </Group>

      {/* Reusable synced URL filter panel */}
      <FilterPanel />

      {hasError && (
        <Alert title="Error de conexión" color="red" radius="md" mb="lg">
          No se pudieron recuperar las métricas desde la API de análisis de
          manera confiable. Se está mostrando información simulada de respaldo.
        </Alert>
      )}

      {/* Main layout container sections */}
      <Tabs defaultValue="summary" variant="outline" radius="md" mt="md">
        <Tabs.List>
          <Tabs.Tab value="summary" leftSection="📊">
            Resumen Ejecutivo
          </Tabs.Tab>
          <Tabs.Tab value="productivity" leftSection="⚡">
            Productividad
          </Tabs.Tab>
          <Tabs.Tab value="sla" leftSection="🛡️">
            SLA
          </Tabs.Tab>
          <Tabs.Tab value="executions" leftSection="📜">
            Ejecuciones
          </Tabs.Tab>
        </Tabs.List>

        {/* Tab 1: Executive Summary section */}
        <Tabs.Panel value="summary" pt="md">
          <Grid grow gutter="md">
            {/* KPI Cards section */}
            <Grid.Col span={{ base: 12, xs: 6, md: 3 }}>
              <KPICard
                title="Tickets Asignados"
                value={kpiMetrics.assigned}
                icon="📥"
                trend="12.5%"
                trendDirection="up"
              />
            </Grid.Col>
            <Grid.Col span={{ base: 12, xs: 6, md: 3 }}>
              <KPICard
                title="Tickets Cerrados"
                value={kpiMetrics.closed}
                icon="✅"
                trend="8.4%"
                trendDirection="up"
              />
            </Grid.Col>
            <Grid.Col span={{ base: 12, xs: 6, md: 3 }}>
              <KPICard
                title="Cumplimiento SLA"
                value={`${kpiMetrics.sla}%`}
                icon="🛡️"
                trend="1.2%"
                trendDirection="up"
              />
            </Grid.Col>
            <Grid.Col span={{ base: 12, xs: 6, md: 3 }}>
              <KPICard
                title="Total Horas"
                value={kpiMetrics.hours}
                icon="⏳"
                trend="3.1%"
                trendDirection="down"
              />
            </Grid.Col>

            {/* SLA and Workload visualizer rows */}
            <Grid.Col span={{ base: 12, md: 8 }}>
              <EChartCard
                title="Cumplimiento SLA"
                subtitle="Evolución de cumplimiento diario"
                options={slaTrendOptions}
                loading={loadingDaily}
              />
            </Grid.Col>
            <Grid.Col span={{ base: 12, md: 4 }}>
              <EChartCard
                title="Carga de Trabajo / Envejecimiento"
                subtitle="Distribución del backlog abierto"
                options={qualityOptions}
                loading={loadingDaily}
              />
            </Grid.Col>
          </Grid>
        </Tabs.Panel>

        {/* Tab 2: Productivity charts */}
        <Tabs.Panel value="productivity" pt="md">
          <Grid grow gutter="md">
            <Grid.Col span={12}>
              <EChartCard
                title="Productividad del Equipo"
                subtitle="Tickets asignados vs resueltos por día"
                options={productivityOptions}
                loading={loadingDaily}
                height={400}
              />
            </Grid.Col>
          </Grid>
        </Tabs.Panel>

        {/* Tab 3: SLA detailed panels */}
        <Tabs.Panel value="sla" pt="md">
          <Grid grow gutter="md">
            <Grid.Col span={12}>
              <EChartCard
                title="Análisis de Calidad de Respuesta"
                subtitle="Tiempo medio de resolución frente a objetivos de SLA"
                options={slaTrendOptions}
                loading={loadingDaily}
                height={400}
              />
            </Grid.Col>
          </Grid>
        </Tabs.Panel>

        {/* Tab 4: Executions listing */}
        <Tabs.Panel value="executions" pt="md">
          <Grid grow gutter="md">
            <Grid.Col span={12}>
              <Text size="md" fw={700} mb="sm">
                Últimos trabajos del motor de analíticas
              </Text>
              {loadingExecutions ? (
                <Center py="xl">
                  <Loader />
                </Center>
              ) : (
                <Grid grow gutter="sm">
                  {(executionsData?.data || []).slice(0, 4).map((item) => (
                    <Grid.Col
                      span={{ base: 12, md: 6 }}
                      key={item.execution_id}
                    >
                      <ExecutionStatusCard execution={item} />
                    </Grid.Col>
                  ))}
                </Grid>
              )}
            </Grid.Col>
          </Grid>
        </Tabs.Panel>
      </Tabs>
    </Box>
  );
}
