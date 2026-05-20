export const emptyOverview = {
  generated_at: null,
  health: { status: "unknown" },
  metrics: {
    api_up: null,
    requests_per_minute: null,
    errors_5xx_per_second: null,
    latency_p95_seconds: null,
    latency_avg_seconds: null,
    endpoints: [],
  },
  prometheus: {
    available: false,
    targets: [],
  },
  grafana: {
    available: false,
    dashboards: [],
    dashboard_url: "http://localhost:3001/d/obrail-api-monitoring/obrail-api-monitoring",
  },
  docker: {
    available: false,
    services: [],
  },
  reports: {
    quality: {},
    diagnostic: null,
  },
};
