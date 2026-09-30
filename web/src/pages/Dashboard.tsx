// Panel general (US-45.01/45.03): todos los proyectos accesibles, su salud y la actividad en vivo.
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../auth";
import { Empty, ErrorBox, fmtDate, Loading, ProjectChip, Section, SemaphoreBadge, Stat, StatusBar } from "../components";
import { useLive } from "../live";
import type { PortfolioProject } from "../types";

export function Dashboard() {
  const projects = useQuery({ queryKey: ["projects"], queryFn: () => api<{ projects: PortfolioProject[] }>("/projects") });
  const { events } = useLive();
  const { me } = useAuth();
  if (projects.isPending) return <Loading what="proyectos" />;
  if (projects.error) return <ErrorBox error={projects.error} />;
  const list = projects.data.projects;
  const ids = list.map((p) => p.project_id);
  const totals = list.reduce(
    (acc, p) => {
      acc.stories += p.stories;
      acc.blocked += p.stories_by_status.BLOCKED ?? 0;
      acc.inProgress += p.stories_by_status.IN_PROGRESS ?? 0;
      acc.red += p.governance.semaphore === "RED" ? 1 : 0;
      return acc;
    },
    { stories: 0, blocked: 0, inProgress: 0, red: 0 },
  );
  const domain = events.filter((e) => e.type !== "activity").slice(0, 25);
  return (
    <div className="page">
      <h1>Panel</h1>
      <div className="stats">
        <Stat label="Proyectos" value={list.length} />
        <Stat label="Historias" value={totals.stories} />
        <Stat label="En curso" value={totals.inProgress} />
        <Stat label="Bloqueadas" value={totals.blocked} />
        <Stat label="Semáforo rojo" value={totals.red} />
      </div>
      <div className="grid-2">
        <Section
          title="Proyectos"
          actions={
            ids.length > 1 && (
              <Link className="button" to={`/kanban?projects=${ids.join(",")}`}>
                Kanban de todos
              </Link>
            )
          }
        >
          {list.length === 0 ? (
            <Empty>
              {me?.role === "admin"
                ? "No hay proyectos. Créalos desde un agente con acm_project_create."
                : "No perteneces a ningún proyecto todavía."}
            </Empty>
          ) : (
            <ul className="project-cards">
              {list.map((p) => (
                <li key={p.project_id} className="project-card" data-project={p.project_id}>
                  <div className="row">
                    <ProjectChip projectId={p.project_id} all={ids} />
                    <Link to={`/p/${p.project_id}`} className="project-name">
                      {p.name}
                    </Link>
                    <SemaphoreBadge value={p.governance.semaphore} />
                  </div>
                  {p.description && <p className="muted">{p.description}</p>}
                  <StatusBar counts={p.stories_by_status} />
                  <p className="small muted">
                    {p.stories} historias · integridad {p.governance.integrity.integrity_status}
                    {!p.governance.writable && <strong className="danger"> · en cuarentena (solo lectura)</strong>} ·
                    última auditoría {fmtDate(p.governance.last_run?.ts)}
                  </p>
                  <div className="row">
                    <Link to={`/p/${p.project_id}/backlog`}>Backlog</Link>
                    <Link to={`/kanban?projects=${p.project_id}`}>Kanban</Link>
                    <Link to={`/p/${p.project_id}/governance`}>Gobernanza</Link>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </Section>
        <Section title="Cambios en tiempo real">
          {domain.length === 0 ? (
            <Empty>Aún no ha llegado ningún cambio en esta sesión. Aparecerán aquí al instante.</Empty>
          ) : (
            <ol className="feed" aria-live="polite">
              {domain.map((e) => (
                <li key={e.seq}>
                  <span className="muted small">{fmtDate(e.ts)}</span>{" "}
                  {e.project_id && <ProjectChip projectId={e.project_id} all={ids} />} <code>{e.type}</code>{" "}
                  {e.entity_type === "story" && e.project_id ? (
                    <Link to={`/p/${e.project_id}/s/${e.entity_id}`}>{e.entity_id}</Link>
                  ) : (
                    e.entity_id
                  )}
                  {typeof e.data.status === "string" && <strong> → {e.data.status}</strong>}{" "}
                  <span className="muted small">por {e.principal}</span>
                </li>
              ))}
            </ol>
          )}
        </Section>
      </div>
    </div>
  );
}
