// Construir el backlog desde la interfaz (US-31.10): requisitos, épicas, features, historias y criterios; enlazar
// requisitos, confirmar cobertura y dividir features. Cada error se muestra junto a su campo, sin perder lo escrito.
import { useState } from "react";
import { post } from "../api";
import { Disclosure, Field, FormStatus, lines, submit, useAction } from "../forms";
import type { Backlog, Epic, Feature } from "../types";

const keys = (projectId: string) => [["project", projectId], ["kanban"], ["projects"]];

function ReqChecklist({
  backlog,
  value,
  onChange,
  name,
}: {
  backlog: Backlog;
  value: string[];
  onChange: (v: string[]) => void;
  name: string;
}) {
  if (backlog.requirements.length === 0) return <p className="small muted">Crea antes un requisito.</p>;
  return (
    <fieldset className="checklist" data-field={name}>
      <legend className="sr-only">Requisitos</legend>
      {backlog.requirements.map((r) => (
        <label key={r.id} className="check">
          <input
            type="checkbox"
            checked={value.includes(r.id)}
            onChange={(e) => onChange(e.target.checked ? [...value, r.id] : value.filter((x) => x !== r.id))}
          />{" "}
          {r.id} {r.title}
        </label>
      ))}
    </fieldset>
  );
}

export function RequirementForm({ projectId }: { projectId: string }) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const create = useAction(() => post(`/projects/${projectId}/requirements`, { title, description }), keys(projectId));
  return (
    <Disclosure label="Nuevo requisito">
      <form
        className="form"
        aria-label="Nuevo requisito"
        onSubmit={submit(() => create.mutate(undefined, { onSuccess: () => { setTitle(""); setDescription(""); } }))}
      >
        <Field label="Título" name="title" error={create.error}>
          <input value={title} onChange={(e) => setTitle(e.target.value)} maxLength={200} required />
        </Field>
        <Field label="Descripción" name="description" error={create.error}>
          <textarea value={description} onChange={(e) => setDescription(e.target.value)} />
        </Field>
        <button className="primary" disabled={create.isPending}>Crear requisito</button>
        <FormStatus error={create.error} done={create.isSuccess} ok="Requisito creado" />
      </form>
    </Disclosure>
  );
}

export function EpicForm({ projectId, backlog }: { projectId: string; backlog: Backlog }) {
  const [title, setTitle] = useState("");
  const [objective, setObjective] = useState("");
  const [scope, setScope] = useState("");
  const [reqs, setReqs] = useState<string[]>([]);
  const create = useAction(
    () => post(`/projects/${projectId}/epics`, { title, objective, scope, requirement_ids: reqs }),
    keys(projectId),
  );
  const reset = () => { setTitle(""); setObjective(""); setScope(""); setReqs([]); };
  return (
    <Disclosure label="Nueva épica">
      <form className="form" aria-label="Nueva épica" onSubmit={submit(() => create.mutate(undefined, { onSuccess: reset }))}>
        <Field label="Título" name="title" error={create.error}>
          <input value={title} onChange={(e) => setTitle(e.target.value)} maxLength={200} required />
        </Field>
        <Field label="Objetivo" name="objective" error={create.error}>
          <textarea value={objective} onChange={(e) => setObjective(e.target.value)} />
        </Field>
        <Field label="Alcance" name="scope" error={create.error}>
          <textarea value={scope} onChange={(e) => setScope(e.target.value)} />
        </Field>
        <Field label="Requisitos que cubre" name="requirement_ids" error={create.error} group>
          <ReqChecklist backlog={backlog} value={reqs} onChange={setReqs} name="requirement_ids" />
        </Field>
        <button className="primary" disabled={create.isPending}>Crear épica</button>
        <FormStatus error={create.error} done={create.isSuccess} ok="Épica creada" />
      </form>
    </Disclosure>
  );
}

export function FeatureForm({ projectId, epic }: { projectId: string; epic: Epic }) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const create = useAction(
    () => post(`/projects/${projectId}/features`, { epic_id: epic.id, title, description }),
    keys(projectId),
  );
  return (
    <Disclosure label={`Nueva feature en ${epic.id}`}>
      <form
        className="form"
        aria-label={`Nueva feature en ${epic.id}`}
        onSubmit={submit(() => create.mutate(undefined, { onSuccess: () => { setTitle(""); setDescription(""); } }))}
      >
        <Field label="Título" name="title" error={create.error}>
          <input value={title} onChange={(e) => setTitle(e.target.value)} maxLength={200} required />
        </Field>
        <Field label="Descripción" name="description" error={create.error}>
          <textarea value={description} onChange={(e) => setDescription(e.target.value)} />
        </Field>
        <button className="primary" disabled={create.isPending}>Crear feature</button>
        <FormStatus error={create.error} done={create.isSuccess} ok="Feature creada" />
      </form>
    </Disclosure>
  );
}

export function EpicActions({ projectId, epic, backlog }: { projectId: string; epic: Epic; backlog: Backlog }) {
  const [reqs, setReqs] = useState<string[]>([]);
  const link = useAction(
    () => post(`/projects/${projectId}/epics/${epic.id}/requirements`, { requirement_ids: reqs }),
    keys(projectId),
  );
  const confirm = useAction(() => post(`/projects/${projectId}/epics/${epic.id}/confirm-coverage`), keys(projectId));
  const unlinked: Backlog = { ...backlog, requirements: backlog.requirements.filter((r) => !epic.requirement_ids.includes(r.id)) };
  return (
    <div className="row">
      {unlinked.requirements.length > 0 && (
        <Disclosure label={`Enlazar requisitos a ${epic.id}`}>
          <form className="form" onSubmit={submit(() => link.mutate(undefined, { onSuccess: () => setReqs([]) }))}>
            <ReqChecklist backlog={unlinked} value={reqs} onChange={setReqs} name="requirement_ids" />
            <button className="primary" disabled={link.isPending || reqs.length === 0}>Enlazar</button>
            <FormStatus error={link.error} done={link.isSuccess} ok="Requisitos enlazados" />
          </form>
        </Disclosure>
      )}
      {!epic.coverage_confirmed_at && (
        <button type="button" onClick={() => confirm.mutate(undefined)} disabled={confirm.isPending}>
          Confirmar cobertura de {epic.id}
        </button>
      )}
      <FormStatus error={confirm.error} done={confirm.isSuccess} ok="Cobertura confirmada" />
    </div>
  );
}

export function SplitForm({ projectId, feature }: { projectId: string; feature: Feature }) {
  const [titles, setTitles] = useState(["", ""]);
  const [assign, setAssign] = useState<Record<string, number>>(() =>
    Object.fromEntries(feature.story_ids.map((s) => [s, 0])),
  );
  const split = useAction(
    () =>
      post(`/projects/${projectId}/features/${feature.id}/split`, {
        parts: titles.map((title, i) => ({ title, story_ids: feature.story_ids.filter((s) => assign[s] === i) })),
      }),
    keys(projectId),
  );
  if (feature.status !== "ACTIVE" || feature.story_ids.length < 2) return null;
  return (
    <Disclosure label={`Dividir ${feature.id}`}>
      <form className="form" aria-label={`Dividir ${feature.id}`} onSubmit={submit(() => split.mutate(undefined))}>
        {titles.map((t, i) => (
          <Field key={i} label={`Título de la parte ${i + 1}`} name={`parts[${i}].title`} error={split.error}>
            <input value={t} onChange={(e) => setTitles(titles.map((x, j) => (j === i ? e.target.value : x)))} required />
          </Field>
        ))}
        <button type="button" onClick={() => setTitles([...titles, ""])}>+ Otra parte</button>
        {feature.story_ids.map((s) => (
          <label key={s} className="check">
            {s} va a la parte{" "}
            <select value={assign[s]} onChange={(e) => setAssign({ ...assign, [s]: Number(e.target.value) })}>
              {titles.map((_, i) => <option key={i} value={i}>{i + 1}</option>)}
            </select>
          </label>
        ))}
        <button className="primary" disabled={split.isPending}>Dividir</button>
        <FormStatus error={split.error} done={split.isSuccess} ok="Feature dividida" />
      </form>
    </Disclosure>
  );
}

export function StoryForm({ projectId, backlog }: { projectId: string; backlog: Backlog }) {
  const features = backlog.epics.flatMap((e) => e.features.filter((f) => f.status === "ACTIVE"));
  const [featureId, setFeatureId] = useState(features[0]?.id ?? "");
  const [asA, setAsA] = useState("");
  const [iWant, setIWant] = useState("");
  const [soThat, setSoThat] = useState("");
  const [reqs, setReqs] = useState<string[]>([]);
  const [criteria, setCriteria] = useState("");
  const [kind, setKind] = useState<"user_story" | "technical">("user_story");
  const [reason, setReason] = useState("");
  const create = useAction(
    () =>
      post(`/projects/${projectId}/stories`, {
        feature_id: featureId,
        as_a: asA,
        i_want: iWant,
        so_that: soThat,
        requirement_ids: reqs,
        acceptance_criteria: lines(criteria),
        kind,
        technical_reason: kind === "technical" ? reason : "",
      }),
    keys(projectId),
  );
  const reset = () => { setAsA(""); setIWant(""); setSoThat(""); setReqs([]); setCriteria(""); setReason(""); };
  if (features.length === 0) return <p className="small muted">Para crear historias, crea antes una épica con una feature.</p>;
  return (
    <Disclosure label="Nueva historia">
      <form className="form" aria-label="Nueva historia" onSubmit={submit(() => create.mutate(undefined, { onSuccess: reset }))}>
        <Field label="Feature" name="feature_id" error={create.error}>
          <select value={featureId} onChange={(e) => setFeatureId(e.target.value)}>
            {features.map((f) => <option key={f.id} value={f.id}>{f.id} — {f.title}</option>)}
          </select>
        </Field>
        <Field label="Tipo" name="kind" error={create.error}>
          <select value={kind} onChange={(e) => setKind(e.target.value as "user_story" | "technical")}>
            <option value="user_story">Historia de usuario</option>
            <option value="technical">Técnica</option>
          </select>
        </Field>
        <Field label="Como" name="as_a" error={create.error}>
          <input value={asA} onChange={(e) => setAsA(e.target.value)} />
        </Field>
        <Field label="Quiero" name="i_want" error={create.error}>
          <input value={iWant} onChange={(e) => setIWant(e.target.value)} />
        </Field>
        <Field label="Para" name="so_that" error={create.error}>
          <input value={soThat} onChange={(e) => setSoThat(e.target.value)} />
        </Field>
        {kind === "technical" && (
          <Field label="Razón técnica" name="technical_reason" error={create.error}>
            <input value={reason} onChange={(e) => setReason(e.target.value)} />
          </Field>
        )}
        <Field label="Requisitos de origen" name="requirement_ids" error={create.error} group>
          <ReqChecklist backlog={backlog} value={reqs} onChange={setReqs} name="requirement_ids" />
        </Field>
        <Field label="Criterios de aceptación (uno por línea)" name="acceptance_criteria" error={create.error}>
          <textarea value={criteria} onChange={(e) => setCriteria(e.target.value)} />
        </Field>
        <button className="primary" disabled={create.isPending}>Crear historia</button>
        <FormStatus error={create.error} done={create.isSuccess} ok="Historia creada" />
      </form>
    </Disclosure>
  );
}

export function CriteriaForm({ projectId, storyId }: { projectId: string; storyId: string }) {
  const [text, setText] = useState("");
  const add = useAction(
    () => post(`/projects/${projectId}/stories/${storyId}/criteria`, { criteria: lines(text) }),
    [["story", projectId, storyId], ["project", projectId]],
  );
  return (
    <Disclosure label="Añadir criterios">
      <form className="form" aria-label="Añadir criterios" onSubmit={submit(() => add.mutate(undefined, { onSuccess: () => setText("") }))}>
        <Field label="Criterios (uno por línea)" name="criteria" error={add.error}>
          <textarea value={text} onChange={(e) => setText(e.target.value)} />
        </Field>
        <button className="primary" disabled={add.isPending}>Añadir</button>
        <FormStatus error={add.error} done={add.isSuccess} ok="Criterios añadidos" />
      </form>
    </Disclosure>
  );
}
