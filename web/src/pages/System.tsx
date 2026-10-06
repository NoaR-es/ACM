// Sistema (US-13.03, US-47.01, US-35.09, EPIC-20, US-31.11/31.12, US-50.09): salud, motores, modelos, ahorro,
// principales y tokens; un admin crea principales y tokens, cambia roles, revoca y refresca motores.
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { api, del, post, put } from "../api";
import { ErrorBox, fmtDate, Loading, Section } from "../components";
import { Disclosure, Field, FormStatus, submit, useAction } from "../forms";
import { ModelsSection } from "./Models";

type Health = { status: string; checked_at: string; components: { name: string; kind: string; status: string; detail: string }[] };
type Engines = { engines: { name: string; kind: string; provider: string; status: string; detail: string; models: string[]; registered: boolean; checked_at: string | null }[] };
type Savings = { groups: { principal: string; project_id: string; method: string; deliveries: number; delivered: number; full_equivalent: number; saved: number }[]; totals: Record<string, number> };
type Principals = { principals: { id: string; role: string; kind: string; created_at: string }[] };
type Tokens = { tokens: { token_id: string; principal_id: string; name: string; prefix: string; active: boolean; use_count: number; last_used_at: string | null; created_at: string }[] };

const ICON: Record<string, string> = { ok: "✔", degraded: "▲", error: "✖", unknown: "?" };

function Health() {
  const q = useQuery({ queryKey: ["health"], queryFn: () => api<Health>("/health"), refetchInterval: 30_000 });
  if (q.isPending) return <Loading what="salud" />;
  if (q.error) return <ErrorBox error={q.error} />;
  return (
    <Section title={`Salud: ${ICON[q.data.status] ?? ""} ${q.data.status} (comprobado ${fmtDate(q.data.checked_at)})`}>
      <table className="table">
        <thead><tr><th>Componente</th><th>Tipo</th><th>Estado</th><th>Detalle</th></tr></thead>
        <tbody>
          {q.data.components.map((c) => (
            <tr key={c.name} className={c.status === "error" ? "is-error" : ""} data-health={c.status}>
              <td><code>{c.name}</code></td>
              <td>{c.kind}</td>
              <td><span className={`health health-${c.status}`}>{ICON[c.status]} {c.status}</span></td>
              <td className="small">{c.detail}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </Section>
  );
}

function NewPrincipal() {
  const [id, setId] = useState("");
  const [kind, setKind] = useState("agent");
  const [role, setRole] = useState("user");
  const create = useAction(() => post("/principals", { principal_id: id, kind, role }), [["principals"]]);
  return (
    <Disclosure label="Nuevo principal">
      <form className="form" aria-label="Nuevo principal" onSubmit={submit(() => create.mutate(undefined, { onSuccess: () => setId("") }))}>
        <Field label="Identificador" name="principal_id" error={create.error}>
          <input value={id} onChange={(e) => setId(e.target.value)} />
        </Field>
        <div className="form-row">
          <Field label="Tipo" name="kind" error={create.error}>
            <select value={kind} onChange={(e) => setKind(e.target.value)}>
              <option value="agent">agente</option>
              <option value="user">usuario</option>
            </select>
          </Field>
          <Field label="Rol global" name="role" error={create.error}>
            <select value={role} onChange={(e) => setRole(e.target.value)}>
              <option value="user">user</option>
              <option value="admin">admin</option>
            </select>
          </Field>
        </div>
        <button className="primary" disabled={create.isPending}>Crear principal</button>
        <FormStatus error={create.error} done={create.isSuccess} ok="Principal creado" />
      </form>
    </Disclosure>
  );
}

function NewToken({ principals }: { principals: string[] }) {
  const [principal, setPrincipal] = useState(principals[0] ?? "");
  const [name, setName] = useState("");
  const [copied, setCopied] = useState(false);
  const create = useAction(() => post<{ token: string; token_id: string }>("/tokens", { principal_id: principal, name }), [["tokens"]]);
  const secret = create.data?.token;
  return (
    <Disclosure label="Nuevo token">
      <form className="form" aria-label="Nuevo token" onSubmit={submit(() => { setCopied(false); create.mutate(undefined); })}>
        <div className="form-row">
          <Field label="Principal" name="principal_id" error={create.error}>
            <select value={principal} onChange={(e) => setPrincipal(e.target.value)}>
              {principals.map((p) => <option key={p} value={p}>{p}</option>)}
            </select>
          </Field>
          <Field label="Nombre del token" name="name" error={create.error}>
            <input value={name} onChange={(e) => setName(e.target.value)} placeholder="portátil, CI…" />
          </Field>
        </div>
        <button className="primary" disabled={create.isPending}>Crear token</button>
        <FormStatus error={create.error} done={false} ok="" />
      </form>
      {secret && (
        <div className="secret" role="status" aria-label="Token nuevo">
          <code data-secret>{secret}</code>
          <button type="button" onClick={() => navigator.clipboard?.writeText(secret).then(() => setCopied(true))}>
            {copied ? "✔ Copiado" : "Copiar"}
          </button>
          <strong>Guárdalo ahora: no se volverá a mostrar.</strong>
        </div>
      )}
    </Disclosure>
  );
}

export function SystemPage() {
  const engines = useQuery({ queryKey: ["engines"], queryFn: () => api<Engines>("/engines") });
  const savings = useQuery({ queryKey: ["savings"], queryFn: () => api<Savings>("/savings") });
  const principals = useQuery({ queryKey: ["principals"], queryFn: () => api<Principals>("/principals") });
  const tokens = useQuery({ queryKey: ["tokens"], queryFn: () => api<Tokens>("/tokens") });
  const refresh = useAction(() => post("/engines/refresh"), [["engines"], ["models"], ["health"]]);
  const setRole = useAction(({ id, role }: { id: string; role: string }) => put(`/principals/${id}/role`, { role }), [["principals"]]);
  const revoke = useAction((id: string) => del(`/tokens/${id}`), [["tokens"]]);
  return (
    <div className="page wide">
      <h1>Sistema</h1>
      <Health />
      <ModelsSection admin />
      <Section
        title="Motores de inferencia"
        actions={
          <button type="button" onClick={() => refresh.mutate(undefined)} disabled={refresh.isPending}>
            {refresh.isPending ? "Comprobando…" : "Comprobar motores"}
          </button>
        }
      >
        {engines.error && <ErrorBox error={engines.error} />}
        {refresh.error && <ErrorBox error={refresh.error} />}
        <table className="table">
          <thead><tr><th>Motor</th><th>Tipo</th><th>Proveedor</th><th>Estado</th><th>Modelos detectados</th><th>Comprobado</th></tr></thead>
          <tbody>
            {engines.data?.engines.map((e) => (
              <tr key={e.name}>
                <td><code>{e.name}</code>{!e.registered && <span className="muted small"> (histórico)</span>}</td>
                <td>{e.kind === "decision" ? "decisión" : "generación"}</td>
                <td>{e.provider}</td>
                <td>{e.status} <span className="small muted">{e.detail}</span></td>
                <td className="small">{e.models.join(", ") || "—"}</td>
                <td className="small">{fmtDate(e.checked_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Section>
      <Section title="Tokens ahorrados a los agentes (segundo cerebro)">
        {savings.error && <ErrorBox error={savings.error} />}
        {savings.data && (
          <>
            <p>
              Total: <strong>{savings.data.totals.saved ?? 0}</strong> tokens ahorrados en {savings.data.totals.deliveries ?? 0} entregas
              ({savings.data.totals.delivered ?? 0} entregados frente a {savings.data.totals.full_equivalent ?? 0} equivalentes).
            </p>
            <table className="table">
              <thead><tr><th>Agente</th><th>Proyecto</th><th>Método</th><th>Entregas</th><th>Entregados</th><th>Equivalente</th><th>Ahorro</th></tr></thead>
              <tbody>
                {savings.data.groups.map((g) => (
                  <tr key={`${g.principal}/${g.project_id}/${g.method}`}>
                    <td>{g.principal}</td><td>{g.project_id}</td><td><code>{g.method}</code></td><td>{g.deliveries}</td>
                    <td>{g.delivered}</td><td>{g.full_equivalent}</td><td><strong>{g.saved}</strong></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </>
        )}
      </Section>
      <div className="grid-2">
        <Section title="Principales">
          {principals.error && <ErrorBox error={principals.error} />}
          <NewPrincipal />
          <table className="table">
            <thead><tr><th>Id</th><th>Tipo</th><th>Rol global</th><th>Alta</th></tr></thead>
            <tbody>
              {principals.data?.principals.map((p) => (
                <tr key={p.id} data-principal={p.id}>
                  <td>{p.id}</td>
                  <td>{p.kind === "agent" ? "agente" : "usuario"}</td>
                  <td>
                    <select aria-label={`Rol global de ${p.id}`} value={p.role} onChange={(e) => setRole.mutate({ id: p.id, role: e.target.value })}>
                      <option value="user">user</option>
                      <option value="admin">admin</option>
                    </select>
                  </td>
                  <td className="small">{fmtDate(p.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {setRole.error && <ErrorBox error={setRole.error} />}
        </Section>
        <Section title="Tokens (nunca se muestra el secreto)">
          {tokens.error && <ErrorBox error={tokens.error} />}
          <NewToken principals={principals.data?.principals.map((p) => p.id) ?? []} />
          <table className="table">
            <thead><tr><th>Token</th><th>Principal</th><th>Nombre</th><th>Estado</th><th>Usos</th><th>Último uso</th><th></th></tr></thead>
            <tbody>
              {tokens.data?.tokens.map((t) => (
                <tr key={t.token_id}>
                  <td><code>{t.prefix}…</code></td><td>{t.principal_id}</td><td>{t.name}</td>
                  <td>{t.active ? "✔ activo" : "✖ revocado"}</td><td>{t.use_count}</td><td className="small">{fmtDate(t.last_used_at)}</td>
                  <td>
                    {t.active && (
                      <button type="button" className="link" onClick={() => revoke.mutate(t.token_id)}>
                        Revocar
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {revoke.error && <ErrorBox error={revoke.error} />}
        </Section>
      </div>
    </div>
  );
}
