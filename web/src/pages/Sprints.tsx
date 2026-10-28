// Sprints del proyecto (EPIC-05, US-05.02..05.09): crear, planificar historias, iniciar (con control de sobrecarga),
// cerrar con traslado de lo no terminado, cancelar, tablero del sprint y resumen de cierre.
import { useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, del, post } from "../api";
import { Empty, ErrorBox, fmtDate, Loading, Section, StatusBadge, StatusBar } from "../components";
import { Disclosure, Field, FormStatus, submit, useAction } from "../forms";
import { KanbanBoard } from "../KanbanBoard";
import type { Kanban, Sprint } from "../types";
import { useBacklog } from "./Project";

const STATUS_TEXT: Record<Sprint["status"], string> = {
  PLANNED: "Planificado",
  ACTIVE: "Activo",
  CLOSED: "Cerrado",
  CANCELLED: "Cancelado",
};

export function useSprints(projectId: string) {
  return useQuery({
    queryKey: ["sprints", projectId],
    queryFn: () => api<{ sprints: Sprint[] }>(`/projects/${projectId}/sprints`),
  });
}

function keys(projectId: string) {
  return [["sprints", projectId], ["project", projectId], ["kanban"]];
}

function CreateSprint({ projectId }: { projectId: string }) {
  const [name, setName] = useState("");
  const [goal, setGoal] = useState("");
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [capacity, setCapacity] = useState("");
  const create = useAction(
    () =>
      post(`/projects/${projectId}/sprints`, {
        name,
        goal,
        start_date: start,
        end_date: end,
        capacity: capacity ? Number(capacity) : null,
      }),
    keys(projectId),
  );
  return (
    <Disclosure label="Nuevo sprint">
      <form className="form" aria-label="Nuevo sprint" onSubmit={submit(() => create.mutate(undefined))}>
        <Field label="Nombre" name="name" error={create.error}>
          <input value={name} onChange={(e) => setName(e.target.value)} maxLength={120} />
        </Field>
        <Field label="Objetivo del sprint" name="goal" error={create.error}>
          <textarea value={goal} onChange={(e) => setGoal(e.target.value)} />
        </Field>
        <div className="form-row">
          <Field label="Inicio" name="start_date" error={create.error}>
            <input type="date" value={start} onChange={(e) => setStart(e.target.value)} />
          </Field>
          <Field label="Fin" name="end_date" error={create.error}>
            <input type="date" value={end} onChange={(e) => setEnd(e.target.value)} />
          </Field>
          <Field label="Capacidad (historias)" name="capacity" error={create.error} hint="Opcional">
            <input type="number" min={1} value={capacity} onChange={(e) => setCapacity(e.target.value)} />
          </Field>
        </div>
        <button className="primary" disabled={create.isPending}>Crear sprint</button>
        <FormStatus error={create.error} done={create.isSuccess} ok="Sprint creado" />
      </form>
    </Disclosure>
  );
}

function SprintCard({ projectId, sprint, all }: { projectId: string; sprint: Sprint; all: Sprint[] }) {
  const backlog = useBacklog(projectId);
  const [pick, setPick] = useState<string[]>([]);
  const [carry, setCarry] = useState("");
  const [showBoard, setShowBoard] = useState(sprint.status === "ACTIVE");
  useEffect(() => {
    if (sprint.status === "ACTIVE") setShowBoard(true); // al iniciarlo, el tablero del sprint se muestra solo
  }, [sprint.status]);
  const k = keys(projectId);
  const add = useAction(() => post<Sprint>(`/projects/${projectId}/sprints/${sprint.id}/stories`, { story_ids: pick }), k);
  const remove = useAction((sid: string) => del(`/projects/${projectId}/sprints/${sprint.id}/stories/${sid}`), k);
  const start = useAction((force: boolean) => post(`/projects/${projectId}/sprints/${sprint.id}/start`, { force }), k);
  const close = useAction(() => post(`/projects/${projectId}/sprints/${sprint.id}/close`, { carry_over_to: carry || null }), k);
  const cancel = useAction(() => post(`/projects/${projectId}/sprints/${sprint.id}/cancel`), k);
  const board = useQuery({
    queryKey: ["kanban", projectId, sprint.id],
    queryFn: () => api<Kanban>(`/kanban?projects=${projectId}&sprint=${sprint.id}`),
    enabled: showBoard,
  });
  const open = sprint.status === "PLANNED" || sprint.status === "ACTIVE";
  const candidates = (backlog.data?.stories ?? []).filter(
    (s) => s.sprint_id === null && !["DONE", "CANCELLED", "DEPRECATED"].includes(s.status),
  );
  const stories = new Map((backlog.data?.stories ?? []).map((s) => [s.id, s]));
  const plannedTargets = all.filter((s) => s.status === "PLANNED" && s.id !== sprint.id);
  const overloaded = start.error && String((start.error as Error).message).includes("sobrecargado");
  return (
    <section className="panel" aria-label={`${sprint.id} ${sprint.name}`} data-sprint={sprint.id}>
      <header className="panel-head">
        <h2>
          {sprint.id} — {sprint.name} <span className="tag">{STATUS_TEXT[sprint.status]}</span>
        </h2>
      </header>
      <p><strong>Objetivo:</strong> {sprint.goal}</p>
      <p className="small muted">
        {sprint.start_date} → {sprint.end_date} · carga {sprint.load}
        {sprint.capacity !== null && ` de ${sprint.capacity}`} historias
        {sprint.overloaded && <strong className="danger"> · ▲ sobrecargado</strong>}
        {sprint.started_at && ` · iniciado ${fmtDate(sprint.started_at)}`}
        {sprint.closed_at && ` · cerrado ${fmtDate(sprint.closed_at)}`}
      </p>
      <StatusBar counts={sprint.stories_by_status} />
      {sprint.story_ids.length === 0 ? (
        <Empty>Sin historias planificadas.</Empty>
      ) : (
        <ul className="story-list">
          {sprint.story_ids.map((sid) => (
            <li key={sid}>
              <Link to={`/p/${projectId}/s/${sid}`}>{sid}</Link>{" "}
              {stories.get(sid) && <StatusBadge status={stories.get(sid)!.status} />} {stories.get(sid)?.i_want}{" "}
              {open && (
                <button type="button" className="link" onClick={() => remove.mutate(sid)}>
                  Quitar
                </button>
              )}
            </li>
          ))}
        </ul>
      )}
      {sprint.summary?.text && <p className="report"><strong>Resumen del cierre:</strong> {sprint.summary.text}</p>}
      {sprint.history.length > 0 && (
        <details>
          <summary>Historial de pertenencia ({sprint.history.length})</summary>
          <ul>
            {sprint.history.map((h) => (
              <li key={h.story_id + h.ended_at}>
                {h.story_id}: {h.outcome} ({fmtDate(h.ended_at)})
              </li>
            ))}
          </ul>
        </details>
      )}
      {open && (
        <Disclosure label={`Planificar historias en ${sprint.id}`}>
          <form className="form" onSubmit={submit(() => add.mutate(undefined, { onSuccess: () => setPick([]) }))}>
            {candidates.length === 0 ? (
              <p className="small muted">No hay historias libres (cada historia solo cabe en un sprint abierto).</p>
            ) : (
              <fieldset className="checklist">
                <legend className="sr-only">Historias</legend>
                {candidates.map((s) => (
                  <label key={s.id} className="check">
                    <input
                      type="checkbox"
                      checked={pick.includes(s.id)}
                      onChange={(e) => setPick(e.target.checked ? [...pick, s.id] : pick.filter((x) => x !== s.id))}
                    />{" "}
                    {s.id} <StatusBadge status={s.status} /> {s.i_want}
                  </label>
                ))}
              </fieldset>
            )}
            <button className="primary" disabled={add.isPending || pick.length === 0}>Añadir al sprint</button>
            {add.data?.warnings?.map((w) => <p key={w} className="small">▲ {w}</p>)}
            <FormStatus error={add.error} done={add.isSuccess} ok="Historias planificadas" />
          </form>
        </Disclosure>
      )}
      <div className="row">
        {sprint.status === "PLANNED" && (
          <button type="button" className="primary" onClick={() => start.mutate(false)} disabled={start.isPending}>
            Iniciar sprint
          </button>
        )}
        {overloaded && (
          <button type="button" onClick={() => start.mutate(true)}>
            Iniciar igualmente (sobrecargado)
          </button>
        )}
        {sprint.status === "ACTIVE" && (
          <>
            <label>
              Lo no terminado{" "}
              <select value={carry} onChange={(e) => setCarry(e.target.value)} aria-label="Destino de lo no terminado">
                <option value="">vuelve al backlog</option>
                {plannedTargets.map((s) => <option key={s.id} value={s.id}>pasa a {s.id}</option>)}
              </select>
            </label>
            <button type="button" className="primary" onClick={() => close.mutate(undefined)} disabled={close.isPending}>
              Cerrar sprint
            </button>
          </>
        )}
        {open && (
          <button type="button" onClick={() => cancel.mutate(undefined)} disabled={cancel.isPending}>
            Cancelar sprint
          </button>
        )}
        {sprint.story_ids.length > 0 && (
          <button type="button" onClick={() => setShowBoard(!showBoard)} aria-expanded={showBoard}>
            {showBoard ? "Ocultar tablero" : "Tablero del sprint"}
          </button>
        )}
      </div>
      {[start, close, cancel, remove].map((m, i) => m.error && <ErrorBox key={i} error={m.error} />)}
      {showBoard && board.data && <KanbanBoard board={board.data} allProjects={[projectId]} />}
    </section>
  );
}

export function SprintsView({ projectId }: { projectId: string }) {
  const sprints = useSprints(projectId);
  if (sprints.isPending) return <Loading what="sprints" />;
  if (sprints.error) return <ErrorBox error={sprints.error} />;
  const list = sprints.data.sprints;
  const order = { ACTIVE: 0, PLANNED: 1, CLOSED: 2, CANCELLED: 3 };
  return (
    <>
      <CreateSprint projectId={projectId} />
      {list.length === 0 ? (
        <Section title="Sprints">
          <Empty>Todavía no hay sprints. Crea uno con su objetivo y fechas.</Empty>
        </Section>
      ) : (
        [...list]
          .sort((a, b) => order[a.status] - order[b.status] || a.id.localeCompare(b.id))
          .map((s) => <SprintCard key={s.id} projectId={projectId} sprint={s} all={list} />)
      )}
    </>
  );
}
