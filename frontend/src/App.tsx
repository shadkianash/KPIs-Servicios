import React from "react";
import { MantineProvider, Title, Text, Stack, Card } from "@mantine/core";
import { theme } from "./theme/theme";
import AppLayout from "./layouts/AppLayout";
import HealthPage from "./pages/HealthPage";

export default function App(): React.JSX.Element {
  return (
    <MantineProvider theme={theme}>
      <AppLayout>
        <Stack gap="xl">
          <Card shadow="xs" padding="lg" radius="md" withBorder>
            <Title order={2} style={{ color: "#2d3748" }} mb="xs">
              KPIs Servicios
            </Title>
            <Text size="md" c="dimmed" fw={500}>
              Bootstrap completed successfully.
            </Text>
          </Card>

          <HealthPage />
        </Stack>
      </AppLayout>
    </MantineProvider>
  );
}
