// Proyecto: resumen, backlog, requisitos, historias, Kanban, gobernanza, miembros y configuración.
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link, NavLink, Route, Routes, useParams } from "react-router-dom";
import { api, post } from "../api";

import {
  Empty, ErrorBox, fmtDate, Loading, Section, SemaphoreBadge, SeverityBadge, Stat, StatusBadge, StatusBar,
} from "../components";
import { KanbanBoard } from "../KanbanBoard";
import { STATUS_LABEL, STATUS_ORDER, type StoryStatus } from "../theme";
import type { Backlog, Governance, Kanban, PortfolioProject, Requirement, Story, WatchdogRun } from "../types";

type ProjectInfo = { project_id: string; name: string; description: string; role: string; schema_version: number };
type Config = { parameters: { key: string; value: unknown; default: unknown; allowed: string; description: string; consumer: string }[] };
type Members = { members: { principal_id: string; role: string; kind: string; added_at: string }[] };

export function useBacklog(projectId: string) {
  return useQuery({ queryKey: ["project", projectId, "backlog"], queryFn: () => api<Backlog>(`/projects/${projectId}/backlog`) });
}

export function ProjectPage() {
  const { projectId = "" } = useParams();
  const info = useQuery({ queryKey: ["project", projectId, "info"], queryFn: () => api<ProjectInfo>(`/projects/${projectId}`) });
  if (info.isPending) return <Loading what="proyecto" />;
  if (info.error) return <ErrorBox error={info.error} />;
  const tabs: [string, string][] = [
    ["", "Resumen"], ["backlog", "Backlog"], ["requirements", "Requisitos"], ["stories", "Historias"],
    ["kanban", "Kanban"], ["governance", "Gobernanza"], ["members", "Miembros"], ["config", "Configuración"],
  ];
  return (
    <div className="page wide">
      <p className="breadcrumb">
        <Link to="/">Panel</Link> / {projectId}
      </p>
      <h1>
        {info.data.name} <span className="muted small">({projectId} · tu rol: {info.data.role})</span>
      </h1>
      {info.data.description && <p className="muted">{info.data.description}</p>}
      <nav className="tabs" aria-label="Secciones del proyecto">
        {tabs.map(([path, label]) => (
          <NavLink key={path} to={`/p/${projectId}/${path}`} end={path === ""}>
            {label}
          </NavLink>
        ))}
      </nav>
      <Routes>
        <Route index element={<Summary projectId={projectId} />} />
        <Route path="backlog" element={<BacklogTree projectId={projectId} />} />
        <Route path="requirements" element={<Requirements projectId={projectId} />} />
        <Route path="stories" element={<Stories projectId={projectId} />} />
        <Route path="kanban" element={<ProjectKanban projectId={projectId} />} />
        <Route path="governance" element={<GovernanceView projectId={projectId} />} />
        <Route path="members" element={<MembersView projectId={projectId} />} />
        <Route path="config" element={<ConfigView projectId={projectId} />} />
      </Routes>
    </div>
  );
}

function Summary({ projectId }: { projectId: string }) {
  const backlog = useBacklog(projectId);
  const portfolio = useQuery({ queryKey: ["projects"], queryFn: () => api<{ projects: PortfolioProject[] }>("/projects") });
  const entry = portfolio.data?.projects.find((p) => p.project_id === projectId);
  if (backlog.isPending) return <Loading what="backlog" />;
  if (backlog.error) return <ErrorBox error={backlog.error} />;
  const b = backlog.data;
  const gaps = Object.entries(b.gaps).filter(([k, v]) => Array.isArray(v) && v.length && k !== "project_id") as [string, string[]][];
  return (
    <>
      <div className="stats">
        <Stat label="Requisitos" value={b.requirements.length} />
        <Stat label="Épicas" value={b.epics.length} />
        <Stat label="Features" value={b.epics.reduce((n, e) => n + e.features.length, 0)} />
        <Stat label="Historias" value={b.stories.length} />
        <Stat label="Criterios" value={b.stories.reduce((n, s) => n + s.acceptance_criteria.length, 0)} />
        <Stat label="Gobernanza" value={entry ? <SemaphoreBadge value={entry.governance.semaphore} /> : "…"} />
      </div>
      <Section title="Historias por estado">
        <StatusBar counts={entry?.stories_by_status ?? {}} />
      </Section>
      <Section title="Huecos de trazabilidad">
        {gaps.length === 0 ? (
          <Empty>Sin huecos: cada requisito, épica, feature e historia está enlazado.</Empty>
        ) : (
          <ul>
            {gaps.map(([k, v]) => (
              <li key={k}>
                <strong>{GAP_LABEL[k] ?? k}:</strong> {v.join(", ")}
              </li>
            ))}
          </ul>
        )}
      </Section>
    </>
  );
}

const GAP_LABEL: Record<string, string> = {
  orphan_requirements: "Requisitos sin historias",
  epics_without_features: "Épicas sin features",
  features_without_stories: "Features sin historias",
  stories_without_criteria: "Historias sin criterios",
  stories_without_requirements: "Historias sin requisito",
};

function BacklogTree({ projectId }: { projectId: string }) {
  const backlog = useBacklog(projectId);
  if (backlog.isPending) return <Loading what="backlog" />;
  if (backlog.error) return <ErrorBox error={backlog.error} />;
  const stories = new Map(backlog.data.stories.map((s) => [s.id, s]));
  if (backlog.data.epics.length === 0) return <Empty>El backlog está vacío.</Empty>;
  return (
    <div className="tree">
      {backlog.data.epics.map((epic) => (
        <details key={epic.id} open className="panel">
          <summary>
            <strong>{epic.id}</strong> {epic.title}{" "}
            <span className="muted small">
              {epic.features.length} features · requisitos {epic.requirement_ids.join(", ") || "—"}
              {epic.coverage_confirmed_at && " · cobertura confirmada"}
            </span>
          </summary>
          <dl className="kv">
            <dt>Objetivo</dt>
            <dd>{epic.objective}</dd>
            <dt>Alcance</dt>
            <dd>{epic.scope}</dd>
          </dl>
          {epic.features.map((f) => (
            <details key={f.id} open className="feature">
              <summary>
                <strong>{f.id}</strong> {f.title}{" "}
                {f.status === "SPLIT" && <span className="tag">dividida en {f.split_into}</span>}
              </summary>
              {f.description && <p className="muted">{f.description}</p>}
              <ul className="story-list">
                {f.story_ids.map((sid) => {
                  const s = stories.get(sid);
                  return s ? (
                    <li key={sid}>
                      <Link to={`/p/${projectId}/s/${sid}`}>{sid}</Link> <StatusBadge status={s.status} /> {s.i_want}{" "}
                      <span className="muted small">({s.acceptance_criteria.length} CA)</span>
                    </li>
                  ) : null;
                })}
              </ul>
            </details>
          ))}
        </details>
      ))}
    </div>
  );
}

type Trace = { requirement: Requirement; epic_ids: string[]; stories: { id: string; status: StoryStatus }[]; orphan: boolean };

function Requirements({ projectId }: { projectId: string }) {
  const backlog = useBacklog(projectId);
  const [open, setOpen] = useState<string | null>(null);
  const trace = useQuery({
    queryKey: ["project", projectId, "trace", open],
    queryFn: () => api<Trace>(`/projects/${projectId}/requirements/${open}/trace`),
    enabled: !!open,
  });
  if (backlog.isPending) return <Loading what="requisitos" />;
  if (backlog.error) return <ErrorBox error={backlog.error} />;
  if (backlog.data.requirements.length === 0) return <Empty>Sin requisitos.</Empty>;
  return (
    <table className="table">
      <caption className="sr-only">Requisitos del proyecto</caption>
      <thead>
        <tr><th>Id</th><th>Título</th><th>Descripción</th><th>Trazabilidad</th></tr>
      </thead>
      <tbody>
        {backlog.data.requirements.map((r) => (
          <tr key={r.id}>
            <td><strong>{r.id}</strong></td>
            <td>{r.title}</td>
            <td className="muted">{r.description || "—"}</td>
            <td>
              <button type="button" onClick={() => setOpen(open === r.id ? null : r.id)} aria-expanded={open === r.id}>
                {open === r.id ? "Ocultar" : "Ver traza"}
              </button>
              {open === r.id && trace.data && (
                <div className="trace">
                  Épicas: {trace.data.epic_ids.join(", ") || "—"}
                  <br />
                  Historias:{" "}
                  {trace.data.stories.length === 0 ? <em>ninguna (requisito huérfano)</em> : trace.data.stories.map((s) => (
                    <span key={s.id}>
                      <Link to={`/p/${projectId}/s/${s.id}`}>{s.id}</Link> <StatusBadge status={s.status} />{" "}
                    </span>
                  ))}
                </div>
              )}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function Stories({ projectId }: { projectId: string }) {
  const backlog = useBacklog(projectId);
  const [status, setStatus] = useState<string>("");
  const [text, setText] = useState("");
  if (backlog.isPending) return <Loading what="historias" />;
  if (backlog.error) return <ErrorBox error={backlog.error} />;
  const q = text.toLowerCase();
  const rows = backlog.data.stories.filter(
    (s: Story) =>
      (!status || s.status === status) &&
      (!q || `${s.id} ${s.as_a} ${s.i_want} ${s.so_that}`.toLowerCase().includes(q)),
  );
  return (
    <>
      <div className="toolbar">
        <label>
          Estado{" "}
          <select value={status} onChange={(e) => setStatus(e.target.value)}>
            <option value="">Todos</option>
            {STATUS_ORDER.map((s) => <option key={s} value={s}>{STATUS_LABEL[s]}</option>)}
          </select>
        </label>
        <label>
          Buscar <input type="search" value={text} onChange={(e) => setText(e.target.value)} />
        </label>
        <span className="muted">{rows.length} de {backlog.data.stories.length}</span>
      </div>
      <table className="table">
        <caption className="sr-only">Historias del proyecto</caption>
        <thead>
          <tr><th>Id</th><th>Estado</th><th>Historia</th><th>Requisitos</th><th>CA</th><th>Actualizada</th></tr>
        </thead>
        <tbody>
          {rows.map((s) => (
            <tr key={s.id}>
              <td><Link to={`/p/${projectId}/s/${s.id}`}>{s.id}</Link></td>
              <td><StatusBadge status={s.status} /></td>
              <td>Como <em>{s.as_a}</em>, quiero <strong>{s.i_want}</strong>, para {s.so_that}</td>
              <td>{s.requirement_ids.join(", ")}</td>
              <td>{s.acceptance_criteria.length}</td>
              <td className="small">{fmtDate(s.updated_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  );
}

function ProjectKanban({ projectId }: { projectId: string }) {
  const board = useQuery({ queryKey: ["kanban", projectId], queryFn: () => api<Kanban>(`/kanban?projects=${projectId}`) });
  if (board.isPending) return <Loading what="tablero" />;
  if (board.error) return <ErrorBox error={board.error} />;
  return <KanbanBoard board={board.data} allProjects={[projectId]} />;
}

function GovernanceView({ projectId }: { projectId: string }) {
  const queryClient = useQueryClient();
  const gov = useQuery({
    queryKey: ["governance", projectId],
    queryFn: () => api<Governance & { history: WatchdogRun[] }>(`/projects/${projectId}/governance`),
  });
  const run = useMutation({
    mutationFn: () => post<WatchdogRun>(`/projects/${projectId}/watchdog`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["governance", projectId] }),
  });
  if (gov.isPending) return <Loading what="gobernanza" />;
  if (gov.error) return <ErrorBox error={gov.error} />;
  const g = gov.data;
  const last = g.history[0];
  return (
    <>
      <Section
        title="Estado de gobernanza"
        actions={
          <button type="button" className="primary" onClick={() => run.mutate()} disabled={run.isPending}>
            {run.isPending ? "Auditando…" : "Auditar ahora"}
          </button>
        }
      >
        <div className="row">
          <SemaphoreBadge value={g.semaphore} large />
          <span>
            Integridad: <strong>{g.integrity.integrity_status}</strong>
            {g.integrity.integrity_detail && ` (${g.integrity.integrity_detail})`} · comprobada{" "}
            {fmtDate(g.integrity.integrity_checked_at)}
          </span>
          {!g.writable && <strong className="danger">En cuarentena: no admite escrituras</strong>}
        </div>
        {run.error && <ErrorBox error={run.error} />}
      </Section>
      <Section title={`Hallazgos de la última auditoría${last ? ` (${fmtDate(last.ts)})` : ""}`}>
        {!last ? (
          <Empty>Todavía no se ha auditado este proyecto.</Empty>
        ) : last.findings.length === 0 ? (
          <Empty>Sin hallazgos.</Empty>
        ) : (
          <table className="table">
            <thead>
              <tr><th>Severidad</th><th>Código</th><th>Objetivo</th><th>Mensaje</th><th>Origen</th></tr>
            </thead>
            <tbody>
              {last.findings.map((f, i) => (
                <tr key={i}>
                  <td><SeverityBadge severity={f.severity} /></td>
                  <td><code>{f.code}</code></td>
                  <td>{/^US-/.test(f.target) ? <Link to={`/p/${projectId}/s/${f.target}`}>{f.target}</Link> : f.target}</td>
                  <td>{f.message}</td>
                  <td className="small">{f.source}{f.engine ? ` · ${f.engine}` : ""}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Section>
      <Section title="Histórico de auditorías">
        <table className="table">
          <thead>
            <tr><th>Fecha</th><th>Semáforo</th><th>Disparo</th><th>Por</th><th>C / W / R / I</th><th>Motores</th></tr>
          </thead>
          <tbody>
            {g.history.map((r) => (
              <tr key={r.id}>
                <td>{fmtDate(r.ts)}</td>
                <td><SemaphoreBadge value={r.semaphore} /></td>
                <td>{r.trigger === "scheduled" ? "periódica" : "manual"}</td>
                <td>{r.principal}</td>
                <td>{r.critical} / {r.warning} / {r.review} / {r.info}</td>
                <td className="small">{r.engines.join(", ") || "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Section>
    </>
  );
}

function MembersView({ projectId }: { projectId: string }) {
  const members = useQuery({ queryKey: ["members", projectId], queryFn: () => api<Members>(`/projects/${projectId}/members`) });
  if (members.isPending) return <Loading what="miembros" />;
  if (members.error) return <ErrorBox error={members.error} />;
  return (
    <table className="table">
      <thead>
        <tr><th>Principal</th><th>Tipo</th><th>Rol en el proyecto</th><th>Desde</th></tr>
      </thead>
      <tbody>
        {members.data.members.map((m) => (
          <tr key={m.principal_id}>
            <td>{m.principal_id}</td>
            <td>{m.kind === "agent" ? "agente" : "usuario"}</td>
            <td>{m.role}</td>
            <td>{fmtDate(m.added_at)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function ConfigView({ projectId }: { projectId: string }) {
  const config = useQuery({ queryKey: ["project", projectId, "config"], queryFn: () => api<Config>(`/projects/${projectId}/config`) });
  if (config.isPending) return <Loading what="configuración" />;
  if (config.error) return <ErrorBox error={config.error} />;
  return (
    <table className="table">
      <thead>
        <tr><th>Parámetro</th><th>Valor</th><th>Por defecto</th><th>Permitido</th><th>Descripción</th><th>Lo usa</th></tr>
      </thead>
      <tbody>
        {config.data.parameters.map((p) => (
          <tr key={p.key}>
            <td><code>{p.key}</code></td>
            <td>{JSON.stringify(p.value)}</td>
            <td className="muted">{JSON.stringify(p.default)}</td>
            <td className="small">{p.allowed}</td>
            <td>{p.description}</td>
            <td className="small muted">{p.consumer}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

