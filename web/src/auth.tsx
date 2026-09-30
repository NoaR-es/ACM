// Sesión (US-31.01): token en sessionStorage, identidad desde /api/v1/me, cierre por 401 o WS 4401.
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";
import { api, ApiError, tokenStore } from "./api";
import type { Me } from "./types";

type Auth = {
  token: string | null;
  me: Me | null;
  isAdmin: boolean;
  login: (token: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<Auth | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => tokenStore.get());
  const queryClient = useQueryClient();
  const me = useQuery({ queryKey: ["me"], queryFn: () => api<Me>("/me"), enabled: !!token, retry: false });

  const logout = useCallback(() => {
    tokenStore.clear();
    setToken(null);
    queryClient.clear();
  }, [queryClient]);

  useEffect(() => {
    const onUnauth = () => logout();
    window.addEventListener("acm:unauthenticated", onUnauth);
    return () => window.removeEventListener("acm:unauthenticated", onUnauth);
  }, [logout]);

  const login = useCallback(
    async (candidate: string) => {
      const clean = candidate.trim();
      const who = await api<Me>("/me", {}, clean); // valida el token antes de guardarlo
      tokenStore.set(clean);
      queryClient.setQueryData(["me"], who);
      setToken(clean);
    },
    [queryClient],
  );

  const value: Auth = { token, me: me.data ?? null, isAdmin: me.data?.role === "admin", login, logout };
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
