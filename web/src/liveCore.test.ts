// Tests del núcleo en vivo (US-31.08): orden por seq, duplicados, reanudación, resync y claves a recargar.
import { describe, expect, it } from "vitest";
import { affectedKeys, authMessage, backoff, receive, type LiveState } from "./liveCore";
import type { AcmEvent } from "./types";

const ev = (seq: number, extra: Partial<AcmEvent> = {}): AcmEvent => ({
  seq, ts: "t", type: "story.status_changed", project_id: "alpha", principal: "bot", entity_type: "story",
  entity_id: "US-01.01", data: { status: "IN_PROGRESS" }, ...extra,
});

describe("canal en vivo (US-06.03, US-21.03)", () => {
  it("aplica eventos en orden y descarta duplicados", () => {
    let s: LiveState = { lastSeq: null, needsResync: false };
    s = receive(s, { type: "ready", principal: "a", seq: 10, latest_seq: 10 }).state;
    const first = receive(s, { type: "event", event: ev(11) });
    expect(first.apply?.seq).toBe(11);
    const dup = receive(first.state, { type: "event", event: ev(11) });
    expect(dup.apply).toBeNull();
    const old = receive(first.state, { type: "event", event: ev(9) });
    expect(old.apply).toBeNull();
    expect(receive(first.state, { type: "event", event: ev(12) }).state.lastSeq).toBe(12);
  });

  it("al reconectar pide lo posterior al último evento aplicado", () => {
    expect(JSON.parse(authMessage("acm_x", { lastSeq: 42, needsResync: false }))).toEqual({
      type: "auth", token: "acm_x", after: 42 });
    expect(JSON.parse(authMessage("acm_x", { lastSeq: null, needsResync: false })).after).toBeNull();
  });

  it("un ready no retrocede el último seq aplicado", () => {
    const s = receive({ lastSeq: 50, needsResync: false }, { type: "ready", principal: "a", seq: 40, latest_seq: 60 });
    expect(s.state.lastSeq).toBe(50);
  });

  it("resync pide recargar todo", () => {
    expect(receive({ lastSeq: 5, needsResync: false }, { type: "resync", reason: "x" }).resync).toBe(true);
  });

  it("reintentos con espera exponencial acotada", () => {
    expect([0, 1, 2, 10].map(backoff)).toEqual([500, 1000, 2000, 10000]);
  });

  it("un cambio de historia invalida Kanban, cartera, proyecto e historia", () => {
    const keys = affectedKeys(ev(1)).map((k) => k.join("/"));
    expect(keys).toEqual(expect.arrayContaining(["kanban", "projects", "project/alpha", "story/alpha/US-01.01"]));
    expect(affectedKeys(ev(2, { type: "activity", entity_type: "operation" }))).toEqual([["activity"]]);
    expect(affectedKeys(ev(3, { type: "watchdog.run", entity_type: "project" })).map((k) => k.join("/"))).toContain(
      "governance/alpha");
  });
});
