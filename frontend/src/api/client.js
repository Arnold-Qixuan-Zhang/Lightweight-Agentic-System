const API_BASE = "http://localhost:8000";

async function handleResponse(response) {
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    const detail = error.detail;
    const message = Array.isArray(detail)
      ? detail.map((e) => e.msg).join(", ")
      : detail || `Request failed (${response.status})`;
    throw new Error(message);
  }
  return response.json();
}

export async function submitTask(instruction) {
  const response = await fetch(`${API_BASE}/api/tasks`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ instruction }),
  });
  return handleResponse(response);
}

export async function getHistory() {
  const response = await fetch(`${API_BASE}/api/history`);
  return handleResponse(response);
}

export function exportHistory() {
  window.open(`${API_BASE}/api/history/export`, "_blank");
}
