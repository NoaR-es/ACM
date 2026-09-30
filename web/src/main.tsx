// Punto de entrada: proveedores (react-query, preferencias, sesión, canal en vivo) y router. Ver control/05_CODIGO/frontend.md.
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { HashRouter } from "react-router-dom";
import { App } from "./App";
import { AuthProvider } from "./auth";
import { LiveProvider } from "./live";
import { PrefsProvider } from "./prefs";
import "./styles.css";

const queryClient = new QueryClient({
  defaultOptions: {
    // Los datos se refrescan por eventos (ADR-018); el refresco periódico es solo una red de seguridad (TD-003).
    queries: { staleTime: 30_000, refetchInterval: 120_000, retry: 1, refetchOnWindowFocus: true },
  },
});

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <PrefsProvider>
        <AuthProvider>
          <LiveProvider>
            <HashRouter>
              <App />
            </HashRouter>
          </LiveProvider>
        </AuthProvider>
      </PrefsProvider>
    </QueryClientProvider>
  </StrictMode>,
);
