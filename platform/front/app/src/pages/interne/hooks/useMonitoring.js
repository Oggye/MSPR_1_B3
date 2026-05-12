import { useCallback, useEffect, useState } from "react";
import { emptyOverview } from "../services/mockData";
import { getInternalOverview, runInternalDiagnostic, runInternalTests } from "../services/api";

export function useMonitoring(refreshMs = 30000) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [lastUpdated, setLastUpdated] = useState("");
  const [actionState, setActionState] = useState({
    runningDiagnostic: false,
    runningTests: false,
    diagnostic: null,
    tests: null,
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

  const runTests = useCallback(async () => {
    setActionState((current) => ({ ...current, runningTests: true }));
    try {
      const result = await runInternalTests();
      setActionState((current) => ({ ...current, tests: result, runningTests: false }));
    } catch (err) {
      setActionState((current) => ({
        ...current,
        runningTests: false,
        tests: { success: false, error: err.message },
      }));
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
    runTests,
    actionState,
  };
}
