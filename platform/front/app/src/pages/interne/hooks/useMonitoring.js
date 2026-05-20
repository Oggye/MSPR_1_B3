import { useCallback, useEffect, useState } from "react";
import { emptyOverview } from "../services/mockData";
import { getInternalOverview, runInternalDiagnostic, runInternalTests, streamInternalTests } from "../services/api";

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
    let stream = null;
    try {
      setActionState((current) => ({
        ...current,
        tests: { success: true, stdout: "", stderr: "", stream: [], streamed: true },
      }));

      stream = streamInternalTests(
        (payload) => {
          setActionState((current) => {
            const previous = current.tests?.stream || [];
            return {
              ...current,
              tests: {
                ...(current.tests || {}),
                stream: [...previous, payload],
                stdout: `${current.tests?.stdout || ""}${payload.line || ""}\n`,
              },
            };
          });
        },
        () => {
          setActionState((current) => ({
            ...current,
            tests: {
              ...(current.tests || {}),
              stream_error: "Flux temps reel indisponible, fallback sur execution standard.",
            },
          }));
        },
        () => {
          setActionState((current) => ({ ...current, runningTests: false }));
        }
      );

      const result = await runInternalTests();
      setActionState((current) => ({
        ...current,
        runningTests: false,
        tests: {
          ...(current.tests || {}),
          ...result,
          stdout: current.tests?.stdout || result.stdout || "",
          stream: current.tests?.stream || [],
        },
      }));
    } catch (err) {
      setActionState((current) => ({
        ...current,
        runningTests: false,
        tests: { success: false, error: err.message },
      }));
    } finally {
      if (stream) {
        stream.close();
      }
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
