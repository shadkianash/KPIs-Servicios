import React from "react";
import { Center, Stack, Title, Text } from "@mantine/core";

export default function App(): React.JSX.Element {
  return (
    <Center
      style={{ width: "100vw", height: "100vh", backgroundColor: "#f8f9fa" }}
    >
      <Stack align="center" gap="md">
        <Title order={1} style={{ color: "#228be6" }}>
          KPIs Servicios
        </Title>
        <Text size="xl" fw={500} c="dimmed">
          Bootstrap completed successfully.
        </Text>
      </Stack>
    </Center>
  );
}
