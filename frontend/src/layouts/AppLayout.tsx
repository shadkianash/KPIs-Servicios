import React from "react";
import {
  AppShell,
  Burger,
  Group,
  Text,
  NavLink,
  Stack,
  Box,
} from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";

interface AppLayoutProps {
  children: React.ReactNode;
}

export default function AppLayout({
  children,
}: AppLayoutProps): React.JSX.Element {
  const [opened, { toggle }] = useDisclosure();

  return (
    <AppShell
      header={{ height: 60 }}
      navbar={{
        width: 250,
        breakpoint: "sm",
        collapsed: { mobile: !opened },
      }}
      padding="md"
    >
      <AppShell.Header>
        <Group h="100%" px="md">
          <Burger opened={opened} onClick={toggle} hiddenFrom="sm" size="sm" />
          <Text size="lg" fw={700} style={{ color: "#228be6" }}>
            KPIs Servicios
          </Text>
        </Group>
      </AppShell.Header>

      <AppShell.Navbar p="md">
        <Stack gap="xs">
          <Text size="xs" fw={700} c="dimmed" px="xs" mb="xs">
            NAVIGATION
          </Text>
          <NavLink label="Health Status" active />
          <NavLink label="Dashboard (Placeholder)" disabled />
          <NavLink label="KPI Configuration" disabled />
        </Stack>
      </AppShell.Navbar>

      <AppShell.Main style={{ backgroundColor: "#f8f9fa" }}>
        <Box style={{ minHeight: "calc(100vh - 140px)" }}>{children}</Box>
        <Box
          component="footer"
          style={{
            borderTop: "1px solid #e9ecef",
            paddingTop: 15,
            marginTop: 30,
          }}
        >
          <Group justify="space-between" px="md">
            <Text size="xs" c="dimmed">
              © 2026 Maximiliano Cittadini. All rights reserved.
            </Text>
            <Text size="xs" c="dimmed">
              Version 0.1.0
            </Text>
          </Group>
        </Box>
      </AppShell.Main>
    </AppShell>
  );
}
