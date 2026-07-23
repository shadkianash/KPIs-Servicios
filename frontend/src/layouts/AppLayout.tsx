import React from "react";
import { useLocation, Link } from "react-router-dom";
import {
  AppShell,
  Group,
  Text,
  ActionIcon,
  Stack,
  Box,
  Breadcrumbs,
  Anchor,
  ColorSchemeScript,
  useMantineColorScheme,
  Menu,
} from "@mantine/core";
import { useUIStore, ThemeMode } from "../stores/uiStore";
import ErrorBoundary from "../components/ErrorBoundary";

interface AppLayoutProps {
  children: React.ReactNode;
}

// Map pathnames to Spanish labels for Breadcrumbs
const BREADCRUMB_MAP: Record<string, string> = {
  "": "Inicio",
  engineers: "Ingenieros",
  clients: "Clientes",
  technologies: "Tecnologías",
  teams: "Equipos",
  executions: "Ejecuciones",
  settings: "Configuración",
  "not-found": "No Encontrado",
};

export default function AppLayout({
  children,
}: AppLayoutProps): React.JSX.Element {
  const location = useLocation();
  const { setColorScheme } = useMantineColorScheme();

  const { themeMode, setThemeMode, sidebarCollapsed, toggleSidebar } =
    useUIStore();

  // Sync stateful theme mode with Mantine's native hook on load
  React.useEffect(() => {
    if (themeMode === "system") {
      setColorScheme("auto");
    } else {
      setColorScheme(themeMode);
    }
  }, [themeMode, setColorScheme]);

  // Handle manual theme changes
  const handleThemeChange = (mode: ThemeMode) => {
    setThemeMode(mode);
  };

  // Derive breadcrumbs dynamically
  const pathnames = location.pathname.split("/").filter((x) => x);
  const breadcrumbItems = [
    <Anchor key="home" component={Link} to="/" size="sm" fw={500}>
      Inicio
    </Anchor>,
    ...pathnames.map((value, index) => {
      const last = index === pathnames.length - 1;
      const to = `/${pathnames.slice(0, index + 1).join("/")}`;
      const label = BREADCRUMB_MAP[value] || value;

      return last ? (
        <Text key={to} size="sm" c="dimmed">
          {label}
        </Text>
      ) : (
        <Anchor key={to} component={Link} to={to} size="sm">
          {label}
        </Anchor>
      );
    }),
  ];

  const currentYear = new Date().getFullYear();

  return (
    <>
      <ColorSchemeScript defaultColorScheme="auto" />
      <AppShell
        header={{ height: 60 }}
        navbar={{
          width: sidebarCollapsed ? 80 : 250,
          breakpoint: "sm",
        }}
        padding="md"
      >
        {/* Header Block */}
        <AppShell.Header
          style={{
            borderBottom: "1px solid var(--mantine-color-default-border)",
          }}
        >
          <Group h="100%" px="md" justify="space-between">
            <Group>
              <ActionIcon
                variant="subtle"
                onClick={toggleSidebar}
                size="lg"
                aria-label="Toggle Sidebar"
              >
                <span style={{ fontSize: "20px" }}>☰</span>
              </ActionIcon>
              <Text
                size="lg"
                fw={800}
                style={{
                  color: "var(--mantine-color-blue-filled)",
                  letterSpacing: "0.5px",
                }}
              >
                CSAP Analytics
              </Text>
            </Group>

            <Group gap="sm">
              <Menu shadow="md" width={140}>
                <Menu.Target>
                  <ActionIcon
                    variant="light"
                    size="lg"
                    title="Cambiar Tema"
                    aria-label="Cambiar Tema"
                  >
                    {themeMode === "light"
                      ? "☀️"
                      : themeMode === "dark"
                        ? "🌙"
                        : "💻"}
                  </ActionIcon>
                </Menu.Target>
                <Menu.Dropdown>
                  <Menu.Item
                    onClick={() => handleThemeChange("light")}
                    leftSection="☀️"
                  >
                    Claro
                  </Menu.Item>
                  <Menu.Item
                    onClick={() => handleThemeChange("dark")}
                    leftSection="🌙"
                  >
                    Oscuro
                  </Menu.Item>
                  <Menu.Item
                    onClick={() => handleThemeChange("system")}
                    leftSection="💻"
                  >
                    Sistema
                  </Menu.Item>
                </Menu.Dropdown>
              </Menu>
            </Group>
          </Group>
        </AppShell.Header>

        {/* Sidebar Navigation Block */}
        <AppShell.Navbar p="xs">
          <Stack gap="xs" style={{ flex: 1 }}>
            {!sidebarCollapsed && (
              <Text
                size="xs"
                fw={800}
                c="dimmed"
                px="sm"
                style={{ letterSpacing: "1px" }}
              >
                MENÚ DE NAVEGACIÓN
              </Text>
            )}

            <Box>
              <Stack gap="4">
                {[
                  { path: "/", label: "Cuadro de Mando", icon: "📊" },
                  { path: "/engineers", label: "Ingenieros", icon: "👥" },
                  { path: "/clients", label: "Clientes", icon: "🏢" },
                  { path: "/technologies", label: "Tecnologías", icon: "🛠️" },
                  { path: "/teams", label: "Equipos", icon: "🛡️" },
                  { path: "/executions", label: "Ejecuciones", icon: "📜" },
                  { path: "/settings", label: "Configuración", icon: "⚙️" },
                ].map((item) => {
                  const isActive = location.pathname === item.path;
                  return (
                    <Box
                      key={item.path}
                      component={Link}
                      to={item.path}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        padding: "10px 14px",
                        borderRadius: "8px",
                        textDecoration: "none",
                        color: isActive
                          ? "var(--mantine-color-blue-filled)"
                          : "var(--mantine-color-text)",
                        backgroundColor: isActive
                          ? "var(--mantine-color-blue-light)"
                          : "transparent",
                        transition: "background-color 0.2s, color 0.2s",
                        fontWeight: isActive ? 600 : 500,
                        fontSize: "14px",
                      }}
                    >
                      <span
                        style={{
                          fontSize: "18px",
                          marginRight: sidebarCollapsed ? "0" : "12px",
                        }}
                      >
                        {item.icon}
                      </span>
                      {!sidebarCollapsed && <span>{item.label}</span>}
                    </Box>
                  );
                })}
              </Stack>
            </Box>
          </Stack>
        </AppShell.Navbar>

        {/* Main Workspace Frame */}
        <AppShell.Main
          style={{
            display: "flex",
            flexDirection: "column",
            minHeight: "100vh",
          }}
        >
          {/* Breadcrumbs Banner */}
          <Box mb="md" mt="xs">
            <Breadcrumbs separator="→">{breadcrumbItems}</Breadcrumbs>
          </Box>

          {/* Core Content Box wrapper in error boundaries */}
          <Box style={{ flex: 1 }}>
            <ErrorBoundary>{children}</ErrorBoundary>
          </Box>

          {/* Footer block */}
          <Box
            component="footer"
            style={{
              borderTop: "1px solid var(--mantine-color-default-border)",
              paddingTop: "20px",
              paddingBottom: "10px",
              marginTop: "40px",
            }}
          >
            <Group justify="space-between" px="md">
              <Text size="xs" c="dimmed">
                © {currentYear} Cyber Services Analytics Platform (CSAP). Todos
                los derechos reservados.
              </Text>
              <Text size="xs" c="dimmed" fw={600}>
                Versión 1.0.0
              </Text>
            </Group>
          </Box>
        </AppShell.Main>
      </AppShell>
    </>
  );
}
