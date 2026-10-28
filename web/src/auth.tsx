// Sesión (US-31.01): token en sessionStorage, identidad desde /api/v1/me, cierre por 401 o WS 4401.
// Modo local (US-14.12 CA-04): si ACM corre en este equipo, `/api/local-session` da un token sin que la persona lo pegue.
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { createContext, useCallback, useContext, useEffect, useRef, useState, type ReactNode } from "react";
import { api, ApiError, tokenStore } from "./api";
import type { Me } from "./types";

const NO_AUTO_KEY = "acm.no-auto-login";

/** Token de la interfaz local, o null si ACM no está en modo local o la petición no procede de este equipo. */
async function localToken(): Promise<string | null> {
  try {
    const res = await fetch("/api/local-session", { headers: { "X-ACM-Local": "1" }, cache: "no-store" });
    const body = (await res.json()) as { token?: string | null };
    return res.ok ? (body.token ?? null) : null;
  } catch {
    return null;
  }
}

type Auth = {
  token: string | null;
  bootstrapping: boolean;
  me: Me | null;
  isAdmin: boolean;
  login: (token: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<Auth | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => tokenStore.get());
  const [bootstrapping, setBootstrapping] = useState<boolean>(() => tokenStore.get() === null);
  const lastLocalTry = useRef(0);
  const queryClient = useQueryClient();
  const me = useQuery({ queryKey: ["me"], queryFn: () => api<Me>("/me"), enabled: !!token, retry: false });

  const logout = useCallback(() => {
    tokenStore.clear();
    setToken(null);
    queryClient.clear();
  }, [queryClient]);

  // Entrada automática en modo local. Como mucho una vez cada 5 s, para no repetirla si el token local fallara.
  const autoLogin = useCallback(async () => {
    try {
      if (sessionStorage.getItem(NO_AUTO_KEY)) return;
    } catch {
      /* sin sessionStorage: se intenta igualmente */
    }
    if (Date.now() - lastLocalTry.current < 5000) return;
    lastLocalTry.current = Date.now();
    const candidate = await localToken();
    if (!candidate) return;
    tokenStore.set(candidate);
    setToken(candidate);
  }, []);

  useEffect(() => {
    if (token) return;
    void autoLogin().finally(() => setBootstrapping(false));
  }, [token, autoLogin]);

  useEffect(() => {
    const onUnauth = () => {
      logout(); // el efecto de arriba vuelve a intentar la entrada local (p. ej. si ACM se reinició)
    };
    window.addEventListener("acm:unauthenticated", onUnauth);
    return () => window.removeEventListener("acm:unauthenticated", onUnauth);
  }, [logout]);

  const login = useCallback(
    async (candidate: string) => {
      const clean = candidate.trim();
      const who = await api<Me>("/me", {}, clean); // valida el token antes de guardarlo
      tokenStore.set(clean);
      try {
        sessionStorage.removeItem(NO_AUTO_KEY);
      } catch {
        /* sin sessionStorage */
      }
      queryClient.setQueryData(["me"], who);
      setToken(clean);
    },
    [queryClient],
  );

  const signOut = useCallback(() => {
    try {
      sessionStorage.setItem(NO_AUTO_KEY, "1"); // salir a propósito no debe volver a entrar solo
    } catch {
      /* sin sessionStorage */
    }
    logout();
  }, [logout]);

  const value: Auth = {
    token,
    bootstrapping,
    me: me.data ?? null,
    isAdmin: me.data?.role === "admin",
    login,
    logout: signOut,
  };
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): Auth {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth fuera de AuthProvider");
  return ctx;
}

export function describeError(e: unknown): string {
  if (e instanceof ApiError) return e.code === "NETWORK" ? e.message : `${e.code}: ${e.message}`;
  return e instanceof Error ? e.message : String(e);
}
