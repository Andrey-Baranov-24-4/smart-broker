const BASE_URL = process.env.REACT_APP_API_URL || "";

async function request(path, { method = "GET", body } = {}) {
  const resp = await fetch(`${BASE_URL}${path}`, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!resp.ok) {
    const detail = await resp.json().catch(() => ({}));
    throw new Error(detail.detail || `Request failed: ${resp.status}`);
  }
  if (resp.status === 204) return null;
  return resp.json();
}

export const api = {
  getPortfolio: () => request("/portfolio"),
  getHistory: () => request("/portfolio/history"),
  addPosition: (payload) => request("/portfolio/positions", { method: "POST", body: payload }),
  deletePosition: (stockId) =>
    request(`/portfolio/positions/${stockId}`, { method: "DELETE" }),
  getPrice: (query) => request(`/prices/${encodeURIComponent(query)}`),
  sendVoiceCommand: (text) =>
    request("/voice/command", { method: "POST", body: { text } }),
};
