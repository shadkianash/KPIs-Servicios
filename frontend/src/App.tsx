import React, { Suspense, lazy } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { MantineProvider, Loader, Center } from "@mantine/core";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { theme } from "./theme/theme";
import AppLayout from "./layouts/AppLayout";

// Initialize TanStack QueryClient
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

// Lazy loaded Pages for optimal code splitting
const DashboardPage = lazy(() => import("./pages/DashboardPage"));
const EngineersPage = lazy(() => import("./pages/EngineersPage"));
const ClientsPage = lazy(() => import("./pages/ClientsPage"));
const TechnologiesPage = lazy(() => import("./pages/TechnologiesPage"));
const TeamsPage = lazy(() => import("./pages/TeamsPage"));
const ExecutionsPage = lazy(() => import("./pages/ExecutionsPage"));
const SettingsPage = lazy(() => import("./pages/SettingsPage"));
const NotFoundPage = lazy(() => import("./pages/NotFoundPage"));

// Page Loader spinner fallback
const PageLoader = (): React.JSX.Element => (
  <Center style={{ height: "50vh" }}>
    <Loader size="lg" variant="dots" />
  </Center>
);

export default function App(): React.JSX.Element {
  return (
    <QueryClientProvider client={queryClient}>
      <MantineProvider theme={theme} defaultColorScheme="light">
        <BrowserRouter>
          <AppLayout>
            <Suspense fallback={<PageLoader />}>
              <Routes>
                <Route path="/" element={<DashboardPage />} />
                <Route path="/engineers" element={<EngineersPage />} />
                <Route path="/clients" element={<ClientsPage />} />
                <Route path="/technologies" element={<TechnologiesPage />} />
                <Route path="/teams" element={<TeamsPage />} />
                <Route path="/executions" element={<ExecutionsPage />} />
                <Route path="/settings" element={<SettingsPage />} />
                <Route path="/not-found" element={<NotFoundPage />} />
                <Route
                  path="*"
                  element={<Navigate to="/not-found" replace />}
                />
              </Routes>
            </Suspense>
          </AppLayout>
        </BrowserRouter>
      </MantineProvider>
    </QueryClientProvider>
  );
}
