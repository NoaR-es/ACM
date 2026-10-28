<!-- GENERADO por control/tools/code_inventory.py a partir del código. No editar a mano: cambia el código (y sus docstrings) y regenera. -->

# Referencia de código (generada)

104 archivos. Documentación narrativa (responsabilidades, invariantes, efectos): `modules.md`, `services.md`, `classes.md`, `functions.md`, `components.md`, `hooks.md`, `frontend.md`, `tests.md`.

## Backend (`src/acm`)

### `src/acm/__init__.py`

ACM — Agile Context Manager.

### `src/acm/__main__.py`

CLI de ACM.

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| función | `main(argv)` | 23 |  |
| función | `_run_stdio(settings)` | 72 | Servidor MCP por stdio. Con `ACM_PRINCIPAL` explícito, una única identidad admin (comportamiento anterior). |
| función | `_admin_command(args)` | 96 |  |

### `src/acm/app.py`

Composición del proceso ACM (ADR-014): FastAPI con `/api` y el servidor MCP montado en `/mcp`.

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| función | `build_service(settings)` | 38 |  |
| función | `build_engines(service, settings)` | 45 | Router de inferencia (ADR-015). Reglas siempre. JEV (Ollaya) si hay `ACM_JEV_URL`: decisiones calibradas. |
| constante | `LOCAL_HOSTS` | 69 | |
| función | `transport_security(settings)` | 73 | Protección contra DNS rebinding del SDK MCP: solo se aceptan los Host locales y los de `ACM_ALLOWED_HOSTS`. |
| función | `async scheduled_watchdog(watchdog, settings)` | 85 | US-13.06: audita todos los proyectos cada `ACM_WATCHDOG_INTERVAL_S` segundos como el admin local. |
| función | `_local_session_token(service, settings)` | 95 | Token efímero del admin local para la interfaz del propio equipo. Cada arranque revoca los anteriores. |
| función | `async prune_events(service, settings)` | 105 | ADR-018: conserva los últimos `ACM_EVENTS_KEEP` eventos; un cliente más atrasado recibe `resync`. |
| función | `create_app(settings)` | 115 |  |

Rutas (2, relativas a su montaje):

| Método | Ruta | Función | Línea | Descripción |
|--------|------|---------|-------|-------------|
| GET | `/api/health` | `health` | 147 | Salud básica: versión y PRAGMAs de la base global (ADR-013: foreign_keys activo). |
| GET | `/api/local-session` | `local_session` | 154 | US-14.12 CA-04: la interfaz de este equipo obtiene su token sin que la persona lo pegue (solo modo local). |

### `src/acm/auth.py`

Autenticación HTTP de ACM (EPIC-20, ADR-017).

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `ANONYMOUS` | 26 | |
| función | `request_principal()` | 29 | Principal de la petición HTTP en curso. Fuera de una petición autenticada no hay identidad. |
| función | `request_token()` | 37 |  |
| clase | `BearerAuth` (—) | 41 |  |
| método | `BearerAuth.__init__(app, identity, audit)` | 42 |  |
| función | `async _reject(send, exc)` | 78 |  |

### `src/acm/config.py`

Configuración de proceso de ACM (variables de entorno).

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `DEFAULT_HOST` | 12 | |
| constante | `DEFAULT_PORT` | 13 | |
| función | `default_data_dir()` | 16 | US-14.12: un único estado por usuario, sea cual sea la carpeta desde la que se abra el agente. |
| clase | `Settings` (—) | 22 |  |
| método | `Settings.from_env(**overrides)` | 45 |  |

### `src/acm/db/__init__.py`

Acceso a SQLite según ADR-013.

### `src/acm/db/connection.py`

Conexiones y transacciones SQLite según ADR-013 (evidencia: SPIKE-001).

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `SYNCHRONOUS_MODES` | 23 | |
| constante | `RETRY_DELAYS_S` | 25 | |
| clase | `NestedTransactionError` (RuntimeError) | 28 | Se intentó abrir `write()` dentro de otra transacción en la misma conexión (error de programación). |
| función | `_is_lock_error(exc)` | 32 |  |
| clase | `Database` (—) | 37 |  |
| método | `Database.__init__(path, *, synchronous, busy_timeout_ms)` | 38 |  |
| método | `Database.set_synchronous(mode)` | 48 | Afecta a las conexiones que se abran a partir de ahora (parámetro con recarga, US-01.03). |
| método | `Database.connection()` | 54 |  |
| método | `Database.pragmas()` | 102 |  |
| método | `Database.write()` | 113 | Transacción de escritura: BEGIN IMMEDIATE → COMMIT, o ROLLBACK ante cualquier excepción. |
| método | `Database.read()` | 144 | Lecturas en autocommit: en WAL no bloquean ni son bloqueadas por un escritor (SPIKE-001 E2). |
| método | `Database.close()` | 149 |  |

### `src/acm/db/migrations.py`

Migrador de esquema versionado (US-18.03, TECH-007).

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| clase | `Migration` (—) | 24 |  |
| función | `validate_catalog(catalog)` | 30 |  |
| función | `current_version(db)` | 39 |  |
| función | `migrate(db, catalog)` | 47 | Aplica en orden las migraciones pendientes y devuelve las versiones aplicadas. |

### `src/acm/db/schema.py`

Catálogos de migraciones de ACM (ADR-011: SQLite es la fuente de verdad del producto; ADR-013).

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `GLOBAL` | 16 | |
| constante | `PROJECT` | 248 | |

### `src/acm/domain/__init__.py`

_(sin docstring de módulo)_

### `src/acm/domain/access.py`

Unirse a proyectos con aprobación de una persona (FEAT-14.06: US-14.14, US-14.15; ADR-024).

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `ACCESS_LEVELS` | 20 | |
| constante | `GRANTABLE_ROLES` | 21 | |
| constante | `MESSAGE_MAX` | 22 | |
| función | `_now()` | 25 |  |
| función | `_not_member(request)` | 29 | Una petición APROBADA de quien ya no es miembro es una retirada: el agente no debe creer que aún tiene acceso. |
| función | `_request(row)` | 36 |  |
| clase | `AccessService` (—) | 51 |  |
| método | `AccessService.__init__(projects)` | 52 |  |
| método | `AccessService.directory(principal)` | 56 | Proyectos que el principal puede ver, con su pertenencia y su última petición (US-14.14 CA-01). |
| método | `AccessService.request_join(principal, project_id, access, message)` | 99 | US-14.14 CA-03: petición pendiente; si ya es miembro o ya hay una pendiente, la devuelve sin duplicarla. |
| método | `AccessService.join_status(principal, project_id)` | 138 | US-14.14 CA-04: estado de la última petición del principal (o MEMBER si ya está dentro). |
| método | `AccessService.list_requests(actor, status)` | 182 | US-14.15 CA-01: peticiones que el actor puede decidir (admin: todas; owner: las de sus proyectos). |
| método | `AccessService.decide(actor, request_id, approve, role)` | 209 | US-14.15 CA-02/CA-03: aprobar (con rol member o viewer) o rechazar una petición pendiente. |

### `src/acm/domain/audit.py`

Auditoría de invocaciones MCP (US-14.10, US-14.11; US-15.07 CA-03 para descargas de skills).

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `RESULT_MAX_CHARS` | 16 | |
| constante | `LIST_MAX` | 17 | |
| constante | `SECRET_KEYS` | 20 | |
| constante | `REDACTED` | 21 | |
| función | `_json(value)` | 24 |  |
| función | `redact(value)` | 28 | Sustituye el valor de las claves secretas (p. ej. el token recién creado) antes de auditar (ADR-017). |
| clase | `AuditService` (—) | 37 |  |
| método | `AuditService.__init__(projects)` | 38 |  |
| método | `AuditService.record(*, principal, operation, arguments, status, duration_ms, result, error, token_id)` | 41 |  |
| método | `AuditService.list(principal, *, limit, filter_principal, operation, project_id)` | 76 | US-14.10: el operador consulta qué invocó cada agente. Solo principales con rol global admin. |

### `src/acm/domain/backlog.py`

Backlog del proyecto: requisitos, épicas, features, historias y criterios de aceptación.

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| función | `_holder(row)` | 26 | Quién tiene un trabajo asignado: el principal y, si hay, su sesión (`claude-code.portatil#3f9a`). |
| constante | `READY_GATE_QUESTIONS` | 32 | |
| constante | `STORY_TRANSITIONS` | 40 | |
| constante | `STORY_STATUSES` | 53 | |
| constante | `READY_GATE_GAPS` | 55 | |
| constante | `REQ_RE` | 62 | |
| constante | `EPIC_RE` | 63 | |
| constante | `FEAT_RE` | 64 | |
| constante | `US_RE` | 65 | |
| constante | `TITLE_MAX` | 66 | |
| constante | `KINDS` | 67 | |
| función | `_now()` | 70 |  |
| función | `_text(value, field, *, required, max_len)` | 74 |  |
| función | `_id_list(value, field, pattern)` | 87 |  |
| función | `_num(n)` | 97 |  |
| clase | `BacklogService` (—) | 101 |  |
| método | `BacklogService.__init__(projects, decisions)` | 102 |  |
| método | `BacklogService.create_requirement(principal, project_id, title, description, requirement_id)` | 143 |  |
| método | `BacklogService.get_requirement(principal, project_id, requirement_id)` | 167 |  |
| método | `BacklogService.list_requirements(principal, project_id)` | 172 |  |
| método | `BacklogService.trace_requirement(principal, project_id, requirement_id)` | 177 | US-03.03: requisito → épicas → features → historias, y las historias que lo implementan. |
| método | `BacklogService.create_epic(principal, project_id, title, objective, scope, requirement_ids, epic_id)` | 203 |  |
| método | `BacklogService.link_epic_requirements(principal, project_id, epic_id, requirement_ids)` | 234 |  |
| método | `BacklogService.get_epic(principal, project_id, epic_id)` | 272 |  |
| método | `BacklogService.list_epics(principal, project_id)` | 276 |  |
| método | `BacklogService.confirm_epic_coverage(principal, project_id, epic_id)` | 281 | US-04.02 CA-03: el Product Owner confirma que las features activas cubren el objetivo de la épica. |
| método | `BacklogService.create_feature(principal, project_id, epic_id, title, description, feature_id)` | 300 |  |
| método | `BacklogService.split_feature(principal, project_id, feature_id, parts)` | 340 | US-04.02 CA-04: divide una feature en ≥2 features nuevas repartiendo todas sus historias. |
| método | `BacklogService.create_story(principal, project_id, feature_id, as_a, i_want, so_that, requirement_ids, acceptance_criteria, kind, technical_reason, story_id)` | 388 |  |
| método | `BacklogService.add_criteria(principal, project_id, story_id, criteria)` | 467 |  |
| método | `BacklogService.get_story(principal, project_id, story_id)` | 504 |  |
| método | `BacklogService.mark_ready(principal, project_id, story_id)` | 508 | US-04.03 CA-04: una historia incompleta no puede pasar a READY. |
| método | `BacklogService.set_status(principal, project_id, story_id, status, reason)` | 576 | US-06.02: mueve una historia a otro estado si la transición está permitida (`STORY_TRANSITIONS`). |
| método | `BacklogService.list_stories(principal, project_id)` | 610 | Todas las historias con sus requisitos y criterios (vista completa para la interfaz y el Kanban). |
| método | `BacklogService.status_history(principal, project_id, story_id)` | 616 |  |
| método | `BacklogService.audit(principal, project_id)` | 627 | Huecos de trazabilidad del backlog (US-03.03 CA-05 y verificación de estructura). |

### `src/acm/domain/chat.py`

Conversación con el modelo local y agente interno de Ollama (US-22.10, US-22.11).

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `PURPOSE` | 33 | |
| constante | `CHAT_PROMPT_VERSION` | 34 | |
| constante | `MAX_TOOL_ROUNDS` | 35 | |
| constante | `HISTORY_MAX` | 36 | |
| constante | `MESSAGE_MAX` | 37 | |
| constante | `TOOL_RESULT_MAX` | 38 | |
| constante | `REPLY_MAX_TOKENS` | 39 | |
| constante | `SYSTEM_PROMPT` | 40 | |
| función | `_fn(name, description, properties, required)` | 51 |  |
| constante | `STORY_ID` | 64 | |
| constante | `TOOLS` | 65 | |
| constante | `TOOL_NAMES` | 94 | |
| función | `_now()` | 97 |  |
| clase | `ChatService` (—) | 101 |  |
| método | `ChatService.__init__(projects, backlog, engines)` | 102 |  |
| método | `ChatService.threads(principal, project_id)` | 224 |  |
| método | `ChatService.get(principal, project_id, thread_id)` | 234 |  |
| método | `ChatService.send(principal, project_id, message, thread_id, title)` | 256 |  |

### `src/acm/domain/config_schema.py`

Esquema de configuración de proyecto, versión 1 (US-01.03; tabla en `refinements/US-01.03.md`).

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `DECISION_ENGINES` | 11 | |
| clase | `Parameter` (—) | 15 |  |
| método | `Parameter.describe(current)` | 25 |  |
| función | `_enum(*options)` | 38 |  |
| función | `_int_range(lo, hi)` | 45 |  |
| función | `_engine_order(value)` | 54 |  |
| constante | `PARAMETERS` | 64 | |
| función | `validate_changes(changes)` | 152 | Valida todos los cambios antes de guardar ninguno (CA-02). Lanza InvalidArgument con el primer error. |
| función | `check_stored(key, value)` | 166 | Valida un valor leído de la base: un valor corrupto es un error de integridad, no se ignora. |

### `src/acm/domain/context.py`

Segundo cerebro: contexto compacto de una historia y ahorro de tokens (US-35.08, US-35.09; ADR-012, ADR-015 §5).

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `ESTIMATION_METHOD` | 28 | |
| constante | `BUDGET_RANGE` | 29 | |
| constante | `SUMMARIZABLE` | 30 | |
| función | `estimate_tokens(value)` | 33 |  |
| función | `_section(name, content, sources)` | 38 |  |
| clase | `ContextService` (—) | 42 |  |
| método | `ContextService.__init__(projects, backlog, engines)` | 43 |  |
| método | `ContextService.compact(principal, project_id, story_id, budget_tokens)` | 93 |  |
| método | `ContextService.savings_report(principal, *, filter_principal, project_id)` | 188 |  |

### `src/acm/domain/errors.py`

Errores de dominio de ACM.

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| clase | `AcmError` (Exception) | 10 |  |
| método | `AcmError.__init__(message, *, field)` | 13 |  |
| clase | `InvalidArgument` (AcmError) | 23 |  |
| clase | `NotFound` (AcmError) | 27 |  |
| clase | `AlreadyExists` (AcmError) | 31 |  |
| clase | `Forbidden` (AcmError) | 35 |  |
| clase | `StorageError` (AcmError) | 39 |  |
| clase | `DataIntegrityError` (AcmError) | 43 |  |
| clase | `MigrationError` (AcmError) | 47 |  |
| clase | `FailedPrecondition` (AcmError) | 51 |  |
| clase | `Unauthenticated` (AcmError) | 55 | Credencial ausente, desconocida o revocada (EPIC-20). |

### `src/acm/domain/identity.py`

Identidad, roles y tokens (EPIC-20; ADR-017).

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `PRINCIPAL_RE` | 24 | |
| constante | `PRINCIPAL_KINDS` | 25 | |
| constante | `PROJECT_ROLES` | 26 | |
| constante | `TOKEN_PREFIX` | 27 | |
| constante | `PREFIX_SHOWN` | 28 | |
| función | `_now()` | 31 |  |
| función | `hash_secret(secret)` | 35 |  |
| función | `_choice(value, options, field)` | 40 |  |
| función | `_principal_id(value, field)` | 46 |  |
| clase | `IdentityService` (—) | 52 |  |
| método | `IdentityService.__init__(projects)` | 53 |  |
| método | `IdentityService.create_principal(actor, principal_id, kind, role)` | 79 |  |
| método | `IdentityService.get_principal(actor, principal_id)` | 100 |  |
| método | `IdentityService.list_principals(actor)` | 117 |  |
| método | `IdentityService.set_global_role(actor, principal_id, role)` | 126 |  |
| método | `IdentityService.set_member(actor, project_id, principal_id, role)` | 143 |  |
| método | `IdentityService.remove_member(actor, project_id, principal_id)` | 169 |  |
| método | `IdentityService.list_members(actor, project_id)` | 201 |  |
| método | `IdentityService.create_token(actor, principal_id, name)` | 212 |  |
| método | `IdentityService.list_tokens(actor, principal_id)` | 240 |  |
| método | `IdentityService.revoke_token(actor, token_id)` | 256 |  |
| método | `IdentityService.authenticate(secret)` | 271 | Devuelve (principal_id, token_id) o lanza UNAUTHENTICATED. Se consulta en cada petición: revocar es |

### `src/acm/domain/models.py`

Catálogo y selección de modelos (US-50.09, US-50.10, US-22.06, US-22.07).

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `KNOWN_PURPOSES` | 21 | |
| constante | `USAGE` | 29 | |
| clase | `ModelService` (—) | 44 |  |
| método | `ModelService.__init__(projects, engines)` | 45 |  |
| método | `ModelService.catalog(principal)` | 70 |  |
| método | `ModelService.select(principal, *, ollama_model, jev_default_model, jev_models_by_purpose, jev_model_notes)` | 113 |  |

### `src/acm/domain/projects.py`

Servicio de proyectos: crear, listar, abrir y configurar (US-01.01, US-01.02, US-01.03, US-01.06).

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `KEY_RE` | 28 | |
| constante | `NAME_MAX` | 29 | |
| constante | `GLOBAL_ROLES` | 30 | |
| función | `_now()` | 33 |  |
| función | `validate_project_id(value, field)` | 37 |  |
| clase | `ProjectService` (—) | 45 |  |
| método | `ProjectService.__init__(data_dir, *, synchronous, local_mode)` | 46 |  |
| método | `ProjectService.close()` | 61 |  |
| método | `ProjectService.ensure_principal(principal_id, role, kind)` | 69 |  |
| método | `ProjectService.principal_kind(principal_id)` | 84 | `user` (persona) o `agent`; FORBIDDEN si el principal no existe. |
| método | `ProjectService.create(principal_id, key, name, description)` | 108 |  |
| método | `ProjectService.list_for(principal_id)` | 205 |  |
| método | `ProjectService.project_db(project_id)` | 219 |  |
| método | `ProjectService.open(principal_id, project_id)` | 238 |  |
| método | `ProjectService.get_config(principal_id, project_id)` | 259 |  |
| método | `ProjectService.set_config(principal_id, project_id, changes)` | 263 |  |
| método | `ProjectService.ensure_writable(project_id)` | 299 | US-13.11: un proyecto con la integridad comprometida no admite escrituras hasta que el Watchdog la |
| método | `ProjectService.system_info()` | 313 |  |

### `src/acm/domain/sprints.py`

Sprints del proyecto (EPIC-05: US-05.02..05.09).

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `SPRINT_RE` | 27 | |
| constante | `SPRINT_STATUSES` | 28 | |
| constante | `OPEN` | 29 | |
| constante | `TERMINAL_STORY` | 30 | |
| constante | `CAPACITY_MAX` | 31 | |
| función | `_now()` | 34 |  |
| función | `_date(value, field)` | 38 |  |
| función | `_text(value, field, max_len)` | 47 |  |
| clase | `SprintService` (—) | 55 |  |
| método | `SprintService.__init__(backlog)` | 56 |  |
| método | `SprintService.get(principal, project_id, sprint_id)` | 83 |  |
| método | `SprintService.list(principal, project_id)` | 87 |  |
| método | `SprintService.create(principal, project_id, name, goal, start_date, end_date, capacity)` | 93 |  |
| método | `SprintService.add_stories(principal, project_id, sprint_id, story_ids)` | 124 |  |
| método | `SprintService.remove_story(principal, project_id, sprint_id, story_id)` | 165 |  |
| método | `SprintService.start(principal, project_id, sprint_id, force)` | 180 |  |
| método | `SprintService.close(principal, project_id, sprint_id, carry_over_to)` | 205 |  |
| método | `SprintService.cancel(principal, project_id, sprint_id)` | 279 |  |

### `src/acm/domain/supervisor.py`

Supervisor ágil autónomo (SPRINT-008): ACM usa sus propios motores para vigilar el trabajo de cada proyecto.

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `SUPERVISOR` | 36 | |
| constante | `STORY_REVIEW` | 37 | |
| constante | `SPRINT_REVIEW` | 38 | |
| constante | `REPORT` | 39 | |
| constante | `REVIEWABLE` | 40 | |
| constante | `SAFE_ACTIONS` | 41 | |
| constante | `REPORT_MAX_TOKENS` | 42 | |
| constante | `STORY_REVIEW_QUESTIONS` | 44 | |
| constante | `SPRINT_RISK_QUESTIONS` | 65 | |
| constante | `REPORT_SYSTEM_PROMPT` | 72 | |
| constante | `REPORT_PROMPT_VERSION` | 77 | |
| función | `_now()` | 80 |  |
| función | `_finding(code, severity, target, message, source, **extra)` | 84 |  |
| función | `_judgement(answer)` | 88 | (¿respuesta afirmativa?, confianza) de una respuesta `noul` guardada; confianza solo si está calibrada. |
| función | `_choice_confidence(answer)` | 94 |  |
| clase | `AgileSupervisor` (—) | 103 |  |
| método | `AgileSupervisor.__init__(projects, backlog, engines)` | 104 |  |
| método | `AgileSupervisor.run(project_id)` | 550 |  |

### `src/acm/domain/watchdog.py`

Watchdog de gobernanza (EPIC-13).

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `SEVERITIES` | 34 | |
| constante | `INACTIVE_STORY` | 35 | |
| constante | `HISTORY_MAX` | 36 | |
| constante | `STORY_FINDINGS` | 38 | |
| constante | `STRUCTURE_FINDINGS` | 44 | |
| función | `_now()` | 51 |  |
| función | `_finding(code, severity, target, message, source, **extra)` | 55 |  |
| función | `semaphore(findings)` | 59 |  |
| clase | `WatchdogService` (—) | 68 |  |
| método | `WatchdogService.__init__(projects, backlog, engines)` | 69 |  |
| método | `WatchdogService.run(principal, project_id, trigger)` | 151 |  |
| método | `WatchdogService.run_all(principal, trigger)` | 226 | US-13.06: audita todos los proyectos. Un fallo en uno no detiene a los demás. |
| método | `WatchdogService.history(principal, project_id, limit)` | 242 |  |
| método | `WatchdogService.status(principal, project_id)` | 260 | Indicadores de gobernanza del proyecto: semáforo y recuentos de la última ejecución. |
| método | `WatchdogService.health(principal, catalog)` | 282 | Estado de cada componente, recalculado en cada llamada (CA-04). |

### `src/acm/domain/work.py`

Colaboración de agentes en un proyecto: ACM reparte el trabajo (FEAT-14.07: US-14.16, US-14.17; ADR-025).

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `SPRINT_PLANNING` | 32 | |
| constante | `SPRINT_CLOSING` | 33 | |
| constante | `BACKLOG` | 34 | |
| constante | `TERMINAL` | 35 | |
| constante | `STEPS` | 37 | |
| función | `_now()` | 71 |  |
| clase | `WorkService` (—) | 75 |  |
| método | `WorkService.__init__(backlog)` | 76 |  |
| método | `WorkService.next_work(principal, project_id, claim)` | 165 | US-14.16 CA-01/CA-02: lo siguiente que toca, asignado al agente que lo pide. |
| método | `WorkService.release(principal, project_id, item)` | 242 | US-14.17 CA-02: el agente libera su trabajo; una persona puede liberar cualquiera. |
| método | `WorkService.claims(principal, project_id)` | 263 | US-14.17 CA-03: quién trabaja en qué ahora mismo (las caducadas no aparecen). |

### `src/acm/events.py`

Eventos de dominio de ACM (EPIC-21, ADR-018).

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `ADMIN_ONLY_TYPES` | 23 | |
| constante | `REPLAY_MAX` | 24 | |
| clase | `EventStore` (—) | 27 |  |
| método | `EventStore.__init__(db)` | 28 |  |
| método | `EventStore.append(type, *, principal, entity_type, entity_id, project_id, data)` | 31 |  |
| método | `EventStore.latest_seq()` | 61 |  |
| método | `EventStore.after(seq, limit)` | 65 | Eventos con `seq` mayor que el dado, en orden (sin filtrar por visibilidad). |
| método | `EventStore.oldest_seq()` | 71 |  |
| método | `EventStore.prune(keep)` | 75 | Conserva los `keep` eventos más recientes. Un cliente que se quedó atrás recibe `resync` (US-21.03). |

### `src/acm/inference/__init__.py`

Inferencia de ACM: puertos de decisión y generación, motores y router (ADR-015, ADR-016).

### `src/acm/inference/jev.py`

Adaptador JEV (EPIC-50; ADR-006, ADR-015): modelos de decisión servidos por Ollaya.

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `DEFAULT_TIMEOUT_S` | 37 | |
| constante | `KEEP_ALIVE` | 38 | |
| clase | `OllayaClient` (—) | 41 |  |
| método | `OllayaClient.__init__(base_url, *, api_key, timeout_s, transport)` | 42 |  |
| método | `OllayaClient.close()` | 54 |  |
| método | `OllayaClient.list_models()` | 77 |  |
| método | `OllayaClient.list_details()` | 84 | Modelos instalados con sus detalles (familia, formato…), para el catálogo (US-50.09). |
| método | `OllayaClient.decide(model, state, questions)` | 98 |  |
| función | `model_installed(model, installed)` | 103 | `laya` equivale a `laya:latest`, como en Ollama/Ollaya; con etiqueta explícita, coincidencia exacta. |
| función | `_question_json(q)` | 109 |  |
| función | `_probabilities(raw, where)` | 116 |  |
| función | `_confidence(raw)` | 122 |  |
| función | `parse_answer(key, q, raw)` | 126 | Traduce una respuesta de Ollaya al `Answer` de ACM; cualquier forma inesperada es ENGINE_ERROR. |
| clase | `JevDecisionEngine` (—) | 158 | `DecisionEngine` sobre Ollaya. Responde cualquier propósito con el modelo que le toque: el que pide el agente |
| método | `JevDecisionEngine.__init__(client, model)` | 164 |  |
| método | `JevDecisionEngine.model_for(purpose)` | 169 |  |
| método | `JevDecisionEngine.model()` | 173 |  |
| método | `JevDecisionEngine.name()` | 177 |  |
| método | `JevDecisionEngine.close()` | 180 |  |
| método | `JevDecisionEngine.supports(request)` | 183 |  |
| método | `JevDecisionEngine.health()` | 186 |  |
| método | `JevDecisionEngine.decide(request)` | 199 |  |

### `src/acm/inference/ollama.py`

Adaptador Ollama (EPIC-22): detección de modelos (US-22.01), generación local (US-22.03) y decisión (ADR-015).

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `DEFAULT_TIMEOUT_S` | 33 | |
| clase | `OllamaClient` (—) | 36 |  |
| método | `OllamaClient.__init__(base_url, *, timeout_s, transport)` | 37 |  |
| método | `OllamaClient.close()` | 43 |  |
| método | `OllamaClient.list_models()` | 65 | US-22.01: modelos instalados según el runtime; nunca se inventa uno que no aparezca aquí (CA-04). |
| método | `OllamaClient.list_details()` | 73 | Modelos instalados con sus detalles (familia, tamaño, cuantización), para el catálogo (US-50.09). |
| método | `OllamaClient.chat(model, messages, *, max_tokens, json_schema, tools)` | 86 |  |
| función | `resolve(ref)` | 112 |  |
| función | `model_health(client, model, endpoint)` | 116 |  |
| clase | `_OllamaEngine` (—) | 128 |  |
| método | `_OllamaEngine.__init__(client, model)` | 132 |  |
| método | `_OllamaEngine.model()` | 138 |  |
| método | `_OllamaEngine.name()` | 142 |  |
| método | `_OllamaEngine.require_model()` | 145 |  |
| método | `_OllamaEngine.close()` | 154 |  |
| método | `_OllamaEngine.health()` | 157 | Sano solo si el runtime responde y el modelo elegido está entre los detectados (US-22.01 CA-03/04). |
| función | `_usage(body)` | 162 |  |
| clase | `OllamaGenerationEngine` (_OllamaEngine) | 170 |  |
| método | `OllamaGenerationEngine.generate(request)` | 171 |  |
| constante | `DECISION_PROMPT_VERSION` | 186 | |
| constante | `DECISION_SYSTEM_PROMPT` | 187 | |
| función | `_options(request)` | 195 | Opciones de cada pregunta con su descripción (la de `criteria` o, si no hay, el propio nombre). |
| clase | `OllamaDecisionEngine` (_OllamaEngine) | 209 | `DecisionEngine` con un modelo generativo local de Ollama: rápido y sin coste, pero no calibrado. |
| método | `OllamaDecisionEngine.supports(request)` | 214 |  |
| método | `OllamaDecisionEngine.decide(request)` | 217 |  |

### `src/acm/inference/ollaya_models.py`

Guía de modelos de Ollaya (JEV) para operadores y agentes (US-50.10).

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `SOURCE` | 15 | |
| constante | `ALL_TYPES` | 16 | |
| función | `_m(summary, best_for, size, notes, types)` | 19 |  |
| constante | `GUIDE` | 23 | |
| constante | `ACM_SUGGESTIONS` | 127 | |
| constante | `CHOOSING` | 135 | |
| función | `guide_for(name)` | 143 | Entrada de la guía para un modelo instalado: su etiqueta exacta (sin `:latest`) o, si no, su familia. |
| función | `overview()` | 151 |  |

### `src/acm/inference/ports.py`

Puertos de inferencia del núcleo (ADR-015, ajustado por ADR-016; diseño en `04_ARQUITECTURA/inference_ports.md`).

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `QUESTION_TYPES` | 17 | |
| constante | `MAX_QUESTIONS` | 18 | |
| constante | `MAX_CHOICE_OPTIONS` | 19 | |
| constante | `SCORE_LEVELS` | 20 | |
| clase | `EngineUnavailable` (AcmError) | 24 | Ningún motor pudo atender la petición, o el motor elegido no está disponible. |
| clase | `EngineError` (AcmError) | 30 | El motor respondió, pero sin una respuesta válida (US-22.03 CA-04: no se declara éxito). |
| clase | `Question` (—) | 38 |  |
| método | `Question.options()` | 43 | Opciones de respuesta: claves de `choice`, niveles de `score` o `true`/`false` de `noul`. |
| clase | `DecisionRequest` (—) | 53 |  |
| método | `DecisionRequest.from_json(project_id, purpose, state, questions, model)` | 88 | Construye la petición desde la forma JSON que recibe la herramienta MCP `acm_decide`. |
| clase | `Answer` (—) | 103 |  |
| método | `Answer.to_json()` | 110 |  |
| clase | `DecisionResult` (—) | 121 |  |
| método | `DecisionResult.to_json()` | 128 |  |
| clase | `EngineHealth` (—) | 139 |  |
| clase | `DecisionEngine` (Protocol) | 146 |  |
| método | `DecisionEngine.supports(request)` | 150 |  |
| método | `DecisionEngine.decide(request)` | 152 |  |
| método | `DecisionEngine.health()` | 154 |  |
| clase | `GenerationRequest` (—) | 159 |  |
| clase | `GenerationResult` (—) | 168 |  |
| clase | `GenerationEngine` (Protocol) | 177 |  |
| método | `GenerationEngine.generate(request)` | 181 |  |
| método | `GenerationEngine.health()` | 183 |  |

### `src/acm/inference/router.py`

Registro de motores (US-47.01) y router con fallback (ADR-015 §3).

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| función | `_now()` | 36 |  |
| clase | `Routed` (—) | 41 | Resultado de una llamada enrutada y el identificador de su registro en `inference_calls` (US-22.03 CA-02). |
| clase | `EngineRegistry` (—) | 48 | Motores disponibles en el proceso y su último estado de salud persistido en la base global. |
| método | `EngineRegistry.__init__(projects)` | 51 |  |
| método | `EngineRegistry.register(engine)` | 56 |  |
| método | `EngineRegistry.close()` | 76 | Libera los recursos de los motores que los tengan (p. ej. el cliente HTTP de Ollama). |
| método | `EngineRegistry.refresh()` | 83 | Comprueba la salud de cada motor y guarda los modelos detectados (US-22.01). |
| método | `EngineRegistry.list()` | 114 |  |
| clase | `EngineRouter` (—) | 127 |  |
| método | `EngineRouter.__init__(projects, registry)` | 128 |  |
| método | `EngineRouter.decide(principal, request)` | 140 |  |
| método | `EngineRouter.has_generation()` | 191 |  |
| método | `EngineRouter.generate(principal, request)` | 194 |  |
| método | `EngineRouter.calls(principal, *, project_id, limit)` | 272 | Registro de llamadas de inferencia (solo admin, como la auditoría MCP). |
| función | `_describe(failures)` | 286 |  |
| función | `require_calibrated(result, consumer)` | 290 | Un consumidor que decide automáticamente (gate) no acepta la «confianza» de un motor no calibrado (ADR-015). |

### `src/acm/inference/rules.py`

`RulesDecisionEngine`: implementación sin modelo del puerto de decisión (US-35.11 CA-02).

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| clase | `Rule` (—) | 21 |  |
| función | `noul(value)` | 27 |  |
| función | `choice(option, options)` | 32 |  |
| función | `score(level, levels)` | 36 | `level` es 1..n sobre `levels` (el valor continuo de un score exacto coincide con un nivel). |
| constante | `STORY_FIELDS` | 42 | |
| función | `_story(state)` | 45 |  |
| función | `story_checks(state)` | 54 | Comprobaciones estructurales de una historia (misma regla READY de US-04.03 CA-04). |
| función | `_check(name)` | 65 |  |
| función | `_readiness(state, q)` | 69 |  |
| función | `_completeness(state, q)` | 76 |  |
| constante | `STORY_QUALITY_RULES` | 85 | |
| constante | `DEFAULT_RULES` | 96 | |
| clase | `RulesDecisionEngine` (—) | 99 |  |
| método | `RulesDecisionEngine.__init__(rules)` | 103 |  |
| método | `RulesDecisionEngine.catalog()` | 106 | Preguntas que sabe responder, por purpose (para la skill y `acm_engines_list`). |
| método | `RulesDecisionEngine.supports(request)` | 113 |  |
| método | `RulesDecisionEngine.decide(request)` | 119 |  |
| método | `RulesDecisionEngine.health()` | 129 |  |

### `src/acm/inference/selection.py`

Modelos elegidos en ACM (US-50.09, US-22.06, US-22.07): un modelo de Ollama y, en Ollaya, uno por defecto y uno

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `CACHE_S` | 19 | |
| constante | `KEYS` | 20 | |
| clase | `ModelSelection` (—) | 23 |  |
| método | `ModelSelection.__init__(projects, *, ollama_model, jev_model)` | 24 |  |
| método | `ModelSelection.get(key)` | 38 |  |
| método | `ModelSelection.source(key)` | 46 | De dónde sale el valor: elegido en ACM, variable de arranque o sin valor. |
| método | `ModelSelection.set(principal, key, value)` | 52 |  |
| método | `ModelSelection.ollama_model()` | 66 |  |
| método | `ModelSelection.jev_model(purpose)` | 69 | US-22.07: el modelo de Ollaya asignado al propósito o, si no hay, el modelo por defecto. |

### `src/acm/local.py`

Modo local de ACM (ADR-023): un agente conectado por stdio sin instalar ni configurar nada más.

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `LOCAL_SESSION_NAME` | 30 | |
| constante | `LOCAL_HOST_HEADERS` | 31 | |
| función | `local_principal(service, settings)` | 34 | Principal del agente que habla por esta conexión; se crea al usarlo por primera vez. |
| función | `port_in_use(host, port)` | 49 |  |
| función | `start_local_ui(settings)` | 55 | Arranca la interfaz local en segundo plano. Devuelve True si lanzó un proceso nuevo. |
| función | `_host_name(host_header)` | 80 |  |
| función | `is_local_request(client_host, host_header, marker)` | 86 | ¿La petición viene de este equipo, a un nombre local y con la cabecera propia de la interfaz? |
| función | `pid_file(settings)` | 91 |  |
| función | `write_pid(settings)` | 95 |  |
| función | `stop_local_ui(settings)` | 99 | `acm stop`: para la interfaz local que arrancó un agente. Devuelve lo que hizo, para mostrarlo. |

### `src/acm/mcp_server.py`

Servidor MCP propio de ACM (ADR-008, ADR-014).

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `SKILLS_EXTENSION` | 50 | |
| constante | `INSTRUCTIONS` | 52 | |
| clase | `AcmMCPServer` (MCPServer) | 64 | MCPServer que deja el cliente y la sesión de cada petición en `current_client` y `current_session`. |
| método | `AcmMCPServer.__init__(*args, stdio, **kwargs)` | 71 |  |
| método | `AcmMCPServer.async call_tool(name, arguments, context)` | 92 |  |
| método | `AcmMCPServer.async read_resource(uri, context)` | 97 |  |
| método | `AcmMCPServer.async get_prompt(name, arguments, context)` | 102 |  |
| clase | `SkillsListParams` (RequestParams) | 108 |  |
| clase | `SkillsGetParams` (RequestParams) | 112 |  |
| función | `build_mcp_server(service, principal, catalog, engines, token_id, stdio)` | 116 | Crea el servidor MCP. |

Herramientas MCP (65):

| Herramienta | Línea | Descripción |
|-------------|-------|-------------|
| `acm_skills_list` | 273 | Lista las skills de ACM (uri, frontmatter con versión, digest y tamaño de cada archivo). |
| `acm_skill_get` | 278 | Devuelve todos los archivos de una skill de ACM (respaldo de skills/get + resources/read). |
| `acm_skills_reload` | 290 | (admin) Relee el catálogo de skills; si cambia, notifica resources/list_changed a los suscritos. |
| `acm_project_create` | 307 | Crea un proyecto ACM con su propia base SQLite. `key` es el project_id: ^[a-z][a-z0-9-]{1,39}$. |
| `acm_project_directory` | 313 | EMPIEZA AQUÍ. Proyectos de ACM con tu rol en cada uno y tus peticiones para unirte. Pregunta a la persona si |
| `acm_project_join` | 319 | Pide unirte a un proyecto existente (`access_level`: write / read). Queda PENDING hasta que una persona la |
| `acm_project_join_status` | 326 | Estado de tu petición para unirte a un proyecto: NONE, PENDING, APPROVED, REJECTED o MEMBER. |
| `acm_project_list` | 332 | Lista los proyectos a los que tienes acceso (con su project_id). |
| `acm_project_open` | 337 | Abre un proyecto: devuelve metadatos, tu rol, versión de esquema y configuración efectiva. |
| `acm_project_config_get` | 342 | Devuelve cada parámetro de configuración del proyecto con su valor actual, por defecto y permitido. |
| `acm_project_config_set` | 348 | Modifica parámetros ({parámetro: valor}). Valida todo antes de guardar; indica cuáles requieren recarga. |
| `acm_system_info` | 354 | Estado de la plataforma: versión, esquema global, nº de proyectos, PRAGMAs y skills activas/rechazadas. |
| `acm_audit_list` | 368 | (admin) Últimas invocaciones MCP auditadas: quién, operación, argumentos, resultado, estado, duración. |
| `acm_requirement_create` | 385 | Registra un requisito (REQ-NNN). `requirement_id` opcional para importar IDs existentes. |
| `acm_requirement_list` | 402 | Lista los requisitos del proyecto. |
| `acm_requirement_trace` | 408 | Trazabilidad de un requisito: sus épicas, las features de esas épicas y las historias que lo implementan. |
| `acm_epic_create` | 416 | Crea una épica (EPIC-NN) con objetivo y alcance obligatorios, opcionalmente asociada a requisitos. |
| `acm_epic_link_requirements` | 447 | Asocia requisitos existentes a una épica. |
| `acm_epic_get` | 461 | Devuelve una épica con sus requisitos y sus features (y las historias de cada feature). |
| `acm_epic_list` | 467 | Lista las épicas del proyecto con sus features e historias. |
| `acm_epic_confirm_coverage` | 472 | Confirma que las features activas de la épica cubren su objetivo (requiere al menos una feature activa). |
| `acm_feature_create` | 480 | Crea una feature (FEAT-NN.MM) dentro de una épica. |
| `acm_feature_split` | 504 | Divide una feature en ≥2: parts=[{title, description?, story_ids}] repartiendo todas sus historias. |
| `acm_story_create` | 510 | Crea una historia (US-NN.MM): actor (as_a), acción (i_want), valor (so_that), ≥1 requisito de origen y |
| `acm_story_add_criteria` | 554 | Añade criterios de aceptación (CA-NN) a una historia. |
| `acm_story_get` | 562 | Devuelve una historia con sus requisitos de origen y criterios de aceptación. |
| `acm_story_mark_ready` | 568 | Pasa una historia de PLANNED a READY si tiene actor, acción, valor, requisito y criterios. |
| `acm_story_set_status` | 574 | Mueve una historia de estado (Kanban) si la transición está permitida. PLANNED → READY: acm_story_mark_ready. |
| `acm_story_history` | 583 | Historial de cambios de estado de una historia (quién, cuándo, de qué a qué y por qué). |
| `acm_backlog_audit` | 589 | Huecos de trazabilidad: requisitos huérfanos, épicas/features vacías, historias sin CA. |
| `acm_sprint_create` | 595 | Crea un sprint SPRINT-NN (PLANNED) con objetivo, fechas AAAA-MM-DD y capacidad opcional en historias. |
| `acm_sprint_list` | 611 | Sprints del proyecto con estado, historias, carga, capacidad y resumen de cierre. |
| `acm_sprint_get` | 616 | Un sprint con sus historias actuales, historial de pertenencia y métricas. |
| `acm_sprint_add_stories` | 622 | Planifica historias en un sprint abierto (una historia, un sprint abierto); avisa si no están READY. |
| `acm_sprint_remove_story` | 629 | Retira una historia de un sprint abierto (queda en su historial como retirada). |
| `acm_sprint_start` | 636 | Inicia un sprint PLANNED. Rechaza si ya hay uno activo o si supera su capacidad (salvo force=true). |
| `acm_sprint_close` | 642 | Cierra el sprint activo: lo DONE queda hecho; el resto pasa a `carry_over_to` o vuelve al backlog. |
| `acm_sprint_cancel` | 649 | Cancela un sprint PLANNED o ACTIVE: sus historias vuelven al backlog sin cambiar de estado. |
| `acm_next_work` | 656 | Qué toca ahora en el proyecto, ya asignado a ti: `action` (implement, verify, refine, plan_sprint, |
| `acm_work_release` | 664 | Libera un trabajo que tienes asignado (al abandonarlo); queda libre para otro agente. |
| `acm_work_list` | 670 | Quién trabaja ahora en qué dentro del proyecto (asignaciones vigentes). |
| `acm_decide` | 677 | Delega una decisión tipada (noul = sí/no, choice = clasificar, score = puntuar) en el motor de decisión. |
| `acm_context_compact` | 700 | Contexto compacto de una historia (historia, CA, requisitos, feature, épica, historias hermanas). |
| `acm_engines_list` | 711 | Motores de inferencia registrados, su último estado, modelos detectados y preguntas que cubren las reglas. |
| `acm_engines_refresh` | 721 | (admin) Comprueba la salud de cada motor y detecta los modelos disponibles en su runtime. |
| `acm_savings_report` | 733 | (admin) Tokens ahorrados por el contexto compacto, agregados por agente y proyecto, con el método usado. |
| `acm_models_list` | 741 | Modelos disponibles: Ollaya (JEV, decisiones) con detalles, propósitos asignados y nota; Ollama (local) |
| `acm_models_select` | 747 | (admin) Elige el modelo de Ollama y, en Ollaya, el de por defecto, uno por propósito y notas de uso. |
| `acm_chat` | 765 | Habla con el modelo local de Ollama en un hilo que ACM conserva: envía solo el mensaje nuevo (y `thread_id` |
| `acm_chat_threads` | 776 | Tus hilos de conversación con el modelo local en el proyecto (un admin ve todos). |
| `acm_chat_get` | 781 | Un hilo con todos sus mensajes, herramientas usadas y modelo. |
| `acm_whoami` | 788 | Tu identidad: principal, tipo (user/agent), rol global, proyectos con su rol y tokens activos. |
| `acm_principal_create` | 793 | (admin) Da de alta un usuario o un agente (kind: user / agent; role global: admin / user). |
| `acm_principal_list` | 801 | (admin) Principales con su tipo y rol global, y los roles disponibles. |
| `acm_principal_set_role` | 806 | (admin) Cambia el rol global (admin / user). Nunca deja el sistema sin admin. |
| `acm_member_set` | 812 | (persona admin u owner del proyecto) Añade un miembro o cambia su rol (owner / member / viewer). Un agente no |
| `acm_member_remove` | 819 | (admin u owner del proyecto) Retira a un miembro. Nunca deja el proyecto sin owner. |
| `acm_member_list` | 825 | Miembros del proyecto con su rol y tipo. |
| `acm_token_create` | 830 | (admin) Crea un token para un principal. El token completo se muestra SOLO en esta respuesta: guárdalo. |
| `acm_token_list` | 836 | Tokens (sin el secreto: solo prefijo, estado y uso). Los tuyos, o los de cualquiera si eres admin. |
| `acm_token_revoke` | 842 | Revoca un token al instante (los tuyos; los ajenos, solo un admin). |
| `acm_watchdog_run` | 848 | Auditoría de gobernanza del proyecto: integridad SQLite, calidad de historias (vía el motor de decisión) y |
| `acm_watchdog_history` | 855 | Histórico de auditorías del proyecto (más recientes primero), con sus hallazgos. |
| `acm_governance_status` | 861 | Indicadores de gobernanza: semáforo y recuentos de la última auditoría, integridad y si admite escrituras. |
| `acm_health` | 867 | (admin) Salud de cada componente: bases SQLite, catálogo de skills y motores de inferencia. |

### `src/acm/sessions.py`

Identidad de los agentes locales: quién es y qué sesión es (ADR-023).

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `PROCESS_SESSION` | 26 | |
| función | `_slug(text)` | 31 |  |
| función | `agent_principal(client, host)` | 35 | `<cliente>.<equipo>` válido como identificador de principal (^[a-z0-9][a-z0-9._-]{1,63}$). |
| función | `session_id()` | 42 | Sesión de la conexión en curso; vacía fuera de una conexión MCP (REST, interfaz, tests). |

### `src/acm/skills_catalog.py`

Catálogo de skills oficiales de ACM (ADR-008; US-15.01, US-15.06, US-15.07).

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `SKILL_PREFIX` | 20 | |
| constante | `DEFAULT_ROOT` | 21 | |
| constante | `NAME_RE` | 22 | |
| constante | `FILE_RE` | 23 | |
| constante | `SEMVER_RE` | 24 | |
| constante | `MAX_FILES` | 25 | |
| constante | `MAX_BYTES` | 26 | |
| clase | `SkillFile` (—) | 30 |  |
| clase | `Skill` (—) | 39 |  |
| método | `Skill.uri()` | 45 |  |
| método | `Skill.entry()` | 48 |  |
| clase | `SkillError` (ValueError) | 56 |  |
| función | `parse_frontmatter(text)` | 60 |  |
| función | `_load_one(directory)` | 79 |  |
| clase | `SkillCatalog` (—) | 122 |  |
| método | `SkillCatalog.__init__(root)` | 123 |  |
| método | `SkillCatalog.reload()` | 151 | Relee el catálogo. Devuelve True si cambió el conjunto de skills o de digests (US-15.06). |
| método | `SkillCatalog.get_by_uri(uri)` | 160 |  |
| método | `SkillCatalog.file(name, filename)` | 164 |  |
| método | `SkillCatalog.entries()` | 169 |  |

### `src/acm/web_api.py`

API REST v1 y WebSocket de eventos de ACM (EPIC-30, EPIC-21; ADR-018).

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `HTTP_STATUS` | 47 | |
| constante | `KANBAN_COLUMNS` | 59 | |
| constante | `WS_POLL_S` | 72 | |
| constante | `WS_AUTH_TIMEOUT_S` | 73 | |
| constante | `WS_ACCESS_REFRESH_S` | 74 | |
| función | `_error_doc(description)` | 77 |  |
| constante | `ERROR_RESPONSES` | 86 | |
| clase | `StatusChange` (BaseModel) | 95 |  |
| clase | `ProjectIn` (BaseModel) | 102 |  |
| clase | `ConfigIn` (BaseModel) | 108 |  |
| clase | `RequirementIn` (BaseModel) | 112 |  |
| clase | `EpicIn` (BaseModel) | 117 |  |
| clase | `RequirementIds` (BaseModel) | 124 |  |
| clase | `FeatureIn` (BaseModel) | 128 |  |
| clase | `SplitIn` (BaseModel) | 134 |  |
| clase | `StoryIn` (BaseModel) | 138 |  |
| clase | `CriteriaIn` (BaseModel) | 149 |  |
| clase | `SprintIn` (BaseModel) | 153 |  |
| clase | `StoryIds` (BaseModel) | 161 |  |
| clase | `StartIn` (BaseModel) | 165 |  |
| clase | `CloseIn` (BaseModel) | 169 |  |
| clase | `RoleIn` (BaseModel) | 173 |  |
| clase | `PrincipalIn` (BaseModel) | 177 |  |
| clase | `TokenIn` (BaseModel) | 183 |  |
| clase | `ModelsIn` (BaseModel) | 188 |  |
| clase | `ApproveIn` (BaseModel) | 195 |  |
| clase | `ChatIn` (BaseModel) | 199 |  |
| función | `error_response(exc)` | 205 |  |
| función | `build_api(service, engines, catalog)` | 212 | Devuelve la sub-app REST (a envolver con `BearerAuth`) y el router del WebSocket (autenticación propia). |
| clase | `Access` (—) | 921 | Qué eventos puede ver un principal (US-21.02 CA-02). Se recalcula cuando cambian pertenencias o roles. |
| método | `Access.__init__(service, principal)` | 924 |  |
| método | `Access.age()` | 934 |  |
| método | `Access.can_see(event)` | 937 |  |

Rutas (59, relativas a su montaje):

| Método | Ruta | Función | Línea | Descripción |
|--------|------|---------|-------|-------------|
| GET | `/me` | `me` | 289 | Tu identidad: principal, tipo, rol global, proyectos y tokens activos. |
| GET | `/meta` | `meta` | 295 | Versión de ACM, estados de historia, transiciones permitidas, columnas del Kanban y último evento. |
| GET | `/projects` | `projects` | 321 | Cartera: proyectos accesibles con su semáforo de gobernanza y las historias por estado. |
| GET | `/projects/{project_id}` | `project` | 327 | Metadatos del proyecto, tu rol y su configuración. |
| GET | `/projects/{project_id}/backlog` | `project_backlog` | 332 | Backlog completo: requisitos, épicas con features, historias con criterios y huecos de trazabilidad. |
| GET | `/projects/{project_id}/stories/{story_id}` | `story` | 344 | Historia con criterios, requisitos, historial de estados y transiciones permitidas. |
| POST | `/projects/{project_id}/stories/{story_id}/status` | `story_status` | 354 | Mueve la historia a otro estado permitido (DONE solo desde VERIFIED). |
| POST | `/projects/{project_id}/stories/{story_id}/ready` | `story_ready` | 365 | Gate de calidad: pasa la historia de PLANNED a READY si está completa. |
| GET | `/projects/{project_id}/requirements/{requirement_id}/trace` | `trace` | 372 | Trazabilidad de un requisito: épicas, features e historias que lo implementan. |
| GET | `/projects/{project_id}/context/{story_id}` | `compact_context` | 377 | Contexto compacto de una historia para agentes, con fuentes y tokens ahorrados. |
| GET | `/projects/{project_id}/members` | `members` | 382 | Miembros del proyecto con su rol y tipo. |
| GET | `/projects/{project_id}/config` | `config` | 387 | Parámetros de configuración del proyecto con valor, valores permitidos y quién los usa. |
| GET | `/projects/{project_id}/governance` | `governance` | 392 | Semáforo, integridad e histórico de auditorías del Watchdog. |
| POST | `/projects/{project_id}/watchdog` | `watchdog_run` | 398 | Ejecuta ahora una auditoría de gobernanza del proyecto. |
| GET | `/kanban` | `kanban` | 405 | Tablero Kanban de uno o varios proyectos (o de un sprint): columnas, transiciones y tarjetas. |
| GET | `/join-requests` | `join_requests` | 458 | Peticiones de agentes para unirse a proyectos que puedes decidir (admin: todas; owner: las suyas). |
| POST | `/join-requests/{request_id}/approve` | `join_approve` | 463 | Aprueba la petición (solo una persona): `role` member (escritura) o viewer (lectura). |
| POST | `/join-requests/{request_id}/reject` | `join_reject` | 472 | Rechaza la petición (solo una persona); el agente lo sabrá al consultar su estado. |
| GET | `/projects/{project_id}/work` | `project_work` | 481 | Quién trabaja ahora en qué dentro del proyecto (asignaciones vigentes de `acm_next_work`). |
| DELETE | `/projects/{project_id}/work/{item}` | `work_release` | 486 | Libera una asignación (una persona puede liberar cualquiera). |
| POST | `/projects` | `project_create` | 495 | Crea un proyecto con su propia base SQLite (`key` = project_id). |
| POST | `/projects/{project_id}/requirements` | `requirement_create` | 511 | Registra un requisito REQ-NNN. |
| POST | `/projects/{project_id}/epics` | `epic_create` | 523 | Crea una épica con objetivo, alcance y requisitos. |
| POST | `/projects/{project_id}/epics/{epic_id}/requirements` | `epic_link` | 537 | Asocia más requisitos a una épica. |
| POST | `/projects/{project_id}/epics/{epic_id}/confirm-coverage` | `epic_confirm` | 549 | Confirma que las features activas cubren el objetivo de la épica. |
| POST | `/projects/{project_id}/features` | `feature_create` | 560 | Crea una feature dentro de una épica. |
| POST | `/projects/{project_id}/features/{feature_id}/split` | `feature_split` | 573 | Divide una feature en ≥2 features nuevas repartiendo todas sus historias. |
| POST | `/projects/{project_id}/stories` | `story_create` | 585 | Crea una historia (de usuario o técnica) enlazada a requisitos, con sus criterios. |
| POST | `/projects/{project_id}/stories/{story_id}/criteria` | `story_criteria` | 603 | Añade criterios de aceptación a una historia. |
| GET | `/projects/{project_id}/sprints` | `sprint_list` | 616 | Sprints con estado, historias, carga, capacidad y resumen de cierre. |
| GET | `/projects/{project_id}/sprints/{sprint_id}` | `sprint_get` | 621 | Un sprint con sus historias e historial de pertenencia. |
| POST | `/projects/{project_id}/sprints` | `sprint_create` | 626 | Crea un sprint PLANNED con objetivo, fechas y capacidad opcional (en historias). |
| POST | `/projects/{project_id}/sprints/{sprint_id}/stories` | `sprint_add` | 641 | Planifica historias en un sprint abierto. |
| DELETE | `/projects/{project_id}/sprints/{sprint_id}/stories/{story_id}` | `sprint_remove` | 653 | Retira una historia de un sprint abierto. |
| POST | `/projects/{project_id}/sprints/{sprint_id}/start` | `sprint_start` | 665 | Inicia un sprint PLANNED (rechaza la sobrecarga salvo force). |
| POST | `/projects/{project_id}/sprints/{sprint_id}/close` | `sprint_close` | 677 | Cierra el sprint activo con resumen; lo no terminado se traslada o vuelve al backlog. |
| POST | `/projects/{project_id}/sprints/{sprint_id}/cancel` | `sprint_cancel` | 689 | Cancela un sprint abierto; sus historias vuelven al backlog. |
| PUT | `/projects/{project_id}/members/{principal_id}` | `member_set` | 697 | (admin/owner) Añade un miembro al proyecto o cambia su rol. |
| DELETE | `/projects/{project_id}/members/{principal_id}` | `member_remove` | 709 | (admin/owner) Retira a un miembro del proyecto. |
| POST | `/principals` | `principal_create` | 720 | (admin) Alta de un usuario o agente. |
| PUT | `/principals/{principal_id}/role` | `principal_role` | 727 | (admin) Cambia el rol global de un principal. |
| POST | `/tokens` | `token_create` | 738 | (admin) Crea un token; el secreto (`token`) solo aparece en esta respuesta y nunca se audita. |
| DELETE | `/tokens/{token_id}` | `token_revoke` | 743 | Revoca un token al instante (los propios, o cualquiera si eres admin). |
| POST | `/engines/refresh` | `engines_refresh` | 748 | (admin) Comprueba de nuevo la salud y los modelos de cada motor, sin reiniciar ACM. |
| GET | `/models` | `models_catalog` | 761 | Catálogo de modelos de Ollama y Ollaya: disponibles, elegidos, propósitos, notas y cómo usarlos. |
| PUT | `/models` | `models_select` | 766 | (admin) Elige el modelo de Ollama y los de Ollaya (por defecto y por propósito); sin reiniciar. |
| GET | `/projects/{project_id}/chat/threads` | `chat_threads` | 772 | Tus hilos de conversación con el modelo local (un admin ve todos). |
| GET | `/projects/{project_id}/chat/threads/{thread_id}` | `chat_thread` | 777 | Un hilo con sus mensajes y las herramientas que usó el modelo. |
| POST | `/projects/{project_id}/chat` | `chat_send` | 782 | Envía un mensaje al asistente local (Ollama) del proyecto; ACM conserva el hilo. |
| GET | `/activity` | `activity` | 796 | Auditoría de invocaciones (solo admin), filtrable por proyecto, principal y operación. |
| GET | `/events` | `events` | 805 | Eventos de dominio posteriores a un seq, filtrados por visibilidad. |
| GET | `/health` | `health` | 817 | Salud de cada componente: bases SQLite, catálogo de skills y motores (solo admin). |
| GET | `/engines` | `engines_list` | 822 | Motores de inferencia registrados, estado, modelos detectados y reglas disponibles. |
| GET | `/savings` | `savings` | 828 | Tokens ahorrados a los agentes por el contexto compacto (solo admin). |
| GET | `/skills` | `skills` | 833 | Catálogo de skills que ACM sirve a los agentes. |
| GET | `/skills/{name}` | `skill` | 838 | Archivos de una skill (Markdown con frontmatter). |
| GET | `/principals` | `principals` | 846 | Principales (usuarios y agentes) y roles disponibles (solo admin). |
| GET | `/tokens` | `tokens` | 851 | Tokens sin su secreto: prefijo, estado y uso. |
| WEBSOCKET | `/api/v1/ws` | `events_ws` | 859 |  |

### `src/acm/webui_app.py`

Interfaz web de ACM (SPRINT-007, ADR-019): los archivos compilados de `web/` servidos en `/`.

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `WEBUI_DIR` | 15 | |
| clase | `SecureStatic` (—) | 18 |  |
| método | `SecureStatic.__init__(directory)` | 19 |  |
| función | `webui_available()` | 45 |  |

## Frontend (`web/src`)

### `web/src/App.tsx`

Cabecera de la aplicación (navegación, estado del canal en vivo, tema, sesión) y tabla de rutas (HashRouter).

| Tipo | Nombre | Línea |
|------|--------|-------|
| componente | `App` | 79 |

### `web/src/KanbanBoard.tsx`

Tablero Kanban de uno o varios proyectos (US-06.01..03). Arrastrar y soltar, o «Mover a…» con teclado.

| Tipo | Nombre | Línea |
|------|--------|-------|
| componente | `KanbanBoard` | 25 |

### `web/src/api.ts`

Cliente de la API REST v1 (06_API/rest_api.md). El token vive en sessionStorage: se borra al cerrar la pestaña.

| Tipo | Nombre | Línea |
|------|--------|-------|
| constante | `API` | 3 |
| clase | `ApiError` | 5 |
| constante | `tokenStore` | 16 |
| función | `api` | 32 |
| función | `post` | 51 |
| función | `put` | 55 |
| función | `patch` | 59 |
| función | `del` | 63 |

### `web/src/auth.tsx`

Sesión (US-31.01): token en sessionStorage, identidad desde /api/v1/me, cierre por 401 o WS 4401.

| Tipo | Nombre | Línea |
|------|--------|-------|
| componente | `AuthProvider` | 32 |
| hook | `useAuth` | 109 |
| función | `describeError` | 115 |

### `web/src/components.tsx`

Componentes compartidos de presentación: badges de estado, semáforo, Markdown, errores, esqueletos de carga.

| Tipo | Nombre | Línea |
|------|--------|-------|
| componente | `StatusBadge` | 10 |
| componente | `SemaphoreBadge` | 29 |
| componente | `SeverityBadge` | 43 |
| componente | `ProjectChip` | 51 |
| componente | `Loading` | 61 |
| componente | `ErrorBox` | 69 |
| componente | `Empty` | 77 |
| componente | `Markdown` | 81 |
| componente | `Section` | 85 |
| componente | `Stat` | 97 |
| función | `fmtDate` | 106 |
| componente | `StatusBar` | 113 |

### `web/src/forms.tsx`

Formularios de escritura (US-31.09..31.12): el error del servidor se muestra junto al campo que lo causó, sin perder

| Tipo | Nombre | Línea |
|------|--------|-------|
| hook | `useAction` | 9 |
| función | `fieldOf` | 17 |
| componente | `Field` | 22 |
| componente | `FormStatus` | 65 |
| componente | `Disclosure` | 82 |
| función | `submit` | 94 |
| función | `lines` | 102 |

### `web/src/kanban.test.ts`

Tests del modelo del Kanban (US-06.06/07): agrupación, filtros y transiciones permitidas.

Tests (5): cada historia en exactamente una columna, también con varios proyectos; filtra por proyecto y por texto; oculta las columnas terminales si se pide; solo permite mover a destinos válidos; READY por el gate; DONE solo desde VERIFIED; aplica en memoria un cambio recibido en vivo solo a la tarjeta de ese proyecto

### `web/src/kanban.ts`

Lógica pura del tablero Kanban (US-06.01, US-06.02).

| Tipo | Nombre | Línea |
|------|--------|-------|
| constante | `TERMINAL` | 5 |
| tipo | `BoardOptions` | 7 |
| función | `visibleColumns` | 9 |
| función | `matches` | 13 |
| función | `groupByColumn` | 24 |
| función | `targets` | 35 |
| función | `canMove` | 40 |
| función | `applyStatus` | 45 |

### `web/src/live.tsx`

Canal en vivo (US-06.03, US-21.02/03): WebSocket autenticado, reanudación por seq y recarga de datos afectados.

| Tipo | Nombre | Línea |
|------|--------|-------|
| tipo | `LiveStatus` | 8 |
| componente | `LiveProvider` | 25 |
| hook | `useLive` | 95 |

### `web/src/liveCore.test.ts`

Tests del núcleo en vivo (US-31.08): orden por seq, duplicados, reanudación, resync y claves a recargar.

Tests (8): aplica eventos en orden y descarta duplicados; al reconectar pide lo posterior al último evento aplicado; un ready no retrocede el último seq aplicado; resync pide recargar todo; reintentos con espera exponencial acotada; un cambio de historia invalida Kanban, cartera, proyecto e historia; recarga sprints y modelos cuando cambian (SPRINT-008); recarga solicitudes de acceso y trabajo asignado (SPRINT-009)

### `web/src/liveCore.ts`

Lógica pura del canal en vivo (US-21.03): orden por seq, sin duplicados, reanudación y resync.

| Tipo | Nombre | Línea |
|------|--------|-------|
| tipo | `LiveState` | 4 |
| tipo | `ServerMessage` | 5 |
| tipo | `Outcome` | 11 |
| función | `receive` | 14 |
| función | `authMessage` | 29 |
| función | `backoff` | 34 |
| función | `affectedKeys` | 39 |

### `web/src/main.tsx`

Punto de entrada: proveedores (react-query, preferencias, sesión, canal en vivo) y router. Ver control/05_CODIGO/frontend.md.

### `web/src/markdown.test.ts`

Tests del Markdown seguro (US-45.02): saneado de HTML ejecutable y frontmatter.

Tests (3): renderiza títulos, tablas y código; elimina HTML ejecutable (XSS); separa el frontmatter

### `web/src/markdown.ts`

Documentación en Markdown (skills, US-15.08..10) renderizada y saneada: nunca HTML ejecutable (XSS).

| Tipo | Nombre | Línea |
|------|--------|-------|
| función | `splitFrontmatter` | 6 |
| función | `renderMarkdown` | 11 |

### `web/src/pages/Activity.tsx`

Actividad (US-14.10, US-31.01/02/04): consola en vivo y auditoría filtrable. Solo admin.

| Tipo | Nombre | Línea |
|------|--------|-------|
| componente | `ActivityPage` | 13 |

### `web/src/pages/Assistant.tsx`

Asistente local del proyecto (US-22.10, US-22.11): conversación con el modelo de Ollama en hilos que ACM conserva.

| Tipo | Nombre | Línea |
|------|--------|-------|
| componente | `AssistantView` | 10 |

### `web/src/pages/BacklogForms.tsx`

Construir el backlog desde la interfaz (US-31.10): requisitos, épicas, features, historias y criterios; enlazar

| Tipo | Nombre | Línea |
|------|--------|-------|
| componente | `RequirementForm` | 39 |
| componente | `EpicForm` | 63 |
| componente | `FeatureForm` | 95 |
| componente | `EpicActions` | 122 |
| componente | `SplitForm` | 151 |
| componente | `StoryForm` | 188 |
| componente | `CriteriaForm` | 255 |

### `web/src/pages/Dashboard.tsx`

Panel general (US-45.01/45.03): todos los proyectos accesibles, su salud y la actividad en vivo.

| Tipo | Nombre | Línea |
|------|--------|-------|
| componente | `Dashboard` | 41 |

### `web/src/pages/Docs.tsx`

Documentación (US-15.08..10, US-30.02): skills que ACM sirve a los agentes, flujo de estados y referencia de la API.

| Tipo | Nombre | Línea |
|------|--------|-------|
| componente | `DocsPage` | 14 |

### `web/src/pages/JoinRequests.tsx`

Solicitudes de acceso de agentes (US-14.15): una persona aprueba (lectura o escritura) o rechaza que un agente se

| Tipo | Nombre | Línea |
|------|--------|-------|
| componente | `JoinRequestsPanel` | 9 |

### `web/src/pages/KanbanPage.tsx`

Kanban de uno o varios proyectos a la vez (US-06.01), seleccionables; la selección vive en la URL.

| Tipo | Nombre | Línea |
|------|--------|-------|
| componente | `KanbanPage` | 9 |

### `web/src/pages/Login.tsx`

Pantalla de acceso con token opaco acm_ (ADR-017); el token nunca sale de sessionStorage.

| Tipo | Nombre | Línea |
|------|--------|-------|
| componente | `Login` | 5 |

### `web/src/pages/Models.tsx`

Modelos (US-50.09, US-50.10, US-22.06): lo que detecta cada runtime, qué es cada modelo de Ollaya (guía) y la

| Tipo | Nombre | Línea |
|------|--------|-------|
| componente | `ModelsSection` | 155 |

### `web/src/pages/Project.tsx`

Proyecto: resumen, backlog, requisitos, historias, Kanban, gobernanza, miembros y configuración.

| Tipo | Nombre | Línea |
|------|--------|-------|
| hook | `useBacklog` | 24 |
| componente | `ProjectPage` | 28 |

### `web/src/pages/Sprints.tsx`

Sprints del proyecto (EPIC-05, US-05.02..05.09): crear, planificar historias, iniciar (con control de sobrecarga),

| Tipo | Nombre | Línea |
|------|--------|-------|
| hook | `useSprints` | 20 |
| componente | `SprintsView` | 215 |

### `web/src/pages/Story.tsx`

Detalle de historia (US-06.06): enunciado, criterios, trazabilidad, estado, historial y contexto compacto.

| Tipo | Nombre | Línea |
|------|--------|-------|
| componente | `StoryPage` | 22 |

### `web/src/pages/Supervisor.tsx`

Supervisor ágil autónomo (US-13.14, US-13.15): informe de la última auditoría (lo hecho, lo pendiente, las

| Tipo | Nombre | Línea |
|------|--------|-------|
| componente | `SupervisorPanel` | 51 |

### `web/src/pages/System.tsx`

Sistema (US-13.03, US-47.01, US-35.09, EPIC-20, US-31.11/31.12, US-50.09): salud, motores, modelos, ahorro,

| Tipo | Nombre | Línea |
|------|--------|-------|
| componente | `SystemPage` | 108 |

### `web/src/prefs.tsx`

Tema claro/oscuro (o el del sistema) aplicado como variables CSS de la paleta verificada (theme.ts).

| Tipo | Nombre | Línea |
|------|--------|-------|
| tipo | `ThemeMode` | 5 |
| componente | `PrefsProvider` | 14 |
| hook | `usePrefs` | 47 |

### `web/src/theme.test.ts`

Tests de la paleta (US-31.07): contraste WCAG AA de texto, franjas y semáforo en ambos temas.

Tests (7): calcula el contraste de referencia (negro/blanco = 21); ${name}: texto base, atenuado y acento sobre fondo y superficies; ${name}: cada estado, semáforo y severidad legible; ${name}: colores de proyecto (etiqueta legible y franja visible); ${name}: semáforo distinguible de la superficie; las variables CSS cubren todos los estados y proyectos; cada proyecto conserva su color con independencia del orden de la lista

### `web/src/theme.ts`

Paleta de ACM (ADR-019): colores con contraste WCAG 2.1 AA verificado por tests (theme.test.ts).

| Tipo | Nombre | Línea |
|------|--------|-------|
| tipo | `ThemeName` | 4 |
| tipo | `Pair` | 5 |
| constante | `STATUS_ORDER` | 7 |
| tipo | `StoryStatus` | 20 |
| constante | `STATUS_LABEL` | 22 |
| tipo | `Palette` | 49 |
| constante | `PALETTES` | 56 |
| función | `luminance` | 159 |
| función | `contrast` | 166 |
| función | `projectIndex` | 172 |
| función | `cssVariables` | 178 |

### `web/src/types.ts`

Tipos de la API REST v1 de ACM (06_API/rest_api.md).

| Tipo | Nombre | Línea |
|------|--------|-------|
| tipo | `Criterion` | 4 |
| tipo | `Story` | 5 |
| tipo | `StoryDetail` | 23 |
| tipo | `Requirement` | 27 |
| tipo | `Feature` | 28 |
| tipo | `Epic` | 37 |
| tipo | `Gaps` | 47 |
| tipo | `Backlog` | 48 |
| tipo | `Semaphore` | 49 |
| tipo | `Finding` | 50 |
| tipo | `WatchdogRun` | 59 |
| tipo | `SupervisorAction` | 78 |
| tipo | `SupervisorSummary` | 92 |
| tipo | `Sprint` | 111 |
| tipo | `ModelGuide` | 137 |
| tipo | `AvailableModel` | 138 |
| tipo | `ModelCatalog` | 146 |
| tipo | `ChatThread` | 164 |
| tipo | `ChatMessage` | 165 |
| tipo | `ChatReply` | 174 |
| tipo | `Governance` | 181 |
| tipo | `PortfolioProject` | 189 |
| tipo | `Card` | 199 |
| tipo | `JoinRequest` | 215 |
| tipo | `Kanban` | 229 |
| tipo | `Me` | 237 |
| tipo | `AcmEvent` | 245 |

## Tests (`tests`)

### `tests/__init__.py`

_(sin docstring de módulo)_

### `tests/conftest.py`

Fixtures compartidas: directorio de datos temporal, `ProjectService` y altas de miembros directas en SQLite.

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `ADMIN` | 16 | |
| función | `data_dir(tmp_path)` | 20 |  |
| función | `service(data_dir)` | 25 |  |
| función | `add_member(data_dir, project_id, principal_id, role)` | 32 | Fixture de datos: da de alta una pertenencia directamente en SQLite. |

### `tests/fake_ollama.py`

Ollama simulado para tests: servidor HTTP real (uvicorn en un hilo) con `/api/tags` y `/api/chat`.

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| clase | `FakeOllamaState` (—) | 22 |  |
| función | `_app(state)` | 35 |  |
| función | `free_port()` | 77 |  |
| clase | `FakeOllama` (—) | 83 |  |
| método | `FakeOllama.__init__()` | 84 |  |

Rutas (2, relativas a su montaje):

| Método | Ruta | Función | Línea | Descripción |
|--------|------|---------|-------|-------------|
| GET | `/api/tags` | `tags` | 39 |  |
| POST | `/api/chat` | `chat` | 45 |  |

### `tests/fake_ollaya.py`

Ollaya simulado para tests: servidor HTTP real con `/api/tags` y `/api/decide` (modelos de decisión JEV).

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `ERRORS` | 21 | |
| clase | `FakeOllayaState` (—) | 29 |  |
| función | `_answer(q, mode)` | 39 |  |
| función | `_app(state)` | 62 |  |
| clase | `FakeOllaya` (—) | 106 |  |
| método | `FakeOllaya.__init__()` | 107 |  |

Rutas (2, relativas a su montaje):

| Método | Ruta | Función | Línea | Descripción |
|--------|------|---------|-------|-------------|
| GET | `/api/tags` | `tags` | 71 |  |
| POST | `/api/decide` | `decide` | 76 |  |

### `tests/live.py`

ACM real por HTTP para los tests: uvicorn en un hilo, con acceso directo a los datos (fixture `acm`).

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `ADMIN` | 24 | |
| clase | `Acm` (—) | 28 |  |
| método | `Acm.token(principal, name)` | 34 |  |
| método | `Acm.audit(**where)` | 37 |  |
| función | `running_acm(data_dir, **settings)` | 47 | ACM real por HTTP en un hilo; `settings` sobrescribe la configuración (p. ej. motores simulados). |
| función | `acm(tmp_path)` | 69 |  |
| función | `async mcp(acm, token)` | 75 |  |

### `tests/test_access.py`

SPRINT-009 — unirse a proyectos con aprobación de una persona: US-14.14 (agente) y US-14.15 (operador).

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `BOT` | 20 | |
| constante | `OTHER` | 21 | |
| función | `anyio_backend()` | 25 |  |
| función | `local(data_dir)` | 30 | ACM en modo local (ADR-023): los agentes ven el directorio y crean sus proyectos. |
| función | `access(local)` | 43 |  |

Tests (13): `test_us1414_ca01_directorio_con_rol_y_peticiones`, `test_us1414_ca01_fuera_del_modo_local_solo_ve_los_suyos`, `test_us1414_ca02_crear_proyecto_nuevo_sin_aprobacion`, `test_us1414_ca03_pedir_unirse_deja_pendiente_y_sin_acceso`, `test_us1414_ca03_entradas_invalidas`, `test_us1414_ca04_consultar_el_estado_de_la_peticion`, `test_us1415_ca01_las_peticiones_pendientes_llegan_en_tiempo_real`, `test_us1415_ca02_aprobar_con_escritura_o_solo_lectura`, `test_us1415_ca02_rol_invalido_y_peticion_ya_decidida`, `test_us1415_ca03_rechazar_y_el_agente_lo_sabe`, `test_us1415_ca04_retirar_a_un_agente_en_cualquier_momento`, `test_us1415_solo_una_persona_decide_y_solo_la_de_su_proyecto`, `test_us1414_flujo_del_agente_por_mcp`

### `tests/test_app.py`

ADR-014 con FastAPI: un proceso ASGI real (uvicorn) sirve /api y /mcp; y el modo stdio del CLI.

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| función | `anyio_backend()` | 24 |  |
| función | `_free_port()` | 28 |  |

Tests (2): `test_fastapi_sirve_api_y_mcp_en_un_proceso`, `test_modo_stdio_del_cli`

### `tests/test_audit.py`

US-14.10 y US-14.11 — auditoría de invocaciones MCP.

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| función | `anyio_backend()` | 19 |  |
| función | `async admin(service)` | 24 |  |
| función | `async _entries(client, **filters)` | 29 |  |

Tests (7): `test_us1410_ca01_admin_lista_invocaciones`, `test_us1410_ca02_filtros`, `test_us1410_ca03_no_admin_rechazado`, `test_us1411_ca01_ca03_argumentos_y_duracion`, `test_us1411_ca02_resultado_truncado`, `test_us1411_ca04_estado_y_error`, `test_us1411_ca05_intentos_no_autorizados`

### `tests/test_auth.py`

EPIC-20: US-20.01 (roles), US-20.02 (autorizar), US-20.03 (tokens), US-20.04 (credenciales por principal),

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| función | `anyio_backend()` | 30 |  |
| función | `async _post_mcp(acm, headers)` | 34 |  |
| función | `_agent(acm, principal, project, role)` | 47 |  |
| función | `_text(result)` | 54 |  |
| función | `_cli(data_dir, *args)` | 321 |  |
| función | `_post_with_host(url, host, token)` | 348 |  |

Tests (24): `test_us2005_ca01_sin_token_401_sin_efectos`, `test_us2005_ca02_token_desconocido_rechazado_y_auditado`, `test_us2005_ca03_cada_peticion_con_su_identidad`, `test_us2003_ca01_token_con_identidad_y_permisos`, `test_us2003_ca02_revocado_deja_de_autorizar_al_instante`, `test_us2003_ca03_token_no_se_muestra_completo`, `test_us2003_ca03_secreto_redactado_en_la_auditoria`, `test_us2003_ca04_uso_trazado`, `test_us2003_solo_admin_crea_tokens_ajenos`, `test_us2004_ca01_usuarios_y_agentes`, `test_us2004_ca02_credenciales_por_principal`, `test_us2004_ca03_auditoria_distingue_principal`, `test_us2001_ca01_roles_definidos`, `test_us2001_ca02_asignar_rol_autorizado`, `test_us2001_ca03_permisos_inmediatos`, `test_us2001_ca04_cambios_auditados`, `test_us2001_nunca_sin_admin_ni_owner`, `test_us2002_ca01_ca02_ca03_permitida_se_ejecuta_denegada_sin_efectos`, `test_us2002_ca04_intento_registrado`, `test_us2002_owner_gestiona_miembros_member_no`, `test_us2008_ca01_ca02_solo_proyectos_propios`, `test_us2008_ca03_admin_accede_a_todos`, `test_cli_crea_principal_y_token_auditados`, `test_td002_host_permitido_por_configuracion`

### `tests/test_backlog.py`

US-03.03, US-04.01, US-04.02, US-04.03 — ver control/01_PRODUCTO/refinements/.

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| función | `backlog(service)` | 16 |  |
| función | `_story(b, feature, req, **kw)` | 21 |  |
| función | `_base(b)` | 41 |  |

Tests (19): `test_us0303_ca01_requisito_localiza_sus_epicas`, `test_us0303_ca02_epica_localiza_sus_features`, `test_us0303_ca03_feature_localiza_sus_historias`, `test_us0303_ca04_historia_identifica_requisitos`, `test_us0303_ca05_requisitos_huerfanos_en_auditoria`, `test_us0401_ca01_id_unico_generado`, `test_us0401_ca02_objetivo_y_alcance_obligatorios`, `test_us0401_ca03_asociar_requisitos`, `test_us0401_ca04_contiene_features`, `test_us0401_ca05_id_explicito_duplicado_rechazado`, `test_us0402_ca01_feature_con_identificador`, `test_us0402_ca02_feature_pertenece_a_una_epica`, `test_us0402_ca03_confirmar_cobertura_del_objetivo`, `test_us0402_ca04_dividir_feature`, `test_us0403_ca01_actor_accion_valor_obligatorios`, `test_us0403_ca02_requisito_de_origen_obligatorio`, `test_us0403_ca03_criterios_de_aceptacion`, `test_us0403_ca04_incompleta_no_pasa_a_ready`, `test_us0403_ca05_tarea_tecnica_requiere_razon`

### `tests/test_context.py`

US-35.08 (contexto compacto) y US-35.09 (tokens ahorrados).

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `LONG` | 25 | |
| clase | `SpyGen` (—) | 28 | Motor de generación de prueba: «resume» devolviendo la primera frase de la entrada. |
| método | `SpyGen.__init__(*, fail, name)` | 33 |  |
| método | `SpyGen.generate(request)` | 37 |  |
| método | `SpyGen.health()` | 43 |  |
| función | `_seed(service, project)` | 47 |  |
| función | `_context(service, *engines)` | 78 |  |
| función | `seeded(service)` | 86 |  |
| función | `ollama()` | 152 |  |
| función | `_deliveries(service)` | 174 |  |
| función | `anyio_backend()` | 231 |  |

Tests (13): `test_us3508_ca01_tamanos_entregado_y_completo`, `test_us3508_ca02_fragmentos_identifican_fuentes`, `test_us3508_ca03_sin_modelo_sin_resumir`, `test_us3508_ca03_modelo_caido_entrega_sin_resumir`, `test_us3508_historia_y_criterios_siempre_literales`, `test_us3508_presupuesto_invalido`, `test_us3508_proyecto_ajeno_rechazado`, `test_us3508_resumen_con_ollama_simulado`, `test_us3509_ca01_cada_entrega_registrada`, `test_us3509_ca02_agregado_por_agente_y_proyecto`, `test_us3509_ca03_metodo_indicado`, `test_us3509_solo_admin`, `test_us3508_us3509_por_mcp`

### `tests/test_db.py`

US-18.01 (persistencia) y US-18.02 (transacciones) — ver control/01_PRODUCTO/refinements/.

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| función | `_db_with_table(path, **kw)` | 23 |  |
| función | `_increment(args)` | 144 |  |
| función | `_hold_lock(path, seconds, ready)` | 165 |  |
| función | `_open_worker(args)` | 196 |  |

Tests (11): `test_pragmas_adr013_activos`, `test_us1801_ca01_estado_relevante_almacenado`, `test_us1801_ca02_ca03_reinicio_reconstruye_desde_sqlite`, `test_us1801_ca04_escritura_fallida_no_deja_inconsistencias`, `test_us1801_transaccion_no_confirmada_desaparece_si_el_proceso_muere`, `test_us1802_ca01_operacion_valida_se_confirma`, `test_us1802_ca02_ca03_fallo_revierte_todo`, `test_us1802_anidamiento_detectado`, `test_us1802_escritores_concurrentes_sin_perdidas`, `test_us1802_reintento_ante_bloqueo_transitorio`, `test_bug001_apertura_concurrente_de_base_nueva`

### `tests/test_inference.py`

US-35.10, US-35.11, US-47.01 (interfaz de decisión, reglas, router) y US-22.01, US-22.03 (Ollama simulado).

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| clase | `FakeJev` (—) | 41 | Motor de decisión con el mismo contrato que tendrá el adaptador JEV (EPIC-50): cubre cualquier pregunta. |
| método | `FakeJev.__init__(*, fail, calibrated, name, provider)` | 44 |  |
| método | `FakeJev.supports(request)` | 48 |  |
| método | `FakeJev.decide(request)` | 51 |  |
| método | `FakeJev.health()` | 63 |  |
| función | `anyio_backend()` | 68 |  |
| función | `router(service)` | 73 |  |
| función | `backlog(service, router)` | 79 |  |
| función | `_quality(state, **questions)` | 98 |  |
| función | `_calls(data_dir)` | 102 |  |
| función | `_order(service, *providers)` | 110 |  |
| constante | `ALL_QUESTIONS` | 114 | |
| constante | `CONSUMERS` | 266 | |
| función | `ollama()` | 317 |  |
| función | `_ollama_router(service, url, model)` | 322 |  |
| función | `_gen(max_tokens)` | 362 |  |

Tests (25): `test_us3510_ca01_respuesta_tipada_con_probabilidades`, `test_us3510_ca02_motor_registrado`, `test_us3510_ca03_sin_motor_error_explicito`, `test_us3510_ca03_fallback_indicado`, `test_us3510_peticion_invalida_rechazada`, `test_us3510_proyecto_ajeno_rechazado`, `test_us3511_ca01_gate_y_herramienta_usan_el_router`, `test_us3511_ca02_reglas_sin_modelo`, `test_us3511_ca03_conectar_jev_no_cambia_consumidores`, `test_us3511_gate_rechaza_motor_no_calibrado`, `test_us3511_gate_detecta_cambio_durante_la_decision`, `test_us4701_ca01_consumidores_no_dependen_de_implementacion`, `test_us4701_ca02_interfaz_abstracta`, `test_us4701_ca03_implementacion_actual_sigue_funcionando`, `test_us2201_ca01_consulta_el_runtime_configurado`, `test_us2201_ca02_modelos_detectados_identificados`, `test_us2201_ca03_runtime_inaccesible_estado_error`, `test_us2201_ca04_no_afirma_modelo_no_detectado`, `test_us2201_configuracion_incompleta_rechazada`, `test_us2203_ca01_peticion_llega_al_modelo_configurado`, `test_us2203_ca02_respuesta_vinculada_a_la_ejecucion`, `test_us2203_ca03_fallo_del_modelo_estado_error`, `test_us2203_ca04_sin_respuesta_valida_no_hay_exito`, `test_engines_refresh_solo_admin`, `test_us2201_cierre_libera_el_cliente_http`

### `tests/test_isolation.py`

US-24.01 y US-24.03 — varios proyectos con backlog y memoria independientes.

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| función | `two(service)` | 17 |  |

Tests (6): `test_us2401_ca01_multiples_proyectos`, `test_us2401_ca02_backlog_independiente`, `test_us2401_ca03_memoria_independiente`, `test_us2401_ca04_cambiar_de_proyecto_cambia_contexto`, `test_us2403_ca01_agente_de_a_no_recupera_memoria_de_b`, `test_us2403_ca03_consultas_limitadas_al_proyecto`

### `tests/test_local_mode.py`

SPRINT-009 — conexión universal de agentes (US-14.12, US-14.13) con procesos reales.

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `HOST` | 30 | |
| función | `anyio_backend()` | 34 |  |
| función | `async agent(data_dir, client, **env)` | 39 | Un agente real: proceso stdio con la entrada estándar de ACM, sin interfaz en segundo plano. |
| función | `_data(result)` | 50 |  |
| clase | `IdentityKinds` (—) | 93 |  |
| método | `IdentityKinds.rows(svc)` | 95 |  |
| función | `daemon(tmp_path)` | 176 | La interfaz local como la arranca un agente: proceso aparte que sobrevive a quien lo lanzó. |

Tests (10): `test_us1412_ca02_un_unico_estado_por_usuario`, `test_us1412_ca03_identidad_valida_y_distinta_por_cliente_y_equipo`, `test_us1412_ca03_cada_cliente_es_un_agente_con_su_nombre`, `test_us1412_ca01_flujo_completo_sin_pasos_previos`, `test_us1412_ca03_dos_sesiones_del_mismo_cliente_no_se_pisan`, `test_us1412_ca03_acm_principal_conserva_la_identidad_admin_unica`, `test_us1412_ca04_solo_peticiones_locales_con_la_cabecera_de_la_interfaz`, `test_us1412_ca04_interfaz_local_en_segundo_plano_sin_token`, `test_us1412_ca04_la_interfaz_sobrevive_y_se_para_con_acm_stop`, `test_us1412_ca04_el_supervisor_trabaja_en_segundo_plano`

### `tests/test_mcp.py`

Frontera MCP: US-01.01 (errores explícitos) y US-01.06 (project_id en cada herramienta).

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `PROJECT_TOOLS` | 17 | |
| constante | `BACKLOG_TOOLS` | 18 | |
| constante | `GLOBAL_TOOLS` | 56 | |
| función | `anyio_backend()` | 87 |  |
| función | `async client(service)` | 92 |  |
| función | `_text(result)` | 97 |  |

Tests (12): `test_us0101_mcp_create_y_errores_explicitos`, `test_us0106_ca01_herramientas_de_proyecto_exigen_project_id`, `test_us0106_ca02_respuestas_incluyen_project_id`, `test_us0106_ca03_project_id_desconocido_error_explicito`, `test_us0106_ca04_instructions_explican_project_id`, `test_us1405_ca01_ca02_descubrir_herramientas`, `test_us1405_ca03_herramientas_de_proyecto_declaran_project_id`, `test_us1406_ca01_operacion_persiste`, `test_us1406_ca02_operacion_rechazada_sin_efectos`, `test_us1407_varios_proyectos_misma_instancia`, `test_us1409_ca01_sin_project_id_no_reutiliza_el_anterior`, `test_us1409_ca02_proyecto_ajeno_rechazado_sin_efectos`

### `tests/test_migrations.py`

US-18.03 — Gestionar migraciones (ver control/01_PRODUCTO/refinements/US-18.03.md).

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `CATALOG` | 18 | |
| función | `_versions(db)` | 25 |  |
| función | `_migrate_worker(path)` | 95 |  |

Tests (7): `test_us1803_ca01_cada_migracion_tiene_version`, `test_us1803_ca02_se_ejecutan_en_orden`, `test_us1803_ca03_migracion_fallida_no_queda_marcada`, `test_us1803_ca04_version_actual_consultable`, `test_us1803_catalogo_invalido_rechazado`, `test_us1803_base_de_version_futura_rechazada`, `test_us1803_migracion_concurrente_una_sola_vez`

### `tests/test_models_chat.py`

Catálogo y selección de modelos (US-50.09, US-50.10, US-22.06, US-22.07) y conversación con el modelo local con

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| función | `anyio_backend()` | 32 |  |
| función | `ollaya()` | 37 |  |
| función | `ollama()` | 43 |  |
| función | `_router(service, **settings)` | 48 |  |
| función | `_both(ollaya, ollama, **extra)` | 54 |  |
| función | `_decide(router, purpose, model)` | 58 |  |
| función | `_seed(service, router)` | 63 |  |

Tests (17): `test_us5009_ca01_muestra_modelos_detectados`, `test_us5009_ca02_elegir_uno_de_ollama_y_varios_de_ollaya`, `test_us5009_ca03_se_aplica_sin_reiniciar_y_prevalece_sobre_el_arranque`, `test_us5009_ca04_notas_del_operador_y_solo_admin`, `test_us2206_us2207_modelo_segun_el_proposito`, `test_us5010_ca01_ca02_catalogo_para_agentes`, `test_us5010_ca03_modelo_concreto_y_caida_indicada`, `test_us2210_ca01_ca02_hilo_con_contexto`, `test_us2210_ca03_hilo_privado`, `test_us2210_ca04_mensajes_conservados`, `test_us2210_ca05_sin_modelo_error_explicito`, `test_us2211_ca01_ca02_consulta_el_proyecto_con_herramientas`, `test_us2211_ca02_permisos_de_quien_pregunta`, `test_us2211_ca03_herramientas_en_el_hilo`, `test_us2211_ca04_rondas_limitadas`, `test_us2210_por_mcp`, `test_us2211_ca04_modelo_que_insiste_en_herramientas_es_error`

### `tests/test_projects.py`

US-01.01, US-01.02, US-01.03 — ver control/01_PRODUCTO/refinements/.

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| función | `_registered(data_dir)` | 18 |  |

Tests (20): `test_us0101_ca01_crea_exactamente_un_proyecto`, `test_us0101_ca02_nombre_vacio_rechazado_identifica_campo`, `test_us0101_limites_de_nombre_y_formato_de_key`, `test_us0101_ca03_duplicado_no_se_crea`, `test_us0101_ca03_creacion_concurrente_mismo_key`, `test_us0101_ca04_fallo_de_almacenamiento_no_deja_registro_parcial`, `test_us0101_ca05_proyecto_creado_se_abre_desde_listado`, `test_us0101_contexto_fisico_creado`, `test_us0101_no_admin_no_puede_crear`, `test_us0102_ca01_listado_solo_proyectos_con_acceso`, `test_us0102_ca02_abrir_carga_contexto`, `test_us0102_ca04_proyecto_inexistente_o_sin_base`, `test_us0102_ca05_cambiar_de_proyecto_no_mezcla_datos`, `test_us0102_no_miembro_recibe_not_found`, `test_us0103_ca01_parametros_con_valor_actual`, `test_us0103_ca02_invalidos_rechazados_sin_guardar`, `test_us0103_ca03_configuracion_persistida`, `test_us0103_ca04_cambios_que_requieren_recarga`, `test_us0103_ca05_configuracion_exclusiva_del_proyecto`, `test_us0103_member_no_puede_modificar`

### `tests/test_realtime.py`

EPIC-06 (Kanban), EPIC-21 (eventos y WebSocket) y EPIC-30 (API REST v1) contra ACM real por HTTP.

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| función | `anyio_backend()` | 26 |  |
| función | `_seed(acm, project, stories)` | 30 |  |
| función | `_ready_in_progress(b, project, story)` | 41 |  |
| función | `_http(acm, token)` | 46 |  |
| función | `async ws(acm, token, after)` | 52 |  |
| función | `async _events(conn, n, *, types, timeout)` | 59 | Los siguientes `n` eventos de dominio (opcionalmente solo de ciertos tipos), en orden de llegada. |
| función | `async _silence(conn, seconds, *, types)` | 72 | Eventos recibidos durante `seconds` (para comprobar que NO llega nada). |
| constante | `DOMAIN` | 83 | |
| constante | `ENDPOINTS` | 371 | |

Tests (25): `test_us0602_ca01_ca02_cambio_permitido_y_registrado`, `test_us0602_ca03_transiciones_no_permitidas`, `test_us0602_done_solo_tras_verificar`, `test_us0602_ca04_el_tablero_refleja_el_estado`, `test_us0601_ca01_ca02_una_columna_por_historia_con_datos`, `test_us0601_ca03_solo_el_contexto_seleccionado_y_varios_a_la_vez`, `test_us0601_ca03_proyecto_ajeno_no_se_muestra`, `test_us0601_ca04_historia_inexistente_no_aparece`, `test_us2101_ca01_ca02_cambio_genera_evento_con_contexto`, `test_us2101_ca03_operacion_revertida_no_publica`, `test_us0603_ca01_ca02_agente_cambia_y_los_clientes_lo_reciben`, `test_us0603_agente_por_stdio_en_otro_proceso`, `test_us0603_ca04_evento_duplicado_no_modifica_dos_veces`, `test_us2102_ca01_ca02_solo_proyectos_autorizados`, `test_us2102_actividad_solo_para_admin`, `test_us2102_ca03_desconexion_libera_la_suscripcion`, `test_us2102_ws_exige_autenticacion`, `test_us2103_ca01_ca02_ca03_ca04_reanuda_sin_perder_ni_duplicar`, `test_us2103_resync_si_los_eventos_ya_no_estan`, `test_us2103_eventos_por_rest`, `test_us3001_ca01_us3002_contrato_documentado`, `test_us3001_ca02_ca04_entradas_invalidas_formato_consistente`, `test_us3001_ca03_autorizacion_aplicada`, `test_us3003_ca01_ca02_ca03_version_en_la_ruta`, `test_us3001_lectura_completa_del_proyecto`

### `tests/test_rest_write.py`

API REST v1 de escritura (SPRINT-008): la parte servidor de US-31.09..31.12 y de los sprints (US-05.05 CA-06).

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| función | `_client(acm, principal)` | 16 |  |
| función | `_ok(resp, status)` | 20 |  |
| función | `_backlog(c)` | 25 |  |

Tests (13): `test_us3109_ca01_crear_proyecto_y_errores`, `test_us3109_ca02_configuracion_valida_todo_antes_de_guardar`, `test_us3109_ca03_solo_owner_o_admin_configuran`, `test_us3110_ca01_crear_todo_el_backlog`, `test_us3110_ca02_anadir_criterios`, `test_us3110_ca03_enlazar_confirmar_y_dividir`, `test_us3110_ca04_error_con_campo`, `test_us3111_ca01_ca02_principales_roles_y_miembros`, `test_us3111_ca03_ca04_token_una_vez_y_revocacion_inmediata`, `test_us3112_ca02_refrescar_motores_solo_admin`, `test_us0505_ca06_sprints_y_kanban_del_sprint`, `test_escrituras_rest_emiten_actividad`, `test_escritura_en_proyecto_ajeno_no_lo_revela`

### `tests/test_second_brain.py`

Segundo cerebro completo (SPRINT-008): JEV vía Ollaya (US-50.01..04) y Ollama como motor de decisión (US-22.04).

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `QUESTIONS` | 32 | |
| función | `anyio_backend()` | 44 |  |
| función | `ollaya()` | 49 |  |
| función | `ollama()` | 55 |  |
| función | `_router(service, **settings)` | 60 |  |
| función | `_jev(ollaya, **extra)` | 66 |  |
| función | `_ollama(ollama)` | 70 |  |
| función | `_request(purpose, questions)` | 74 |  |
| función | `_calls(data_dir)` | 78 |  |
| función | `_status(router)` | 86 |  |

Tests (16): `test_us5001_ca01_registra_jev_y_comprueba_salud`, `test_us5001_ca02_envia_la_clave_del_servidor`, `test_us5001_ca03_servidor_caido_o_sin_modelo_no_afecta_a_los_demas`, `test_us5001_ca04_configuracion_incompleta`, `test_us5002_ca01_acm_decide_responde_jev_calibrado`, `test_us5002_ca02_traduccion_al_contrato_de_acm`, `test_us5002_ca03_respuesta_invalida_es_engine_error`, `test_us5002_ca03_servidor_ocupado_es_no_disponible`, `test_us5003_ca01_decision_a_jev_y_resumen_a_ollama`, `test_us5003_ca02_sin_jev_decide_ollama_sin_calibrar`, `test_us5003_ca03_orden_por_proyecto_sin_reiniciar`, `test_us5004_ca01_ca02_cada_decision_registra_su_motor`, `test_us2204_ca01_registra_generacion_y_decision`, `test_us2204_ca02_solo_elige_entre_las_opciones`, `test_us2204_ca03_el_gate_no_acepta_a_ollama`, `test_us2204_ca04_respuesta_fuera_de_opciones_es_error`

### `tests/test_skills.py`

US-15.01, US-15.04..US-15.10 — catálogo de skills y extensión MCP Skills (SEP-2640).

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `ANY` | 26 | |
| constante | `OFFICIAL` | 27 | |
| clase | `SkillsListRequest` (Request[SkillsListParams, Literal['skills/list']]) | 30 |  |
| clase | `SkillsGetRequest` (Request[SkillsGetParams, Literal['skills/get']]) | 35 |  |
| función | `anyio_backend()` | 41 |  |
| función | `skills_dir(tmp_path)` | 46 |  |
| función | `async client(service, skills_dir)` | 53 |  |
| función | `_write_skill(root, folder, body, **fm)` | 58 |  |
| función | `async _tool_names(client)` | 71 |  |
| función | `_skill_text(name)` | 75 |  |
| constante | `TOOL_RE` | 240 | |

Tests (31): `test_us1501_ca01_id_y_version`, `test_us1501_ca02_ca03_capacidades_y_dependencias`, `test_us1501_ca04_skill_invalida_no_se_activa`, `test_us1501_ca04_rechazo_en_cascada`, `test_us1504_ca01_instructions_piden_cargar_skills`, `test_us1504_ca02_capacidades_declaradas`, `test_us1504_ca03_skills_list`, `test_us1505_ca01_leer_cada_archivo_y_verificar_digest`, `test_us1505_ca02_skills_get_y_error`, `test_us1505_ca03_herramientas_de_respaldo`, `test_us1506_ca01_version_en_frontmatter`, `test_us1506_ca02_digest_cambia_solo_si_cambia_el_contenido`, `test_us1506_ca03_notificacion_al_cambiar_catalogo`, `test_us1506_recargar_requiere_admin`, `test_us1507_ca01_skills_oficiales_versionadas_con_el_codigo`, `test_us1507_ca02_skill_retirada_desaparece`, `test_us1507_ca03_descargas_auditadas`, `test_us1508_ca01_acm_schema_valida`, `test_us1508_ca02_ca03_documenta_exactamente_las_herramientas`, `test_us1508_ca04_modelo_y_flujo`, `test_us1509_ca01_acm_invest_valida`, `test_us1509_ca02_ca03_invest_y_criterios_binarios`, `test_us1509_us1510_ca04_solo_herramientas_existentes`, `test_us1510_ca01_acm_discovery_valida`, `test_us1510_ca02_ca03_preguntas_y_registro`, `test_us1413_ca01_instructions_breves_y_remiten_al_proceso`, `test_us1413_ca02_mismo_contenido_por_herramienta_recurso_y_prompt`, `test_us1413_ca02_leer_las_skills_queda_auditado`, `test_us1413_ca03_acm_workflow_describe_el_proceso_de_principio_a_fin`, `test_us1413_ca03_acm_workflow_solo_cita_herramientas_existentes`, `test_us1413_ca03_pasos_de_acm_next_work_existen`

### `tests/test_sprints.py`

Sprints (EPIC-05): US-05.02..05.09 contra el dominio real y el servidor MCP (SQLite en un directorio temporal).

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| función | `anyio_backend()` | 21 |  |
| función | `backlog(service)` | 26 |  |
| función | `sprints(backlog)` | 40 |  |
| función | `_new(sprints, capacity, name)` | 44 |  |
| función | `_done(backlog, sid)` | 48 |  |
| función | `_closing(sprints, backlog)` | 96 |  |

Tests (22): `test_us0502_ca01_identificador_y_objetivo`, `test_us0502_ca02_historias_vinculadas`, `test_us0502_ca04_estados_definidos`, `test_us0502_un_solo_sprint_activo`, `test_us0503_ca01_terminadas_y_no_terminadas`, `test_us0503_ca02_trasladar_no_terminadas`, `test_us0503_ca02_sin_destino_vuelven_al_backlog`, `test_us0503_ca03_resumen_del_sprint`, `test_us0503_ca04_historial_conservado`, `test_us0504_ca01_objetivo_fechas_y_capacidad`, `test_us0504_ca02_fechas_invalidas`, `test_us0504_ca03_capacidad_fuera_de_rango`, `test_us0505_ca01_ca05_asignar_y_retirar`, `test_us0505_ca02_una_historia_un_sprint_abierto`, `test_us0505_ca03_terminales_rechazadas`, `test_us0505_ca04_aviso_si_no_esta_ready`, `test_us0506_ca01_ca02_metricas_conservadas`, `test_us0507_us0508_capacidad_y_carga`, `test_us0509_ca01_ca02_sobrecarga_detectada_antes_de_iniciar`, `test_us0509_sprint_vacio_no_se_inicia`, `test_us0502_sprints_por_mcp_con_eventos`, `test_us0502_cancelar_por_mcp`

### `tests/test_supervisor.py`

Supervisor ágil autónomo (SPRINT-008): US-13.14, US-13.15, US-04.10, US-04.14, US-04.15 y US-43.08.

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `NO` | 28 | |
| constante | `YES` | 29 | |
| constante | `SMALL` | 30 | |
| constante | `LARGE` | 36 | |
| función | `ollaya()` | 45 |  |
| función | `ollama()` | 52 |  |
| función | `_setup(service, **settings)` | 57 |  |
| función | `_jev(ollaya)` | 69 |  |
| función | `_ollama(ollama)` | 73 |  |
| función | `_codes(run, target)` | 77 |  |
| función | `_action(run, type_, target)` | 81 |  |
| función | `_age(data_dir, story_id, iso)` | 85 |  |
| función | `_decides(ollaya)` | 92 |  |

Tests (15): `test_us1314_ca01_revisa_historias_sprints_y_kanban`, `test_us1314_ca02_juicio_delegado_con_motor_y_calibracion`, `test_us1314_ca03_no_repite_revisiones_sin_cambios`, `test_us1314_ca04_informe_con_modelo_local`, `test_us1314_ca04_informe_sin_modelo`, `test_us1315_ca01_solo_acciones_seguras`, `test_us1315_ca02_calibrado_y_umbral`, `test_us1315_ca03_auditada_como_supervisor_y_reversible`, `test_us1315_ca04_modos_apagado_proponer_aplicar`, `test_us1315_devuelve_a_planned_y_saca_canceladas`, `test_us0410_ca01_historia_grande_o_no_testeable`, `test_us0414_ca01_evalua_invest`, `test_us0415_ca01_criterios_vagos`, `test_us4308_ca01_prediccion_de_riesgo`, `test_us1315_ca01_accion_desconocida_nunca_figura_como_aplicada`

### `tests/test_watchdog.py`

EPIC-13 — Watchdog: US-13.03 (salud), 13.05 (integridad), 13.06 (continuo), 13.07 (historias sin criterios),

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| función | `anyio_backend()` | 31 |  |
| función | `_seed(service, project)` | 35 |  |
| función | `_watchdog(service, router)` | 47 |  |
| función | `_break_foreign_key(data_dir, project)` | 52 |  |
| función | `_repair_foreign_key(data_dir, project)` | 60 |  |
| función | `_corrupt_page_header(data_dir, service, project)` | 67 | Corrompe la cabecera de una página B-tree (determinista: SQLite no puede leer la base). |

Tests (22): `test_us1305_ca01_detecta_relaciones_rotas`, `test_us1305_ca01_detecta_base_danada`, `test_us1305_ca02_us1311_ca01_ca03_escrituras_bloqueadas_sin_efectos`, `test_us1311_ca02_bloqueo_explicado`, `test_us1305_ca03_reparada_se_levanta_la_cuarentena`, `test_us1307_ca01_historia_sin_criterios_detectada`, `test_us1307_ca02_evaluada_por_el_motor_de_decision`, `test_us1307_ca03_historia_completa_sin_hallazgos`, `test_us1307_motor_no_calibrado_pide_revision`, `test_us3511_ca01_watchdog_consume_la_interfaz`, `test_us1310_ca01_reglas_del_semaforo`, `test_us1310_ca02_ca03_indicadores_del_proyecto`, `test_us1312_ca01_ca02_ca03_auditoria_completa_por_mcp`, `test_us1313_ca01_ca02_ca03_historico`, `test_us1313_ca04_historico_aislado_por_proyecto`, `test_us1306_ca01_se_ejecuta_periodicamente`, `test_us1306_ca02_fallo_en_un_proyecto_no_detiene_a_los_demas`, `test_us1306_ca03_intervalo_configurable_y_solo_admin`, `test_us1303_ca01_ca02_componentes_con_estado`, `test_us1303_ca03_componente_degradado_identificado`, `test_us1303_ca04_informacion_actualizada`, `test_us1303_solo_admin`

### `tests/test_webui.py`

SPRINT-007 — interfaz web (e2e con Chromium contra ACM real): US-31.06/07/08, US-06.06/07, US-31.01/02/04,

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `REQUIRED` | 27 | |
| constante | `LOCAL_CHROMIUM` | 28 | |
| función | `_unavailable(reason)` | 31 |  |
| función | `browser()` | 38 |  |
| función | `seed(acm)` | 50 |  |
| función | `ui(acm, browser)` | 76 |  |
| función | `login(acm, browser, token, **context)` | 83 |  |
| función | `go(page, acm, route)` | 92 |  |
| función | `in_thread(fn)` | 96 | Ejecuta un agente MCP async en otro hilo: el hilo del test ya tiene el bucle de Playwright. |
| función | `card(page, project, story)` | 117 |  |
| constante | `CONTRAST_JS` | 190 | |

Tests (23): `test_us3106_ca01_cada_dato_tiene_vista`, `test_us3106_ca02_navegar_desde_una_historia`, `test_us3106_ca03_documentacion_de_acm`, `test_us3106_ca04_solo_lo_accesible`, `test_us3107_ca01_contraste_aa_en_ambos_temas`, `test_us3107_ca02_nunca_solo_color`, `test_us3107_ca03_elegir_tema`, `test_us3107_ca04_mover_con_teclado`, `test_us3108_ca01_cambio_de_agente_sin_recargar`, `test_us3108_ca02_indicador_de_conexion`, `test_us3108_ca03_reconexion_recupera_los_cambios`, `test_us0607_ca01_elegir_proyectos`, `test_us0607_ca02_color_y_nombre_del_proyecto`, `test_us0607_ca03_mezclados_o_por_carril`, `test_us0607_ca04_arrastrar_permitido_y_rechazo`, `test_us0606_ca01_ca02_ca03_abrir_tarjeta_con_contexto`, `test_us3104_us2109_feed_en_vivo_de_herramientas`, `test_us3101_us3102_consola_filtrable`, `test_us4503_panel_global_de_varios_proyectos`, `test_us4502_acceder_a_elementos_desde_el_panel`, `test_us0102_ca03_proyecto_activo_identificado`, `test_us0102_ca04_proyecto_inexistente_informa_y_no_queda_seleccionado`, `test_ui_sin_errores_de_consola_y_cabeceras_de_seguridad`

### `tests/test_webui_agents.py`

SPRINT-009 — la interfaz para los agentes (e2e con Chromium contra ACM real): entrada local sin token (US-14.12

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| función | `local_ui(tmp_path, browser)` | 28 | ACM en modo local (como `acm serve --local`) y un navegador que NO tiene ningún token. |

Tests (5): `test_us1412_ca04_la_interfaz_local_entra_sola`, `test_us1412_ca04_con_tokens_sigue_pidiendolos`, `test_us1415_ca01_ca02_ca03_aprobar_y_rechazar_en_tiempo_real`, `test_us1415_ca04_expulsar_a_un_agente_desde_miembros`, `test_us1417_ca03_el_kanban_muestra_el_agente_asignado`

### `tests/test_webui_ops.py`

SPRINT-008 — operar ACM desde la interfaz (e2e con Chromium contra ACM real): US-31.09..31.12, sprints (US-05.02,

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| función | `ui(acm, browser)` | 28 |  |
| función | `ai(tmp_path, browser)` | 36 |  |
| función | `form(page, name)` | 51 |  |
| función | `open_form(page, label)` | 55 |  |

Tests (13): `test_us3109_ca01_crear_proyecto_desde_el_panel`, `test_us3109_ca02_editar_configuracion`, `test_us3109_ca03_miembro_no_edita_configuracion`, `test_us3110_ca01_ca04_crear_backlog_desde_la_interfaz`, `test_us3110_ca02_anadir_criterios_desde_la_ficha`, `test_us3110_ca03_enlazar_confirmar_y_dividir`, `test_us3111_ca01_ca02_principales_y_miembros`, `test_us3111_ca03_ca04_token_una_vez_y_revocar`, `test_us3112_ca01_ca02_ca03_motores_desde_la_interfaz`, `test_us0502_us0505_us0509_us0503_sprint_completo`, `test_us1314_ca05_us1315_ca03_informe_acciones_y_deshacer`, `test_us5009_modelos_desde_la_interfaz`, `test_us2210_us2211_asistente_del_proyecto`

### `tests/test_work.py`

SPRINT-009 — reparto de trabajo entre agentes: US-14.16 (pedir trabajo) y US-14.17 (asignación con caducidad).

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| función | `anyio_backend()` | 27 |  |
| función | `local(data_dir)` | 32 |  |
| función | `backlog(local)` | 46 |  |
| función | `_stories(backlog, n, ready)` | 54 |  |
| función | `work(backlog)` | 62 |  |
| función | `_active_sprint(backlog, stories)` | 66 |  |
| función | `_expire(local, item)` | 73 |  |

Tests (16): `test_us1416_ca01_responde_lo_que_toca_segun_el_estado`, `test_us1416_ca01_avanza_con_el_estado_de_la_historia`, `test_us1416_ca01_sprint_planificado_sin_iniciar`, `test_us1416_ca02_dos_agentes_nunca_reciben_lo_mismo`, `test_us1416_ca02_sin_trabajo_libre_espera`, `test_us1416_ca02_consultar_sin_asignar`, `test_us1416_ca03_historia_asignada_a_otro_no_se_cambia`, `test_us1416_acceso_de_solo_lectura_no_recibe_trabajo`, `test_us1417_ca01_la_asignacion_se_renueva_al_tocar_la_historia`, `test_us1417_ca01_caducada_queda_libre_para_otro`, `test_us1417_ca01_plazo_configurable`, `test_us1417_ca02_liberar_el_trabajo`, `test_us1417_ca02_pedir_otra_cosa_libera_lo_que_ya_no_corresponde`, `test_us1417_ca03_mismo_cliente_en_dos_sesiones_no_se_pisa`, `test_us1417_ca03_se_ve_quien_trabaja_en_que`, `test_us1416_flujo_del_agente_por_mcp`

## Herramientas de control (`control/tools`)

### `control/tools/code_inventory.py`

Inventario de código de ACM → `control/05_CODIGO/code_reference.md` (generado; no editar a mano).

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `ROOT` | 23 | |
| constante | `OUT` | 24 | |
| constante | `INVENTORY` | 25 | |
| constante | `PY_DIRS` | 26 | |
| constante | `TS_DIR` | 27 | |
| constante | `SKIP_PARTS` | 28 | |
| constante | `HEADER` | 29 | |
| función | `rel(p)` | 35 |  |
| función | `first_line(doc)` | 39 |  |
| función | `signature(fn)` | 43 |  |
| función | `decorator_route(fn)` | 56 |  |
| función | `python_file(path)` | 67 |  |
| constante | `TS_EXPORT` | 127 | |
| función | `ts_kind(kind, name, path)` | 132 |  |
| función | `ts_file(path)` | 144 |  |
| función | `code_files()` | 161 |  |
| función | `render()` | 169 |  |
| función | `undocumented()` | 192 |  |
| función | `headerless()` | 197 |  |
| función | `main()` | 209 |  |

### `control/tools/derive_backlog.py`

Genera el backlog UNIFICADO de ACM a partir de dos fuentes de producto (ADR-010).

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `ROOT` | 32 | |
| constante | `OUT_DIR` | 33 | |
| constante | `SRC_A_REL` | 34 | |
| constante | `SRC_B_REL` | 35 | |
| constante | `SRC_A` | 36 | |
| constante | `SRC_B` | 37 | |
| constante | `STATUS_FILE` | 39 | |
| constante | `ALLOWED_STATUS` | 40 | |
| constante | `STATUS` | 42 | |
| constante | `DEDUPE_FILE` | 44 | |
| constante | `REFINEMENTS_DIR` | 46 | |
| constante | `READY_SECTIONS` | 47 | |
| constante | `NEW_EPICS` | 52 | |
| constante | `FEATURE_MAP` | 66 | |
| constante | `MVP_EPICS` | 121 | |
| constante | `POST_MVP_A_STORIES` | 123 | |
| constante | `B_MVP_EPICS` | 136 | |
| constante | `B_POST_MVP_FEATURES` | 137 | |
| constante | `DUP_THRESHOLD` | 142 | |
| clase | `Story` (—) | 147 |  |
| clase | `Feature` (—) | 167 |  |
| clase | `Epic` (—) | 175 |  |
| clase | `Item` (—) | 185 |  |
| constante | `A_EPIC` | 192 | |
| constante | `A_FEAT` | 193 | |
| constante | `A_US` | 194 | |
| constante | `A_CA` | 195 | |
| constante | `A_SECTION` | 196 | |
| constante | `A_ROLE` | 197 | |
| función | `parse_a(text)` | 200 |  |
| constante | `B_EPIC` | 248 | |
| constante | `B_FEAT` | 249 | |
| constante | `B_US` | 250 | |
| constante | `B_TECH` | 251 | |
| constante | `B_SPIKE` | 252 | |
| constante | `BOLD` | 253 | |
| función | `parse_b(text)` | 256 |  |
| constante | `STOP` | 306 | |
| función | `words(s)` | 311 |  |
| función | `jaccard(a, b)` | 317 |  |
| función | `unify(a_epics, b_epics)` | 321 |  |
| función | `apply_dedupe(epics, errors)` | 390 |  |
| función | `load_refinements(epics, errors)` | 414 |  |
| constante | `REPO_ROOT` | 446 | |
| constante | `TEST_REF` | 447 | |
| función | `check_test_refs(epics, errors)` | 450 | Trazabilidad historia → test: cada test citado en "Pruebas" debe existir en el repositorio. |
| función | `missing_sections(s)` | 463 |  |
| función | `status_of(s)` | 467 | Estado efectivo: explícito en item_status.json > fusionada (CANCELLED) > READY calculado > PLANNED. |
| constante | `HEADER` | 479 | |
| función | `stories_of(e)` | 483 |  |
| función | `active(stories)` | 487 | Historias vivas: excluye las fusionadas por duplicado (sus criterios ya están en la historia destino). |
| función | `epic_scope(e)` | 492 |  |
| función | `feat_scope(f)` | 496 |  |
| función | `origin_label(e)` | 500 |  |
| función | `render_epics(epics)` | 506 |  |
| función | `render_features(epics)` | 524 |  |
| función | `render_stories(epics)` | 536 |  |
| función | `render_backlog(epics, techs, spikes)` | 582 |  |
| función | `render_tech(techs, spikes)` | 618 |  |
| función | `render_mapping(b_epics, mapping)` | 628 |  |
| función | `main()` | 644 |  |

### `control/tools/evidence.py`

Genera la matriz de evidencia criterio de aceptación ↔ test de un sprint.

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `REF_LINE` | 25 | |
| constante | `PENDING_LINE` | 26 | |
| constante | `CA_CODE` | 27 | |
| función | `junit_results(path)` | 30 | ({'módulo::test': 'PASS'/'FAIL'/'SKIP'}, nº de casos). Un test parametrizado falla si falla un caso. |
| función | `main(sprint, junit)` | 47 |  |

