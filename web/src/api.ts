// Cliente de la API REST v1 (06_API/rest_api.md). El token vive en sessionStorage: se borra al cerrar la pestaña.
const TOKEN_KEY = "acm.token";
export const API = "/api/v1";

export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
    public field: string | null = null,
  ) {
    super(message);
  }
}

export const tokenStore = {
  get(): string | null {
    try {
      return sessionStorage.getItem(TOKEN_KEY);
    } catch {
      return null;
    }
  },
  set(token: string): void {
    sessionStorage.setItem(TOKEN_KEY, token);
  },
  clear(): void {
    sessionStorage.removeItem(TOKEN_KEY);
  },
};

export async function api<T>(path: string, init: RequestInit = {}, token = tokenStore.get()): Promise<T> {
  const headers = new Headers(init.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (init.body) headers.set("Content-Type", "application/json");
  let res: Response;
  try {
    res = await fetch(`${API}${path}`, { ...init, headers });
  } catch {
    throw new ApiError(0, "NETWORK", "No se pudo contactar con ACM");
  }
  const body = await res.json().catch(() => null);
  if (!res.ok) {
    const err = body?.error ?? {};
    if (res.status === 401) window.dispatchEvent(new CustomEvent("acm:unauthenticated"));
    throw new ApiError(res.status, err.code ?? `HTTP_${res.status}`, err.message ?? res.statusText, err.field ?? null);
  }
  return body as T;
}

export function post<T>(path: string, data?: unknown): Promise<T> {
  return api<T>(path, { method: "POST", body: data === undefined ? undefined : JSON.stringify(data) });
}
