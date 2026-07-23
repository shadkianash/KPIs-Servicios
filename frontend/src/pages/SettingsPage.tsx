import React from "react";
import {
  Container,
  Title,
  Text,
  Card,
  Stack,
  Switch,
  Group,
  Box,
  Button,
} from "@mantine/core";

export default function SettingsPage(): React.JSX.Element {
  return (
    <Container fluid>
      <Box mb="md">
        <Title order={1}>Configuración</Title>
        <Text size="sm" c="dimmed">
          Administración de parámetros de cálculo de KPIs, umbrales y conexiones
        </Text>
      </Box>

      <Card shadow="sm" radius="md" withBorder p="lg">
        <Stack gap="md">
          <Box>
            <Text size="md" fw={700} mb="xs">
              Cálculo de SLA por Defecto
            </Text>
            <Text size="xs" c="dimmed" mb="md">
              Establece el objetivo de tiempo de resolución para las colas
              operativas.
            </Text>
            <Switch
              label="Habilitar horas de exclusión de fin de semana"
              defaultChecked
              disabled
            />
          </Box>

          <Box>
            <Text size="md" fw={700} mb="xs">
              Ingesta de Datos
            </Text>
            <Text size="xs" c="dimmed" mb="md">
              Determina el comportamiento ante discrepancias o inconsistencias
              en los campos del archivo CSV.
            </Text>
            <Switch
              label="Ignorar filas con errores leves de formato"
              defaultChecked
              disabled
            />
          </Box>

          <Box>
            <Text size="md" fw={700} mb="xs">
              Caché del Servidor
            </Text>
            <Text size="xs" c="dimmed" mb="md">
              Administra la persistencia temporal de Redis para optimizar la
              velocidad.
            </Text>
            <Group>
              <Button size="xs" variant="outline" color="red" disabled>
                Vaciar Caché de Redis
              </Button>
            </Group>
          </Box>
        </Stack>
      </Card>
    </Container>
  );
}
