# Servidor MCP de ACM

Estado: **IMPLEMENTED (SPRINT-001..005)**. Por HTTP exige token Bearer de ACM (ADR-017). `src/acm/mcp_server.py`: herramientas de proyecto (SPRINT-001), backlog, auditoría y extensión Skills con 3 skills oficiales (SPRINT-002). Pendientes: skills US-15.11/15.12 y autenticación (EPIC-20). Topología: ADR-014. Decisiones: ADR-005 (Python) y ADR-008 (servidor propio + skills). Historias (numeración unificada, ADR-010): servidor propio FEAT-14.02..14.04 (US-14.04..US-14.11); registro y versionado de skills FEAT-15.01 (US-15.01, US-15.03); distribución FEAT-15.02 (US-15.04..US-15.07); catálogo FEAT-15.03 (US-15.08..US-15.12). ACM como *cliente* MCP (US-14.01..14.03) es POST-MVP.

## Principio
El servidor MCP **es ACM**: los agentes IA se conectan a él para operar sobre los proyectos. Al conectarse, reciben las instrucciones y las skills necesarias para usar ACM correctamente.

## Flujo de conexión previsto
1. Conexión → el servidor declara `resources`, `tools` y la extensión `io.modelcontextprotocol/skills` (`directoryRead=false`), y devuelve `instructions` que piden cargar las skills de ACM. `prompts`: por decidir.
2. El agente llama a `skills/list` → recibe el catálogo (`skill://acm/...`) con `digest` y `size` por archivo.
3. El agente descarga cada archivo con `resources/read` (o con `skills/get`).
4. El agente opera mediante herramientas MCP indicando **`project_id` en cada llamada** (US-14.08). No existe "proyecto seleccionado" por sesión (ADR-014, prueba D1).
5. Si el catálogo cambia → notificación de cambio de lista de recursos; el agente compara `digest` y vuelve a descargar lo que haya cambiado.

Clientes sin extensión de skills: herramientas de respaldo `acm_skills_list` y `acm_skill_get` (validadas en el prototipo).

## Catálogo inicial de skills (FEAT-15.03)
| Skill | URI | Historia | Propósito |
|-------|-----|----------|-----------|
| acm-schema | `skill://acm/acm-schema/SKILL.md` | US-15.08 | Modelo de datos y flujo de trabajo de ACM: qué entidades hay, cómo se relacionan y qué herramientas usar en cada paso — IMPLEMENTED v1.0.0 |
| acm-invest | `skill://acm/acm-invest/SKILL.md` | US-15.09 | Validar historias según INVEST y criterios binarios — IMPLEMENTED v1.0.0 |
| acm-discovery | `skill://acm/acm-discovery/SKILL.md` | US-15.10 | Discovery Socrático antes de crear backlog — IMPLEMENTED v1.0.0 |
| acm-error-analysis | `skill://acm/acm-error-analysis/SKILL.md` | US-15.11 | Análisis de errores y causa raíz con registro en ACM — PLANNED (EPIC-29) |
| acm-documentation | `skill://acm/acm-documentation/SKILL.md` | US-15.12 | Documentación viva enlazada a requisitos y evidencias — PLANNED (EPIC-25) |

Frontmatter obligatorio (US-15.01): `name` (= carpeta), `description`, `version` (semver), `capabilities` (lista no vacía), `dependencies` (lista; una dependencia inactiva desactiva en cascada). Ubicación: `src/acm/skills/<nombre>/`, versionadas con el código (US-15.07). Una skill inválida no se sirve. Recarga: `acm_skills_reload` (admin) publica `notifications/resources/list_changed` si el catálogo cambió.

## Límites de la extensión (SEP-2640)
- Hasta 512 recursos y 16 MiB por skill.
- Error `-32602` si la skill no existe; `-32603` para errores internos.

## Seguridad
- Las skills se sirven como contenido de solo lectura.
- No se incluyen scripts ejecutables en el MVP.
- Acceso autenticado (EPIC-20, pendiente). Descargas auditadas (US-14.11/US-15.07 CA-03): `skills/list`, `skills/get` y `resources/read` quedan en `mcp_audit`.

## Resultados de SPIKE-002 (2026-09-30, SDK `mcp` 2.2.0)

| # | Pregunta | Respuesta | Evidencia |
|---|----------|-----------|-----------|
| 1 | ¿El SDK soporta `2026-07-28` y la extensión Skills? | Soporta y negocia `2026-07-28`. **No trae** la extensión Skills, pero su API `Extension` (métodos, recursos y ajustes propios) permite implementarla: `skills/list`, `skills/get`, recursos `skill://acm/...` con digest sha256, error `-32602` para skill inexistente. | `test_proto.py` 11/11 PASS |
| 2 | ¿Transporte y convivencia con API y WebSocket? | Streamable HTTP montado en `/mcp` de una app Starlette junto a `/api/health` y `/ws`, en un solo proceso uvicorn (el `session_manager.run()` del SDK se arranca en el lifespan de la app). stdio también funciona con el mismo servidor. Una herramienta MCP publicó un evento que recibió el WebSocket. | `test_asgi_topology.py` 4/4, `test_proto.py` (stdio) |
| 3 | ¿Aislamiento multi-proyecto por sesión? | Con `2026-07-28` cada petición HTTP es autocontenida: el servidor **no conservó** el proyecto seleccionado entre dos llamadas del mismo cliente (el `ctx.session` era distinto en cada una). El proyecto explícito en cada llamada, validado contra el alcance del llamante, aísla y rechaza el acceso cruzado. | `test_session_isolation.py` 3/3 |
| 4 | ¿Qué clientes cargan automáticamente las skills servidas? | **UNKNOWN.** No verificable en este entorno. Mitigación: `instructions` + herramientas de respaldo. | — |

Hallazgo adicional: el SDK devuelve al agente "Error executing tool …" ante excepciones genéricas y oculta el motivo (GAP-007). El producto debe emitir errores de herramienta con mensaje explícito.

## Fuentes
- https://github.com/modelcontextprotocol/ext-skills (especificación estable `skills.mdx`)
- https://modelcontextprotocol.io/seps/2640-skills-extension
- https://devblogs.microsoft.com/agent-framework/discover-agent-skills-from-mcp-servers-in-net/

## Herramientas implementadas (SPRINT-001, 2026-09-30)

| Herramienta | Argumentos | Devuelve | Errores (`CODE: motivo`) | Historia |
|-------------|------------|----------|--------------------------|----------|
| `acm_project_create` | `key`, `name`, `description?` | resumen con `project_id` | INVALID_ARGUMENT (`key`/`name`), ALREADY_EXISTS, FORBIDDEN, STORAGE_ERROR | US-01.01 |
| `acm_project_list` | — | lista de proyectos accesibles | FORBIDDEN (principal desconocido) | US-01.02 |
| `acm_project_open` | `project_id` | metadatos, `role`, `schema_version`, `config` | INVALID_ARGUMENT, NOT_FOUND | US-01.02, US-01.06 |
| `acm_project_config_get` | `project_id` | `parameters` con valor, defecto, permitido, recarga | NOT_FOUND | US-01.03 |
| `acm_project_config_set` | `project_id`, `changes` | `parameters`, `changed`, `requires_reload` | INVALID_ARGUMENT (parámetro), FORBIDDEN, NOT_FOUND | US-01.03 |
| `acm_system_info` | — | versión, versión de esquema global, nº de proyectos, PRAGMAs | STORAGE_ERROR | US-18.03 CA-04 |

Transportes: Streamable HTTP en `/mcp/` (`acm serve`) y stdio (`acm mcp-stdio`). Identidad: `ACM_PRINCIPAL` hasta EPIC-20.
GAP-007 mitigado: los errores de dominio se convierten en `ToolError` y el agente recibe `Error executing tool <x>: CODE: motivo`.

## Herramientas añadidas en SPRINT-002 (2026-09-30)

Todas las de proyecto exigen `project_id` y lo devuelven. Cualquier rol del proyecto (owner, member) y los admin pueden escribir el backlog; un proyecto no accesible responde `NOT_FOUND`. Toda invocación (herramientas, `skills/list`, `skills/get`, `resources/read`) se registra en `mcp_audit`.

| Herramienta | Argumentos principales | Errores | Historia |
|-------------|------------------------|---------|----------|
| `acm_skills_list` | — | — | US-15.05 CA-03 |
| `acm_skill_get` | `name` | NOT_FOUND | US-15.05 CA-03 |
| `acm_skills_reload` | — | FORBIDDEN (no admin) | US-15.06, US-15.07 |
| `acm_audit_list` | `limit` (1..500), `principal_id?`, `operation?`, `project_id?` | FORBIDDEN (no admin), INVALID_ARGUMENT | US-14.10 |
| `acm_requirement_create` / `_list` / `_trace` | `title`, `description?`, `requirement_id?` / — / `requirement_id` | INVALID_ARGUMENT, ALREADY_EXISTS, NOT_FOUND | US-03.03 |
| `acm_epic_create` / `_link_requirements` / `_get` / `_list` / `_confirm_coverage` | `title`, `objective`, `scope`, `requirement_ids?`, `epic_id?` | INVALID_ARGUMENT, NOT_FOUND, FAILED_PRECONDITION (sin features activas) | US-04.01, US-04.02 |
| `acm_feature_create` / `_split` | `epic_id`, `title` / `feature_id`, `parts` (≥2, cada historia en una sola parte) | INVALID_ARGUMENT, NOT_FOUND, FAILED_PRECONDITION | US-04.02 |
| `acm_story_create` / `_add_criteria` / `_get` / `_mark_ready` | `feature_id`, `as_a`, `i_want`, `so_that`, `requirement_ids` (≥1), `acceptance_criteria?`, `kind`, `technical_reason` | INVALID_ARGUMENT, NOT_FOUND, FAILED_PRECONDITION (lista de huecos) | US-04.03 |
| `acm_backlog_audit` | — | NOT_FOUND | US-03.03, US-04.03 |

## Herramientas añadidas en SPRINT-003 (2026-09-30) — segundo cerebro

| Herramienta | Argumentos | Devuelve | Errores | Historia |
|-------------|------------|----------|---------|----------|
| `acm_decide` | `project_id`, `purpose`, `questions` ({clave: {type, instructions, criteria}}), `state` | `answers` tipadas (`value`, `probabilities`, `confidence`, `calibrated`), `engine`, `usage`, `fallback_from`, `call_id` | INVALID_ARGUMENT, NOT_FOUND, ENGINE_UNAVAILABLE | US-35.10 |
| `acm_context_compact` | `project_id`, `story_id`, `budget_tokens?` (64..200000; por defecto `context.max_tokens`) | `sections` con `sources`, `delivered_tokens`, `full_equivalent_tokens`, `saved_tokens`, `estimation_method`, `summarized`, `not_summarized_reason`, `delivery_id` | INVALID_ARGUMENT, NOT_FOUND | US-35.08 |
| `acm_engines_list` | — | motores (estado, modelos detectados, `registered`) y catálogo de reglas | — | US-47.01, US-22.01 |
| `acm_engines_refresh` | — | motores tras comprobar su salud | FORBIDDEN (no admin) | US-22.01 |
| `acm_savings_report` | `principal_id?`, `project_id?` | grupos por agente/proyecto/método y totales | FORBIDDEN (no admin), INVALID_ARGUMENT | US-35.09 |

## Herramientas añadidas en SPRINT-004 (2026-09-30) — identidad

| Herramienta | Argumentos | Quién | Historia |
|-------------|------------|-------|----------|
| `acm_whoami` | — | cualquiera | US-20.03 CA-01 |
| `acm_principal_create` | `principal_id`, `kind` (user/agent), `role?` | admin | US-20.04 |
| `acm_principal_list` | — | admin | US-20.01 CA-01 |
| `acm_principal_set_role` | `principal_id`, `role` | admin | US-20.01 |
| `acm_member_set` / `acm_member_remove` / `acm_member_list` | `project_id`, `principal_id`, `role` | admin/owner (listar: miembros) | US-20.01, US-20.08 |
| `acm_token_create` | `principal_id`, `name` | admin | US-20.03 (el secreto solo en esta respuesta) |
| `acm_token_list` / `acm_token_revoke` | `principal_id?` / `token_id` | propios; ajenos, admin | US-20.03 |

Errores nuevos: `UNAUTHENTICATED` (HTTP 401, antes de llegar a MCP).

## Herramientas añadidas en SPRINT-005 (2026-09-30) — Watchdog

| Herramienta | Argumentos | Devuelve | Quién | Historia |
|-------------|------------|----------|-------|----------|
| `acm_watchdog_run` | `project_id` | `run_id`, `semaphore`, `integrity`, `counts`, `engines`, `findings` [{code, severity, target, message, source}] | miembros del proyecto | US-13.12 |
| `acm_watchdog_history` | `project_id`, `limit?` (1..200) | `runs` de la más reciente a la más antigua, con hallazgos | miembros | US-13.13 |
| `acm_governance_status` | `project_id` | `semaphore` (o `UNKNOWN`), `last_run`, `integrity`, `writable` | miembros | US-13.10 |
| `acm_health` | — | `status`, `checked_at`, `components` [{name, kind, status, detail}] | admin | US-13.03 |

Error nuevo: `DATA_INTEGRITY` en escrituras sobre un proyecto en cuarentena (US-13.11). Total: 44 herramientas.

Extensión Skills: `skills/list` y `skills/get` (`-32602` si la skill no existe); archivos en `skill://acm/{skill}/{filename}` (una skill retirada deja de ser legible). Capacidad declarada: `extensions["io.modelcontextprotocol/skills"] = {"directoryRead": false}`.
