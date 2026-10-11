const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Turn a FastAPI error body into one readable sentence.
function errorMessage(body, status) {
  const detail = body?.detail;
  if (typeof detail === "string") return detail; // 404, 500, 502
  if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg; // 422
  return `Request failed (${status}).`;
}

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch {
    throw new Error("Cannot reach the server. Is the backend running?");
  }

  const body = await response.json().catch(() => null);
  if (!response.ok) throw new Error(errorMessage(body, response.status));
  return body;
}

export function createEntry(text) {
  return request("/entries", { method: "POST", body: JSON.stringify({ text }) });
}

export function listEntries() {
  return request("/entries");
}

export function getEntry(id) {
  return request(`/entries/${id}`);
}
