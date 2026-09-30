// Lógica pura del tablero Kanban (US-06.01, US-06.02).
import type { StoryStatus } from "./theme";
import type { Card } from "./types";

export const TERMINAL: StoryStatus[] = ["CANCELLED", "DEPRECATED"];

export type BoardOptions = { showTerminal: boolean; text: string; projects: string[] | null };

export function visibleColumns(columns: StoryStatus[], opts: Pick<BoardOptions, "showTerminal">): StoryStatus[] {
  return opts.showTerminal ? columns : columns.filter((c) => !TERMINAL.includes(c));
}

export function matches(card: Card, opts: BoardOptions): boolean {
  if (opts.projects && !opts.projects.includes(card.project_id)) return false;
  const q = opts.text.trim().toLowerCase();
  if (!q) return true;
  return [card.id, card.i_want, card.as_a, card.so_that, card.feature_id, card.epic_id, card.project_id]
    .join(" ")
    .toLowerCase()
    .includes(q);
}

/** Cada tarjeta en exactamente una columna: la de su estado (US-06.01 CA-01). */
export function groupByColumn(cards: Card[], columns: StoryStatus[], opts: BoardOptions): Record<string, Card[]> {
  const out: Record<string, Card[]> = Object.fromEntries(columns.map((c) => [c, [] as Card[]]));
  for (const card of cards) {
    if (!matches(card, opts) || !(card.status in out)) continue;
    out[card.status].push(card);
  }
  for (const c of columns) out[c].sort((a, b) => a.project_id.localeCompare(b.project_id) || a.id.localeCompare(b.id));
  return out;
}

/** Destinos válidos desde un estado. PLANNED → READY pasa por el gate (endpoint /ready), no por set_status. */
export function targets(transitions: Record<string, StoryStatus[]>, from: StoryStatus): StoryStatus[] {
  const base = transitions[from] ?? [];
  return from === "PLANNED" ? ["READY", ...base] : base;
}

export function canMove(transitions: Record<string, StoryStatus[]>, from: StoryStatus, to: StoryStatus): boolean {
  return from !== to && targets(transitions, from).includes(to);
}

/** Aplica al tablero en memoria un cambio de estado recibido en vivo (sin esperar a recargar). */
export function applyStatus(cards: Card[], projectId: string, storyId: string, status: StoryStatus): Card[] {
  return cards.map((c) => (c.project_id === projectId && c.id === storyId ? { ...c, status } : c));
}
