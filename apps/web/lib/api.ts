export const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8123";

async function req(path: string, init?: RequestInit) {
  const r = await fetch(`${API}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
  });
  if (!r.ok) throw new Error(`${r.status} ${await r.text()}`);
  const ct = r.headers.get("content-type") || "";
  return ct.includes("json") ? r.json() : r.text();
}

export const api = {
  datasets: (params: Record<string, string | number | boolean>) => {
    const q = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => { if (v !== "" && v !== undefined) q.set(k, String(v)); });
    return req(`/api/v1/datasets?${q.toString()}`);
  },
  dataset: (id: string) => req(`/api/v1/datasets/${id}`),
  compare: (ids: string[]) => req(`/api/v1/datasets/compare`, { method: "POST", body: JSON.stringify({ ids }) }),
  publishers: () => req(`/api/v1/publishers`),
  taxonomy: () => req(`/api/v1/taxonomy`),
  kits: () => req(`/api/v1/kits`),
  sources: () => req(`/api/v1/sources`),
  health: () => req(`/api/v1/health`),
  projects: () => req(`/api/v1/projects`),
  createProject: (b: unknown) => req(`/api/v1/projects`, { method: "POST", body: JSON.stringify(b) }),
  project: (id: string) => req(`/api/v1/projects/${id}`),
  patchProject: (id: string, b: unknown) => req(`/api/v1/projects/${id}`, { method: "PATCH", body: JSON.stringify(b) }),
  post: (path: string, b: unknown) => req(path, { method: "POST", body: JSON.stringify(b) }),
  patch: (path: string, b: unknown) => req(path, { method: "PATCH", body: JSON.stringify(b) }),
  get: (path: string) => req(path),
  del: (path: string) => req(path, { method: "DELETE" }),
  exportPlan: (id: string, format = "markdown") =>
    fetch(`${API}/api/v1/projects/${id}/export?format=${format}`).then((r) => r.text()),
  info: (ids: string[]) => req(`/api/v1/datasets/info`, { method: "POST", body: JSON.stringify({ ids }) }),
  thumbnail: (id: string) => req(`/api/v1/datasets/${id}/thumbnail`),
  kit: (slug: string) => req(`/api/v1/kits/${slug}`),
  instantiate: (slug: string, b: unknown) => req(`/api/v1/kits/${slug}/instantiate`, { method: "POST", body: JSON.stringify(b) }),
  graph: (id: string) => req(`/api/v1/projects/${id}/graph`),
  steps: (id: string) => req(`/api/v1/projects/${id}/steps`),
  transformations: (id: string) => req(`/api/v1/projects/${id}/transformations`),
  submitDataset: (b: unknown) => req(`/api/v1/submissions`, { method: "POST", body: JSON.stringify(b) }),
  rules: () => req(`/api/v1/admin/rules`),
  patchRule: (rule: string, b: unknown) => req(`/api/v1/admin/rules/${rule}`, { method: "PATCH", body: JSON.stringify(b) }),
  testRules: () => req(`/api/v1/admin/rules/test`, { method: "POST", body: JSON.stringify({}) }),
  submissions: () => req(`/api/v1/admin/submissions?status=all`),
  moderate: (id: string, b: unknown) => req(`/api/v1/admin/submissions/${id}/moderate`, { method: "POST", body: JSON.stringify(b) }),
  staging: () => req(`/api/v1/staging`),
  aiTools: () => req(`/api/v1/ai/tools`),
  aiChat: (b: unknown) => req(`/api/v1/ai/chat`, { method: "POST", body: JSON.stringify(b) }),
  aiStatus: () => req(`/api/v1/ai/status`),
};

export const CAVEAT =
  "Landing-page reachability does not prove download access, licence permission, scientific fitness or resolved metadata.";
