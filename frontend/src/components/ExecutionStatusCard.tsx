import React from "react";
import { Card, Group, Badge, Text, Stack, Grid, Box } from "@mantine/core";
import { KPIExecution } from "../types";

interface ExecutionStatusCardProps {
  execution: KPIExecution;
}

export default function ExecutionStatusCard({
  execution,
}: ExecutionStatusCardProps): React.JSX.Element {
  const statusColor =
    execution.execution_status === "COMPLETED"
      ? "green"
      : execution.execution_status === "FAILED"
        ? "red"
        : "blue";

  const dateStr = execution.started_at
    ? new Date(execution.started_at).toLocaleString("es-ES")
    : "Fecha desconocida";

  return (
    <Card shadow="xs" radius="md" withBorder p="md">
      <Group justify="space-between" mb="xs">
        <Box>
          <Text size="sm" fw={700}>
            ID de Ejecución: {execution.execution_id.substring(0, 8)}...
          </Text>
          <Text size="xs" c="dimmed">
            {dateStr}
          </Text>
        </Box>
        <Badge color={statusColor} variant="light">
          {execution.execution_status}
        </Badge>
      </Group>

      <Grid grow mt="sm">
        <Grid.Col span={4}>
          <Stack gap={2}>
            <Text size="xs" c="dimmed">
              Tickets Procesados
            </Text>
            <Text size="sm" fw={700}>
              {execution.processed_tickets}
            </Text>
          </Stack>
        </Grid.Col>
        <Grid.Col span={4}>
          <Stack gap={2}>
            <Text size="xs" c="dimmed">
              Horas de Trabajo
            </Text>
            <Text size="sm" fw={700}>
              {execution.processed_time_entries}
            </Text>
          </Stack>
        </Grid.Col>
        <Grid.Col span={4}>
          <Stack gap={2}>
            <Text size="xs" c="dimmed">
              Snapshots Generados
            </Text>
            <Text size="sm" fw={700}>
              {execution.generated_daily_snapshots +
                execution.generated_monthly_snapshots}
            </Text>
          </Stack>
        </Grid.Col>
      </Grid>
    </Card>
  );
}
