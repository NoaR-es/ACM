"""Sprints del proyecto (EPIC-05: US-05.02..05.09).

Un sprint (SPRINT-NN) tiene nombre, objetivo, fechas (AAAA-MM-DD) y capacidad opcional, medida en historias porque
ACM no guarda estimaciones. Estados: PLANNED → ACTIVE → CLOSED, o CANCELLED desde PLANNED o ACTIVE.

Reglas:
- Una historia solo puede estar en un sprint abierto (PLANNED o ACTIVE) a la vez, y no puede ser terminal (DONE,
  CANCELLED, DEPRECATED). Añadir una historia que no está READY se permite, pero se avisa.
- Solo hay un sprint ACTIVE por proyecto. Iniciar un sprint con más historias que su capacidad se rechaza salvo que
  se fuerce (US-05.09: la sobrecarga se detecta antes de iniciar).
- Al cerrar, las historias DONE quedan como hechas; el resto se traslada a otro sprint PLANNED o vuelve al backlog
  (US-05.03 CA-02). El cierre guarda un resumen con las métricas (US-05.03 CA-03, US-05.06) y las filas de pertenencia
  no se borran: el historial del sprint se conserva (US-05.03 CA-04).
"""

from __future__ import annotations

import json
import re
import sqlite3
from datetime import UTC, date, datetime
from typing import Any

from acm.domain.backlog import US_RE, BacklogService
from acm.domain.errors import FailedPrecondition, InvalidArgument, NotFound

SPRINT_RE = re.compile(r"^SPRINT-(\d{2,})$")
SPRINT_STATUSES = ("PLANNED", "ACTIVE", "CLOSED", "CANCELLED")
OPEN = ("PLANNED", "ACTIVE")
TERMINAL_STORY = ("DONE", "CANCELLED", "DEPRECATED")
CAPACITY_MAX = 1000


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _date(value: Any, field: str) -> str:
    if not isinstance(value, str):
        raise InvalidArgument("debe ser una fecha AAAA-MM-DD", field=field)
    try:
        return date.fromisoformat(value.strip()).isoformat()
    except ValueError as exc:
        raise InvalidArgument("debe ser una fecha válida AAAA-MM-DD", field=field) from exc


def _text(value: Any, field: str, max_len: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InvalidArgument("es obligatorio y no puede estar vacío", field=field)
    if len(value.strip()) > max_len:
        raise InvalidArgument(f"máximo {max_len} caracteres", field=field)
    return value.strip()


class SprintService:
    def __init__(self, backlog: BacklogService):
        self.backlog = backlog
        self.projects = backlog.projects

    # ------------------------------------------------------------------ lectura
    def _sprint(self, conn: sqlite3.Connection, sprint_id: str) -> dict[str, Any]:
        row = conn.execute("SELECT * FROM sprints WHERE id = ?", (sprint_id,)).fetchone()
        if row is None:
            raise NotFound(f"{sprint_id!r} no existe en este proyecto", field="sprint_id")
        sprint = dict(row)
        sprint["summary"] = json.loads(sprint.pop("summary_json"))
        members = conn.execute(
            "SELECT ss.story_id, ss.added_at, ss.added_by, ss.ended_at, ss.outcome, st.status "
            "FROM sprint_stories ss JOIN stories st ON st.id = ss.story_id WHERE ss.sprint_id = ? "
            "ORDER BY ss.story_id",
            (sprint_id,),
        ).fetchall()
        current = [dict(m) for m in members if m["ended_at"] is None]
        sprint["story_ids"] = [m["story_id"] for m in current]
        sprint["history"] = [dict(m) for m in members if m["ended_at"] is not None]
        sprint["stories_by_status"] = {}
        for m in current:
            sprint["stories_by_status"][m["status"]] = sprint["stories_by_status"].get(m["status"], 0) + 1
        sprint["load"] = len(current)
        sprint["overloaded"] = sprint["capacity"] is not None and sprint["load"] > sprint["capacity"]
        return sprint

    def get(self, principal: str, project_id: str, sprint_id: str) -> dict[str, Any]:
        with self.backlog._db(principal, project_id).read() as conn:
            return {"project_id": project_id, **self._sprint(conn, sprint_id)}

    def list(self, principal: str, project_id: str) -> dict[str, Any]:
        with self.backlog._db(principal, project_id).read() as conn:
            ids = [r[0] for r in conn.execute("SELECT id FROM sprints ORDER BY start_date, id")]
            return {"project_id": project_id, "sprints": [self._sprint(conn, i) for i in ids]}

    # ------------------------------------------------------------------ US-05.02 / US-05.04 / US-05.07
    def create(
        self,
        principal: str,
        project_id: str,
        name: Any,
        goal: Any,
        start_date: Any,
        end_date: Any,
        capacity: Any = None,
    ) -> dict[str, Any]:
        name = _text(name, "name", 120)
        goal = _text(goal, "goal", 2000)
        start, end = _date(start_date, "start_date"), _date(end_date, "end_date")
        if end < start:
            raise InvalidArgument("no puede ser anterior a start_date", field="end_date")
        if capacity is not None and (
            not isinstance(capacity, int) or isinstance(capacity, bool) or not 1 <= capacity <= CAPACITY_MAX
        ):
            raise InvalidArgument(f"debe ser un entero entre 1 y {CAPACITY_MAX} (historias) o nulo", field="capacity")
        db = self.backlog._db(principal, project_id, write=True)
        with db.write() as conn:
            nums = [int(SPRINT_RE.match(r[0]).group(1)) for r in conn.execute("SELECT id FROM sprints")]  # type: ignore[union-attr]
            sprint_id = f"SPRINT-{max(nums, default=0) + 1:02d}"
            conn.execute(
                "INSERT INTO sprints(id, name, goal, start_date, end_date, capacity, created_at, created_by) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (sprint_id, name, goal, start, end, capacity, _now(), principal),
            )
        return self._emit(principal, project_id, "sprint.created", sprint_id)

    # ------------------------------------------------------------------ US-05.05
    def add_stories(self, principal: str, project_id: str, sprint_id: str, story_ids: Any) -> dict[str, Any]:
        if not isinstance(story_ids, list) or not story_ids:
            raise InvalidArgument("indica al menos una historia", field="story_ids")
        if any(not isinstance(s, str) or not US_RE.match(s) for s in story_ids) or len(set(story_ids)) != len(
            story_ids
        ):
            raise InvalidArgument("debe ser una lista de US-NN.MM sin repetidos", field="story_ids")
        db = self.backlog._db(principal, project_id, write=True)
        warnings: list[str] = []
        with db.write() as conn:
            sprint = self._sprint(conn, sprint_id)
            if sprint["status"] not in OPEN:
                raise FailedPrecondition(f"{sprint_id} está {sprint['status']}: no admite historias")
            for sid in story_ids:
                story = conn.execute("SELECT status FROM stories WHERE id = ?", (sid,)).fetchone()
                if story is None:
                    raise NotFound(f"{sid!r} no existe en este proyecto", field="story_ids")
                if story["status"] in TERMINAL_STORY:
                    raise FailedPrecondition(f"{sid} está {story['status']}: no puede planificarse en un sprint")
                other = conn.execute(
                    "SELECT ss.sprint_id FROM sprint_stories ss JOIN sprints s ON s.id = ss.sprint_id "
                    "WHERE ss.story_id = ? AND ss.ended_at IS NULL AND s.status IN ('PLANNED', 'ACTIVE')",
                    (sid,),
                ).fetchone()
                if other is not None:
                    raise FailedPrecondition(
                        f"{sid} ya está en {other[0]}: una historia solo cabe en un sprint abierto"
                    )
                if story["status"] == "PLANNED":
                    warnings.append(f"{sid} no está READY: refínala antes de empezar")
                conn.execute(
                    "INSERT INTO sprint_stories(sprint_id, story_id, added_at, added_by) VALUES (?, ?, ?, ?) "
                    "ON CONFLICT(sprint_id, story_id) DO UPDATE SET added_at = excluded.added_at, "
                    "added_by = excluded.added_by, ended_at = NULL, outcome = NULL",
                    (sprint_id, sid, _now(), principal),
                )
        result = self._emit(principal, project_id, "sprint.updated", sprint_id)
        if result["overloaded"]:
            warnings.append(f"{sprint_id} supera su capacidad: {result['load']} historias de {result['capacity']}")
        return result | {"warnings": warnings}

    def remove_story(self, principal: str, project_id: str, sprint_id: str, story_id: str) -> dict[str, Any]:
        db = self.backlog._db(principal, project_id, write=True)
        with db.write() as conn:
            sprint = self._sprint(conn, sprint_id)
            if sprint["status"] not in OPEN:
                raise FailedPrecondition(f"{sprint_id} está {sprint['status']}: su historial no se modifica")
            if story_id not in sprint["story_ids"]:
                raise NotFound(f"{story_id} no está en {sprint_id}", field="story_id")
            conn.execute(
                "UPDATE sprint_stories SET ended_at = ?, outcome = 'removed' WHERE sprint_id = ? AND story_id = ?",
                (_now(), sprint_id, story_id),
            )
        return self._emit(principal, project_id, "sprint.updated", sprint_id)

    # ------------------------------------------------------------------ US-05.02 CA-04 / US-05.09
    def start(self, principal: str, project_id: str, sprint_id: str, force: Any = False) -> dict[str, Any]:
        if not isinstance(force, bool):
            raise InvalidArgument("debe ser true o false", field="force")
        db = self.backlog._db(principal, project_id, write=True)
        with db.write() as conn:
            sprint = self._sprint(conn, sprint_id)
            if sprint["status"] != "PLANNED":
                raise FailedPrecondition(f"{sprint_id} está {sprint['status']}; solo un sprint PLANNED puede iniciarse")
            active = conn.execute("SELECT id FROM sprints WHERE status = 'ACTIVE'").fetchone()
            if active is not None:
                raise FailedPrecondition(f"ya hay un sprint activo ({active[0]}): ciérralo antes de iniciar otro")
            if not sprint["story_ids"]:
                raise FailedPrecondition(f"{sprint_id} no tiene historias")
            if sprint["overloaded"] and not force:
                raise FailedPrecondition(
                    f"{sprint_id} está sobrecargado: {sprint['load']} historias para una capacidad de "
                    f"{sprint['capacity']}. Retira historias o inícialo forzando (force=true)"
                )
            conn.execute(
                "UPDATE sprints SET status = 'ACTIVE', started_at = ?, started_by = ? WHERE id = ?",
                (_now(), principal, sprint_id),
            )
        return self._emit(principal, project_id, "sprint.started", sprint_id)

    # ------------------------------------------------------------------ US-05.03 / US-05.06
    def close(self, principal: str, project_id: str, sprint_id: str, carry_over_to: Any = None) -> dict[str, Any]:
        db = self.backlog._db(principal, project_id, write=True)
        with db.write() as conn:
            sprint = self._sprint(conn, sprint_id)
            if sprint["status"] != "ACTIVE":
                raise FailedPrecondition(f"{sprint_id} está {sprint['status']}; solo un sprint ACTIVE se cierra")
            if carry_over_to is not None:
                if not isinstance(carry_over_to, str) or carry_over_to == sprint_id:
                    raise InvalidArgument("debe ser otro sprint del proyecto", field="carry_over_to")
                target = self._sprint(conn, carry_over_to)
                if target["status"] != "PLANNED":
                    raise FailedPrecondition(f"{carry_over_to} está {target['status']}: solo se traslada a un PLANNED")
            now = _now()
            statuses = {
                r[0]: r[1]
                for r in conn.execute(
                    "SELECT ss.story_id, st.status FROM sprint_stories ss JOIN stories st ON st.id = ss.story_id "
                    "WHERE ss.sprint_id = ? AND ss.ended_at IS NULL",
                    (sprint_id,),
                )
            }
            done = sorted(s for s, st in statuses.items() if st == "DONE")
            not_done = sorted(s for s in statuses if s not in done)
            for sid in done:
                conn.execute(
                    "UPDATE sprint_stories SET ended_at = ?, outcome = 'done' WHERE sprint_id = ? AND story_id = ?",
                    (now, sprint_id, sid),
                )
            for sid in not_done:
                outcome = "carried_over" if carry_over_to else "returned"
                conn.execute(
                    "UPDATE sprint_stories SET ended_at = ?, outcome = ? WHERE sprint_id = ? AND story_id = ?",
                    (now, outcome, sprint_id, sid),
                )
                if carry_over_to:
                    conn.execute(
                        "INSERT INTO sprint_stories(sprint_id, story_id, added_at, added_by) VALUES (?, ?, ?, ?) "
                        "ON CONFLICT(sprint_id, story_id) DO UPDATE SET added_at = excluded.added_at, "
                        "added_by = excluded.added_by, ended_at = NULL, outcome = NULL",
                        (carry_over_to, sid, now, principal),
                    )
            by_status: dict[str, int] = {}
            for st in statuses.values():
                by_status[st] = by_status.get(st, 0) + 1
            planned = len(statuses)
            summary = {
                "goal": sprint["goal"],
                "start_date": sprint["start_date"],
                "end_date": sprint["end_date"],
                "closed_on": now[:10],
                "capacity": sprint["capacity"],
                "stories": planned,
                "done": done,
                "not_done": not_done,
                "carried_over_to": carry_over_to,
                "completion_pct": round(100 * len(done) / planned) if planned else 0,
                "stories_by_status": by_status,
                "text": (
                    f"{sprint_id} «{sprint['name']}»: {len(done)} de {planned} historias terminadas"
                    f" ({round(100 * len(done) / planned) if planned else 0} %). "
                    + (
                        f"Sin terminar: {', '.join(not_done)}; "
                        + (f"trasladadas a {carry_over_to}." if carry_over_to else "vuelven al backlog.")
                        if not_done
                        else "Todas terminadas."
                    )
                ),
            }
            conn.execute(
                "UPDATE sprints SET status = 'CLOSED', closed_at = ?, closed_by = ?, summary_json = ? WHERE id = ?",
                (now, principal, json.dumps(summary, ensure_ascii=False), sprint_id),
            )
        return self._emit(principal, project_id, "sprint.closed", sprint_id)

    def cancel(self, principal: str, project_id: str, sprint_id: str) -> dict[str, Any]:
        db = self.backlog._db(principal, project_id, write=True)
        with db.write() as conn:
            sprint = self._sprint(conn, sprint_id)
            if sprint["status"] not in OPEN:
                raise FailedPrecondition(f"{sprint_id} ya está {sprint['status']}")
            now = _now()
            conn.execute(
                "UPDATE sprint_stories SET ended_at = ?, outcome = 'returned' WHERE sprint_id = ? AND ended_at IS NULL",
                (now, sprint_id),
            )
            conn.execute(
                "UPDATE sprints SET status = 'CANCELLED', closed_at = ?, closed_by = ? WHERE id = ?",
                (now, principal, sprint_id),
            )
        return self._emit(principal, project_id, "sprint.cancelled", sprint_id)

    # ------------------------------------------------------------------ eventos (ADR-018)
    def _emit(self, principal: str, project_id: str, type: str, sprint_id: str) -> dict[str, Any]:
        result = self.get(principal, project_id, sprint_id)
        self.projects.events.append(
            type,
            principal=principal,
            project_id=project_id,
            entity_type="sprint",
            entity_id=sprint_id,
            data={"status": result["status"], "name": result["name"], "load": result["load"]},
        )
        return result
