import { KPICardPolicy, KPIEvaluationResult } from "../types";

// Configurable metric thresholds for future customer-specific SLA policies
export const KPI_POLICIES: Record<string, KPICardPolicy> = {
  sla_compliance: {
    id: "sla_compliance",
    name: "Cumplimiento de SLA",
    target: 95.0,
    warning: 90.0,
    critical: 85.0,
    direction: "higher-is-better",
    unit: "%",
  },
  avg_resolution_time: {
    id: "avg_resolution_time",
    name: "Tiempo Promedio de Resolución",
    target: 24.0, // hours
    warning: 48.0,
    critical: 72.0,
    direction: "lower-is-better",
    unit: "h",
  },
  avg_response_time: {
    id: "avg_response_time",
    name: "Tiempo Promedio de Respuesta",
    target: 1.0, // hours
    warning: 2.0,
    critical: 4.0,
    direction: "lower-is-better",
    unit: "h",
  },
  open_backlog: {
    id: "open_backlog",
    name: "Volumen de Backlog Abierto",
    target: 30, // tickets
    warning: 60,
    critical: 100,
    direction: "lower-is-better",
    unit: " tickets",
  },
  reopened_backlog: {
    id: "reopened_backlog",
    name: "Tickets Reabiertos",
    target: 5,
    warning: 10,
    critical: 20,
    direction: "lower-is-better",
    unit: " tickets",
  },
};

/**
 * Dynamically evaluates a metric value against a configurable threshold policy
 */
export function evaluateKPI(
  metricId: string,
  value: number
): KPIEvaluationResult {
  const policy = KPI_POLICIES[metricId];

  if (!policy) {
    return {
      status: "neutral",
      color: "gray",
      message: "No hay política definida para esta métrica.",
    };
  }

  const { target, warning, direction, unit, name } = policy;

  if (direction === "higher-is-better") {
    if (value >= target) {
      return {
        status: "success",
        color: "green",
        message: `${name} de ${value}${unit} cumple con el objetivo operativo de >= ${target}${unit}.`,
      };
    } else if (value >= warning) {
      return {
        status: "warning",
        color: "orange",
        message: `${name} de ${value}${unit} está por debajo del objetivo operacional pero dentro de la tolerancia de advertencia.`,
      };
    } else {
      return {
        status: "critical",
        color: "red",
        message: `${name} de ${value}${unit} ha caído en el umbral crítico por debajo de ${warning}${unit}.`,
      };
    }
  } else {
    // lower-is-better
    if (value <= target) {
      return {
        status: "success",
        color: "green",
        message: `${name} de ${value}${unit} cumple con el objetivo operativo de <= ${target}${unit}.`,
      };
    } else if (value <= warning) {
      return {
        status: "warning",
        color: "orange",
        message: `${name} de ${value}${unit} ha excedido el objetivo de rendimiento pero está dentro del umbral de advertencia.`,
      };
    } else {
      return {
        status: "critical",
        color: "red",
        message: `${name} de ${value}${unit} está en estado crítico al superar el límite de tolerancia de ${warning}${unit}.`,
      };
    }
  }
}
