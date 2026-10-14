// Solicitudes de acceso de agentes (US-14.15): una persona aprueba (lectura o escritura) o rechaza que un agente se
// una a un proyecto. Mientras no se aprueba, el agente no ve nada del proyecto.
import { useQuery } from "@tanstack/react-query";
import { api, post } from "../api";
import { ErrorBox, fmtDate, ProjectChip, Section } from "../components";
import { useAction } from "../forms";
import type { JoinRequest } from "../types";

export function JoinRequestsPanel({ projectIds }: { projectIds: string[] }) {
  const requests = useQuery({
    queryKey: ["join-requests"],
    queryFn: () => api<{ requests: JoinRequest[]; can_decide: boolean }>("/join-requests?status=PENDING"),
  });
  const keys = [["join-requests"], ["projects"], ["me"]];
  const approve = useAction(
    ({ id, role }: { id: number; role: "member" | "viewer" }) => post(`/join-requests/${id}/approve`, { role }),
    keys,
  );
  const reject = useAction((id: number) => post(`/join-requests/${id}/reject`), keys);
  if (requests.isPending || requests.error || requests.data.requests.length === 0) {
    return requests.error ? <ErrorBox error={requests.error} /> : null; // sin peticiones no se ocupa sitio
  }
  const { requests: list, can_decide: canDecide } = requests.data;
  return (
    <Section title="Solicitudes de acceso">
      <p className="small muted">
        Un agente pide unirse a un proyecto. No ve nada de él hasta que lo apruebes.
        {!canDecide && " Solo una persona puede aprobar o rechazar."}
      </p>
      <ul className="join-requests">
        {list.map((r) => (
          <li key={r.request_id} className="project-card" data-request={r.request_id}>
            <div className="row">
              <strong>{r.principal_id}</strong>
              <span>quiere unirse a</span>
              <ProjectChip projectId={r.project_id} all={projectIds} />
              <span className="tag">{r.access === "read" ? "pide lectura" : "pide escritura"}</span>
            </div>
            {r.message && <p className="muted">«{r.message}»</p>}
            <p className="small muted">Pedido {fmtDate(r.created_at)}</p>
            {canDecide && (
              <div className="row">
                <button
                  type="button"
                  className="primary"
                  disabled={approve.isPending || reject.isPending}
                  onClick={() => approve.mutate({ id: r.request_id, role: "member" })}
                >
                  Aprobar con escritura
                </button>
                <button
                  type="button"
                  disabled={approve.isPending || reject.isPending}
                  onClick={() => approve.mutate({ id: r.request_id, role: "viewer" })}
                >
                  Aprobar solo lectura
                </button>
                <button
                  type="button"
                  disabled={approve.isPending || reject.isPending}
                  onClick={() => reject.mutate(r.request_id)}
                >
                  Rechazar
                </button>
              </div>
            )}
          </li>
        ))}
      </ul>
      {[approve, reject].map((m, i) => m.error && <ErrorBox key={i} error={m.error} />)}
    </Section>
  );
}
