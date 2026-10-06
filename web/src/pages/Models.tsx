// Modelos (US-50.09, US-50.10, US-22.06): lo que detecta cada runtime, qué es cada modelo de Ollaya (guía) y la
// elección de ACM: un modelo de Ollama y, en Ollaya, uno por defecto y uno por propósito. Solo un admin elige.
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { api, put } from "../api";
import { ErrorBox, Loading, Section } from "../components";
import { Field, FormStatus, submit, useAction } from "../forms";
import type { AvailableModel, ModelCatalog } from "../types";

function details(m: AvailableModel): string {
  const d = m.details as Record<string, string>;
  return [d.family, d.parameter_size, d.quantization_level, d.format].filter(Boolean).join(" · ");
}

function OllamaModels({ cat, admin }: { cat: ModelCatalog; admin: boolean }) {
  const o = cat.ollama;
  const [model, setModel] = useState(o.selected ?? "");
  const save = useAction(() => put("/models", { ollama_model: model }), [["models"], ["engines"]]);
  if (!o.configured) return <p className="muted">{o.hint}</p>;
  return (
    <>
      <p className="small">
        {o.endpoint} · elegido: <strong>{o.selected ?? "ninguno"}</strong> ({o.source === "acm" ? "elegido en ACM" : o.source === "env" ? "variable de arranque" : "sin elegir"})
      </p>
      {o.error && <p className="error" role="alert">{o.error}</p>}
      <table className="table">
        <thead><tr><th>Modelo</th><th>Detalles</th></tr></thead>
        <tbody>
          {o.available?.map((m) => (
            <tr key={m.name}>
              <td><code>{m.name}</code>{m.name === o.selected && <span className="tag">elegido</span>}</td>
              <td className="small">{details(m)}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {admin && (
        <form className="form-row" aria-label="Elegir modelo de Ollama" onSubmit={submit(() => save.mutate(undefined))}>
          <Field label="Modelo de Ollama" name="ollama_model" error={save.error}>
            <select value={model} onChange={(e) => setModel(e.target.value)}>
              <option value="">—</option>
              {o.available?.map((m) => <option key={m.name} value={m.name}>{m.name}</option>)}
            </select>
          </Field>
          <button className="primary" disabled={!model || save.isPending}>Usar este modelo</button>
          <FormStatus error={save.error} done={save.isSuccess} ok="Modelo de Ollama elegido" />
        </form>
      )}
      <p className="small muted">{cat.usage.ollama}</p>
    </>
  );
}

function JevModels({ cat, admin }: { cat: ModelCatalog; admin: boolean }) {
  const j = cat.jev;
  const purposes = [...Object.keys(cat.purposes), ...cat.seen_purposes];
  const [defaultModel, setDefault] = useState(j.default_model ?? "");
  const [byPurpose, setByPurpose] = useState<Record<string, string>>(j.models_by_purpose ?? {});
  const [notes, setNotes] = useState<Record<string, string>>(
    Object.fromEntries((j.available ?? []).map((m) => [m.name, m.note ?? ""])),
  );
  const [extra, setExtra] = useState("");
  const save = useAction(
    () =>
      put("/models", {
        jev_default_model: defaultModel || null,
        jev_models_by_purpose: Object.fromEntries(Object.entries(byPurpose).filter(([, m]) => m)),
        jev_model_notes: notes,
      }),
    [["models"], ["engines"]],
  );
  if (!j.configured) return <p className="muted">{j.hint}</p>;
  const names = (j.available ?? []).map((m) => m.name);
  return (
    <>
      <p className="small">
        {j.endpoint} · por defecto: <strong>{j.default_model ?? "ninguno"}</strong>
      </p>
      {j.error && <p className="error" role="alert">{j.error}</p>}
      <table className="table">
        <thead><tr><th>Modelo</th><th>Qué es (guía)</th><th>Para qué</th><th>Propósitos asignados</th><th>Nota del operador</th></tr></thead>
        <tbody>
          {j.available?.map((m) => (
            <tr key={m.name} data-model={m.name}>
              <td>
                <code>{m.name}</code>
                {m.default && <span className="tag">por defecto</span>}
                <div className="small muted">{details(m)}</div>
              </td>
              <td className="small">{m.guide ? m.guide.summary : <em>Sin guía: no es un modelo conocido de Ollaya.</em>}</td>
              <td className="small">{m.guide?.best_for}{m.guide?.notes && <><br />▲ {m.guide.notes}</>}</td>
              <td className="small">{m.purposes?.join(", ") || "—"}</td>
              <td>
                {admin ? (
                  <input aria-label={`Nota de ${m.name}`} value={notes[m.name] ?? ""} onChange={(e) => setNotes({ ...notes, [m.name]: e.target.value })} />
                ) : (
                  m.note || "—"
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {j.guide && (
        <details>
          <summary>Cómo elegir (fuente: {j.guide.source})</summary>
          <ul>{j.guide.choosing.map((c) => <li key={c}>{c}</li>)}</ul>
          <p className="small">Sugerencias de ACM por propósito:</p>
          <ul className="small">{Object.entries(j.guide.acm_suggestions).map(([k, v]) => <li key={k}><strong>{k}:</strong> {v}</li>)}</ul>
        </details>
      )}
      {admin && (
        <form className="form" aria-label="Elegir modelos de Ollaya" onSubmit={submit(() => save.mutate(undefined))}>
          <Field label="Modelo por defecto" name="jev_default_model" error={save.error}>
            <select value={defaultModel} onChange={(e) => setDefault(e.target.value)}>
              <option value="">—</option>
              {names.map((n) => <option key={n} value={n}>{n}</option>)}
            </select>
          </Field>
          <Field label="Modelo por propósito" name="jev_models_by_purpose" error={save.error} group>
            <table className="table compact">
              <tbody>
                {[...new Set([...purposes, ...Object.keys(byPurpose)])].map((p) => (
                  <tr key={p}>
                    <td><code>{p}</code><div className="small muted">{cat.purposes[p] ?? "propósito usado por agentes"}</div></td>
                    <td>
                      <select aria-label={`Modelo para ${p}`} value={byPurpose[p] ?? ""} onChange={(e) => setByPurpose({ ...byPurpose, [p]: e.target.value })}>
                        <option value="">(por defecto)</option>
                        {names.map((n) => <option key={n} value={n}>{n}</option>)}
                      </select>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Field>
          <div className="form-row">
            <label className="field">
              <span className="field-label">Otro propósito</span>
              <input value={extra} onChange={(e) => setExtra(e.target.value)} placeholder="ticket.triage" />
            </label>
            <button type="button" disabled={!extra.trim()} onClick={() => { setByPurpose({ ...byPurpose, [extra.trim()]: "" }); setExtra(""); }}>
              Añadir propósito
            </button>
          </div>
          <button className="primary" disabled={save.isPending}>Guardar modelos de Ollaya</button>
          <FormStatus error={save.error} done={save.isSuccess} ok="Modelos de Ollaya guardados" />
        </form>
      )}
      <p className="small muted">{cat.usage.jev}</p>
    </>
  );
}

export function ModelsSection({ admin }: { admin: boolean }) {
  const cat = useQuery({ queryKey: ["models"], queryFn: () => api<ModelCatalog>("/models") });
  if (cat.isPending) return <Loading what="modelos" />;
  if (cat.error) return <ErrorBox error={cat.error} />;
  return (
    <div className="grid-2">
      <Section title="Modelos de decisión — Ollaya (JEV)">
        <JevModels key={JSON.stringify(cat.data.jev.models_by_purpose) + cat.data.jev.default_model} cat={cat.data} admin={admin} />
      </Section>
      <Section title="Modelo local — Ollama">
        <OllamaModels key={cat.data.ollama.selected ?? "-"} cat={cat.data} admin={admin} />
      </Section>
    </div>
  );
}
