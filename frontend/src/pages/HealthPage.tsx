import React, { useEffect, useState } from "react";
import { Alert, Badge, Card, Group, Loader, Text } from "@mantine/core";
import { apiClient } from "../services/apiClient";

interface HealthData {
  status: string;
  service: string;
  version: string;
}

export default function HealthPage(): React.JSX.Element {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiClient
      .get<HealthData>("/health")
      .then((res) => {
        setHealth(res.data);
        setError(null);
      })
      .catch((err) => {
        console.error("Failed to fetch health state:", err);
        setError("Backend is unreachable. Please verify if the API service is currently active.");
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  return (
    <Card shadow="sm" padding="lg" radius="md" withBorder style={{ maxWidth: 450, margin: "20px auto" }}>
      <Text fw={700} size="lg" mb="md">
        Backend status
      </Text>

      {loading && (
        <Group align="center" gap="xs">
          <Loader size="sm" />
          <Text size="sm" c="dimmed">
            Fetching API health status...
          </Text>
        </Group>
      )}

      {error && (
        <Alert color="red" title="Connection Error" radius="md">
          {error}
        </Alert>
      )}

      {health && (
        <Group justify="space-between" align="center">
          <div>
            <Text size="sm" fw={500}>
              Service: {health.service}
            </Text>
            <Text size="xs" c="dimmed">
              Version: {health.version}
            </Text>
          </div>
          <Badge color={health.status === "ok" ? "green" : "orange"} variant="light" size="lg">
            {health.status.toUpperCase()}
          </Badge>
        </Group>
      )}
    </Card>
  );
}
