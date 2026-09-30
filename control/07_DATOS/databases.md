# Bases de datos (SPRINT-001; v2 en SPRINT-002, 2026-09-30)

| Base | Ruta | Motor | Propósito | Esquema | Migraciones |
|------|------|-------|-----------|---------|-------------|
| Global | `<ACM_DATA_DIR>/acm.db` | SQLite 3 (WAL) | Principales, registro de proyectos, pertenencias, auditoría MCP | `acm.db.schema.GLOBAL` v2 | `schema_migrations` |
| Proyecto | `<ACM_DATA_DIR>/projects/<project_id>/project.db` | SQLite 3 (WAL) | Metadatos y configuración del proyecto y backlog (y, en el futuro, todo su estado: ADR-011) | `acm.db.schema.PROJECT` v2 | `schema_migrations` |

## Esquema global v1
| Tabla | Columnas | Restricciones |
|-------|----------|---------------|
| `principals` | `id`, `role`, `created_at` | `role IN ('admin','user')`, `length(id) 1..64` |
| `projects` | `id`, `name`, `description`, `created_at`, `created_by`, `db_path` | PK `id`; `name` 1..120; FK `created_by → principals` |
| `project_members` | `project_id`, `principal_id`, `role`, `added_at` | PK compuesta; `role IN ('owner','member')`; FK con `ON DELETE CASCADE` hacia `projects` |

## Esquema de proyecto v1
| Tabla | Columnas | Uso |
|-------|----------|-----|
| `project_meta` | `key`, `value` | `project_id` (comprobado al abrir: la base pertenece a su proyecto), `created_at` |
| `config` | `key`, `value_json`, `updated_at`, `updated_by` | parámetros de US-01.03 |

## Esquema global v2 (SPRINT-002)
| Tabla | Columnas | Restricciones / índices |
|-------|----------|-------------------------|
| `mcp_audit` | `id`, `ts`, `principal`, `operation`, `project_id`, `arguments_json`, `status`, `error`, `result_json`, `result_truncated`, `duration_ms` | `status IN ('ok','error')`; índices por `(principal, id)` y `(project_id, id)`. Retención: sin política (MISSING, EPIC-44). Secretos en argumentos: sin redacción (EPIC-44) |

## Esquema de proyecto v2 (SPRINT-002)
| Tabla | Uso | Restricciones |
|-------|-----|---------------|
| `requirements` | Requisitos `REQ-NNN` | `title` no vacío |
| `epics` | Épicas `EPIC-NN` con objetivo, alcance y confirmación de cobertura (`coverage_confirmed_at/_by`) | — |
| `epic_requirements` | Épica ↔ requisito | FK a ambas |
| `features` | Features `FEAT-NN.MM` | `status IN ('ACTIVE','SPLIT')`; `split_into` con las features resultantes |
| `stories` | Historias `US-NN.MM` de usuario o técnicas | `kind IN ('user_story','technical')`; una técnica exige `technical_reason`; `status` dentro de los estados permitidos |
| `story_requirements` | Historia ↔ requisito (trazabilidad US-03.03) | FK a ambas |
| `acceptance_criteria` | CA `CA-NN` por historia | PK (`story_id`, `code`) |

Configuración de conexión: ADR-013. Backups: MISSING (EPIC-40).
