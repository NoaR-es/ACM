// Tablero Kanban de uno o varios proyectos (US-06.01..03). Arrastrar y soltar, o «Mover a…» con teclado.
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo, useState, type DragEvent } from "react";
import { Link } from "react-router-dom";
import { post } from "./api";
import { describeError } from "./auth";
import { ProjectChip } from "./components";
import { canMove, groupByColumn, targets, visibleColumns, type BoardOptions } from "./kanban";
import { useLive } from "./live";
import { projectIndex, STATUS_LABEL, type StoryStatus } from "./theme";
import type { Card, Kanban } from "./types";

const HIGHLIGHT_MS = 4000;
type Layout = "columns" | "swimlanes";

function useNow(intervalMs: number): number {
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    const t = setInterval(() => setNow(Date.now()), intervalMs);
    return () => clearInterval(t);
  }, [intervalMs]);
  return now;
}

export function KanbanBoard({ board, allProjects }: { board: Kanban; allProjects: string[] }) {
  const queryClient = useQueryClient();
  const live = useLive();
  const now = useNow(1000);
  const multi = board.projects.length > 1;
  const [text, setText] = useState("");
  const [showTerminal, setShowTerminal] = useState(false);
  const [layout, setLayout] = useState<Layout>("columns");
  const [dragging, setDragging] = useState<Card | null>(null);
  const [message, setMessage] = useState<{ kind: "ok" | "error"; text: string } | null>(null);

  const opts: BoardOptions = { showTerminal, text, projects: null };
  const columns = visibleColumns(board.columns, opts);

  const move = useMutation({
    mutationFn: ({ card, to }: { card: Card; to: StoryStatus }) =>
      card.status === "PLANNED" && to === "READY"
        ? post(`/projects/${card.project_id}/stories/${card.id}/ready`)
        : post(`/projects/${card.project_id}/stories/${card.id}/status`, { status: to }),
    onSuccess: (_d, { card, to }) => {
      setMessage({ kind: "ok", text: `${card.project_id} · ${card.id} → ${STATUS_LABEL[to]}` });
      queryClient.invalidateQueries({ queryKey: ["kanban"] });
    },
    onError: (e, { card }) => setMessage({ kind: "error", text: `${card.project_id} · ${card.id}: ${describeError(e)}` }),
  });

  const request = (card: Card, to: StoryStatus) => {
    if (!canMove(board.transitions, card.status, to)) {
      setMessage({
        kind: "error",
        text: `${card.id}: ${STATUS_LABEL[card.status]} → ${STATUS_LABEL[to]} no está permitido`,
      });
      return;
    }
    move.mutate({ card, to });
  };

  const onDrop = (e: DragEvent, to: StoryStatus) => {
    e.preventDefault();
    if (dragging) request(dragging, to);
    setDragging(null);
  };

  const lanes = layout === "swimlanes" && multi ? board.projects : [null];

  return (
    <div className="kanban-wrap">
      <div className="toolbar" role="toolbar" aria-label="Opciones del tablero">
        <label>
          Buscar <input type="search" value={text} onChange={(e) => setText(e.target.value)} placeholder="id, texto, épica…" />
        </label>
        <label className="check">
          <input type="checkbox" checked={showTerminal} onChange={(e) => setShowTerminal(e.target.checked)} /> Mostrar
          canceladas y obsoletas
        </label>
        {multi && (
          <label>
            Vista{" "}
            <select value={layout} onChange={(e) => setLayout(e.target.value as Layout)}>
              <option value="columns">Columnas (proyectos mezclados)</option>
              <option value="swimlanes">Un carril por proyecto</option>
            </select>
          </label>
        )}
        <span className="muted">{board.cards.length} historias</span>
      </div>
      <div role="status" aria-live="polite" className={message ? `flash ${message.kind}` : "sr-only"}>
        {message?.text}
      </div>
      {lanes.map((lane) => {
        const grouped = groupByColumn(board.cards, columns, { ...opts, projects: lane ? [lane] : null });
        return (
          <div key={lane ?? "all"} className="lane">
            {lane && (
              <h3 className="lane-title">
                <ProjectChip projectId={lane} all={allProjects} />
              </h3>
            )}
            <div className="board" data-testid={`board-${lane ?? "all"}`}>
              {columns.map((col) => {
                const allowed = dragging ? canMove(board.transitions, dragging.status, col) : false;
                return (
                  <section
                    key={col}
                    className={`column${dragging ? (allowed ? " drop-ok" : " drop-no") : ""}`}
                    data-column={col}
                    aria-label={`${STATUS_LABEL[col]}: ${grouped[col].length} historias`}
                    onDragOver={(e) => e.preventDefault() /* se acepta siempre: el rechazo se explica al soltar */}
                    onDrop={(e) => onDrop(e, col)}
                  >
                    <header
                      className="column-head"
                      style={{ background: `var(--status-${col}-bg)`, color: `var(--status-${col}-fg)` }}
                    >
                      <span>{STATUS_LABEL[col]}</span>
                      <span className="count">{grouped[col].length}</span>
                    </header>
                    <ol className="cards">
                      {grouped[col].map((card) => (
                        <KanbanCard
                          key={`${card.project_id}/${card.id}`}
                          card={card}
                          multi={multi}
                          allProjects={allProjects}
                          transitions={board.transitions}
                          highlighted={now - (live.changedAt(card.project_id, card.id) ?? 0) < HIGHLIGHT_MS}
                          busy={move.isPending}
                          onDragStart={() => setDragging(card)}
                          onDragEnd={() => setDragging(null)}
                          onMove={(to) => request(card, to)}
                        />
                      ))}
                    </ol>
                  </section>
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
}

function KanbanCard(props: {
  card: Card;
  multi: boolean;
  allProjects: string[];
  transitions: Kanban["transitions"];
  highlighted: boolean;
  busy: boolean;
  onDragStart: () => void;
  onDragEnd: () => void;
  onMove: (to: StoryStatus) => void;
}) {
  const { card, multi, allProjects, transitions, highlighted } = props;
  const i = projectIndex(card.project_id, allProjects);
  const options = useMemo(() => targets(transitions, card.status), [transitions, card.status]);
  return (
    <li
      className={`card${highlighted ? " changed" : ""}`}
      style={{ borderLeftColor: `var(--project-${i}-stripe)` }}
      draggable
      onDragStart={(e) => {
        e.dataTransfer.setData("text/plain", `${card.project_id}/${card.id}`);
        props.onDragStart();
      }}
      onDragEnd={props.onDragEnd}
      data-card={`${card.project_id}/${card.id}`}
      data-status={card.status}
    >
      <div className="card-top">
        {multi && <ProjectChip projectId={card.project_id} all={allProjects} link={false} />}
        <Link to={`/p/${card.project_id}/s/${card.id}`} className="card-id">
          {card.id}
        </Link>
        {card.kind === "technical" && <span className="tag">técnica</span>}
        {highlighted && <span className="tag live-tag">actualizada</span>}
      </div>
      <p className="card-title">{card.i_want}</p>
      <p className="card-meta">
        Como {card.as_a} · {card.criteria} CA · {card.feature_id}
      </p>
      {options.length > 0 && (
        <label className="move">
          <span className="sr-only">Mover {card.id} a</span>
          <select
            value=""
            disabled={props.busy}
            onChange={(e) => e.target.value && props.onMove(e.target.value as StoryStatus)}
            aria-label={`Mover ${card.project_id} ${card.id} a`}
          >
            <option value="">Mover a…</option>
            {options.map((s) => (
              <option key={s} value={s}>
                {STATUS_LABEL[s]}
              </option>
            ))}
          </select>
        </label>
      )}
    </li>
  );
}
