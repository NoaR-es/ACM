// Lógica pura del canal en vivo (US-21.03): orden por seq, sin duplicados, reanudación y resync.
import type { AcmEvent } from "./types";

export type LiveState = { lastSeq: number | null; needsResync: boolean };
export type ServerMessage =
  | { type: "ready"; principal: string; seq: number; latest_seq: number }
  | { type: "event"; event: AcmEvent }
  | { type: "resync"; reason: string }
  | { type: "error"; error: string };

export type Outcome = { state: LiveState; apply: AcmEvent | null; resync: boolean };

/** Decide qué hacer con un mensaje del servidor. Un evento con seq ≤ al último aplicado se descarta (duplicado). */
export function receive(state: LiveState, msg: ServerMessage): Outcome {
  switch (msg.type) {
    case "ready":
      return { state: { lastSeq: Math.max(state.lastSeq ?? 0, msg.seq), needsResync: false }, apply: null, resync: false };
    case "resync":
      return { state: { ...state, needsResync: false }, apply: null, resync: true };
    case "event":
      if (state.lastSeq !== null && msg.event.seq <= state.lastSeq) return { state, apply: null, resync: false };
      return { state: { ...state, lastSeq: msg.event.seq }, apply: msg.event, resync: false };
    default:
      return { state, apply: null, resync: false };
  }
}

/** Mensaje de autenticación: al reconectar pide los eventos posteriores al último aplicado. */
export function authMessage(token: string, state: LiveState): string {
  return JSON.stringify({ type: "auth", token, after: state.lastSeq });
}

/** Espera antes de reintentar la conexión: exponencial con tope. */
export function backoff(attempt: number): number {
  return Math.min(500 * 2 ** attempt, 10_000);
}

/** Claves de datos que un evento deja obsoletas (la interfaz las recarga). */
export function affectedKeys(e: AcmEvent): string[][] {
  const keys: string[][] = [["projects"], ["kanban"]];
  if (e.type === "activity") return [["activity"]];
  if (e.project_id) {
    keys.push(["project", e.project_id]);
    if (e.entity_type === "story") keys.push(["story", e.project_id, e.entity_id]);
    if (e.type === "watchdog.run") keys.push(["governance", e.project_id]);
    if (e.type === "member.changed") keys.push(["members", e.project_id], ["me"]);
  }
  if (e.type === "principal.changed") keys.push(["principals"], ["me"]);
  return keys;
}
