# Servicios de dominio (backend)

Actualizado: 2026-09-30 (SPRINT-007). Todos son **síncronos** (sqlite3; ADR-013/016): la frontera MCP y la API REST los ejecutan en hilos de trabajo. Todos reciben el `principal` que actúa y lanzan `AcmError` (`classes.md`), nunca excepciones genéricas hacia la frontera. Firmas exactas y líneas: `code_reference.md`.

Grafo de dependencias (sin ciclos):

```text
ProjectService ──► Database, migrate, EventStore
  ├── IdentityService
  ├── AuditService
  ├── EngineRegistry / EngineRouter ──► RulesDecisionEngine, OllamaGenerationEngine
  ├── BacklogService ──► EngineRouter
  │     ├── ContextService ──► EngineRouter
  │     └── WatchdogService ──► EngineRouter
Consumidores: mcp_server.build_mcp_server, web_api.build_api, app.create_app, __main__ (CLI)
```

## `ProjectService` — `src/acm/domain/projects.py`
- **Responsabilidad:** base global (`acm.db`), registro de proyectos y sus bases (`projects/<id>/project.db`), principales, pertenencias, configuración de proyecto, cuarentena por integridad. Expone `global_db`, `events` (`EventStore`) y `project_db(id)` al resto de servicios.
- **API pública:**

| Método | Entrada | Salida | Errores | Efectos |
|--------|---------|--------|---------|---------|
| `ensure_principal(id, role, kind="user")` | id, rol global | — | INVALID_ARGUMENT | alta si no existe |
| `create(principal, key, name, description)` | datos del proyecto | resumen | INVALID_ARGUMENT, FORBIDDEN (no admin), ALREADY_EXISTS, STORAGE_ERROR | directorio + base migrada + registro + owner; evento `project.created`; atómico (limpia si falla) |
| `list_for(principal)` | — | proyectos accesibles | FORBIDDEN (principal desconocido) | — |
| `open(principal, project_id)` | — | metadatos, rol, versión de esquema, configuración | NOT_FOUND | — |
| `get_config` / `set_config(principal, project_id, changes)` | cambios `{parámetro: valor}` | parámetros, `changed`, `requires_reload` | INVALID_ARGUMENT, FORBIDDEN (no owner/admin), NOT_FOUND, DATA_INTEGRITY (cuarentena) | escribe `config`; evento `project.config_changed` |
| `ensure_writable(project_id)` | — | — | DATA_INTEGRITY si `integrity_status = 'corrupt'` | — |
| `project_db(project_id)` | — | `Database` cacheada | — | abre y migra la base si hace falta |
| `system_info()` | — | versión de esquema, nº de proyectos, PRAGMAs | — | — |
| `_principal_role`, `_project_role` | — | rol | FORBIDDEN / NOT_FOUND | uso interno de todos los servicios |
- **Invariantes:** `project_id` = `key` inmutable (`^[a-z][a-z0-9-]{1,39}$`); un proyecto ajeno responde NOT_FOUND (no se revela su existencia); toda escritura de proyecto pasa por `ensure_writable`.

## `BacklogService` — `src/acm/domain/backlog.py`
- **Responsabilidad:** backlog del proyecto (EPIC-03/04, EPIC-06): requisitos `REQ-NNN`, épicas `EPIC-NN`, features `FEAT-NN.MM`, historias `US-NN.MM`, criterios `CA-NN`, gate READY, flujo de estados y su historial, auditoría de huecos.
- **Dependencias:** `ProjectService`, `EngineRouter` (gate READY vía interfaz de decisión, US-35.11).
- **API pública (todas con `principal, project_id` primero):**

| Método | Salida | Errores principales | Efectos (tras COMMIT: evento) |
|--------|--------|---------------------|-------------------------------|
| `create_requirement(title, description, requirement_id?)` | requisito | INVALID_ARGUMENT, ALREADY_EXISTS | `requirement.created` |
| `get_requirement`, `list_requirements`, `trace_requirement(requirement_id)` | requisito / lista / traza (épicas, historias, `orphan`) | NOT_FOUND | — |
| `create_epic(title, objective, scope, requirement_ids?, epic_id?)` | épica con features | INVALID_ARGUMENT, NOT_FOUND (requisito) | `epic.created` |
| `link_epic_requirements`, `confirm_epic_coverage` | épica | FAILED_PRECONDITION (sin features activas) | `epic.updated` |
| `get_epic`, `list_epics` | árbol épica → features → `story_ids` | NOT_FOUND | — |
| `create_feature(epic_id, title, description?, feature_id?)` | feature | NOT_FOUND | `feature.created` |
| `split_feature(feature_id, parts)` | épica + `split_into` | INVALID_ARGUMENT (cada historia en exactamente una parte) | `feature.split` |
| `create_story(feature_id, as_a, i_want, so_that, requirement_ids, acceptance_criteria?, kind, technical_reason, story_id?)` | historia | INVALID_ARGUMENT (técnica sin razón, sin requisito) | `story.created` |
| `add_criteria(story_id, criteria)` | historia | INVALID_ARGUMENT | `story.updated` |
| `get_story`, `list_stories`, `status_history(story_id)` | historia(s) / historial | NOT_FOUND | — |
| `mark_ready(story_id)` | historia en READY | FAILED_PRECONDITION (huecos, no PLANNED, motor no calibrado, cambió durante la decisión) | historial + `story.status_changed` |
| `set_status(story_id, status, reason?)` | historia | INVALID_ARGUMENT, FAILED_PRECONDITION (transición no permitida) | historial + `story.status_changed` |
| `audit()` | huecos de trazabilidad y `clean` | NOT_FOUND | — |
- **Constantes:** `STORY_TRANSITIONS` (flujo; DONE solo desde VERIFIED), `READY_GATE_QUESTIONS` / `READY_GATE_GAPS`.
- **Invariantes:** IDs generados dentro de la transacción; cualquier rol del proyecto escribe; toda escritura comprueba `ensure_writable`; el gate no retiene el bloqueo mientras decide y rechaza si la historia cambió.

## `IdentityService` — `src/acm/domain/identity.py`
- **Responsabilidad:** principales (`user`/`agent`), roles globales y de proyecto, tokens (EPIC-20, ADR-017).

| Método | Quién | Errores | Efectos |
|--------|-------|---------|---------|
| `create_principal(actor, id, kind, role)` | admin | FORBIDDEN, INVALID_ARGUMENT | evento `principal.changed` |
| `get_principal`, `list_principals` | uno mismo / admin | FORBIDDEN, NOT_FOUND | — |
| `set_global_role(actor, id, role)` | admin | FAILED_PRECONDITION (último admin) | evento `principal.changed` |
| `set_member`, `remove_member(actor, project_id, id, role?)` | admin u owner | FAILED_PRECONDITION (último owner), NOT_FOUND | evento `member.changed` |
| `list_members` | miembros | NOT_FOUND | — |
| `create_token(actor, principal_id, name)` | admin | FORBIDDEN, NOT_FOUND | guarda sha256 + prefijo; devuelve el secreto **una vez** |
| `list_tokens`, `revoke_token` | los propios; ajenos, admin | FORBIDDEN, NOT_FOUND | revocación inmediata |
| `authenticate(secret)` | — | UNAUTHENTICATED | anota `last_used_at`/`use_count` |
- **Invariantes:** nunca se guarda ni se devuelve de nuevo el secreto; siempre ≥1 admin y ≥1 owner por proyecto.

## `AuditService` — `src/acm/domain/audit.py`
- **Responsabilidad:** registro de invocaciones (MCP, REST `rest:*`, CLI `cli:*`, rechazos HTTP `http:auth`) y su consulta (US-14.10/11).
- `record(principal, operation, arguments, status, duration_ms, result?, error?, token_id?)`: redacta `token`/`secret`/`password` (`redact`), trunca el resultado a 4000 caracteres con marca. No es atómico con la operación (TD-001).
- `list(principal, limit, filter_principal, operation, project_id)`: solo admin; más recientes primero.

## `ContextService` — `src/acm/domain/context.py`
- **Responsabilidad:** contexto compacto de una historia (US-35.08) y ahorro de tokens (US-35.09).
- `compact(principal, project_id, story_id, budget_tokens?)`: secciones con `sources`; resume las de apoyo con `EngineRouter.generate` si no caben; registra la entrega en `context_deliveries`. Estimación `chars/4@v1`.
- `savings_report(principal, filter_principal?, project_id?)`: solo admin; agregados por agente, proyecto y método.
- **Invariantes:** la historia y sus criterios nunca se resumen; un resumen que no reduce se descarta; sin modelo se entrega sin resumir con motivo.

## `WatchdogService` — `src/acm/domain/watchdog.py`
- **Responsabilidad:** gobernanza (EPIC-13): integridad SQLite, calidad de historias vía interfaz de decisión, estructura, semáforo, histórico, cuarentena, salud por componente.
- `run(principal, project_id, trigger)`, `run_all(principal, trigger)` (admin), `history(principal, project_id, limit)`, `status(principal, project_id)`, `health(principal, catalog)` (admin).
- **Efectos:** actualiza `projects.integrity_*`, inserta en `watchdog_runs`, evento `watchdog.run`, llamadas en `inference_calls`.
- **Invariantes:** no evalúa nada sobre una base corrupta; respuesta no calibrada → REVIEW, nunca WARNING.

## `EngineRegistry` / `EngineRouter` — `src/acm/inference/router.py`
- **Responsabilidad:** motores de inferencia disponibles (US-47.01) y enrutado con fallback (ADR-015).
- `EngineRegistry.register(engine)`, `refresh()` (salud y modelos detectados en `inference_engines`), `list()`, `close()`.
- `EngineRouter.decide(principal, request) → Routed`, `generate(principal, request) → Routed`, `has_generation()`, `calls(principal, …)` (admin).
- **Invariantes:** el motor de reglas siempre está registrado; orden por `decision.engine_order`; cada llamada queda en `inference_calls`; los consumidores nunca importan un motor concreto (test `test_us4701_ca01_*`).

## `EventStore` — `src/acm/events.py`
- **Responsabilidad:** eventos de dominio persistidos (ADR-018): `append(...) → seq`, `after(seq, limit)`, `latest_seq()`, `oldest_seq()`, `prune(keep)`.
- **Invariantes:** se llama después del COMMIT; nunca revierte una operación ya confirmada (fallo → log, TD-003).

## `SkillCatalog` — `src/acm/skills_catalog.py`
- **Responsabilidad:** skills oficiales (EPIC-15): `reload() → cambió`, `entries()`, `get_by_uri(uri)`, `file(name, filename)`, `skills`, `rejected`.
- **Invariantes:** una skill inválida (frontmatter, semver, capacidades, dependencias en cascada, límites SEP-2640) no se sirve.
