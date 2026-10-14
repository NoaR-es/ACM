// Kanban de uno o varios proyectos a la vez (US-06.01), seleccionables; la selección vive en la URL.
import { useQuery } from "@tanstack/react-query";
import { useSearchParams } from "react-router-dom";
import { api } from "../api";
import { ErrorBox, Loading, ProjectChip } from "../components";
import { KanbanBoard } from "../KanbanBoard";
import type { Kanban, PortfolioProject } from "../types";

export function KanbanPage() {
  const [params, setParams] = useSearchParams();
  const projects = useQuery({ queryKey: ["projects"], queryFn: () => api<{ projects: PortfolioProject[] }>("/projects") });
  const all = projects.data?.projects.map((p) => p.project_id) ?? [];
  const selected = (params.get("projects") ?? "").split(",").filter(Boolean);
  const effective = selected.length ? selected : all;
  const board = useQuery({
    queryKey: ["kanban", effective.join(",")],
    queryFn: () => api<Kanban>(`/kanban?projects=${encodeURIComponent(effective.join(","))}`),
    enabled: projects.isSuccess && effective.length > 0,
  });
  const toggle = (id: string) => {
    const next = effective.includes(id) ? effective.filter((p) => p !== id) : [...effective, id];
    setParams(next.length && next.length !== all.length ? { projects: next.join(",") } : {});
  };
  if (projects.isPending) return <Loading what="proyectos" />;
  if (projects.error) return <ErrorBox error={projects.error} />;
  return (
    <div className="page wide">
      <h1>Kanban {effective.length > 1 ? `· ${effective.length} proyectos` : effective[0] ? `· ${effective[0]}` : ""}</h1>
      <fieldset className="project-picker">
        <legend>Proyectos en el tablero</legend>
        {all.map((id) => (
          <label key={id} className="check">
            <input type="checkbox" checked={effective.includes(id)} onChange={() => toggle(id)} />{" "}
            <ProjectChip projectId={id} all={all} link={false} />
          </label>
        ))}
        {all.length > 1 && (
          <button type="button" onClick={() => setParams({})}>
            Todos
          </button>
        )}
      </fieldset>
      {all.length === 0 && <p className="empty">No tienes proyectos.</p>}
      {board.isPending && effective.length > 0 && <Loading what="tablero" />}
      {board.error && <ErrorBox error={board.error} />}
      {board.data && <KanbanBoard board={board.data} allProjects={all} />}
    </div>
  );
}
