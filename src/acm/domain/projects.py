"""Servicio de proyectos: crear, listar, abrir y configurar (US-01.01, US-01.02, US-01.03, US-01.06).

Almacenamiento (ADR-011, ADR-013):
- `<data_dir>/acm.db`: principales, registro de proyectos y pertenencias.
- `<data_dir>/projects/<project_id>/project.db`: metadatos y configuración de cada proyecto.

Todos los métodos son síncronos (sqlite3); la frontera MCP los ejecuta en hilos de trabajo.
"""

from __future__ import annotations

import json
import re
import shutil
import sqlite3
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from acm.db import schema
from acm.db.connection import Database
from acm.db.migrations import current_version, migrate
from acm.domain.config_schema import PARAMETERS, check_stored, validate_changes
from acm.domain.errors import AlreadyExists, Forbidden, InvalidArgument, NotFound, StorageError

KEY_RE = re.compile(r"^[a-z][a-z0-9-]{1,39}$")
NAME_MAX = 120
GLOBAL_ROLES = ("admin", "user")


def _now() -> str:
    return datetime.now(UTC).isoformat()


def validate_project_id(value: Any, field: str = "project_id") -> str:
    if not isinstance(value, str) or not KEY_RE.match(value):
        raise InvalidArgument(
            "formato inválido: se espera ^[a-z][a-z0-9-]{1,39}$ (sin mayúsculas ni espacios)", field=field
        )
    return value


class ProjectService:
    def __init__(self, data_dir: Path | str, *, synchronous: str = "FULL"):
        self.data_dir = Path(data_dir)
        self.projects_dir = self.data_dir / "projects"
        try:
            self.projects_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise StorageError(f"el directorio de datos no es escribible: {self.data_dir}: {exc}") from exc
        self.global_db = Database(self.data_dir / "acm.db", synchronous=synchronous)
        migrate(self.global_db, schema.GLOBAL)
        self._project_dbs: dict[str, Database] = {}
        self._dbs_lock = threading.Lock()

    def close(self) -> None:
        with self._dbs_lock:
            for db in self._project_dbs.values():
                db.close()
            self._project_dbs.clear()
        self.global_db.close()

    # ---------------------------------------------------------------- principales
    def ensure_principal(self, principal_id: str, role: str, kind: str = "user") -> None:
        if role not in GLOBAL_ROLES:
            raise InvalidArgument(f"rol global inválido; válidos: {list(GLOBAL_ROLES)}", field="role")
        with self.global_db.write() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO principals(id, role, kind, created_at) VALUES (?, ?, ?, ?)",
                (principal_id, role, kind, _now()),
            )

    def _principal_role(self, conn: sqlite3.Connection, principal_id: str) -> str:
        row = conn.execute("SELECT role FROM principals WHERE id = ?", (principal_id,)).fetchone()
        if row is None:
            raise Forbidden(f"principal desconocido: {principal_id!r}")
        return str(row["role"])

    def _project_role(self, principal_id: str, project_id: str) -> str:
        """Rol efectivo en el proyecto; NOT_FOUND si no existe o no es accesible (no se revela su existencia)."""
        validate_project_id(project_id)
        with self.global_db.read() as conn:
            global_role = self._principal_role(conn, principal_id)
            exists = conn.execute("SELECT 1 FROM projects WHERE id = ?", (project_id,)).fetchone()
            member = conn.execute(
                "SELECT role FROM project_members WHERE project_id = ? AND principal_id = ?", (project_id, principal_id)
            ).fetchone()
        if exists and global_role == "admin":
            return "admin"
        if exists and member:
            return str(member["role"])
        raise NotFound(f"project_id {project_id!r} no existe o no es accesible")

    # ------------------------------------------------------------------- crear
    def create(self, principal_id: str, key: Any, name: Any, description: Any = "") -> dict[str, Any]:
        key = validate_project_id(key, field="key")
        if not isinstance(name, str) or not name.strip():
            raise InvalidArgument("es obligatorio y no puede estar vacío", field="name")
        name = name.strip()
        if len(name) > NAME_MAX:
            raise InvalidArgument(f"máximo {NAME_MAX} caracteres (tiene {len(name)})", field="name")
        if description is None:
            description = ""
        if not isinstance(description, str):
            raise InvalidArgument("debe ser texto", field="description")

        with self.global_db.read() as conn:
            if self._principal_role(conn, principal_id) != "admin":
                raise Forbidden("solo un principal con rol global 'admin' puede crear proyectos")
            if conn.execute("SELECT 1 FROM projects WHERE id = ?", (key,)).fetchone():
                raise AlreadyExists(f"ya existe un proyecto con identificador {key!r}", field="key")

        project_dir = self.projects_dir / key
        try:
            project_dir.mkdir(exist_ok=False)
        except FileExistsError as exc:
            raise AlreadyExists(
                f"ya existe un proyecto (o un directorio residual) con identificador {key!r}", field="key"
            ) from exc
        except OSError as exc:
            raise StorageError(f"no se pudo crear el directorio del proyecto; no se ha creado nada: {exc}") from exc

        created_at = _now()
        db_path = project_dir / "project.db"
        try:
            self._init_project_db(db_path, key, created_at)
        except Exception as exc:
            shutil.rmtree(project_dir, ignore_errors=True)
            raise StorageError(f"no se pudo crear la base del proyecto; no se ha creado nada: {exc}") from exc

        try:
            self._register(key, name, description, created_at, principal_id, db_path)
        except sqlite3.IntegrityError as exc:
            shutil.rmtree(project_dir, ignore_errors=True)
            raise AlreadyExists(f"ya existe un proyecto con identificador {key!r}", field="key") from exc
        except Exception as exc:
            shutil.rmtree(project_dir, ignore_errors=True)
            raise StorageError(f"no se pudo registrar el proyecto; no se ha creado nada: {exc}") from exc
        return self._summary(key)

    def _init_project_db(self, db_path: Path, key: str, created_at: str) -> None:
        db = Database(db_path)
        try:
            migrate(db, schema.PROJECT)
            with db.write() as conn:
                conn.executemany(
                    "INSERT INTO project_meta(key, value) VALUES (?, ?)",
                    [("project_id", key), ("created_at", created_at)],
                )
        finally:
            db.close()

    def _register(
        self, key: str, name: str, description: str, created_at: str, principal_id: str, db_path: Path
    ) -> None:
        with self.global_db.write() as conn:
            conn.execute(
                "INSERT INTO projects(id, name, description, created_at, created_by, db_path) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (key, name, description, created_at, principal_id, str(db_path)),
            )
            conn.execute(
                "INSERT INTO project_members(project_id, principal_id, role, added_at) VALUES (?, ?, 'owner', ?)",
                (key, principal_id, created_at),
            )

    def _summary(self, project_id: str) -> dict[str, Any]:
        with self.global_db.read() as conn:
            row = conn.execute(
                "SELECT id, name, description, created_at, created_by, db_path FROM projects WHERE id = ?",
                (project_id,),
            ).fetchone()
        return {
            "project_id": row["id"],
            "name": row["name"],
            "description": row["description"],
            "created_at": row["created_at"],
            "created_by": row["created_by"],
            "db_path": row["db_path"],
        }

    # ------------------------------------------------------------------ listar
    def list_for(self, principal_id: str) -> list[dict[str, Any]]:
        with self.global_db.read() as conn:
            role = self._principal_role(conn, principal_id)
            if role == "admin":
                rows = conn.execute("SELECT id FROM projects ORDER BY id").fetchall()
            else:
                rows = conn.execute(
                    "SELECT p.id FROM projects p JOIN project_members m ON m.project_id = p.id "
                    "WHERE m.principal_id = ? ORDER BY p.id",
                    (principal_id,),
                ).fetchall()
        return [self._summary(r["id"]) for r in rows]

    # ------------------------------------------------------------------- abrir
    def project_db(self, project_id: str) -> Database:
        with self._dbs_lock:
            db = self._project_dbs.get(project_id)
            if db is not None:
                return db
            db_path = self.projects_dir / project_id / "project.db"
            if not db_path.is_file():
                raise NotFound(f"project_id {project_id!r}: base del proyecto no encontrada")
            db = Database(db_path)
            migrate(db, schema.PROJECT)
            with db.read() as conn:
                row = conn.execute("SELECT value FROM project_meta WHERE key = 'project_id'").fetchone()
            if row is None or row["value"] != project_id:
                db.close()
                raise StorageError(f"la base {db_path} no pertenece al proyecto {project_id!r}")
            self._project_dbs[project_id] = db
        db.set_synchronous(self._stored_config(db).get("sqlite.synchronous", PARAMETERS["sqlite.synchronous"].default))
        return db

    def open(self, principal_id: str, project_id: str) -> dict[str, Any]:
        role = self._project_role(principal_id, project_id)
        db = self.project_db(project_id)
        return {
            **self._summary(project_id),
            "role": role,
            "schema_version": current_version(db),
            "config": self._effective_config(db),
        }

    # -------------------------------------------------------------- configurar
    @staticmethod
    def _stored_config(db: Database) -> dict[str, Any]:
        with db.read() as conn:
            rows = conn.execute("SELECT key, value_json FROM config").fetchall()
        return {r["key"]: check_stored(r["key"], json.loads(r["value_json"])) for r in rows}

    def _effective_config(self, db: Database) -> list[dict[str, Any]]:
        stored = self._stored_config(db)
        return [p.describe(stored.get(k, p.default)) for k, p in PARAMETERS.items()]

    def get_config(self, principal_id: str, project_id: str) -> dict[str, Any]:
        self._project_role(principal_id, project_id)
        return {"project_id": project_id, "parameters": self._effective_config(self.project_db(project_id))}

    def set_config(self, principal_id: str, project_id: str, changes: Any) -> dict[str, Any]:
        role = self._project_role(principal_id, project_id)
        if role not in ("admin", "owner"):
            raise Forbidden("solo el owner del proyecto o un admin puede modificar su configuración")
        changes = validate_changes(changes)
        db = self.project_db(project_id)
        before = self._stored_config(db)
        if changes:
            now = _now()
            with db.write() as conn:
                conn.executemany(
                    "INSERT INTO config(key, value_json, updated_at, updated_by) VALUES (?, ?, ?, ?) "
                    "ON CONFLICT(key) DO UPDATE SET value_json = excluded.value_json, "
                    "updated_at = excluded.updated_at, updated_by = excluded.updated_by",
                    [(k, json.dumps(v), now, principal_id) for k, v in changes.items()],
                )
            if "sqlite.synchronous" in changes:
                db.set_synchronous(changes["sqlite.synchronous"])
        changed = [k for k, v in changes.items() if before.get(k, PARAMETERS[k].default) != v]
        return {
            "project_id": project_id,
            "parameters": self._effective_config(db),
            "changed": changed,
            "requires_reload": [k for k in changed if PARAMETERS[k].requires_reload],
        }

    # ----------------------------------------------------------------- sistema
    def system_info(self) -> dict[str, Any]:
        with self.global_db.read() as conn:
            n = conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
        return {
            "global_schema_version": current_version(self.global_db),
            "projects": n,
            "sqlite": self.global_db.pragmas(),
            "sqlite_version": sqlite3.sqlite_version,
        }
