// Tema claro/oscuro (o el del sistema) aplicado como variables CSS de la paleta verificada (theme.ts).
import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { cssVariables, PALETTES, type ThemeName } from "./theme";

export type ThemeMode = "system" | ThemeName;
type Prefs = { mode: ThemeMode; theme: ThemeName; setMode: (m: ThemeMode) => void };
const PrefsContext = createContext<Prefs | null>(null);
const KEY = "acm.theme";

function systemTheme(): ThemeName {
  return window.matchMedia?.("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

export function PrefsProvider({ children }: { children: ReactNode }) {
  const [mode, setModeState] = useState<ThemeMode>(() => {
    try {
      return (localStorage.getItem(KEY) as ThemeMode) || "system";
    } catch {
      return "system";
    }
  });
  const [sys, setSys] = useState<ThemeName>(systemTheme);
  useEffect(() => {
    const mq = window.matchMedia?.("(prefers-color-scheme: dark)");
    const on = () => setSys(systemTheme());
    mq?.addEventListener("change", on);
    return () => mq?.removeEventListener("change", on);
  }, []);
  const theme: ThemeName = mode === "system" ? sys : mode;
  useEffect(() => {
    const root = document.documentElement;
    for (const [k, v] of Object.entries(cssVariables(PALETTES[theme]))) root.style.setProperty(k, v);
    root.dataset.theme = theme;
    root.style.colorScheme = theme;
  }, [theme]);
  const setMode = (m: ThemeMode) => {
    setModeState(m);
    try {
      localStorage.setItem(KEY, m);
    } catch {
      /* sin almacenamiento: solo esta sesión */
    }
  };
  return <PrefsContext.Provider value={{ mode, theme, setMode }}>{children}</PrefsContext.Provider>;
}

export function usePrefs(): Prefs {
  const ctx = useContext(PrefsContext);
  if (!ctx) throw new Error("usePrefs fuera de PrefsProvider");
  return ctx;
}
