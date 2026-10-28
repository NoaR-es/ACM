"""Colaboración de agentes en un proyecto: ACM reparte el trabajo (FEAT-14.07: US-14.16, US-14.17; ADR-025).

El proceso ágil lo lleva ACM, no un agente concreto. Cada agente pide `next_work` y recibe lo siguiente que toca
según el estado del proyecto, ya asignado a él. Con un agente, ese agente lo hace todo; con varios, se reparten sin
hablar entre ellos porque ACM no da a dos el mismo trabajo.

Orden (primero terminar, luego empezar):
1. Lo que el propio agente ya tiene asignado y sigue pendiente (continuar).
2. Sprint activo: historias en curso o fallidas sin dueño (implementar), implementadas o en pruebas (verificar),
   READY (implementar). Si todas están terminadas: cerrar el sprint.
3. Sin sprint activo: iniciar el planificado que tenga historias, o planificar uno con las historias READY.
4. Historias PLANNED: refinarlas hasta que pasen el gate READY.
5. Sin historias: construir el backlog.

Asignaciones (`work_claims`): una por elemento (historia o tarea del proyecto). Caducan a los `work.claim_ttl_minutes`
sin que el agente las toque; cambiar la historia o volver a pedir trabajo las renueva
(`BacklogService._guard_claim`).
Una persona siempre puede mover el trabajo y liberar cualquier asignación.
"""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime, timedelta
from typing import Any

from acm.domain.backlog import BacklogService, _holder
from acm.domain.config_schema import PARAMETERS
from acm.domain.errors import Forbidden, NotFound
from acm.sessions import session_id

SPRINT_PLANNING = "sprint-planning"
SPRINT_CLOSING = "sprint-closing"
BACKLOG = "backlog"
TERMINAL = ("VERIFIED", "DONE", "CANCELLED", "DEPRECATED")

STEPS = {
    "implement": [
        "acm_context_compact(project_id, story_id) para el contexto mínimo",
        "acm_story_set_status(..., 'IN_PROGRESS') si está READY",
        "implementa en el repositorio y, al terminar, acm_story_set_status(..., 'IMPLEMENTED')",
        "acm_next_work para lo siguiente",
    ],
    "verify": [
        "acm_story_get para leer sus criterios de aceptación",
        "acm_story_set_status(..., 'TESTING') y comprueba cada criterio con pruebas reales",
        "acm_story_set_status(..., 'VERIFIED') si todos pasan, o 'FAILED' explicando cuál falla",
        "acm_next_work",
    ],
    "refine": [
        "acm_story_get y completa lo que falte: acm_story_add_criteria (criterios verificables), requisitos",
        "acm_story_mark_ready cuando esté completa (el gate explica qué falta)",
        "acm_next_work",
    ],
    "plan_sprint": [
        "acm_sprint_create con objetivo, fechas y capacidad",
        "acm_sprint_add_stories con historias READY",
        "acm_sprint_start",
        "acm_next_work",
    ],
    "start_sprint": ["acm_sprint_get para revisar el plan", "acm_sprint_start", "acm_next_work"],
    "close_sprint": ["acm_sprint_close (lo no terminado vuelve al backlog o pasa a otro sprint)", "acm_next_work"],
    "build_backlog": [
        "pregunta a la persona qué hay que construir si no lo sabes",
        "acm_requirement_create, acm_epic_create, acm_feature_create, acm_story_create con criterios",
        "acm_next_work",
    ],
}


def _now() -> datetime:
    return datetime.now(UTC)


class WorkService:
    def __init__(self, backlog: BacklogService):
        self.backlog = backlog
        self.projects = backlog.projects

    def _ttl(self, project_id: str) -> int:
        db = self.projects.project_db(project_id)
        minutes = self.projects._stored_config(db).get(
            "work.claim_ttl_minutes", PARAMETERS["work.claim_ttl_minutes"].default
        )
        return int(minutes) * 60

    def _writable(self, principal: str, project_id: str):
        role = self.projects._project_role(principal, project_id)  # NOT_FOUND si no es accesible
        if role == "viewer":
            raise Forbidden("tienes acceso de solo lectura a este proyecto: no se te puede asignar trabajo")
        return self.backlog._db(principal, project_id, write=True)

    # --------------------------------------------------------------- candidatos
    @staticmethod
    def _candidates(conn: sqlite3.Connection) -> list[dict[str, Any]]:
        """Trabajo pendiente en orden de prioridad, sin tener en cuenta las asignaciones."""
        stories = {r["id"]: r for r in conn.execute("SELECT id, status, i_want FROM stories ORDER BY id").fetchall()}
        active = conn.execute("SELECT id, name FROM sprints WHERE status = 'ACTIVE'").fetchone()
        out: list[dict[str, Any]] = []

        def story(sid: str, action: str, reason: str) -> None:
            out.append({"item": sid, "action": action, "story_id": sid, "reason": reason})

        if active is not None:
            sprint_stories = [
                r[0]
                for r in conn.execute(
                    "SELECT story_id FROM sprint_stories WHERE sprint_id = ? AND ended_at IS NULL ORDER BY story_id",
                    (active["id"],),
                )
            ]
            for status, action, why in (
                (("IN_PROGRESS", "FAILED"), "implement", "está en curso o falló en {sprint} y nadie la tiene"),
                (("IMPLEMENTED", "TESTING"), "verify", "está implementada en {sprint}: verifica sus criterios"),
                (("READY",), "implement", "está lista en {sprint}"),
            ):
                for sid in sprint_stories:
                    if stories[sid]["status"] in status:
                        story(sid, action, f"{sid} {why.format(sprint=active['id'])}")
            pending = [sid for sid in sprint_stories if stories[sid]["status"] not in TERMINAL]
            if sprint_stories and not pending:
                out.append(
                    {
                        "item": SPRINT_CLOSING,
                        "action": "close_sprint",
                        "sprint_id": active["id"],
                        "reason": f"todas las historias de {active['id']} están terminadas: ciérralo",
                    }
                )
        else:
            planned = conn.execute(
                "SELECT s.id FROM sprints s WHERE s.status = 'PLANNED' AND EXISTS (SELECT 1 FROM sprint_stories ss "
                "WHERE ss.sprint_id = s.id AND ss.ended_at IS NULL) ORDER BY s.start_date, s.id LIMIT 1"
            ).fetchone()
            ready_free = conn.execute(
                "SELECT COUNT(*) FROM stories st WHERE st.status = 'READY' AND NOT EXISTS ("
                "SELECT 1 FROM sprint_stories ss JOIN sprints s ON s.id = ss.sprint_id "
                "WHERE ss.story_id = st.id AND ss.ended_at IS NULL AND s.status IN ('PLANNED', 'ACTIVE'))"
            ).fetchone()[0]
            if planned is not None:
                out.append(
                    {
                        "item": SPRINT_PLANNING,
                        "action": "start_sprint",
                        "sprint_id": planned["id"],
                        "reason": f"no hay sprint activo y {planned['id']} está planificado: inícialo",
                    }
                )
            elif ready_free:
                out.append(
                    {
                        "item": SPRINT_PLANNING,
                        "action": "plan_sprint",
                        "reason": f"no hay sprint activo y hay {ready_free} historias READY: planifica un sprint",
                    }
                )
        for sid, row in stories.items():
            if row["status"] == "PLANNED":
                story(sid, "refine", f"{sid} está en PLANNED: complétala hasta que pase el gate READY")
        if not stories:
            out.append({"item": BACKLOG, "action": "build_backlog", "reason": "el proyecto no tiene historias todavía"})
        return out

    # --------------------------------------------------------------- operaciones
    def next_work(self, principal: str, project_id: str, claim: bool = True) -> dict[str, Any]:
        """US-14.16 CA-01/CA-02: lo siguiente que toca, asignado al agente que lo pide."""
        if not isinstance(claim, bool):
            claim = bool(claim)
        db = self._writable(principal, project_id)
        if claim:
            self.projects.ensure_writable(project_id)
        ttl = self._ttl(project_id)
        now = _now()
        session = session_id()

        def mine(row: Any) -> bool:
            return bool(row["principal"] == principal and row["session"] == session)

        with db.write() as conn:
            conn.execute("DELETE FROM work_claims WHERE expires_at <= ?", (now.isoformat(),))
            candidates = self._candidates(conn)
            by_item = {c["item"]: c for c in candidates}
            claims = {r["item"]: r for r in conn.execute("SELECT * FROM work_claims").fetchall()}
            # Asignaciones propias que ya no corresponden a nada pendiente (o cambiaron de acción): se liberan.
            for item, row in list(claims.items()):
                if mine(row) and (item not in by_item or by_item[item]["action"] != row["action"]):
                    conn.execute("DELETE FROM work_claims WHERE item = ?", (item,))
                    del claims[item]
            chosen, continuing = None, False
            for c in candidates:
                owner = claims.get(c["item"])
                if owner is not None and mine(owner):
                    chosen, continuing = c, True
                    break
            if chosen is None:
                chosen = next((c for c in candidates if c["item"] not in claims), None)
            granted = None
            if chosen is not None and claim:
                expires = (now + timedelta(seconds=ttl)).isoformat()
                conn.execute(
                    "INSERT INTO work_claims(item, action, principal, session, claimed_at, expires_at, ttl_s) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?) ON CONFLICT(item) DO UPDATE SET expires_at = excluded.expires_at",
                    (chosen["item"], chosen["action"], principal, session, now.isoformat(), expires, ttl),
                )
                granted = {"item": chosen["item"], "expires_at": expires, "ttl_minutes": ttl // 60}
            others = [
                {"item": r["item"], "action": r["action"], "agent": _holder(r), "expires_at": r["expires_at"]}
                for r in conn.execute("SELECT * FROM work_claims ORDER BY item")
                if not mine(r)
            ]
        result: dict[str, Any] = {"project_id": project_id, "others_working": others}
        if chosen is None:
            busy = "otros agentes tienen asignado el trabajo pendiente" if others else "no queda trabajo pendiente"
            return result | {
                "action": "idle",
                "reason": busy,
                "steps": ["acm_watchdog_run para revisar la salud del proyecto", "vuelve a pedir trabajo más tarde"],
            }
        result |= {
            "action": chosen["action"],
            "item": chosen["item"],
            "reason": chosen["reason"],
            "continuing": continuing,
            "steps": STEPS[chosen["action"]],
            "claim": granted,
        }
        if chosen.get("story_id"):
            result["story"] = self.backlog.get_story(principal, project_id, chosen["story_id"])
        if chosen.get("sprint_id"):
            result["sprint_id"] = chosen["sprint_id"]
        if granted is not None:
            self.projects.events.append(
                "work.claimed",
                principal=principal,
                project_id=project_id,
                entity_type="work",
                entity_id=chosen["item"],
                data={"action": chosen["action"], "expires_at": granted["expires_at"]},
            )
        return result

    def release(self, principal: str, project_id: str, item: str) -> dict[str, Any]:
        """US-14.17 CA-02: el agente libera su trabajo; una persona puede liberar cualquiera."""
        db = self.backlog._db(principal, project_id, write=True)
        with db.write() as conn:
            row = conn.execute("SELECT principal, session FROM work_claims WHERE item = ?", (item,)).fetchone()
            if row is None:
                raise NotFound(f"{item!r} no está asignado a nadie", field="item")
            mine = row["principal"] == principal and row["session"] == session_id()
            if not mine and self.projects.principal_kind(principal) != "user":
                raise Forbidden(f"{item} está asignado a {_holder(row)}: solo él o una persona pueden liberarlo")
            conn.execute("DELETE FROM work_claims WHERE item = ?", (item,))
        self.projects.events.append(
            "work.released",
            principal=principal,
            project_id=project_id,
            entity_type="work",
            entity_id=item,
            data={"was": _holder(row)},
        )
        return {"project_id": project_id, "item": item, "released": True, "was": _holder(row)}

    def claims(self, principal: str, project_id: str) -> dict[str, Any]:
        """US-14.17 CA-03: quién trabaja en qué ahora mismo (las caducadas no aparecen)."""
        with self.backlog._db(principal, project_id).read() as conn:
            rows = conn.execute(
                "SELECT * FROM work_claims WHERE expires_at > ? ORDER BY item", (_now().isoformat(),)
            ).fetchall()
        return {
            "project_id": project_id,
            "claims": [
                {"item": r["item"], "action": r["action"], "agent": _holder(r), "expires_at": r["expires_at"]}
                for r in rows
            ],
        }
