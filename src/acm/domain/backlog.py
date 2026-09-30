"""Backlog del proyecto: requisitos, épicas, features, historias y criterios de aceptación.

Historias: US-03.03 (trazabilidad requisito ↔ backlog), US-04.01 (épicas), US-04.02 (features),
US-04.03 (historias). Todo vive en la base SQLite del propio proyecto (ADR-011): los backlogs de
proyectos distintos son independientes por construcción (US-24.01, US-24.03).

IDs (mismo formato que el backlog de ACM): REQ-NNN, EPIC-NN, FEAT-NN.MM, US-NN.MM (la historia se numera
dentro de su épica). Se generan dentro de la transacción de escritura, o se aceptan explícitos si
respetan el formato y no existen (útil para importar backlogs existentes).
"""

from __future__ import annotations

import re
import sqlite3
from datetime import UTC, datetime
from typing import Any

from acm.domain.errors import AlreadyExists, FailedPrecondition, Forbidden, InvalidArgument, NotFound
from acm.domain.projects import ProjectService
from acm.inference.ports import DecisionRequest, Question
from acm.inference.router import EngineRouter, require_calibrated

# Gate READY (US-04.03 CA-04) expresado como preguntas `noul` de la interfaz de decisión (US-35.11).
READY_GATE_QUESTIONS: dict[str, Question] = {
    "has_statement": Question("noul", "¿Tiene rol, objetivo y beneficio?"),
    "has_requirements": Question("noul", "¿Enlaza algún requisito de origen?"),
    "has_acceptance_criteria": Question("noul", "¿Tiene criterios de aceptación?"),
    "technical_reason_ok": Question("noul", "Si es técnica, ¿declara su razón?"),
}
# US-06.02: transiciones permitidas de una historia. PLANNED → READY solo por el gate (`mark_ready`); DONE solo desde
# VERIFIED (CLAUDE.md: DONE = implementado, probado, verificado y revisado).
STORY_TRANSITIONS: dict[str, tuple[str, ...]] = {
    "PLANNED": ("CANCELLED",),
    "READY": ("IN_PROGRESS", "PLANNED", "CANCELLED"),
    "IN_PROGRESS": ("IMPLEMENTED", "BLOCKED", "READY", "CANCELLED"),
    "BLOCKED": ("IN_PROGRESS", "CANCELLED"),
    "IMPLEMENTED": ("TESTING", "IN_PROGRESS"),
    "TESTING": ("VERIFIED", "FAILED"),
    "FAILED": ("IN_PROGRESS",),
    "VERIFIED": ("DONE", "IN_PROGRESS"),
    "DONE": ("DEPRECATED",),
    "CANCELLED": (),
    "DEPRECATED": (),
}
STORY_STATUSES = tuple(STORY_TRANSITIONS)

READY_GATE_GAPS = {
    "has_statement": "falta rol, objetivo o beneficio (as_a, i_want, so_that)",
    "has_requirements": "sin requisito de origen",
    "has_acceptance_criteria": "sin criterios de aceptación",
    "technical_reason_ok": "tarea técnica sin razón explícita",
}

REQ_RE = re.compile(r"^REQ-(\d{3,})$")
EPIC_RE = re.compile(r"^EPIC-(\d{2,})$")
FEAT_RE = re.compile(r"^FEAT-(\d{2,})\.(\d{2,})$")
US_RE = re.compile(r"^US-(\d{2,})\.(\d{2,})$")
TITLE_MAX = 200
KINDS = ("user_story", "technical")


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _text(value: Any, field: str, *, required: bool = True, max_len: int | None = None) -> str:
    if value is None and not required:
        return ""
    if not isinstance(value, str):
        raise InvalidArgument("debe ser texto", field=field)
    value = value.strip()
    if required and not value:
        raise InvalidArgument("es obligatorio y no puede estar vacío", field=field)
    if max_len is not None and len(value) > max_len:
        raise InvalidArgument(f"máximo {max_len} caracteres (tiene {len(value)})", field=field)
    return value


def _id_list(value: Any, field: str, pattern: re.Pattern[str]) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or any(not isinstance(v, str) or not pattern.match(v) for v in value):
        raise InvalidArgument(f"debe ser una lista de identificadores con formato {pattern.pattern}", field=field)
    if len(set(value)) != len(value):
        raise InvalidArgument("contiene identificadores repetidos", field=field)
    return list(value)


def _num(n: int) -> str:
    return f"{n:02d}"


class BacklogService:
    def __init__(self, projects: ProjectService, decisions: EngineRouter | None = None):
        self.projects = projects
        # El gate READY decide a través de la interfaz de decisión común (US-35.11 CA-01), nunca de un motor concreto.
        self.decisions = decisions if decisions is not None else EngineRouter(projects)

    # ---------------------------------------------------------------- eventos (ADR-018)
    def _emit(
        self, principal: str, project_id: str, type: str, entity_type: str, entity_id: str, data: dict[str, Any]
    ) -> None:
        self.projects.events.append(
            type, principal=principal, project_id=project_id, entity_type=entity_type, entity_id=entity_id, data=data
        )

    @staticmethod
    def _story_data(story: dict[str, Any]) -> dict[str, Any]:
        return {k: story[k] for k in ("status", "feature_id", "epic_id", "i_want", "kind")}

    # ---------------------------------------------------------------- acceso
    def _db(self, principal: str, project_id: str, *, write: bool = False):
        """Cualquier rol del proyecto (admin, owner, member) puede leer y escribir el backlog."""
        role = self.projects._project_role(principal, project_id)  # NOT_FOUND si no es accesible
        if write and role not in ("admin", "owner", "member"):
            raise Forbidden("sin permiso para modificar el backlog")
        if write:
            self.projects.ensure_writable(project_id)
        return self.projects.project_db(project_id)

    @staticmethod
    def _must_exist(conn: sqlite3.Connection, table: str, ident: str, field: str) -> sqlite3.Row:
        row = conn.execute(f"SELECT * FROM {table} WHERE id = ?", (ident,)).fetchone()
        if row is None:
            raise NotFound(f"{ident!r} no existe en este proyecto", field=field)
        return row

    @staticmethod
    def _check_requirements(conn: sqlite3.Connection, ids: list[str], field: str) -> None:
        for rid in ids:
            if conn.execute("SELECT 1 FROM requirements WHERE id = ?", (rid,)).fetchone() is None:
                raise NotFound(f"requisito {rid!r} no existe en este proyecto", field=field)

    # ------------------------------------------------------------ requisitos
    def create_requirement(
        self, principal: str, project_id: str, title: Any, description: Any = "", requirement_id: Any = None
    ) -> dict[str, Any]:
        title = _text(title, "title", max_len=TITLE_MAX)
        description = _text(description, "description", required=False)
        db = self._db(principal, project_id, write=True)
        with db.write() as conn:
            rid = self._new_id(
                conn,
                "requirements",
                requirement_id,
                REQ_RE,
                "requirement_id",
                lambda n: f"REQ-{n:03d}",
                lambda m: int(m.group(1)),
            )
            conn.execute(
                "INSERT INTO requirements(id, title, description, created_at, created_by) VALUES (?, ?, ?, ?, ?)",
                (rid, title, description, _now(), principal),
            )
        result = self.get_requirement(principal, project_id, rid)
        self._emit(principal, project_id, "requirement.created", "requirement", rid, {"title": result["title"]})
        return result

    def get_requirement(self, principal: str, project_id: str, requirement_id: str) -> dict[str, Any]:
        with self._db(principal, project_id).read() as conn:
            row = self._must_exist(conn, "requirements", requirement_id, "requirement_id")
            return {"project_id": project_id, **dict(row)}

    def list_requirements(self, principal: str, project_id: str) -> dict[str, Any]:
        with self._db(principal, project_id).read() as conn:
            rows = conn.execute("SELECT * FROM requirements ORDER BY id").fetchall()
        return {"project_id": project_id, "requirements": [dict(r) for r in rows]}

    def trace_requirement(self, principal: str, project_id: str, requirement_id: str) -> dict[str, Any]:
        """US-03.03: requisito → épicas → features → historias, y las historias que lo implementan."""
        with self._db(principal, project_id).read() as conn:
            req = dict(self._must_exist(conn, "requirements", requirement_id, "requirement_id"))
            epic_ids = [
                r[0]
                for r in conn.execute(
                    "SELECT epic_id FROM epic_requirements WHERE requirement_id = ? ORDER BY epic_id", (requirement_id,)
                )
            ]
            story_rows = conn.execute(
                "SELECT s.id, s.feature_id, s.epic_id, s.status FROM stories s JOIN story_requirements sr "
                "ON sr.story_id = s.id WHERE sr.requirement_id = ? ORDER BY s.id",
                (requirement_id,),
            ).fetchall()
            epics = [self._epic_tree(conn, eid) for eid in sorted(set(epic_ids) | {r["epic_id"] for r in story_rows})]
        return {
            "project_id": project_id,
            "requirement": req,
            "epic_ids": epic_ids,
            "epics": epics,
            "stories": [dict(r) for r in story_rows],
            "orphan": not story_rows,
        }

    # ---------------------------------------------------------------- épicas
    def create_epic(
        self,
        principal: str,
        project_id: str,
        title: Any,
        objective: Any,
        scope: Any,
        requirement_ids: Any = None,
        epic_id: Any = None,
    ) -> dict[str, Any]:
        title = _text(title, "title", max_len=TITLE_MAX)
        objective = _text(objective, "objective")
        scope = _text(scope, "scope")
        req_ids = _id_list(requirement_ids, "requirement_ids", REQ_RE)
        db = self._db(principal, project_id, write=True)
        with db.write() as conn:
            self._check_requirements(conn, req_ids, "requirement_ids")
            eid = self._new_id(
                conn, "epics", epic_id, EPIC_RE, "epic_id", lambda n: f"EPIC-{_num(n)}", lambda m: int(m.group(1))
            )
            conn.execute(
                "INSERT INTO epics(id, title, objective, scope, created_at, created_by) VALUES (?, ?, ?, ?, ?, ?)",
                (eid, title, objective, scope, _now(), principal),
            )
            conn.executemany(
                "INSERT INTO epic_requirements(epic_id, requirement_id) VALUES (?, ?)", [(eid, r) for r in req_ids]
            )
        result = self.get_epic(principal, project_id, eid)
        self._emit(principal, project_id, "epic.created", "epic", eid, {"title": result["title"]})
        return result

    def link_epic_requirements(
        self, principal: str, project_id: str, epic_id: str, requirement_ids: Any
    ) -> dict[str, Any]:
        req_ids = _id_list(requirement_ids, "requirement_ids", REQ_RE)
        if not req_ids:
            raise InvalidArgument("indica al menos un requisito", field="requirement_ids")
        db = self._db(principal, project_id, write=True)
        with db.write() as conn:
            self._must_exist(conn, "epics", epic_id, "epic_id")
            self._check_requirements(conn, req_ids, "requirement_ids")
            conn.executemany(
                "INSERT OR IGNORE INTO epic_requirements(epic_id, requirement_id) VALUES (?, ?)",
                [(epic_id, r) for r in req_ids],
            )
        result = self.get_epic(principal, project_id, epic_id)
        self._emit(
            principal, project_id, "epic.updated", "epic", epic_id, {"requirement_ids": result["requirement_ids"]}
        )
        return result

    def _epic_tree(self, conn: sqlite3.Connection, epic_id: str) -> dict[str, Any]:
        epic = dict(self._must_exist(conn, "epics", epic_id, "epic_id"))
        epic["requirement_ids"] = [
            r[0]
            for r in conn.execute(
                "SELECT requirement_id FROM epic_requirements WHERE epic_id = ? ORDER BY requirement_id", (epic_id,)
            )
        ]
        features = []
        for f in conn.execute("SELECT * FROM features WHERE epic_id = ? ORDER BY id", (epic_id,)).fetchall():
            fd = dict(f)
            fd["story_ids"] = [
                r[0] for r in conn.execute("SELECT id FROM stories WHERE feature_id = ? ORDER BY id", (f["id"],))
            ]
            features.append(fd)
        epic["features"] = features
        return epic

    def get_epic(self, principal: str, project_id: str, epic_id: str) -> dict[str, Any]:
        with self._db(principal, project_id).read() as conn:
            return {"project_id": project_id, **self._epic_tree(conn, epic_id)}

    def list_epics(self, principal: str, project_id: str) -> dict[str, Any]:
        with self._db(principal, project_id).read() as conn:
            ids = [r[0] for r in conn.execute("SELECT id FROM epics ORDER BY id")]
            return {"project_id": project_id, "epics": [self._epic_tree(conn, i) for i in ids]}

    def confirm_epic_coverage(self, principal: str, project_id: str, epic_id: str) -> dict[str, Any]:
        """US-04.02 CA-03: el Product Owner confirma que las features activas cubren el objetivo de la épica."""
        db = self._db(principal, project_id, write=True)
        with db.write() as conn:
            self._must_exist(conn, "epics", epic_id, "epic_id")
            active = conn.execute(
                "SELECT COUNT(*) FROM features WHERE epic_id = ? AND status = 'ACTIVE'", (epic_id,)
            ).fetchone()[0]
            if active == 0:
                raise FailedPrecondition(f"{epic_id} no tiene features activas que puedan cubrir su objetivo")
            conn.execute(
                "UPDATE epics SET coverage_confirmed_at = ?, coverage_confirmed_by = ? WHERE id = ?",
                (_now(), principal, epic_id),
            )
        result = self.get_epic(principal, project_id, epic_id)
        self._emit(principal, project_id, "epic.updated", "epic", epic_id, {"coverage_confirmed": True})
        return result

    # -------------------------------------------------------------- features
    def create_feature(
        self, principal: str, project_id: str, epic_id: str, title: Any, description: Any = "", feature_id: Any = None
    ) -> dict[str, Any]:
        title = _text(title, "title", max_len=TITLE_MAX)
        description = _text(description, "description", required=False)
        db = self._db(principal, project_id, write=True)
        with db.write() as conn:
            fid = self._insert_feature(conn, principal, epic_id, title, description, feature_id)
        with db.read() as conn:
            feature = dict(conn.execute("SELECT * FROM features WHERE id = ?", (fid,)).fetchone())
        result = {"project_id": project_id, **feature, "story_ids": []}
        self._emit(principal, project_id, "feature.created", "feature", feature["id"], {"epic_id": feature["epic_id"]})
        return result

    def _insert_feature(
        self, conn: sqlite3.Connection, principal: str, epic_id: str, title: str, description: str, feature_id: Any
    ) -> str:
        m = EPIC_RE.match(epic_id) if isinstance(epic_id, str) else None
        if not m:
            raise InvalidArgument(f"formato inválido: se espera {EPIC_RE.pattern}", field="epic_id")
        self._must_exist(conn, "epics", epic_id, "epic_id")
        epic_num = m.group(1)
        fid = self._new_id(
            conn,
            "features",
            feature_id,
            FEAT_RE,
            "feature_id",
            lambda n: f"FEAT-{epic_num}.{_num(n)}",
            lambda mm: int(mm.group(2)),
            scope_sql="epic_id = ?",
            scope_args=(epic_id,),
            same_parent=lambda mm: mm.group(1) == epic_num,
        )
        conn.execute(
            "INSERT INTO features(id, epic_id, title, description, created_at, created_by) VALUES (?, ?, ?, ?, ?, ?)",
            (fid, epic_id, title, description, _now(), principal),
        )
        return fid

    def split_feature(self, principal: str, project_id: str, feature_id: str, parts: Any) -> dict[str, Any]:
        """US-04.02 CA-04: divide una feature en ≥2 features nuevas repartiendo todas sus historias."""
        if not isinstance(parts, list) or len(parts) < 2:
            raise InvalidArgument("indica al menos 2 partes", field="parts")
        db = self._db(principal, project_id, write=True)
        with db.write() as conn:
            feat = self._must_exist(conn, "features", feature_id, "feature_id")
            if feat["status"] != "ACTIVE":
                raise FailedPrecondition(f"{feature_id} ya fue dividida ({feat['split_into']})")
            current = {r[0] for r in conn.execute("SELECT id FROM stories WHERE feature_id = ?", (feature_id,))}
            assigned: list[str] = []
            clean = []
            for i, part in enumerate(parts):
                if not isinstance(part, dict):
                    raise InvalidArgument(
                        "cada parte debe ser un objeto {title, description?, story_ids}", field=f"parts[{i}]"
                    )
                story_ids = _id_list(part.get("story_ids", []), f"parts[{i}].story_ids", US_RE)
                clean.append(
                    (
                        _text(part.get("title"), f"parts[{i}].title", max_len=TITLE_MAX),
                        _text(part.get("description", ""), f"parts[{i}].description", required=False),
                        story_ids,
                    )
                )
                assigned += story_ids
            if sorted(assigned) != sorted(current) or len(assigned) != len(set(assigned)):
                raise InvalidArgument(
                    f"cada historia de {feature_id} debe asignarse a exactamente una parte "
                    f"(historias: {sorted(current)})",
                    field="parts",
                )
            new_ids = []
            for title, description, story_ids in clean:
                fid = self._insert_feature(conn, principal, feat["epic_id"], title, description, None)
                new_ids.append(fid)
                conn.executemany(
                    "UPDATE stories SET feature_id = ?, updated_at = ? WHERE id = ?",
                    [(fid, _now(), s) for s in story_ids],
                )
            conn.execute(
                "UPDATE features SET status = 'SPLIT', split_into = ? WHERE id = ?", (",".join(new_ids), feature_id)
            )
        result = self.get_epic(principal, project_id, feat["epic_id"]) | {"split_into": new_ids}
        self._emit(principal, project_id, "feature.split", "feature", feature_id, {"split_into": new_ids})
        return result

    # --------------------------------------------------------------- historias
    def create_story(
        self,
        principal: str,
        project_id: str,
        feature_id: str,
        as_a: Any,
        i_want: Any,
        so_that: Any,
        requirement_ids: Any,
        acceptance_criteria: Any = None,
        kind: Any = "user_story",
        technical_reason: Any = "",
        story_id: Any = None,
    ) -> dict[str, Any]:
        as_a = _text(as_a, "as_a")
        i_want = _text(i_want, "i_want")
        so_that = _text(so_that, "so_that")
        req_ids = _id_list(requirement_ids, "requirement_ids", REQ_RE)
        if not req_ids:
            raise InvalidArgument("toda historia necesita al menos un requisito de origen", field="requirement_ids")
        if kind not in KINDS:
            raise InvalidArgument(f"debe ser uno de {list(KINDS)}", field="kind")
        technical_reason = _text(technical_reason, "technical_reason", required=False)
        if kind == "technical" and not technical_reason:
            raise InvalidArgument(
                "una tarea técnica solo puede registrarse como historia con una razón explícita",
                field="technical_reason",
            )
        criteria = self._criteria_list(acceptance_criteria)
        db = self._db(principal, project_id, write=True)
        with db.write() as conn:
            feat = self._must_exist(conn, "features", feature_id, "feature_id")
            if feat["status"] != "ACTIVE":
                raise FailedPrecondition(f"{feature_id} fue dividida; usa una de {feat['split_into']}")
            self._check_requirements(conn, req_ids, "requirement_ids")
            epic_num = EPIC_RE.match(feat["epic_id"]).group(1)
            sid = self._new_id(
                conn,
                "stories",
                story_id,
                US_RE,
                "story_id",
                lambda n: f"US-{epic_num}.{_num(n)}",
                lambda mm: int(mm.group(2)),
                scope_sql="epic_id = ?",
                scope_args=(feat["epic_id"],),
                same_parent=lambda mm: mm.group(1) == epic_num,
            )
            now = _now()
            conn.execute(
                "INSERT INTO stories(id, epic_id, feature_id, kind, as_a, i_want, so_that, "
                "technical_reason, created_at, created_by, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (sid, feat["epic_id"], feature_id, kind, as_a, i_want, so_that, technical_reason, now, principal, now),
            )
            conn.executemany(
                "INSERT INTO story_requirements(story_id, requirement_id) VALUES (?, ?)", [(sid, r) for r in req_ids]
            )
            self._insert_criteria(conn, principal, sid, criteria)
        result = self.get_story(principal, project_id, sid)
        self._emit(principal, project_id, "story.created", "story", result["id"], self._story_data(result))
        return result

    @staticmethod
    def _criteria_list(value: Any) -> list[str]:
        if value is None:
            return []
        if not isinstance(value, list) or any(not isinstance(c, str) or not c.strip() for c in value):
            raise InvalidArgument("debe ser una lista de textos no vacíos", field="acceptance_criteria")
        return [c.strip() for c in value]

    @staticmethod
    def _insert_criteria(conn: sqlite3.Connection, principal: str, story_id: str, criteria: list[str]) -> None:
        n = conn.execute("SELECT COUNT(*) FROM acceptance_criteria WHERE story_id = ?", (story_id,)).fetchone()[0]
        now = _now()
        conn.executemany(
            "INSERT INTO acceptance_criteria(story_id, code, text, created_at, created_by) VALUES (?, ?, ?, ?, ?)",
            [(story_id, f"CA-{n + i:02d}", c, now, principal) for i, c in enumerate(criteria, 1)],
        )

    def add_criteria(self, principal: str, project_id: str, story_id: str, criteria: Any) -> dict[str, Any]:
        items = self._criteria_list(criteria)
        if not items:
            raise InvalidArgument("indica al menos un criterio", field="criteria")
        db = self._db(principal, project_id, write=True)
        with db.write() as conn:
            self._must_exist(conn, "stories", story_id, "story_id")
            self._insert_criteria(conn, principal, story_id, items)
            conn.execute("UPDATE stories SET updated_at = ? WHERE id = ?", (_now(), story_id))
        result = self.get_story(principal, project_id, story_id)
        self._emit(principal, project_id, "story.updated", "story", result["id"], self._story_data(result))
        return result

    def _story(self, conn: sqlite3.Connection, story_id: str) -> dict[str, Any]:
        story = dict(self._must_exist(conn, "stories", story_id, "story_id"))
        story["requirement_ids"] = [
            r[0]
            for r in conn.execute(
                "SELECT requirement_id FROM story_requirements WHERE story_id = ? ORDER BY requirement_id", (story_id,)
            )
        ]
        story["acceptance_criteria"] = [
            dict(r)
            for r in conn.execute(
                "SELECT code, text FROM acceptance_criteria WHERE story_id = ? ORDER BY code", (story_id,)
            )
        ]
        return story

    def get_story(self, principal: str, project_id: str, story_id: str) -> dict[str, Any]:
        with self._db(principal, project_id).read() as conn:
            return {"project_id": project_id, **self._story(conn, story_id)}

    def mark_ready(self, principal: str, project_id: str, story_id: str) -> dict[str, Any]:
        """US-04.03 CA-04: una historia incompleta no puede pasar a READY.

        La comprobación se pide al router de decisión (`story.quality`); con el orden por defecto la responde el motor
        de reglas. El gate solo acepta respuestas calibradas y no retiene el bloqueo de escritura mientras se decide:
        si la historia cambia entre la decisión y la escritura, se rechaza y hay que reintentar.
        """
        db = self._db(principal, project_id, write=True)
        with db.read() as conn:
            story = self._story(conn, story_id)
        if story["status"] != "PLANNED":
            raise FailedPrecondition(f"{story_id} está en {story['status']}; solo PLANNED puede pasar a READY")
        request = DecisionRequest(
            state=story, questions=READY_GATE_QUESTIONS, purpose="story.quality", project_id=project_id
        )
        result = self.decisions.decide(principal, request).result
        require_calibrated(result, "gate READY")
        gaps = [READY_GATE_GAPS[k] for k in READY_GATE_QUESTIONS if float(result.answers[k].value) < 0.5]
        if gaps:
            raise FailedPrecondition(f"{story_id} no puede pasar a READY: {'; '.join(gaps)}")
        with db.write() as conn:
            if self._story(conn, story_id) != story:
                raise FailedPrecondition(f"{story_id} cambió mientras se validaba; vuelve a intentarlo")
            self._change_status(conn, principal, story_id, "PLANNED", "READY", "gate READY superado")
        result = self.get_story(principal, project_id, story_id)
        self._emit(
            principal,
            project_id,
            "story.status_changed",
            "story",
            result["id"],
            self._story_data(result) | {"from": "PLANNED"},
        )
        return result

    @staticmethod
    def _change_status(
        conn: sqlite3.Connection, principal: str, story_id: str, old: str, new: str, reason: str
    ) -> None:
        now = _now()
        conn.execute("UPDATE stories SET status = ?, updated_at = ? WHERE id = ?", (new, now, story_id))
        conn.execute(
            "INSERT INTO story_status_history(story_id, from_status, to_status, reason, changed_at, changed_by) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (story_id, old, new, reason, now, principal),
        )

    def set_status(
        self, principal: str, project_id: str, story_id: str, status: Any, reason: Any = ""
    ) -> dict[str, Any]:
        """US-06.02: mueve una historia a otro estado si la transición está permitida (`STORY_TRANSITIONS`)."""
        if not isinstance(status, str) or status not in STORY_STATUSES:
            raise InvalidArgument(f"debe ser uno de {list(STORY_STATUSES)}", field="status")
        if reason is None:
            reason = ""
        if not isinstance(reason, str) or len(reason) > 500:
            raise InvalidArgument("debe ser texto de hasta 500 caracteres", field="reason")
        db = self._db(principal, project_id, write=True)
        with db.write() as conn:
            current = self._story(conn, story_id)["status"]
            if status == current:
                raise FailedPrecondition(f"{story_id} ya está en {status}")
            if current == "PLANNED" and status == "READY":
                raise FailedPrecondition("PLANNED → READY solo pasa por el gate: usa acm_story_mark_ready")
            allowed = STORY_TRANSITIONS[current]
            if status not in allowed:
                raise FailedPrecondition(
                    f"transición no permitida para {story_id}: {current} → {status}; permitidas: {list(allowed)}"
                )
            self._change_status(conn, principal, story_id, current, status, reason.strip())
        result = self.get_story(principal, project_id, story_id)
        self._emit(
            principal,
            project_id,
            "story.status_changed",
            "story",
            result["id"],
            self._story_data(result) | {"from": current},
        )
        return result

    def list_stories(self, principal: str, project_id: str) -> dict[str, Any]:
        """Todas las historias con sus requisitos y criterios (vista completa para la interfaz y el Kanban)."""
        with self._db(principal, project_id).read() as conn:
            ids = [r[0] for r in conn.execute("SELECT id FROM stories ORDER BY id")]
            return {"project_id": project_id, "stories": [self._story(conn, i) for i in ids]}

    def status_history(self, principal: str, project_id: str, story_id: str) -> dict[str, Any]:
        with self._db(principal, project_id).read() as conn:
            self._must_exist(conn, "stories", story_id, "story_id")
            rows = conn.execute(
                "SELECT from_status, to_status, reason, changed_at, changed_by FROM story_status_history "
                "WHERE story_id = ? ORDER BY id",
                (story_id,),
            ).fetchall()
        return {"project_id": project_id, "story_id": story_id, "history": [dict(r) for r in rows]}

    # ---------------------------------------------------------------- auditoría
    def audit(self, principal: str, project_id: str) -> dict[str, Any]:
        """Huecos de trazabilidad del backlog (US-03.03 CA-05 y verificación de estructura)."""
        with self._db(principal, project_id).read() as conn:

            def ids(sql: str) -> list[str]:
                return [r[0] for r in conn.execute(sql)]

            report = {
                "orphan_requirements": ids(
                    "SELECT id FROM requirements WHERE id NOT IN "
                    "(SELECT requirement_id FROM story_requirements) ORDER BY id"
                ),
                "epics_without_features": ids(
                    "SELECT id FROM epics WHERE id NOT IN "
                    "(SELECT epic_id FROM features WHERE status = 'ACTIVE') ORDER BY id"
                ),
                "features_without_stories": ids(
                    "SELECT id FROM features WHERE status = 'ACTIVE' AND id NOT IN "
                    "(SELECT feature_id FROM stories) ORDER BY id"
                ),
                "stories_without_criteria": ids(
                    "SELECT id FROM stories WHERE id NOT IN (SELECT story_id FROM acceptance_criteria) ORDER BY id"
                ),
                "stories_without_requirements": ids(
                    "SELECT id FROM stories WHERE id NOT IN (SELECT story_id FROM story_requirements) ORDER BY id"
                ),
            }
        return {"project_id": project_id, **report, "clean": not any(report.values())}

    # ------------------------------------------------------------------- IDs
    @staticmethod
    def _new_id(
        conn: sqlite3.Connection,
        table: str,
        explicit: Any,
        pattern: re.Pattern[str],
        field: str,
        fmt,
        number,
        *,
        scope_sql: str = "1 = 1",
        scope_args: tuple = (),
        same_parent=None,
    ) -> str:
        if explicit is not None:
            m = pattern.match(explicit) if isinstance(explicit, str) else None
            if not m:
                raise InvalidArgument(f"formato inválido: se espera {pattern.pattern}", field=field)
            if same_parent is not None and not same_parent(m):
                raise InvalidArgument("el número de épica del identificador no coincide con su épica", field=field)
            if conn.execute(f"SELECT 1 FROM {table} WHERE id = ?", (explicit,)).fetchone():
                raise AlreadyExists(f"ya existe {explicit!r} en este proyecto", field=field)
            return explicit
        existing = [r[0] for r in conn.execute(f"SELECT id FROM {table} WHERE {scope_sql}", scope_args)]
        highest = max((number(pattern.match(i)) for i in existing if pattern.match(i)), default=0)
        return fmt(highest + 1)
