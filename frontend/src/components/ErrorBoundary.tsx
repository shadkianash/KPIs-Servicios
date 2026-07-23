import React, { Component, ErrorInfo, ReactNode } from "react";
import {
  Card,
  Title,
  Text,
  Button,
  Stack,
  Container,
  Center,
} from "@mantine/core";

interface Props {
  children?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error(
      "ErrorBoundary caught an uncaught exception:",
      error,
      errorInfo
    );
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.href = "/";
  };

  public render() {
    if (this.state.hasError) {
      return (
        <Container size="sm" py="xl">
          <Center style={{ minHeight: "60vh" }}>
            <Card
              shadow="md"
              padding="xl"
              radius="md"
              withBorder
              style={{ width: "100%" }}
            >
              <Stack align="center" gap="md">
                <Title
                  order={2}
                  style={{ color: "var(--mantine-color-red-6)" }}
                >
                  ¡Algo salió mal!
                </Title>
                <Text size="md" ta="center">
                  Ha ocurrido un error inesperado al renderizar esta sección de
                  la aplicación.
                </Text>
                {this.state.error && (
                  <Text
                    size="sm"
                    c="dimmed"
                    style={{ fontStyle: "italic", wordBreak: "break-all" }}
                  >
                    Detalle: {this.state.error.message}
                  </Text>
                )}
                <Button
                  onClick={this.handleReset}
                  variant="outline"
                  color="red"
                >
                  Volver a cargar la aplicación
                </Button>
              </Stack>
            </Card>
          </Center>
        </Container>
      );
    }

    return this.props.children;
  }
}
export default ErrorBoundary;
