// Cabecera de la aplicación (navegación, estado del canal en vivo, tema, sesión) y tabla de rutas (HashRouter).
import { NavLink, Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./auth";
import { useLive, type LiveStatus } from "./live";
import { ActivityPage } from "./pages/Activity";
import { Dashboard } from "./pages/Dashboard";
import { DocsPage } from "./pages/Docs";
import { KanbanPage } from "./pages/KanbanPage";
import { Login } from "./pages/Login";
import { ProjectPage } from "./pages/Project";
import { StoryPage } from "./pages/Story";
import { SystemPage } from "./pages/System";
import { usePrefs, type ThemeMode } from "./prefs";

const LIVE_TEXT: Record<LiveStatus, string> = {
  live: "En vivo",
  connecting: "Conectando…",
  reconnecting: "Reconectando…",
  offline: "Sin conexión",
};

function LiveIndicator() {
  const { status, announcement } = useLive();
  return (
    <>
      <span className={`live live-${status}`} data-live={status} title="Canal de eventos en tiempo real">
        <span className="dot" aria-hidden="true" /> {LIVE_TEXT[status]}
      </span>
      <span className="sr-only" role="status" aria-live="polite">
        {announcement}
      </span>
    </>
  );
}

function Header() {
  const { me, isAdmin, logout } = useAuth();
  const { mode, setMode } = usePrefs();
  return (
    <header className="topbar">
      <a className="skip" href="#main">
        Saltar al contenido
      </a>
      <NavLink to="/" className="brand">
        ACM
      </NavLink>
      <nav aria-label="Principal">
        <NavLink to="/" end>
          Panel
        </NavLink>
        <NavLink to="/kanban">Kanban</NavLink>
        <NavLink to="/docs">Documentación</NavLink>
        {isAdmin && <NavLink to="/activity">Actividad</NavLink>}
        {isAdmin && <NavLink to="/system">Sistema</NavLink>}
      </nav>
      <div className="topbar-right">
        <LiveIndicator />
        <label>
          <span className="sr-only">Tema</span>
          <select value={mode} onChange={(e) => setMode(e.target.value as ThemeMode)} aria-label="Tema de color">
            <option value="system">Tema del sistema</option>
            <option value="light">Claro</option>
            <option value="dark">Oscuro</option>
          </select>
        </label>
        <span className="me" title={me ? `${me.kind} · rol ${me.role}` : ""}>
          {me?.id ?? "…"} {me && <span className="tag">{me.role}</span>}
        </span>
        <button type="button" onClick={logout}>
          Salir
        </button>
      </div>
    </header>
  );
}

export function App() {
  const { token, isAdmin } = useAuth();
  if (!token) return <Login />;
  return (
    <>
      <Header />
      <main id="main" tabIndex={-1}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/kanban" element={<KanbanPage />} />
          <Route path="/p/:projectId/s/:storyId" element={<StoryPage />} />
          <Route path="/p/:projectId/*" element={<ProjectPage />} />
          <Route path="/docs" element={<DocsPage />} />
          <Route path="/activity" element={isAdmin ? <ActivityPage /> : <Navigate to="/" />} />
          <Route path="/system" element={isAdmin ? <SystemPage /> : <Navigate to="/" />} />
          <Route path="*" element={<p className="empty">Página no encontrada.</p>} />
        </Routes>
      </main>
    </>
  );
}
