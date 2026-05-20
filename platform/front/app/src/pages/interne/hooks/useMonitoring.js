import { useCallback, useEffect, useState } from "react";
import { emptyOverview } from "../../../services/mockData";
import { getInternalOverview, runInternalDiagnostic, streamInternalTestsCategory } from "../../../services/api_interne";

const TEST_CATEGORIES = [
  { key: "unit", label: "Unit Tests" },
  { key: "integration", label: "Integration Tests" },
  { key: "backend-e2e", label: "Backend E2E" },
  { key: "frontend-e2e", label: "Frontend E2E" },
];

const initialTestsState = TEST_CATEGORIES.reduce((acc, item) => {
  acc[item.key] = {
    label: item.label,
    running: false,
    status: "idle",
    lines: [],
    count: 0,
    error: "",
  };
  return acc;
}, {});

export function useMonitoring(refreshMs = 30000) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [lastUpdated, setLastUpdated] = useState("");
  const [actionState, setActionState] = useState({
    runningDiagnostic: false,
    diagnostic: null,
    tests: initialTestsState,
  });

  const refresh = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const overview = await getInternalOverview();
      setData(overview);
      setLastUpdated(new Date().toLocaleString());
    } catch (err) {
      setError(err.message || "Impossible de charger les donnees internes.");
      setData((current) => current || emptyOverview);
    } finally {
      setLoading(false);
    }
  }, []);

  const runDiagnostic = useCallback(async () => {
    setActionState((current) => ({ ...current, runningDiagnostic: true }));
    try {
      const result = await runInternalDiagnostic();
      setActionState((current) => ({ ...current, diagnostic: result, runningDiagnostic: false }));
      await refresh();
    } catch (err) {
      setActionState((current) => ({
        ...current,
        runningDiagnostic: false,
        diagnostic: { success: false, error: err.message },
      }));
    }
  }, [refresh]);

  const runTestsByCategory = useCallback(async (category) => {
    let stream = null;
    setActionState((current) => ({
      ...current,
      tests: {
        ...current.tests,
        [category]: {
          ...(current.tests?.[category] || {}),
          running: true,
          status: "running",
          lines: [],
          count: 0,
          error: "",
        },
      },
    }));

    try {
      await new Promise((resolve) => {
        stream = streamInternalTestsCategory(
          category,
          (payload) => {
            setActionState((current) => {
              const prev = current.tests?.[category] || {};
              const nextLines = payload.kind === "log" ? [...(prev.lines || []), payload.line] : (prev.lines || []);
              let nextStatus = prev.status || "running";
              if (payload.kind === "section_end") {
                nextStatus = payload.line.includes(": ok") ? "passed" : "failed";
              }
              return {
                ...current,
                tests: {
                  ...current.tests,
                  [category]: {
                    ...prev,
                    lines: nextLines,
                    count: nextLines.length,
                    status: nextStatus,
                  },
                },
              };
            });
          },
          (err) => {
            setActionState((current) => ({
              ...current,
              tests: {
                ...current.tests,
                [category]: {
                  ...(current.tests?.[category] || {}),
                  running: false,
                  status: "failed",
                  error: err?.message || "Erreur de streaming des tests.",
                },
              },
            }));
            resolve();
          },
          () => {
            setActionState((current) => ({
              ...current,
              tests: {
                ...current.tests,
                [category]: {
                  ...(current.tests?.[category] || {}),
                  running: false,
                  status: (current.tests?.[category]?.status === "failed") ? "failed" : (current.tests?.[category]?.status || "passed"),
                },
              },
            }));
            resolve();
          }
        );
      });
    } finally {
      if (stream) stream.close();
    }
  }, []);

  useEffect(() => {
    refresh();
    const interval = window.setInterval(refresh, refreshMs);
    return () => window.clearInterval(interval);
  }, [refresh, refreshMs]);

  return {
    data,
    loading,
    error,
    lastUpdated,
    refresh,
    runDiagnostic,
    runTestsByCategory,
    actionState,
    testCategories: TEST_CATEGORIES,
  };
}
