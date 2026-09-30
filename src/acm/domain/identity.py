"""Identidad, roles y tokens (EPIC-20; ADR-017).

- Principales de tipo `user` o `agent`, cada uno con sus propias credenciales (US-20.04).
- Roles: globales `admin` | `user`; de proyecto `owner` | `member` (US-20.01). Un admin gestiona los roles globales;
  un admin o un owner del proyecto gestiona sus miembros. Nunca se queda el sistema sin admin ni un proyecto sin owner.
- Tokens opacos `acm_<aleatorio>`: se muestran completos una sola vez; se guarda su hash sha256 y un prefijo
  visible. Autorizan como su principal (sus roles) mientras no estén revocados; cada uso se anota (US-20.03).
"""

from __future__ import annotations

import hashlib
import re
import secrets
import sqlite3
from datetime import UTC, datetime
from typing import Any

from acm.domain.errors import FailedPrecondition, Forbidden, InvalidArgument, NotFound, Unauthenticated
from acm.domain.projects import GLOBAL_ROLES, ProjectService

PRINCIPAL_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{1,63}$")
PRINCIPAL_KINDS = ("user", "agent")
PROJECT_ROLES = ("owner", "member")
TOKEN_PREFIX = "acm_"
PREFIX_SHOWN = 12  # "acm_" + 8 caracteres: suficiente para reconocerlo, inútil para usarlo


def _now() -> str:
    return datetime.now(UTC).isoformat()


def hash_secret(secret: str) -> str:
    # Los tokens son aleatorios de 256 bits: un hash rápido basta (no son contraseñas elegidas por personas).
    return hashlib.sha256(secret.encode("utf-8")).hexdigest()


def _choice(value: Any, options: tuple[str, ...], field: str) -> str:
    if not isinstance(value, str) or value not in options:
        raise InvalidArgument(f"debe ser uno de {list(options)}", field=field)
    return value


def _principal_id(value: Any, field: str = "principal_id") -> str:
    if not isinstance(value, str) or not PRINCIPAL_RE.match(value):
        raise InvalidArgument("debe cumplir ^[a-z0-9][a-z0-9._-]{1,63}$", field=field)
    return value


class IdentityService:
    def __init__(self, projects: ProjectService):
        self.projects = projects

    # ------------------------------------------------------------------ comprobaciones
    def _require_admin(self, conn: sqlite3.Connection, actor: str, action: str) -> None:
        if self.projects._principal_role(conn, actor) != "admin":
            raise Forbidden(f"solo un admin puede {action}")

    def _require_project_manager(self, actor: str, project_id: str) -> None:
        role = self.projects._project_role(actor, project_id)  # NOT_FOUND si no es accesible
        if role not in ("admin", "owner"):
            raise Forbidden("solo un admin o un owner del proyecto puede gestionar sus miembros")

    @staticmethod
    def _must_principal(conn: sqlite3.Connection, principal_id: str) -> sqlite3.Row:
        row = conn.execute("SELECT * FROM principals WHERE id = ?", (principal_id,)).fetchone()
        if row is None:
            raise NotFound(f"el principal {principal_id!r} no existe", field="principal_id")
        return row

    # ------------------------------------------------------------------ principales (US-20.04, US-20.01)
    def create_principal(self, actor: str, principal_id: Any, kind: Any, role: Any = "user") -> dict[str, Any]:
        principal_id = _principal_id(principal_id)
        kind = _choice(kind, PRINCIPAL_KINDS, "kind")
        role = _choice(role, GLOBAL_ROLES, "role")
        with self.projects.global_db.write() as conn:
            self._require_admin(conn, actor, "crear principales")
            if conn.execute("SELECT 1 FROM principals WHERE id = ?", (principal_id,)).fetchone():
                raise InvalidArgument(f"ya existe el principal {principal_id!r}", field="principal_id")
            conn.execute(
                "INSERT INTO principals(id, role, kind, created_at) VALUES (?, ?, ?, ?)",
                (principal_id, role, kind, _now()),
            )
        return self.get_principal(actor, principal_id)

    def get_principal(self, actor: str, principal_id: str) -> dict[str, Any]:
        with self.projects.global_db.read() as conn:
            if actor != principal_id:
                self._require_admin(conn, actor, "consultar otros principales")
            row = dict(self._must_principal(conn, principal_id))
            row["projects"] = [
                dict(r)
                for r in conn.execute(
                    "SELECT project_id, role FROM project_members WHERE principal_id = ? ORDER BY project_id",
                    (principal_id,),
                )
            ]
            row["active_tokens"] = conn.execute(
                "SELECT COUNT(*) FROM api_tokens WHERE principal_id = ? AND revoked_at IS NULL", (principal_id,)
            ).fetchone()[0]
        return row

    def list_principals(self, actor: str) -> dict[str, Any]:
        with self.projects.global_db.read() as conn:
            self._require_admin(conn, actor, "listar principales")
            rows = conn.execute("SELECT id, role, kind, created_at FROM principals ORDER BY id").fetchall()
        return {
            "principals": [dict(r) for r in rows],
            "roles": {"global": list(GLOBAL_ROLES), "project": list(PROJECT_ROLES)},
        }

    def set_global_role(self, actor: str, principal_id: Any, role: Any) -> dict[str, Any]:
        principal_id = _principal_id(principal_id)
        role = _choice(role, GLOBAL_ROLES, "role")
        with self.projects.global_db.write() as conn:
            self._require_admin(conn, actor, "cambiar roles globales")
            current = self._must_principal(conn, principal_id)["role"]
            if current == "admin" and role != "admin":
                admins = conn.execute("SELECT COUNT(*) FROM principals WHERE role = 'admin'").fetchone()[0]
                if admins == 1:
                    raise FailedPrecondition("no se puede retirar el rol admin al último admin")
            conn.execute("UPDATE principals SET role = ? WHERE id = ?", (role, principal_id))
        return self.get_principal(actor, principal_id)

    # ------------------------------------------------------------------ miembros de proyecto (US-20.01, US-20.08)
    def set_member(self, actor: str, project_id: str, principal_id: Any, role: Any) -> dict[str, Any]:
        principal_id = _principal_id(principal_id)
        role = _choice(role, PROJECT_ROLES, "role")
        self._require_project_manager(actor, project_id)
        with self.projects.global_db.write() as conn:
            self._must_principal(conn, principal_id)
            current = conn.execute(
                "SELECT role FROM project_members WHERE project_id = ? AND principal_id = ?", (project_id, principal_id)
            ).fetchone()
            if current and current["role"] == "owner" and role != "owner":
                self._keep_an_owner(conn, project_id)
            conn.execute(
                "INSERT INTO project_members(project_id, principal_id, role, added_at) VALUES (?, ?, ?, ?) "
                "ON CONFLICT(project_id, principal_id) DO UPDATE SET role = excluded.role",
                (project_id, principal_id, role, _now()),
            )
        return self.list_members(actor, project_id)

    def remove_member(self, actor: str, project_id: str, principal_id: Any) -> dict[str, Any]:
        principal_id = _principal_id(principal_id)
        self._require_project_manager(actor, project_id)
        with self.projects.global_db.write() as conn:
            current = conn.execute(
                "SELECT role FROM project_members WHERE project_id = ? AND principal_id = ?", (project_id, principal_id)
            ).fetchone()
            if current is None:
                raise NotFound(f"{principal_id!r} no es miembro de {project_id!r}", field="principal_id")
            if current["role"] == "owner":
                self._keep_an_owner(conn, project_id)
            conn.execute(
                "DELETE FROM project_members WHERE project_id = ? AND principal_id = ?", (project_id, principal_id)
            )
        return self.list_members(actor, project_id)

    @staticmethod
    def _keep_an_owner(conn: sqlite3.Connection, project_id: str) -> None:
        owners = conn.execute(
            "SELECT COUNT(*) FROM project_members WHERE project_id = ? AND role = 'owner'", (project_id,)
        ).fetchone()[0]
        if owners == 1:
            raise FailedPrecondition(f"{project_id!r} no puede quedarse sin owner")

    def list_members(self, actor: str, project_id: str) -> dict[str, Any]:
        self.projects._project_role(actor, project_id)
        with self.projects.global_db.read() as conn:
            rows = conn.execute(
                "SELECT m.principal_id, m.role, p.kind, m.added_at FROM project_members m "
                "JOIN principals p ON p.id = m.principal_id WHERE m.project_id = ? ORDER BY m.principal_id",
                (project_id,),
            ).fetchall()
        return {"project_id": project_id, "members": [dict(r) for r in rows]}

    # ------------------------------------------------------------------ tokens (US-20.03)
    def create_token(self, actor: str, principal_id: Any, name: Any) -> dict[str, Any]:
        principal_id = _principal_id(principal_id)
        if not isinstance(name, str) or not 1 <= len(name.strip()) <= 80:
            raise InvalidArgument("debe tener entre 1 y 80 caracteres", field="name")
        secret = TOKEN_PREFIX + secrets.token_urlsafe(32)
        token_id = "tok_" + secrets.token_hex(6)
        with self.projects.global_db.write() as conn:
            self._require_admin(conn, actor, "crear tokens")
            self._must_principal(conn, principal_id)
            conn.execute(
                "INSERT INTO api_tokens(id, principal_id, name, prefix, secret_hash, created_at, created_by) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (token_id, principal_id, name.strip(), secret[:PREFIX_SHOWN], hash_secret(secret), _now(), actor),
            )
        # Única vez que el secreto sale de ACM (CA-03). La auditoría lo redacta (AuditService).
        return {**self._token(token_id), "token": secret}

    def _token(self, token_id: str) -> dict[str, Any]:
        with self.projects.global_db.read() as conn:
            row = conn.execute(
                "SELECT id AS token_id, principal_id, name, prefix, created_at, created_by, revoked_at, revoked_by, "
                "last_used_at, use_count FROM api_tokens WHERE id = ?",
                (token_id,),
            ).fetchone()
        if row is None:
            raise NotFound(f"el token {token_id!r} no existe", field="token_id")
        return {**dict(row), "active": row["revoked_at"] is None}

    def list_tokens(self, actor: str, principal_id: Any = None) -> dict[str, Any]:
        with self.projects.global_db.read() as conn:
            if principal_id is None or principal_id != actor:
                self._require_admin(conn, actor, "listar tokens de otros principales")
            if principal_id is None:
                ids = [r[0] for r in conn.execute("SELECT id FROM api_tokens ORDER BY created_at, id")]
            else:
                ids = [
                    r[0]
                    for r in conn.execute(
                        "SELECT id FROM api_tokens WHERE principal_id = ? ORDER BY created_at, id",
                        (_principal_id(principal_id),),
                    )
                ]
        return {"tokens": [self._token(i) for i in ids]}

    def revoke_token(self, actor: str, token_id: Any) -> dict[str, Any]:
        if not isinstance(token_id, str):
            raise InvalidArgument("debe ser texto", field="token_id")
        with self.projects.global_db.write() as conn:
            row = conn.execute("SELECT principal_id, revoked_at FROM api_tokens WHERE id = ?", (token_id,)).fetchone()
            if row is None:
                raise NotFound(f"el token {token_id!r} no existe", field="token_id")
            if row["principal_id"] != actor:  # cada principal puede revocar los suyos; los ajenos, solo un admin
                self._require_admin(conn, actor, "revocar tokens de otros principales")
            if row["revoked_at"] is None:
                conn.execute(
                    "UPDATE api_tokens SET revoked_at = ?, revoked_by = ? WHERE id = ?", (_now(), actor, token_id)
                )
        return self._token(token_id)

    def authenticate(self, secret: Any) -> tuple[str, str]:
        """Devuelve (principal_id, token_id) o lanza UNAUTHENTICATED. Se consulta en cada petición: revocar es
        inmediato (US-20.03 CA-02). Anota el uso (CA-04)."""
        if not isinstance(secret, str) or not secret.startswith(TOKEN_PREFIX):
            raise Unauthenticated("falta un token Bearer de ACM válido")
        with self.projects.global_db.write() as conn:
            row = conn.execute(
                "SELECT id, principal_id, revoked_at FROM api_tokens WHERE secret_hash = ?", (hash_secret(secret),)
            ).fetchone()
            if row is None:
                raise Unauthenticated("token desconocido")
            if row["revoked_at"] is not None:
                raise Unauthenticated(f"el token {row['id']} está revocado")
            conn.execute(
                "UPDATE api_tokens SET last_used_at = ?, use_count = use_count + 1 WHERE id = ?", (_now(), row["id"])
            )
        return str(row["principal_id"]), str(row["id"])
