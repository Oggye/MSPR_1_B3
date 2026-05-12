const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`Erreur API ${response.status} sur ${path}`);
  }

  return response.json();
}

export function getInternalOverview() {
  return request("/api/internal/overview");
}

export function runInternalDiagnostic() {
  return request("/api/internal/diagnostic/run", { method: "POST" });
}

export function runInternalTests() {
  return request("/api/internal/tests/run", { method: "POST" });
}
