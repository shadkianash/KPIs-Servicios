import React from "react";
import { Card, Text, Group, Box } from "@mantine/core";

interface KPICardProps {
  title: string;
  value: string | number;
  trend?: string;
  trendDirection?: "up" | "down" | "neutral";
  icon?: string;
}

export default function KPICard({
  title,
  value,
  trend,
  trendDirection = "neutral",
  icon,
}: KPICardProps): React.JSX.Element {
  const trendColor =
    trendDirection === "up"
      ? "var(--mantine-color-green-6)"
      : trendDirection === "down"
        ? "var(--mantine-color-red-6)"
        : "var(--mantine-color-dimmed)";

  return (
    <Card shadow="sm" radius="md" withBorder p="md">
      <Group justify="space-between" align="flex-start">
        <Box style={{ flex: 1 }}>
          <Text
            size="xs"
            fw={700}
            c="dimmed"
            style={{ letterSpacing: "0.5px" }}
          >
            {title.toUpperCase()}
          </Text>
          <Text size="xl" fw={800} mt="xs">
            {value}
          </Text>
        </Box>
        {icon && (
          <Box
            style={{
              fontSize: "24px",
              padding: "6px",
              backgroundColor: "var(--mantine-color-blue-light)",
              borderRadius: "8px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            {icon}
          </Box>
        )}
      </Group>

      {trend && (
        <Group gap="xs" mt="xs">
          <Text size="xs" fw={700} style={{ color: trendColor }}>
            {trendDirection === "up"
              ? "▲"
              : trendDirection === "down"
                ? "▼"
                : "•"}{" "}
            {trend}
          </Text>
          <Text size="xs" c="dimmed">
            vs período anterior
          </Text>
        </Group>
      )}
    </Card>
  );
}
