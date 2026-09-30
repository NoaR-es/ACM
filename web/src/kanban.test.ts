// Tests del modelo del Kanban (US-06.06/07): agrupación, filtros y transiciones permitidas.
import { describe, expect, it } from "vitest";
import { applyStatus, canMove, groupByColumn, targets, visibleColumns } from "./kanban";
import { STATUS_ORDER, type StoryStatus } from "./theme";
import type { Card } from "./types";

const card = (project_id: string, id: string, status: StoryStatus, i_want = "hacer algo"): Card => ({
  project_id, id, status, i_want, as_a: "operador", so_that: "valor", kind: "user_story", feature_id: "FEAT-01.01",
  epic_id: "EPIC-01", requirement_ids: ["REQ-001"], updated_at: "t", criteria: 1,
});
const TRANSITIONS = {
  PLANNED: ["CANCELLED"], READY: ["IN_PROGRESS", "PLANNED", "CANCELLED"], IN_PROGRESS: ["IMPLEMENTED", "BLOCKED"],
  VERIFIED: ["DONE", "IN_PROGRESS"], DONE: ["DEPRECATED"],
} as Record<string, StoryStatus[]>;
const ALL = { showTerminal: true, text: "", projects: null };

describe("tablero Kanban (US-06.01, US-06.02)", () => {
  const cards = [card("alpha", "US-01.01", "READY"), card("beta", "US-01.01", "IN_PROGRESS", "abrir"),
                 card("alpha", "US-01.02", "CANCELLED")];

  it("cada historia en exactamente una columna, también con varios proyectos", () => {
    const g = groupByColumn(cards, [...STATUS_ORDER], ALL);
    const placed = Object.values(g).flat();
    expect(placed).toHaveLength(3);
    expect(g.READY.map((c) => `${c.project_id}/${c.id}`)).toEqual(["alpha/US-01.01"]);
    expect(g.IN_PROGRESS.map((c) => c.project_id)).toEqual(["beta"]);
  });

  it("filtra por proyecto y por texto", () => {
    expect(Object.values(groupByColumn(cards, [...STATUS_ORDER], { ...ALL, projects: ["beta"] })).flat()).toHaveLength(1);
    expect(Object.values(groupByColumn(cards, [...STATUS_ORDER], { ...ALL, text: "abrir" })).flat()[0].project_id).toBe("beta");
  });

  it("oculta las columnas terminales si se pide", () => {
    expect(visibleColumns([...STATUS_ORDER], { showTerminal: false })).not.toContain("CANCELLED");
  });

  it("solo permite mover a destinos válidos; READY por el gate; DONE solo desde VERIFIED", () => {
    expect(targets(TRANSITIONS, "PLANNED")).toEqual(["READY", "CANCELLED"]);
    expect(canMove(TRANSITIONS, "READY", "IN_PROGRESS")).toBe(true);
    expect(canMove(TRANSITIONS, "IN_PROGRESS", "DONE")).toBe(false);
    expect(canMove(TRANSITIONS, "VERIFIED", "DONE")).toBe(true);
    expect(canMove(TRANSITIONS, "READY", "READY")).toBe(false);
  });

  it("aplica en memoria un cambio recibido en vivo solo a la tarjeta de ese proyecto", () => {
    const next = applyStatus(cards, "beta", "US-01.01", "IMPLEMENTED");
    expect(next.find((c) => c.project_id === "beta")?.status).toBe("IMPLEMENTED");
    expect(next.find((c) => c.project_id === "alpha" && c.id === "US-01.01")?.status).toBe("READY");
  });
});
