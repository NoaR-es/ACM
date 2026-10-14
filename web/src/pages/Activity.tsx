// Actividad (US-14.10, US-31.01/02/04): consola en vivo y auditoría filtrable. Solo admin.
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "../api";
import { Empty, ErrorBox, fmtDate, Loading, Section } from "../components";
import { useLive } from "../live";

type Entry = {
  id: number; ts: string; principal: string; operation: string; project_id: string | null; status: "ok" | "error";
  error: string; duration_ms: number; arguments: Record<string, unknown>; token_id: string | null;
};

export function ActivityPage() {
  const [filters, setFilters] = useState({ project_id: "", principal_id: "", operation: "", onlyErrors: false });
  const params = new URLSearchParams({ limit: "200" });
  if (filters.project_id) params.set("project_id", filters.project_id);
  if (filters.principal_id) params.set("principal_id", filters.principal_id);
  if (filters.operation) params.set("operation", filters.operation);
  const audit = useQuery({ queryKey: ["activity", params.toString()], queryFn: () => api<{ entries: Entry[] }>(`/activity?${params}`) });
  const { events } = useLive();
  const live = events.filter((e) => e.type === "activity").slice(0, 30);
  const rows = (audit.data?.entries ?? []).filter((e) => !filters.onlyErrors || e.status === "error");
  const set = (k: keyof typeof filters, v: string | boolean) => setFilters((f) => ({ ...f, [k]: v }));
  return (
    <div className="page wide">
      <h1>Actividad</h1>
      <Section title="En directo: herramientas que ejecutan los agentes">
        {live.length === 0 ? (
          <Empty>Esperando actividad…</Empty>
        ) : (
          <ol className="feed" aria-live="polite">
            {live.map((e) => (
              <li key={e.seq} className={e.data.status === "error" ? "is-error" : ""}>
                <span className="small muted">{fmtDate(e.ts)}</span> <strong>{e.principal}</strong> →{" "}
                <code>{e.entity_id}</code> {e.project_id && <span className="muted">en {e.project_id}</span>}{" "}
                {e.data.status === "error" ? <strong className="danger">✖ {String(e.data.error)}</strong> : "✔"}
              </li>
            ))}
          </ol>
        )}
      </Section>
      <Section title="Auditoría de invocaciones">
        <div className="toolbar">
          <label>Proyecto <input value={filters.project_id} onChange={(e) => set("project_id", e.target.value)} /></label>
          <label>Principal <input value={filters.principal_id} onChange={(e) => set("principal_id", e.target.value)} /></label>
          <label>Operación <input value={filters.operation} onChange={(e) => set("operation", e.target.value)} placeholder="acm_story_set_status" /></label>
          <label className="check"><input type="checkbox" checked={filters.onlyErrors} onChange={(e) => set("onlyErrors", e.target.checked)} /> Solo errores</label>
          <button type="button" onClick={() => setFilters({ project_id: "", principal_id: "", operation: "", onlyErrors: false })}>Limpiar filtros</button>
        </div>
        {audit.isPending && <Loading what="auditoría" />}
        {audit.error && <ErrorBox error={audit.error} />}
        {audit.data && (
          <table className="table">
            <thead>
              <tr><th>Fecha</th><th>Principal</th><th>Operación</th><th>Proyecto</th><th>Estado</th><th>ms</th><th>Argumentos</th></tr>
            </thead>
            <tbody>
              {rows.map((e) => (
                <tr key={e.id} className={e.status === "error" ? "is-error" : ""}>
                  <td className="small">{fmtDate(e.ts)}</td>
                  <td>{e.principal}{e.token_id && <span className="muted small"> ({e.token_id})</span>}</td>
                  <td><code>{e.operation}</code></td>
                  <td>{e.project_id ?? "—"}</td>
                  <td>{e.status === "ok" ? "✔ ok" : <strong className="danger">✖ {e.error}</strong>}</td>
                  <td>{e.duration_ms.toFixed(1)}</td>
                  <td className="small"><code>{JSON.stringify(e.arguments)}</code></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        {audit.data && rows.length === 0 && <Empty>Ningún resultado con estos filtros.</Empty>}
      </Section>
    </div>
  );
}
