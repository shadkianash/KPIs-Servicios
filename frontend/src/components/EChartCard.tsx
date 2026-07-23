import React, { useEffect, useRef } from "react";
import { Card, Text, LoadingOverlay, Center, Box } from "@mantine/core";
import * as echarts from "echarts";
import { useUIStore } from "../stores/uiStore";

interface EChartCardProps {
  title: string;
  subtitle?: string;
  loading?: boolean;
  options: echarts.EChartsOption;
  height?: number | string;
}

export default function EChartCard({
  title,
  subtitle,
  loading = false,
  options,
  height = 300,
}: EChartCardProps): React.JSX.Element {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);
  const themeMode = useUIStore((state) => state.themeMode);

  // Initialize & configure the chart canvas
  useEffect(() => {
    if (!chartRef.current) return;

    // Detect light vs dark theme for charts
    const isDark =
      themeMode === "dark" ||
      (themeMode === "system" &&
        window.matchMedia("(prefers-color-scheme: dark)").matches);

    // Initialize ECharts instance
    chartInstance.current = echarts.init(
      chartRef.current,
      isDark ? "dark" : undefined
    );
    chartInstance.current.setOption(options);

    // Dynamic resize handler using ResizeObserver
    const resizeObserver = new ResizeObserver(() => {
      chartInstance.current?.resize();
    });
    resizeObserver.observe(chartRef.current);

    return () => {
      resizeObserver.disconnect();
      chartInstance.current?.dispose();
      chartInstance.current = null;
    };
  }, [options, themeMode]);

  return (
    <Card shadow="sm" radius="md" withBorder style={{ position: "relative" }}>
      <LoadingOverlay
        visible={loading}
        zIndex={1000}
        overlayProps={{ radius: "sm", blur: 1 }}
      />

      <Box mb="sm">
        <Text size="md" fw={700}>
          {title}
        </Text>
        {subtitle && (
          <Text size="xs" c="dimmed">
            {subtitle}
          </Text>
        )}
      </Box>

      <Box style={{ width: "100%", height }}>
        {options && (
          <div
            ref={chartRef}
            style={{ width: "100%", height: "100%", minHeight: "150px" }}
          />
        )}
        {!options && !loading && (
          <Center style={{ height: "100%" }}>
            <Text size="sm" c="dimmed">
              Sin datos disponibles
            </Text>
          </Center>
        )}
      </Box>
    </Card>
  );
}
