# Bases de datos (SPRINT-001; v2 en SPRINT-002; global v3 en SPRINT-003; global v4 en SPRINT-004; global v5 en SPRINT-005; global v6 y proyecto v3 en SPRINT-006, 2026-09-30)

| Base | Ruta | Motor | Propósito | Esquema | Migraciones |
|------|------|-------|-----------|---------|-------------|
| Global | `<ACM_DATA_DIR>/acm.db` | SQLite 3 (WAL) | Principales, registro de proyectos, pertenencias, auditoría MCP, motores y llamadas de inferencia, entregas de contexto, tokens de acceso, Watchdog, eventos | `acm.db.schema.GLOBAL` v6 | `schema_migrations` |
| Proyecto | `<ACM_DATA_DIR>/projects/<project_id>/project.db` | SQLite 3 (WAL) | Metadatos y configuración del proyecto y backlog con historial de estados (y, en el futuro, todo su estado: ADR-011) | `acm.db.schema.PROJECT` v3 | `schema_migrations` |

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

## Esquema global v3 (SPRINT-003)
| Tabla | Uso | Restricciones |
|-------|-----|---------------|
| `inference_engines` | Motores registrados: nombre, tipo, proveedor, endpoint, último estado, detalle, modelos detectados, fecha | PK `name`; `kind IN ('decision','generation')`; `status IN ('unknown','ok','error')` |
| `inference_calls` | Cada llamada de inferencia: principal, proyecto, tipo, propósito, motor, `fallback_from`, estado, error, duración, tokens | `status IN ('ok','error')`; índice `(project_id, id)` |
| `context_deliveries` | Cada entrega de contexto compacto: principal, proyecto, historia, tokens entregados y equivalente completo, método, si se resumió, motor | tokens ≥ 0; índice `(principal, project_id)` |

Retención de `inference_calls` y `context_deliveries`: sin política (MISSING, EPIC-44).

## Esquema global v4 (SPRINT-004)
| Cambio | Detalle |
|--------|---------|
| `principals.kind` | `user` \| `agent` (por defecto `user` para los existentes) |
| `api_tokens` | `id` (`tok_…`), `principal_id`, `name`, `prefix` (12 caracteres), `secret_hash` (sha256, UNIQUE), `created_at/_by`, `revoked_at/_by`, `last_used_at`, `use_count` |
| `mcp_audit.token_id` | Token de la invocación (NULL en stdio y CLI) |

## Esquema global v5 (SPRINT-005)
| Cambio | Detalle |
|--------|---------|
| `projects.integrity_status` / `integrity_detail` / `integrity_checked_at` | `unknown` \| `ok` \| `corrupt`; `corrupt` bloquea las escrituras del proyecto (US-13.11) |
| `watchdog_runs` | Histórico de auditorías: proyecto, fecha, trigger (`manual` \| `scheduled`), principal, semáforo, recuentos por severidad, hallazgos (JSON), motores, duración. Retención: sin política (MISSING, EPIC-44) |

## Esquema global v6 (SPRINT-006)
| Tabla | Uso |
|-------|-----|
| `events` | Eventos de dominio: `seq` (orden total), `ts`, `type`, `project_id`, `principal`, `entity_type`, `entity_id`, `data_json`. Retención: últimos `ACM_EVENTS_KEEP` (ADR-018) |

## Esquema de proyecto v3 (SPRINT-006)
| Tabla | Uso |
|-------|-----|
| `story_status_history` | Cada cambio de estado de una historia: de, a, motivo, quién, cuándo (US-06.02 CA-02) |

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
