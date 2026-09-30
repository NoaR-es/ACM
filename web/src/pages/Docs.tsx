// Documentación (US-15.08..10, US-30.02): skills que ACM sirve a los agentes, flujo de estados y referencia de la API.
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "../api";
import { ErrorBox, Loading, Markdown, Section, StatusBadge } from "../components";
import { splitFrontmatter } from "../markdown";
import { STATUS_ORDER, type StoryStatus } from "../theme";

type SkillEntry = { uri: string; frontmatter: Record<string, unknown> };
type SkillDoc = { name: string; frontmatter: Record<string, unknown>; files: Record<string, string> };
type Meta = { acm_version: string; transitions: Record<StoryStatus, StoryStatus[]>; kanban_columns: StoryStatus[] };
type OpenApi = { info: { version: string }; paths: Record<string, Record<string, { summary?: string; description?: string }>> };

export function DocsPage() {
  const skills = useQuery({ queryKey: ["skills"], queryFn: () => api<{ skills: SkillEntry[] }>("/skills") });
  const [selected, setSelected] = useState<string>("acm-schema");
  const doc = useQuery({ queryKey: ["skill", selected], queryFn: () => api<SkillDoc>(`/skills/${selected}`) });
  const meta = useQuery({ queryKey: ["meta"], queryFn: () => api<Meta>("/meta") });
  const openapi = useQuery({ queryKey: ["openapi"], queryFn: () => api<OpenApi>("/openapi.json") });
  return (
    <div className="page wide">
      <h1>Documentación</h1>
      <div className="grid-docs">
        <nav aria-label="Skills" className="panel">
          <h2>Skills de ACM</h2>
          {skills.isPending && <Loading what="skills" />}
          {skills.error && <ErrorBox error={skills.error} />}
          <ul className="nav-list">
            {skills.data?.skills.map((s) => {
              const name = String(s.frontmatter.name);
              return (
                <li key={name}>
                  <button type="button" className={name === selected ? "link active" : "link"} onClick={() => setSelected(name)} aria-current={name === selected}>
                    {name} <span className="muted small">v{String(s.frontmatter.version)}</span>
                  </button>
                </li>
              );
            })}
          </ul>
        </nav>
        <article className="panel" aria-label={`Skill ${selected}`}>
          {doc.isPending && <Loading what="documento" />}
          {doc.error && <ErrorBox error={doc.error} />}
          {doc.data &&
            Object.entries(doc.data.files).map(([file, text]) => {
              const { body } = splitFrontmatter(text);
              return (
                <div key={file}>
                  <table className="table compact">
                    <tbody>
                      {Object.entries(doc.data.frontmatter).map(([k, v]) => (
                        <tr key={k}><th>{k}</th><td>{Array.isArray(v) ? v.join(", ") : String(v)}</td></tr>
                      ))}
                    </tbody>
                  </table>
                  <Markdown text={body} />
                </div>
              );
            })}
        </article>
      </div>
      <Section title="Flujo de estados de las historias">
        {meta.data && (
          <table className="table">
            <thead><tr><th>Desde</th><th>Puede pasar a</th></tr></thead>
            <tbody>
              {STATUS_ORDER.map((s) => (
                <tr key={s}>
                  <td><StatusBadge status={s} /></td>
                  <td>
                    {(s === "PLANNED" ? (["READY", ...(meta.data.transitions[s] ?? [])] as StoryStatus[]) : meta.data.transitions[s] ?? []).map((t) => (
                      <StatusBadge key={t} status={t} />
                    ))}
                    {s === "PLANNED" && <span className="muted small"> (READY solo a través del gate de calidad)</span>}
                    {(meta.data.transitions[s] ?? []).length === 0 && s !== "PLANNED" && <span className="muted">estado terminal</span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Section>
      <Section title={`Referencia de la API REST${openapi.data ? ` (v${openapi.data.info.version})` : ""}`}>
        {openapi.error && <ErrorBox error={openapi.error} />}
        {openapi.data && (
          <table className="table">
            <thead><tr><th>Método</th><th>Ruta</th><th>Descripción</th></tr></thead>
            <tbody>
              {Object.entries(openapi.data.paths).flatMap(([path, ops]) =>
                Object.entries(ops).map(([method, op]) => (
                  <tr key={`${method} ${path}`}>
                    <td><code>{method.toUpperCase()}</code></td>
                    <td><code>/api/v1{path}</code></td>
                    <td>{op.description ?? op.summary ?? ""}</td>
                  </tr>
                )),
              )}
            </tbody>
          </table>
        )}
      </Section>
    </div>
  );
}
