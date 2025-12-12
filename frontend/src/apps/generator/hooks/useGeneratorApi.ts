import { getMutatingHeaders } from "@/security/csrf";

const API_BASE = import.meta.env.VITE_API_BASE_URL as string | undefined;
const apiUrl = (path: string) => (API_BASE ? `${API_BASE}${path}` : path);

export async function apiGenerate(model_key: string, count: number) {
  const res = await fetch(apiUrl("/api/generator/generate/"), {
    method: "POST",
    credentials: "include",
    headers: getMutatingHeaders(),
    body: JSON.stringify({ model_key, count }),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || "Nepodarilo sa generovať");
  }
  return res.json(); // expects {job_id, created, total}
}

export async function apiClearAllState() {
  const res = await fetch(apiUrl("/api/generator/clear-all-state/"), {
    method: "POST",
    credentials: "include",
    headers: getMutatingHeaders(),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || "Mazanie zlyhalo");
  }
  return res.json(); // include job_id if present
}

export async function apiCancelJob(jobId: string) {
  const res = await fetch(apiUrl(`/api/generator/progress/${jobId}/cancel/`), {
    method: "POST",
    credentials: "include",
    headers: getMutatingHeaders(),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || `Cancel zlyhal (HTTP ${res.status})`);
  }
  const json = await res.json();
  return json;
}

