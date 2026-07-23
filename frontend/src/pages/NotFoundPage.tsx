import React from "react";
import { Title, Text, Button, Container, Stack } from "@mantine/core";
import { useNavigate } from "react-router-dom";

export default function NotFoundPage(): React.JSX.Element {
  const navigate = useNavigate();
  return (
    <Container
      fluid
      style={{
        height: "60vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <Stack align="center" gap="md">
        <Title
          order={1}
          style={{ fontSize: 48, color: "var(--mantine-color-red-6)" }}
        >
          404
        </Title>
        <Title order={3}>Página no encontrada</Title>
        <Text c="dimmed">
          La página que está buscando no existe o ha sido movida.
        </Text>
        <Button onClick={() => navigate("/")} variant="light">
          Volver al Inicio
        </Button>
      </Stack>
    </Container>
  );
}
