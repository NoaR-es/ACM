"""Catálogos de migraciones de ACM (ADR-011: SQLite es la fuente de verdad del producto; ADR-013).

- GLOBAL: base de plataforma `<data_dir>/acm.db` — principales, registro de proyectos, pertenencias.
- PROJECT: base de cada proyecto `<data_dir>/projects/<id>/project.db` — metadatos y configuración.

Una migración publicada no se modifica: los cambios van en migraciones nuevas (US-18.03).
"""

from __future__ import annotations

from acm.db.migrations import Migration

GLOBAL: tuple[Migration, ...] = (
    Migration(
        1,
        "principals_projects_members",
        (
            """CREATE TABLE principals (
            id TEXT PRIMARY KEY CHECK (length(id) BETWEEN 1 AND 64),
            role TEXT NOT NULL CHECK (role IN ('admin', 'user')),
            created_at TEXT NOT NULL
        )""",
            """CREATE TABLE projects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL CHECK (length(name) BETWEEN 1 AND 120),
            description TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            created_by TEXT NOT NULL REFERENCES principals(id),
            db_path TEXT NOT NULL
        )""",
            """CREATE TABLE project_members (
            project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            principal_id TEXT NOT NULL REFERENCES principals(id),
            role TEXT NOT NULL CHECK (role IN ('owner', 'member')),
            added_at TEXT NOT NULL,
            PRIMARY KEY (project_id, principal_id)
        )""",
            "CREATE INDEX idx_project_members_principal ON project_members(principal_id)",
        ),
    ),
)

PROJECT: tuple[Migration, ...] = (
    Migration(
        1,
        "meta_config",
        (
            """CREATE TABLE project_meta (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )""",
            """CREATE TABLE config (
            key TEXT PRIMARY KEY,
            value_json TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            updated_by TEXT NOT NULL
        )""",
        ),
    ),
)
