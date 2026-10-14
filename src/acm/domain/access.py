"""Unirse a proyectos con aprobación de una persona (FEAT-14.06: US-14.14, US-14.15; ADR-024).

- Un agente ve el directorio de proyectos (`directory`): en modo local, todos (ADR-023); si no, solo los suyos.
- Crea uno nuevo sin pedir permiso (queda como owner) o pide unirse a uno existente (`request_join`). Hasta que una
  persona lo apruebe no accede a nada del proyecto: para él sigue sin ser accesible (NOT_FOUND), como uno ajeno.
- Aprueba o rechaza una **persona** (principal `user`) que sea admin o owner del proyecto, desde la interfaz
  (`decide`). Al aprobar elige el acceso: `member` (escritura) o `viewer` (lectura). Un agente nunca decide.
- Como mucho hay una petición pendiente por agente y proyecto (índice único parcial); pedir otra vez devuelve la misma.
"""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from typing import Any

from acm.domain.errors import FailedPrecondition, Forbidden, InvalidArgument, NotFound
from acm.domain.projects import ProjectService, validate_project_id

ACCESS_LEVELS = {"read": "viewer", "write": "member"}
GRANTABLE_ROLES = ("member", "viewer")
MESSAGE_MAX = 500


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _request(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "request_id": row["id"],
        "project_id": row["project_id"],
        "principal_id": row["principal_id"],
        "access": row["access"],
        "message": row["message"],
        "status": row["status"],
        "created_at": row["created_at"],
        "decided_at": row["decided_at"],
        "decided_by": row["decided_by"],
        "granted_role": row["granted_role"],
    }


class AccessService:
    def __init__(self, projects: ProjectService):
        self.projects = projects

    # ------------------------------------------------------------------ agente
    def directory(self, principal: str) -> dict[str, Any]:
        """Proyectos que el principal puede ver, con su pertenencia y su última petición (US-14.14 CA-01)."""
        with self.projects.global_db.read() as conn:
            global_role = self.projects._principal_role(conn, principal)
            everything = self.projects.local_mode or global_role == "admin"
            rows = conn.execute(
                "SELECT p.id, p.name, p.description, p.created_by, p.created_at, m.role "
                "FROM projects p LEFT JOIN project_members m ON m.project_id = p.id AND m.principal_id = ? "
                "ORDER BY p.id",
                (principal,),
            ).fetchall()
            latest = {
                r["project_id"]: r
                for r in conn.execute(
                    "SELECT * FROM join_requests WHERE principal_id = ? ORDER BY id", (principal,)
                ).fetchall()
            }
        projects = []
        for r in rows:
            role = "admin" if global_role == "admin" else r["role"]
            if role is None and not everything:
                continue
            request = latest.get(r["id"])
            projects.append(
                {
                    "project_id": r["id"],
                    "name": r["name"],
                    "description": r["description"],
                    "created_by": r["created_by"],
                    "created_at": r["created_at"],
                    "your_role": role,
                    "join_request": _request(request) if request is not None and role is None else None,
                }
            )
        return {
            "principal": principal,
            "projects": projects,
            "how_to": (
                "Pregunta a la persona con la que trabajas si crear un proyecto nuevo (acm_project_create, sin "
                "aprobación) o unirte a uno de estos (acm_project_join; espera a que lo apruebe en la interfaz de ACM)."
            ),
        }

    def request_join(self, principal: str, project_id: Any, access: Any = "write", message: Any = "") -> dict[str, Any]:
        """US-14.14 CA-03: petición pendiente; si ya es miembro o ya hay una pendiente, la devuelve sin duplicarla."""
        project_id = validate_project_id(project_id)
        if access not in ACCESS_LEVELS:
            raise InvalidArgument(f"acceso inválido; válidos: {sorted(ACCESS_LEVELS)}", field="access")
        if message is None:
            message = ""
        if not isinstance(message, str) or len(message) > MESSAGE_MAX:
            raise InvalidArgument(f"texto de hasta {MESSAGE_MAX} caracteres", field="message")
        with self.projects.global_db.write() as conn:
            self.projects._principal_role(conn, principal)
            self._must_project(conn, project_id)
            member = conn.execute(
                "SELECT role FROM project_members WHERE project_id = ? AND principal_id = ?", (project_id, principal)
            ).fetchone()
            if member is not None:
                return {"project_id": project_id, "status": "MEMBER", "role": member["role"]}
            pending = conn.execute(
                "SELECT * FROM join_requests WHERE project_id = ? AND principal_id = ? AND status = 'PENDING'",
                (project_id, principal),
            ).fetchone()
            if pending is not None:
                return self._status(pending)
            cur = conn.execute(
                "INSERT INTO join_requests(project_id, principal_id, access, message, created_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (project_id, principal, access, message.strip(), _now()),
            )
            row = conn.execute("SELECT * FROM join_requests WHERE id = ?", (cur.lastrowid,)).fetchone()
        self.projects.events.append(
            "join.requested",
            principal=principal,
            project_id=project_id,
            entity_type="join_request",
            entity_id=str(row["id"]),
            data={"principal_id": principal, "access": access},
        )
        return self._status(row)

    def join_status(self, principal: str, project_id: Any) -> dict[str, Any]:
        """US-14.14 CA-04: estado de la última petición del principal (o MEMBER si ya está dentro)."""
        project_id = validate_project_id(project_id)
        with self.projects.global_db.read() as conn:
            self.projects._principal_role(conn, principal)
            self._must_project(conn, project_id)
            member = conn.execute(
                "SELECT role FROM project_members WHERE project_id = ? AND principal_id = ?", (project_id, principal)
            ).fetchone()
            if member is not None:
                return {"project_id": project_id, "status": "MEMBER", "role": member["role"]}
            row = conn.execute(
                "SELECT * FROM join_requests WHERE project_id = ? AND principal_id = ? ORDER BY id DESC LIMIT 1",
                (project_id, principal),
            ).fetchone()
        if row is None:
            return {"project_id": project_id, "status": "NONE", "next": "acm_project_join"}
        return self._status(row)

    @staticmethod
    def _status(row: sqlite3.Row) -> dict[str, Any]:
        result = _request(row)
        result["next"] = {
            "PENDING": "Espera: una persona debe aprobarla en la interfaz de ACM (Panel → Solicitudes). Consulta con "
            "acm_project_join_status; mientras tanto el proyecto no es accesible.",
            "APPROVED": f"Ya eres {row['granted_role']} del proyecto: empieza con acm_next_work.",
            "REJECTED": "La petición fue rechazada; pregunta a la persona antes de volver a pedirlo.",
        }[row["status"]]
        return result

    def _must_project(self, conn: sqlite3.Connection, project_id: str) -> None:
        if conn.execute("SELECT 1 FROM projects WHERE id = ?", (project_id,)).fetchone() is None:
            raise NotFound(f"project_id {project_id!r} no existe")

    # ------------------------------------------------------------------ persona
    def _require_decider(self, actor: str, project_id: str) -> None:
        role = self.projects._project_role(actor, project_id)  # NOT_FOUND si no es accesible
        if role not in ("admin", "owner"):
            raise Forbidden("solo un admin o un owner del proyecto puede decidir quién se une")
        if self.projects.principal_kind(actor) != "user":
            raise Forbidden("solo una persona puede aprobar o rechazar el acceso a un proyecto")

    def list_requests(self, actor: str, status: Any = "PENDING") -> dict[str, Any]:
        """US-14.15 CA-01: peticiones que el actor puede decidir (admin: todas; owner: las de sus proyectos)."""
        if status not in ("PENDING", "APPROVED", "REJECTED", "ALL"):
            raise InvalidArgument("estado inválido; válidos: PENDING, APPROVED, REJECTED, ALL", field="status")
        with self.projects.global_db.read() as conn:
            global_role = self.projects._principal_role(conn, actor)
            sql = (
                "SELECT r.*, p.name AS project_name, pr.kind AS kind FROM join_requests r "
                "JOIN projects p ON p.id = r.project_id JOIN principals pr ON pr.id = r.principal_id"
            )
            where, params = [], []
            if status != "ALL":
                where.append("r.status = ?")
                params.append(status)
            if global_role != "admin":
                where.append(
                    "r.project_id IN (SELECT project_id FROM project_members WHERE principal_id = ? AND role = 'owner')"
                )
                params.append(actor)
            if where:
                sql += " WHERE " + " AND ".join(where)
            rows = conn.execute(sql + " ORDER BY r.id DESC LIMIT 200", params).fetchall()
        return {
            "requests": [{**_request(r), "project_name": r["project_name"], "kind": r["kind"]} for r in rows],
            "can_decide": self.projects.principal_kind(actor) == "user",
        }

    def decide(self, actor: str, request_id: Any, approve: bool, role: Any = None) -> dict[str, Any]:
        """US-14.15 CA-02/CA-03: aprobar (con rol member o viewer) o rechazar una petición pendiente."""
        if not isinstance(request_id, int) or isinstance(request_id, bool):
            raise InvalidArgument("debe ser un entero", field="request_id")
        with self.projects.global_db.read() as conn:
            row = conn.execute("SELECT * FROM join_requests WHERE id = ?", (request_id,)).fetchone()
        if row is None:
            raise NotFound(f"la petición {request_id} no existe", field="request_id")
        self._require_decider(actor, row["project_id"])
        if row["status"] != "PENDING":
            raise FailedPrecondition(f"la petición {request_id} ya está {row['status']}")
        granted = None
        if approve:
            granted = role if role is not None else ACCESS_LEVELS[row["access"]]
            if granted not in GRANTABLE_ROLES:
                raise InvalidArgument(f"rol inválido; válidos: {list(GRANTABLE_ROLES)}", field="role")
        now = _now()
        with self.projects.global_db.write() as conn:
            changed = conn.execute(
                "UPDATE join_requests SET status = ?, decided_at = ?, decided_by = ?, granted_role = ? "
                "WHERE id = ? AND status = 'PENDING'",
                ("APPROVED" if approve else "REJECTED", now, actor, granted, request_id),
            ).rowcount
            if changed == 0:
                raise FailedPrecondition(f"la petición {request_id} ya se decidió")
            if approve:
                conn.execute(
                    "INSERT INTO project_members(project_id, principal_id, role, added_at) VALUES (?, ?, ?, ?) "
                    "ON CONFLICT(project_id, principal_id) DO NOTHING",
                    (row["project_id"], row["principal_id"], granted, now),
                )
            decided = conn.execute("SELECT * FROM join_requests WHERE id = ?", (request_id,)).fetchone()
        self.projects.events.append(
            "join.decided",
            principal=actor,
            project_id=row["project_id"],
            entity_type="join_request",
            entity_id=str(request_id),
            data={"principal_id": row["principal_id"], "status": decided["status"], "role": granted},
        )
        if approve:
            self.projects.events.append(
                "member.changed",
                principal=actor,
                project_id=row["project_id"],
                entity_type="member",
                entity_id=row["principal_id"],
                data={"role": granted},
            )
        return _request(decided)
