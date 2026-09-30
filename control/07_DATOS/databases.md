# Bases de datos (implementado en SPRINT-001, 2026-09-30)

| Base | Ruta | Motor | Propósito | Esquema | Migraciones |
|------|------|-------|-----------|---------|-------------|
| Global | `<ACM_DATA_DIR>/acm.db` | SQLite 3 (WAL) | Principales, registro de proyectos, pertenencias | `acm.db.schema.GLOBAL` v1 | `schema_migrations` |
| Proyecto | `<ACM_DATA_DIR>/projects/<project_id>/project.db` | SQLite 3 (WAL) | Metadatos y configuración del proyecto (y, en el futuro, todo su estado: ADR-011) | `acm.db.schema.PROJECT` v1 | `schema_migrations` |

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

Configuración de conexión: ADR-013. Backups: MISSING (EPIC-40).
