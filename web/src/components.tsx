// Componentes compartidos de presentación: badges de estado, semáforo, Markdown, errores, esqueletos de carga.
import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { describeError } from "./auth";
import { renderMarkdown } from "./markdown";
import { projectIndex, STATUS_LABEL, type StoryStatus } from "./theme";
import type { Finding, Semaphore } from "./types";

// El color nunca es la única señal (WCAG 1.4.1): cada badge lleva texto y, en el semáforo, un símbolo.
export function StatusBadge({ status }: { status: StoryStatus }) {
  return (
    <span
      className="badge"
      data-status={status}
      style={{ background: `var(--status-${status}-bg)`, color: `var(--status-${status}-fg)` }}
    >
      {STATUS_LABEL[status] ?? status}
    </span>
  );
}

const SEMAPHORE_TEXT: Record<Semaphore, [string, string]> = {
  GREEN: ["✔", "Verde"],
  AMBER: ["▲", "Ámbar"],
  RED: ["✖", "Rojo"],
  UNKNOWN: ["?", "Sin auditar"],
};

export function SemaphoreBadge({ value, large = false }: { value: Semaphore; large?: boolean }) {
  const [icon, text] = SEMAPHORE_TEXT[value] ?? ["?", value];
  return (
    <span
      className={`badge semaphore${large ? " large" : ""}`}
      data-semaphore={value}
      style={{ background: `var(--sem-${value}-bg)`, color: `var(--sem-${value}-fg)` }}
      title={`Semáforo de gobernanza: ${text}`}
    >
      <span aria-hidden="true">{icon}</span> {text}
    </span>
  );
}

export function SeverityBadge({ severity }: { severity: Finding["severity"] }) {
  return (
    <span className="badge" style={{ background: `var(--sev-${severity}-bg)`, color: `var(--sev-${severity}-fg)` }}>
      {severity}
    </span>
  );
}

export function ProjectChip({ projectId, all, link = true }: { projectId: string; all: string[]; link?: boolean }) {
  const i = projectIndex(projectId, all);
  const chip = (
    <span className="chip" style={{ background: `var(--project-${i}-bg)`, color: `var(--project-${i}-fg)` }}>
      {projectId}
    </span>
  );
  return link ? <Link to={`/p/${projectId}`}>{chip}</Link> : chip;
}

export function Loading({ what = "datos" }: { what?: string }) {
  return (
    <p className="muted" role="status">
      Cargando {what}…
    </p>
  );
}

export function ErrorBox({ error }: { error: unknown }) {
  return (
    <div className="error" role="alert">
      {describeError(error)}
    </div>
  );
}

export function Empty({ children }: { children: ReactNode }) {
  return <p className="empty">{children}</p>;
}

export function Markdown({ text }: { text: string }) {
  return <div className="markdown" dangerouslySetInnerHTML={{ __html: renderMarkdown(text) }} />;
}

export function Section({ title, children, actions }: { title: string; children: ReactNode; actions?: ReactNode }) {
  return (
    <section className="panel" aria-label={title}>
      <header className="panel-head">
        <h2>{title}</h2>
        {actions && <div className="actions">{actions}</div>}
      </header>
      {children}
    </section>
  );
}

export function Stat({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="stat">
      <span className="stat-value">{value}</span>
      <span className="stat-label">{label}</span>
    </div>
  );
}

export function fmtDate(iso: string | null | undefined): string {
  if (!iso) return "—";
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? iso : d.toLocaleString("es-ES", { dateStyle: "short", timeStyle: "medium" });
}

/** Barra de distribución de historias por estado (con texto accesible). */
export function StatusBar({ counts }: { counts: Partial<Record<StoryStatus, number>> }) {
  const total = Object.values(counts).reduce((a, b) => a + (b ?? 0), 0);
  const parts = (Object.entries(counts) as [StoryStatus, number][]).filter(([, n]) => n > 0);
  const label = parts.map(([s, n]) => `${STATUS_LABEL[s]}: ${n}`).join(", ") || "sin historias";
  return (
    <div className="statusbar" role="img" aria-label={`Historias por estado — ${label}`}>
      {total === 0 ? (
        <span className="statusbar-empty">Sin historias</span>
      ) : (
        parts.map(([s, n]) => (
          <span
            key={s}
            className="statusbar-seg"
            style={{ flexGrow: n, background: `var(--status-${s}-bg)`, color: `var(--status-${s}-fg)` }}
            title={`${STATUS_LABEL[s]}: ${n}`}
          >
            {n}
          </span>
        ))
      )}
    </div>
  );
}
