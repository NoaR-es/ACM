"""Catálogos de migraciones de ACM (ADR-011: SQLite es la fuente de verdad del producto; ADR-013).

- GLOBAL: base de plataforma `<data_dir>/acm.db` — principales, registro de proyectos, pertenencias, auditoría MCP (v2).
- PROJECT: base de cada proyecto `<data_dir>/projects/<id>/project.db` — metadatos, configuración y backlog (v2).

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
    Migration(
        2,
        "mcp_audit",
        (
            """CREATE TABLE mcp_audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            principal TEXT NOT NULL,
            operation TEXT NOT NULL,
            project_id TEXT,
            arguments_json TEXT NOT NULL,
            status TEXT NOT NULL CHECK (status IN ('ok', 'error')),
            error TEXT NOT NULL DEFAULT '',
            result_json TEXT NOT NULL DEFAULT '',
            result_truncated INTEGER NOT NULL DEFAULT 0 CHECK (result_truncated IN (0, 1)),
            duration_ms REAL NOT NULL
        )""",
            "CREATE INDEX idx_mcp_audit_principal ON mcp_audit(principal, id)",
            "CREATE INDEX idx_mcp_audit_project ON mcp_audit(project_id, id)",
        ),
    ),
    Migration(
        3,
        "inference",
        (
            # US-47.01 / US-22.01: motores registrados y su último estado de salud (modelos detectados, no supuestos)
            """CREATE TABLE inference_engines (
            name TEXT PRIMARY KEY,
            kind TEXT NOT NULL CHECK (kind IN ('decision', 'generation')),
            provider TEXT NOT NULL,
            endpoint TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL CHECK (status IN ('unknown', 'ok', 'error')),
            detail TEXT NOT NULL DEFAULT '',
            models_json TEXT NOT NULL DEFAULT '[]',
            checked_at TEXT
        )""",
            # US-35.10 CA-02 / US-22.03 CA-02: cada llamada de inferencia con su motor y su resultado
            """CREATE TABLE inference_calls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            principal TEXT NOT NULL,
            project_id TEXT NOT NULL,
            kind TEXT NOT NULL CHECK (kind IN ('decision', 'generation')),
            purpose TEXT NOT NULL,
            engine TEXT NOT NULL DEFAULT '',
            fallback_from TEXT,
            status TEXT NOT NULL CHECK (status IN ('ok', 'error')),
            error TEXT NOT NULL DEFAULT '',
            duration_ms REAL NOT NULL,
            input_tokens INTEGER,
            output_tokens INTEGER
        )""",
            "CREATE INDEX idx_inference_calls_project ON inference_calls(project_id, id)",
            # US-35.09: cada entrega de contexto con el tamaño entregado y el equivalente completo
            """CREATE TABLE context_deliveries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            principal TEXT NOT NULL,
            project_id TEXT NOT NULL,
            story_id TEXT NOT NULL,
            delivered_tokens INTEGER NOT NULL CHECK (delivered_tokens >= 0),
            full_tokens INTEGER NOT NULL CHECK (full_tokens >= 0),
            method TEXT NOT NULL,
            summarized INTEGER NOT NULL CHECK (summarized IN (0, 1)),
            engine TEXT NOT NULL DEFAULT ''
        )""",
            "CREATE INDEX idx_context_deliveries_principal ON context_deliveries(principal, project_id)",
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
    Migration(
        2,
        "backlog",
        (
            """CREATE TABLE requirements (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL CHECK (length(title) BETWEEN 1 AND 200),
            description TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            created_by TEXT NOT NULL
        )""",
            """CREATE TABLE epics (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL CHECK (length(title) BETWEEN 1 AND 200),
            objective TEXT NOT NULL CHECK (length(trim(objective)) > 0),
            scope TEXT NOT NULL CHECK (length(trim(scope)) > 0),
            coverage_confirmed_at TEXT,
            coverage_confirmed_by TEXT,
            created_at TEXT NOT NULL,
            created_by TEXT NOT NULL
        )""",
            """CREATE TABLE epic_requirements (
            epic_id TEXT NOT NULL REFERENCES epics(id),
            requirement_id TEXT NOT NULL REFERENCES requirements(id),
            PRIMARY KEY (epic_id, requirement_id)
        )""",
            """CREATE TABLE features (
            id TEXT PRIMARY KEY,
            epic_id TEXT NOT NULL REFERENCES epics(id),
            title TEXT NOT NULL CHECK (length(title) BETWEEN 1 AND 200),
            description TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'SPLIT')),
            split_into TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            created_by TEXT NOT NULL
        )""",
            """CREATE TABLE stories (
            id TEXT PRIMARY KEY,
            epic_id TEXT NOT NULL REFERENCES epics(id),
            feature_id TEXT NOT NULL REFERENCES features(id),
            kind TEXT NOT NULL CHECK (kind IN ('user_story', 'technical')),
            as_a TEXT NOT NULL,
            i_want TEXT NOT NULL,
            so_that TEXT NOT NULL,
            technical_reason TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'PLANNED' CHECK (status IN ('PLANNED', 'READY', 'IN_PROGRESS', 'BLOCKED',
                'IMPLEMENTED', 'TESTING', 'VERIFIED', 'FAILED', 'DEPRECATED', 'CANCELLED', 'DONE')),
            created_at TEXT NOT NULL,
            created_by TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            CHECK (kind = 'user_story' OR length(trim(technical_reason)) > 0)
        )""",
            """CREATE TABLE story_requirements (
            story_id TEXT NOT NULL REFERENCES stories(id),
            requirement_id TEXT NOT NULL REFERENCES requirements(id),
            PRIMARY KEY (story_id, requirement_id)
        )""",
            """CREATE TABLE acceptance_criteria (
            story_id TEXT NOT NULL REFERENCES stories(id),
            code TEXT NOT NULL,
            text TEXT NOT NULL CHECK (length(trim(text)) > 0),
            created_at TEXT NOT NULL,
            created_by TEXT NOT NULL,
            PRIMARY KEY (story_id, code)
        )""",
            "CREATE INDEX idx_features_epic ON features(epic_id)",
            "CREATE INDEX idx_stories_feature ON stories(feature_id)",
            "CREATE INDEX idx_story_requirements_req ON story_requirements(requirement_id)",
            "CREATE INDEX idx_epic_requirements_req ON epic_requirements(requirement_id)",
        ),
    ),
)
