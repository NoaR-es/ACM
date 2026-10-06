// Supervisor ágil autónomo (US-13.14, US-13.15): informe de la última auditoría (lo hecho, lo pendiente, las
// incongruencias), acciones que ACM aplicó por sí solo —con botón para deshacerlas— y propuestas pendientes.
import { post } from "../api";
import { Empty, ErrorBox, Markdown, Section } from "../components";
import { useAction } from "../forms";
import type { SupervisorAction, WatchdogRun } from "../types";

const ACTION_TEXT: Record<string, string> = {
  "story.mark_ready": "Pasar a READY",
  "story.back_to_planned": "Devolver a PLANNED",
  "sprint.remove_story": "Sacar del sprint",
  "story.split": "Dividir la historia",
  "sprint.close": "Cerrar el sprint",
  "story.review_stale": "Revisar historia estancada",
};

function Undo({ projectId, action }: { projectId: string; action: SupervisorAction }) {
  const undo = useAction(async () => {
    if (action.type === "story.mark_ready") {
      return post(`/projects/${projectId}/stories/${action.target}/status`, { status: "PLANNED", reason: "deshacer supervisor" });
    }
    if (action.type === "story.back_to_planned") return post(`/projects/${projectId}/stories/${action.target}/ready`);
    return post(`/projects/${projectId}/sprints/${action.sprint_id}/stories`, { story_ids: [action.target] });
  }, [["project", projectId], ["governance", projectId], ["sprints", projectId], ["kanban"]]);
  if (undo.isSuccess) return <span className="small">✔ deshecho</span>;
  return (
    <>
      <button type="button" className="link" onClick={() => undo.mutate(undefined)} disabled={undo.isPending}>
        Deshacer
      </button>
      {undo.error && <ErrorBox error={undo.error} />}
    </>
  );
}

function ActionRow({ projectId, a }: { projectId: string; a: SupervisorAction }) {
  return (
    <tr data-action={a.type}>
      <td>{ACTION_TEXT[a.type] ?? a.type}</td>
      <td>{a.target}{a.sprint_id ? ` (${a.sprint_id})` : ""}</td>
      <td>{a.reason}{a.error && <strong className="danger"> — {a.error}</strong>}</td>
      <td className="small">
        {a.engine} {a.calibrated ? "· calibrado" : "· sin calibrar"}
        {a.confidence !== null && ` · ${Math.round(a.confidence * 100)} %`}
      </td>
      <td>{a.applied ? <Undo projectId={projectId} action={a} /> : a.safe ? "propuesta (modo proponer)" : "propuesta"}</td>
    </tr>
  );
}

export function SupervisorPanel({ projectId, run }: { projectId: string; run: WatchdogRun | undefined }) {
  if (!run) return null;
  const applied = run.actions.filter((a) => a.applied);
  const proposed = run.actions.filter((a) => !a.applied);
  const s = run.summary ?? {};
  return (
    <>
      <Section title={`Informe del supervisor${run.report_engine ? ` (redactado por ${run.report_engine})` : ""}`}>
        {run.report ? <div className="report"><Markdown text={run.report} /></div> : <Empty>Supervisor apagado en este proyecto.</Empty>}
        {s.active_sprint?.risk && (
          <p>
            Riesgo del sprint {s.active_sprint.id}: <strong>{s.active_sprint.risk}</strong> (según {s.active_sprint.risk_engine})
          </p>
        )}
      </Section>
      <Section title={`Acciones aplicadas por ACM (${applied.length})`}>
        {applied.length === 0 ? (
          <Empty>ACM no ha cambiado nada por su cuenta en esta auditoría.</Empty>
        ) : (
          <table className="table">
            <thead><tr><th>Acción</th><th>Sobre</th><th>Motivo</th><th>Decidido por</th><th></th></tr></thead>
            <tbody>{applied.map((a, i) => <ActionRow key={i} projectId={projectId} a={a} />)}</tbody>
          </table>
        )}
      </Section>
      <Section title={`Propuestas (${proposed.length})`}>
        {proposed.length === 0 ? (
          <Empty>Sin propuestas.</Empty>
        ) : (
          <table className="table">
            <thead><tr><th>Acción</th><th>Sobre</th><th>Motivo</th><th>Decidido por</th><th>Estado</th></tr></thead>
            <tbody>{proposed.map((a, i) => <ActionRow key={i} projectId={projectId} a={a} />)}</tbody>
          </table>
        )}
      </Section>
    </>
  );
}

