<!-- GENERADO por control/tools/code_inventory.py a partir del código. No editar a mano: cambia el código (y sus docstrings) y regenera. -->

# Referencia de código (generada)

75 archivos. Documentación narrativa (responsabilidades, invariantes, efectos): `modules.md`, `services.md`, `classes.md`, `functions.md`, `components.md`, `hooks.md`, `frontend.md`, `tests.md`.

## Backend (`src/acm`)

### `src/acm/__init__.py`

ACM — Agile Context Manager.

### `src/acm/__main__.py`

CLI de ACM.

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| función | `main(argv)` | 20 |  |
| función | `_admin_command(args)` | 70 |  |

### `src/acm/app.py`

Composición del proceso ACM (ADR-014): FastAPI con `/api` y el servidor MCP montado en `/mcp`.

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| función | `build_service(settings)` | 34 |  |
| función | `build_engines(service, settings)` | 41 | Router de inferencia: reglas siempre; Ollama si `ACM_OLLAMA_URL` y `ACM_OLLAMA_MODEL` están configurados. |
| constante | `LOCAL_HOSTS` | 51 | |
| función | `transport_security(settings)` | 55 | Protección contra DNS rebinding del SDK MCP: solo se aceptan los Host locales y los de `ACM_ALLOWED_HOSTS`. |
| función | `async scheduled_watchdog(watchdog, settings)` | 67 | US-13.06: audita todos los proyectos cada `ACM_WATCHDOG_INTERVAL_S` segundos como el admin local. |
| función | `async prune_events(service, settings)` | 77 | ADR-018: conserva los últimos `ACM_EVENTS_KEEP` eventos; un cliente más atrasado recibe `resync`. |
| función | `create_app(settings)` | 87 |  |

Rutas (1, relativas a su montaje):

| Método | Ruta | Función | Línea | Descripción |
|--------|------|---------|-------|-------------|
| GET | `/api/health` | `health` | 118 | Salud básica: versión y PRAGMAs de la base global (ADR-013: foreign_keys activo). |

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
| clase | `Settings` (—) | 17 |  |
| método | `Settings.from_env(**overrides)` | 32 |  |

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
| constante | `GLOBAL` | 14 | |
| constante | `PROJECT` | 185 | |

### `src/acm/domain/__init__.py`

_(sin docstring de módulo)_

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
| constante | `READY_GATE_QUESTIONS` | 25 | |
| constante | `STORY_TRANSITIONS` | 33 | |
| constante | `STORY_STATUSES` | 46 | |
| constante | `READY_GATE_GAPS` | 48 | |
| constante | `REQ_RE` | 55 | |
| constante | `EPIC_RE` | 56 | |
| constante | `FEAT_RE` | 57 | |
| constante | `US_RE` | 58 | |
| constante | `TITLE_MAX` | 59 | |
| constante | `KINDS` | 60 | |
| función | `_now()` | 63 |  |
| función | `_text(value, field, *, required, max_len)` | 67 |  |
| función | `_id_list(value, field, pattern)` | 80 |  |
| función | `_num(n)` | 90 |  |
| clase | `BacklogService` (—) | 94 |  |
| método | `BacklogService.__init__(projects, decisions)` | 95 |  |
| método | `BacklogService.create_requirement(principal, project_id, title, description, requirement_id)` | 136 |  |
| método | `BacklogService.get_requirement(principal, project_id, requirement_id)` | 160 |  |
| método | `BacklogService.list_requirements(principal, project_id)` | 165 |  |
| método | `BacklogService.trace_requirement(principal, project_id, requirement_id)` | 170 | US-03.03: requisito → épicas → features → historias, y las historias que lo implementan. |
| método | `BacklogService.create_epic(principal, project_id, title, objective, scope, requirement_ids, epic_id)` | 196 |  |
| método | `BacklogService.link_epic_requirements(principal, project_id, epic_id, requirement_ids)` | 227 |  |
| método | `BacklogService.get_epic(principal, project_id, epic_id)` | 265 |  |
| método | `BacklogService.list_epics(principal, project_id)` | 269 |  |
| método | `BacklogService.confirm_epic_coverage(principal, project_id, epic_id)` | 274 | US-04.02 CA-03: el Product Owner confirma que las features activas cubren el objetivo de la épica. |
| método | `BacklogService.create_feature(principal, project_id, epic_id, title, description, feature_id)` | 293 |  |
| método | `BacklogService.split_feature(principal, project_id, feature_id, parts)` | 333 | US-04.02 CA-04: divide una feature en ≥2 features nuevas repartiendo todas sus historias. |
| método | `BacklogService.create_story(principal, project_id, feature_id, as_a, i_want, so_that, requirement_ids, acceptance_criteria, kind, technical_reason, story_id)` | 381 |  |
| método | `BacklogService.add_criteria(principal, project_id, story_id, criteria)` | 460 |  |
| método | `BacklogService.get_story(principal, project_id, story_id)` | 489 |  |
| método | `BacklogService.mark_ready(principal, project_id, story_id)` | 493 | US-04.03 CA-04: una historia incompleta no puede pasar a READY. |
| método | `BacklogService.set_status(principal, project_id, story_id, status, reason)` | 540 | US-06.02: mueve una historia a otro estado si la transición está permitida (`STORY_TRANSITIONS`). |
| método | `BacklogService.list_stories(principal, project_id)` | 574 | Todas las historias con sus requisitos y criterios (vista completa para la interfaz y el Kanban). |
| método | `BacklogService.status_history(principal, project_id, story_id)` | 580 |  |
| método | `BacklogService.audit(principal, project_id)` | 591 | Huecos de trazabilidad del backlog (US-03.03 CA-05 y verificación de estructura). |

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
| función | `validate_changes(changes)` | 101 | Valida todos los cambios antes de guardar ninguno (CA-02). Lanza InvalidArgument con el primer error. |
| función | `check_stored(key, value)` | 115 | Valida un valor leído de la base: un valor corrupto es un error de integridad, no se ignora. |

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
| constante | `PRINCIPAL_RE` | 22 | |
| constante | `PRINCIPAL_KINDS` | 23 | |
| constante | `PROJECT_ROLES` | 24 | |
| constante | `TOKEN_PREFIX` | 25 | |
| constante | `PREFIX_SHOWN` | 26 | |
| función | `_now()` | 29 |  |
| función | `hash_secret(secret)` | 33 |  |
| función | `_choice(value, options, field)` | 38 |  |
| función | `_principal_id(value, field)` | 44 |  |
| clase | `IdentityService` (—) | 50 |  |
| método | `IdentityService.__init__(projects)` | 51 |  |
| método | `IdentityService.create_principal(actor, principal_id, kind, role)` | 72 |  |
| método | `IdentityService.get_principal(actor, principal_id)` | 93 |  |
| método | `IdentityService.list_principals(actor)` | 110 |  |
| método | `IdentityService.set_global_role(actor, principal_id, role)` | 119 |  |
| método | `IdentityService.set_member(actor, project_id, principal_id, role)` | 136 |  |
| método | `IdentityService.remove_member(actor, project_id, principal_id)` | 162 |  |
| método | `IdentityService.list_members(actor, project_id)` | 194 |  |
| método | `IdentityService.create_token(actor, principal_id, name)` | 205 |  |
| método | `IdentityService.list_tokens(actor, principal_id)` | 233 |  |
| método | `IdentityService.revoke_token(actor, token_id)` | 249 |  |
| método | `IdentityService.authenticate(secret)` | 264 | Devuelve (principal_id, token_id) o lanza UNAUTHENTICATED. Se consulta en cada petición: revocar es |

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
| método | `ProjectService.__init__(data_dir, *, synchronous)` | 46 |  |
| método | `ProjectService.close()` | 59 |  |
| método | `ProjectService.ensure_principal(principal_id, role, kind)` | 67 |  |
| método | `ProjectService.create(principal_id, key, name, description)` | 98 |  |
| método | `ProjectService.list_for(principal_id)` | 195 |  |
| método | `ProjectService.project_db(project_id)` | 209 |  |
| método | `ProjectService.open(principal_id, project_id)` | 228 |  |
| método | `ProjectService.get_config(principal_id, project_id)` | 249 |  |
| método | `ProjectService.set_config(principal_id, project_id, changes)` | 253 |  |
| método | `ProjectService.ensure_writable(project_id)` | 289 | US-13.11: un proyecto con la integridad comprometida no admite escrituras hasta que el Watchdog la |
| método | `ProjectService.system_info()` | 303 |  |

### `src/acm/domain/watchdog.py`

Watchdog de gobernanza (EPIC-13).

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `SEVERITIES` | 31 | |
| constante | `INACTIVE_STORY` | 32 | |
| constante | `HISTORY_MAX` | 33 | |
| constante | `STORY_FINDINGS` | 35 | |
| constante | `STRUCTURE_FINDINGS` | 41 | |
| función | `_now()` | 48 |  |
| función | `_finding(code, severity, target, message, source, **extra)` | 52 |  |
| función | `semaphore(findings)` | 56 |  |
| clase | `WatchdogService` (—) | 65 |  |
| método | `WatchdogService.__init__(projects, backlog, engines)` | 66 |  |
| método | `WatchdogService.run(principal, project_id, trigger)` | 147 |  |
| método | `WatchdogService.run_all(principal, trigger)` | 201 | US-13.06: audita todos los proyectos. Un fallo en uno no detiene a los demás. |
| método | `WatchdogService.history(principal, project_id, limit)` | 217 |  |
| método | `WatchdogService.status(principal, project_id)` | 233 | Indicadores de gobernanza del proyecto: semáforo y recuentos de la última ejecución. |
| método | `WatchdogService.health(principal, catalog)` | 255 | Estado de cada componente, recalculado en cada llamada (CA-04). |

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

### `src/acm/inference/ollama.py`

Adaptador Ollama (EPIC-22): detección de modelos (US-22.01) y generación local (US-22.03).

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `DEFAULT_TIMEOUT_S` | 16 | |
| clase | `OllamaClient` (—) | 19 |  |
| método | `OllamaClient.__init__(base_url, *, timeout_s, transport)` | 20 |  |
| método | `OllamaClient.close()` | 26 |  |
| método | `OllamaClient.list_models()` | 48 | US-22.01: modelos instalados según el runtime; nunca se inventa uno que no aparezca aquí (CA-04). |
| método | `OllamaClient.chat(model, messages, *, max_tokens, json_schema)` | 56 |  |
| clase | `OllamaGenerationEngine` (—) | 70 |  |
| método | `OllamaGenerationEngine.__init__(client, model)` | 73 |  |
| método | `OllamaGenerationEngine.close()` | 79 |  |
| método | `OllamaGenerationEngine.health()` | 82 | Sano solo si el runtime responde y el modelo configurado está entre los detectados (US-22.01 CA-03/04). |
| método | `OllamaGenerationEngine.generate(request)` | 92 |  |

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
| método | `DecisionRequest.from_json(project_id, purpose, state, questions)` | 84 | Construye la petición desde la forma JSON que recibe la herramienta MCP `acm_decide`. |
| clase | `Answer` (—) | 97 |  |
| método | `Answer.to_json()` | 104 |  |
| clase | `DecisionResult` (—) | 115 |  |
| método | `DecisionResult.to_json()` | 122 |  |
| clase | `EngineHealth` (—) | 133 |  |
| clase | `DecisionEngine` (Protocol) | 140 |  |
| método | `DecisionEngine.supports(request)` | 144 |  |
| método | `DecisionEngine.decide(request)` | 146 |  |
| método | `DecisionEngine.health()` | 148 |  |
| clase | `GenerationRequest` (—) | 153 |  |
| clase | `GenerationResult` (—) | 162 |  |
| clase | `GenerationEngine` (Protocol) | 171 |  |
| método | `GenerationEngine.generate(request)` | 175 |  |
| método | `GenerationEngine.health()` | 177 |  |

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
| método | `EngineRegistry.list()` | 104 |  |
| clase | `EngineRouter` (—) | 117 |  |
| método | `EngineRouter.__init__(projects, registry)` | 118 |  |
| método | `EngineRouter.decide(principal, request)` | 129 |  |
| método | `EngineRouter.has_generation()` | 180 |  |
| método | `EngineRouter.generate(principal, request)` | 183 |  |
| método | `EngineRouter.calls(principal, *, project_id, limit)` | 261 | Registro de llamadas de inferencia (solo admin, como la auditoría MCP). |
| función | `_describe(failures)` | 275 |  |
| función | `require_calibrated(result, consumer)` | 279 | Un consumidor que decide automáticamente (gate) no acepta la «confianza» de un motor no calibrado (ADR-015). |

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

### `src/acm/mcp_server.py`

Servidor MCP propio de ACM (ADR-008, ADR-014).

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `SKILLS_EXTENSION` | 41 | |
| constante | `INSTRUCTIONS` | 43 | |
| clase | `SkillsListParams` (RequestParams) | 59 |  |
| clase | `SkillsGetParams` (RequestParams) | 63 |  |
| función | `build_mcp_server(service, principal, catalog, engines, token_id)` | 67 | Crea el servidor MCP. |

Herramientas MCP (46):

| Herramienta | Línea | Descripción |
|-------------|-------|-------------|
| `acm_skills_list` | 188 | Lista las skills de ACM (uri, frontmatter con versión, digest y tamaño de cada archivo). |
| `acm_skill_get` | 193 | Devuelve todos los archivos de una skill de ACM (respaldo de skills/get + resources/read). |
| `acm_skills_reload` | 205 | (admin) Relee el catálogo de skills; si cambia, notifica resources/list_changed a los suscritos. |
| `acm_project_create` | 222 | Crea un proyecto ACM con su propia base SQLite. `key` es el project_id: ^[a-z][a-z0-9-]{1,39}$. |
| `acm_project_list` | 228 | Lista los proyectos a los que tienes acceso (con su project_id). |
| `acm_project_open` | 233 | Abre un proyecto: devuelve metadatos, tu rol, versión de esquema y configuración efectiva. |
| `acm_project_config_get` | 238 | Devuelve cada parámetro de configuración del proyecto con su valor actual, por defecto y permitido. |
| `acm_project_config_set` | 244 | Modifica parámetros ({parámetro: valor}). Valida todo antes de guardar; indica cuáles requieren recarga. |
| `acm_system_info` | 250 | Estado de la plataforma: versión, esquema global, nº de proyectos, PRAGMAs y skills activas/rechazadas. |
| `acm_audit_list` | 264 | (admin) Últimas invocaciones MCP auditadas: quién, operación, argumentos, resultado, estado, duración. |
| `acm_requirement_create` | 281 | Registra un requisito (REQ-NNN). `requirement_id` opcional para importar IDs existentes. |
| `acm_requirement_list` | 298 | Lista los requisitos del proyecto. |
| `acm_requirement_trace` | 304 | Trazabilidad de un requisito: sus épicas, las features de esas épicas y las historias que lo implementan. |
| `acm_epic_create` | 312 | Crea una épica (EPIC-NN) con objetivo y alcance obligatorios, opcionalmente asociada a requisitos. |
| `acm_epic_link_requirements` | 343 | Asocia requisitos existentes a una épica. |
| `acm_epic_get` | 357 | Devuelve una épica con sus requisitos y sus features (y las historias de cada feature). |
| `acm_epic_list` | 363 | Lista las épicas del proyecto con sus features e historias. |
| `acm_epic_confirm_coverage` | 368 | Confirma que las features activas de la épica cubren su objetivo (requiere al menos una feature activa). |
| `acm_feature_create` | 376 | Crea una feature (FEAT-NN.MM) dentro de una épica. |
| `acm_feature_split` | 400 | Divide una feature en ≥2: parts=[{title, description?, story_ids}] repartiendo todas sus historias. |
| `acm_story_create` | 406 | Crea una historia (US-NN.MM): actor (as_a), acción (i_want), valor (so_that), ≥1 requisito de origen y |
| `acm_story_add_criteria` | 450 | Añade criterios de aceptación (CA-NN) a una historia. |
| `acm_story_get` | 458 | Devuelve una historia con sus requisitos de origen y criterios de aceptación. |
| `acm_story_mark_ready` | 464 | Pasa una historia de PLANNED a READY si tiene actor, acción, valor, requisito y criterios. |
| `acm_story_set_status` | 470 | Mueve una historia de estado (Kanban) si la transición está permitida. PLANNED → READY: acm_story_mark_ready. |
| `acm_story_history` | 479 | Historial de cambios de estado de una historia (quién, cuándo, de qué a qué y por qué). |
| `acm_backlog_audit` | 485 | Huecos de trazabilidad: requisitos huérfanos, épicas/features vacías, historias sin CA. |
| `acm_decide` | 491 | Delega una decisión tipada (noul = sí/no, choice = clasificar, score = puntuar) en el motor de decisión. |
| `acm_context_compact` | 508 | Contexto compacto de una historia (historia, CA, requisitos, feature, épica, historias hermanas). |
| `acm_engines_list` | 519 | Motores de inferencia registrados, su último estado, modelos detectados y preguntas que cubren las reglas. |
| `acm_engines_refresh` | 529 | (admin) Comprueba la salud de cada motor y detecta los modelos disponibles en su runtime. |
| `acm_savings_report` | 541 | (admin) Tokens ahorrados por el contexto compacto, agregados por agente y proyecto, con el método usado. |
| `acm_whoami` | 549 | Tu identidad: principal, tipo (user/agent), rol global, proyectos con su rol y tokens activos. |
| `acm_principal_create` | 554 | (admin) Da de alta un usuario o un agente (kind: user / agent; role global: admin / user). |
| `acm_principal_list` | 562 | (admin) Principales con su tipo y rol global, y los roles disponibles. |
| `acm_principal_set_role` | 567 | (admin) Cambia el rol global (admin / user). Nunca deja el sistema sin admin. |
| `acm_member_set` | 573 | (admin u owner del proyecto) Añade un miembro o cambia su rol (owner / member). |
| `acm_member_remove` | 579 | (admin u owner del proyecto) Retira a un miembro. Nunca deja el proyecto sin owner. |
| `acm_member_list` | 585 | Miembros del proyecto con su rol y tipo. |
| `acm_token_create` | 590 | (admin) Crea un token para un principal. El token completo se muestra SOLO en esta respuesta: guárdalo. |
| `acm_token_list` | 596 | Tokens (sin el secreto: solo prefijo, estado y uso). Los tuyos, o los de cualquiera si eres admin. |
| `acm_token_revoke` | 602 | Revoca un token al instante (los tuyos; los ajenos, solo un admin). |
| `acm_watchdog_run` | 608 | Auditoría de gobernanza del proyecto: integridad SQLite, calidad de historias (vía el motor de decisión) y |
| `acm_watchdog_history` | 615 | Histórico de auditorías del proyecto (más recientes primero), con sus hallazgos. |
| `acm_governance_status` | 621 | Indicadores de gobernanza: semáforo y recuentos de la última auditoría, integridad y si admite escrituras. |
| `acm_health` | 627 | (admin) Salud de cada componente: bases SQLite, catálogo de skills y motores de inferencia. |

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
| constante | `HTTP_STATUS` | 40 | |
| constante | `KANBAN_COLUMNS` | 52 | |
| constante | `WS_POLL_S` | 65 | |
| constante | `WS_AUTH_TIMEOUT_S` | 66 | |
| constante | `WS_ACCESS_REFRESH_S` | 67 | |
| función | `_error_doc(description)` | 70 |  |
| constante | `ERROR_RESPONSES` | 79 | |
| clase | `StatusChange` (BaseModel) | 88 |  |
| función | `error_response(exc)` | 93 |  |
| función | `build_api(service, engines, catalog)` | 100 | Devuelve la sub-app REST (a envolver con `BearerAuth`) y el router del WebSocket (autenticación propia). |
| clase | `Access` (—) | 438 | Qué eventos puede ver un principal (US-21.02 CA-02). Se recalcula cuando cambian pertenencias o roles. |
| método | `Access.__init__(service, principal)` | 441 |  |
| método | `Access.age()` | 451 |  |
| método | `Access.can_see(event)` | 454 |  |

Rutas (25, relativas a su montaje):

| Método | Ruta | Función | Línea | Descripción |
|--------|------|---------|-------|-------------|
| GET | `/me` | `me` | 158 | Tu identidad: principal, tipo, rol global, proyectos y tokens activos. |
| GET | `/meta` | `meta` | 164 | Versión de ACM, estados de historia, transiciones permitidas, columnas del Kanban y último evento. |
| GET | `/projects` | `projects` | 190 | Cartera: proyectos accesibles con su semáforo de gobernanza y las historias por estado. |
| GET | `/projects/{project_id}` | `project` | 196 | Metadatos del proyecto, tu rol y su configuración. |
| GET | `/projects/{project_id}/backlog` | `project_backlog` | 201 | Backlog completo: requisitos, épicas con features, historias con criterios y huecos de trazabilidad. |
| GET | `/projects/{project_id}/stories/{story_id}` | `story` | 213 | Historia con criterios, requisitos, historial de estados y transiciones permitidas. |
| POST | `/projects/{project_id}/stories/{story_id}/status` | `story_status` | 223 | Mueve la historia a otro estado permitido (DONE solo desde VERIFIED). |
| POST | `/projects/{project_id}/stories/{story_id}/ready` | `story_ready` | 234 | Gate de calidad: pasa la historia de PLANNED a READY si está completa. |
| GET | `/projects/{project_id}/requirements/{requirement_id}/trace` | `trace` | 241 | Trazabilidad de un requisito: épicas, features e historias que lo implementan. |
| GET | `/projects/{project_id}/context/{story_id}` | `compact_context` | 246 | Contexto compacto de una historia para agentes, con fuentes y tokens ahorrados. |
| GET | `/projects/{project_id}/members` | `members` | 251 | Miembros del proyecto con su rol y tipo. |
| GET | `/projects/{project_id}/config` | `config` | 256 | Parámetros de configuración del proyecto con valor, valores permitidos y quién los usa. |
| GET | `/projects/{project_id}/governance` | `governance` | 261 | Semáforo, integridad e histórico de auditorías del Watchdog. |
| POST | `/projects/{project_id}/watchdog` | `watchdog_run` | 267 | Ejecuta ahora una auditoría de gobernanza del proyecto. |
| GET | `/kanban` | `kanban` | 274 | Tablero Kanban de uno o varios proyectos: columnas, transiciones y tarjetas. |
| GET | `/activity` | `activity` | 313 | Auditoría de invocaciones (solo admin), filtrable por proyecto, principal y operación. |
| GET | `/events` | `events` | 322 | Eventos de dominio posteriores a un seq, filtrados por visibilidad. |
| GET | `/health` | `health` | 334 | Salud de cada componente: bases SQLite, catálogo de skills y motores (solo admin). |
| GET | `/engines` | `engines_list` | 339 | Motores de inferencia registrados, estado, modelos detectados y reglas disponibles. |
| GET | `/savings` | `savings` | 345 | Tokens ahorrados a los agentes por el contexto compacto (solo admin). |
| GET | `/skills` | `skills` | 350 | Catálogo de skills que ACM sirve a los agentes. |
| GET | `/skills/{name}` | `skill` | 355 | Archivos de una skill (Markdown con frontmatter). |
| GET | `/principals` | `principals` | 363 | Principales (usuarios y agentes) y roles disponibles (solo admin). |
| GET | `/tokens` | `tokens` | 368 | Tokens sin su secreto: prefijo, estado y uso. |
| WEBSOCKET | `/api/v1/ws` | `events_ws` | 376 |  |

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
| componente | `App` | 77 |

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

### `web/src/auth.tsx`

Sesión (US-31.01): token en sessionStorage, identidad desde /api/v1/me, cierre por 401 o WS 4401.

| Tipo | Nombre | Línea |
|------|--------|-------|
| componente | `AuthProvider` | 17 |
| hook | `useAuth` | 49 |
| función | `describeError` | 55 |

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

Tests (6): aplica eventos en orden y descarta duplicados; al reconectar pide lo posterior al último evento aplicado; un ready no retrocede el último seq aplicado; resync pide recargar todo; reintentos con espera exponencial acotada; un cambio de historia invalida Kanban, cartera, proyecto e historia

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

### `web/src/pages/Dashboard.tsx`

Panel general (US-45.01/45.03): todos los proyectos accesibles, su salud y la actividad en vivo.

| Tipo | Nombre | Línea |
|------|--------|-------|
| componente | `Dashboard` | 10 |

### `web/src/pages/Docs.tsx`

Documentación (US-15.08..10, US-30.02): skills que ACM sirve a los agentes, flujo de estados y referencia de la API.

| Tipo | Nombre | Línea |
|------|--------|-------|
| componente | `DocsPage` | 14 |

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

### `web/src/pages/Project.tsx`

Proyecto: resumen, backlog, requisitos, historias, Kanban, gobernanza, miembros y configuración.

| Tipo | Nombre | Línea |
|------|--------|-------|
| hook | `useBacklog` | 18 |
| componente | `ProjectPage` | 22 |

### `web/src/pages/Story.tsx`

Detalle de historia (US-06.06): enunciado, criterios, trazabilidad, estado, historial y contexto compacto.

| Tipo | Nombre | Línea |
|------|--------|-------|
| componente | `StoryPage` | 21 |

### `web/src/pages/System.tsx`

Sistema (US-13.03, US-47.01, US-35.09, EPIC-20): salud por componente, motores, ahorro, principales y tokens.

| Tipo | Nombre | Línea |
|------|--------|-------|
| componente | `SystemPage` | 37 |

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
| tipo | `StoryDetail` | 22 |
| tipo | `Requirement` | 26 |
| tipo | `Feature` | 27 |
| tipo | `Epic` | 36 |
| tipo | `Gaps` | 46 |
| tipo | `Backlog` | 47 |
| tipo | `Semaphore` | 48 |
| tipo | `Finding` | 49 |
| tipo | `WatchdogRun` | 57 |
| tipo | `Governance` | 71 |
| tipo | `PortfolioProject` | 79 |
| tipo | `Card` | 89 |
| tipo | `Kanban` | 103 |
| tipo | `Me` | 110 |
| tipo | `AcmEvent` | 118 |

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
| clase | `FakeOllamaState` (—) | 21 |  |
| función | `_app(state)` | 28 |  |
| función | `free_port()` | 58 |  |
| clase | `FakeOllama` (—) | 64 |  |
| método | `FakeOllama.__init__()` | 65 |  |

Rutas (2, relativas a su montaje):

| Método | Ruta | Función | Línea | Descripción |
|--------|------|---------|-------|-------------|
| GET | `/api/tags` | `tags` | 32 |  |
| POST | `/api/chat` | `chat` | 37 |  |

### `tests/live.py`

ACM real por HTTP para los tests: uvicorn en un hilo, con acceso directo a los datos (fixture `acm`).

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `ADMIN` | 24 | |
| clase | `Acm` (—) | 28 |  |
| método | `Acm.token(principal, name)` | 34 |  |
| método | `Acm.audit(**where)` | 37 |  |
| función | `acm(tmp_path)` | 47 |  |
| función | `async mcp(acm, token)` | 68 |  |

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
| función | `_cli(data_dir, *args)` | 320 |  |
| función | `_post_with_host(url, host, token)` | 347 |  |

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
| función | `_gen(max_tokens)` | 357 |  |

Tests (25): `test_us3510_ca01_respuesta_tipada_con_probabilidades`, `test_us3510_ca02_motor_registrado`, `test_us3510_ca03_sin_motor_error_explicito`, `test_us3510_ca03_fallback_indicado`, `test_us3510_peticion_invalida_rechazada`, `test_us3510_proyecto_ajeno_rechazado`, `test_us3511_ca01_gate_y_herramienta_usan_el_router`, `test_us3511_ca02_reglas_sin_modelo`, `test_us3511_ca03_conectar_jev_no_cambia_consumidores`, `test_us3511_gate_rechaza_motor_no_calibrado`, `test_us3511_gate_detecta_cambio_durante_la_decision`, `test_us4701_ca01_consumidores_no_dependen_de_implementacion`, `test_us4701_ca02_interfaz_abstracta`, `test_us4701_ca03_implementacion_actual_sigue_funcionando`, `test_us2201_ca01_consulta_el_runtime_configurado`, `test_us2201_ca02_modelos_detectados_identificados`, `test_us2201_ca03_runtime_inaccesible_estado_error`, `test_us2201_ca04_no_afirma_modelo_no_detectado`, `test_us2201_configuracion_incompleta_rechazada`, `test_us2203_ca01_peticion_llega_al_modelo_configurado`, `test_us2203_ca02_respuesta_vinculada_a_la_ejecucion`, `test_us2203_ca03_fallo_del_modelo_estado_error`, `test_us2203_ca04_sin_respuesta_valida_no_hay_exito`, `test_engines_refresh_solo_admin`, `test_us2201_cierre_libera_el_cliente_http`

### `tests/test_isolation.py`

US-24.01 y US-24.03 — varios proyectos con backlog y memoria independientes.

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| función | `two(service)` | 17 |  |

Tests (6): `test_us2401_ca01_multiples_proyectos`, `test_us2401_ca02_backlog_independiente`, `test_us2401_ca03_memoria_independiente`, `test_us2401_ca04_cambiar_de_proyecto_cambia_contexto`, `test_us2403_ca01_agente_de_a_no_recupera_memoria_de_b`, `test_us2403_ca03_consultas_limitadas_al_proyecto`

### `tests/test_mcp.py`

Frontera MCP: US-01.01 (errores explícitos) y US-01.06 (project_id en cada herramienta).

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `PROJECT_TOOLS` | 17 | |
| constante | `BACKLOG_TOOLS` | 18 | |
| constante | `GLOBAL_TOOLS` | 45 | |
| función | `anyio_backend()` | 68 |  |
| función | `async client(service)` | 73 |  |
| función | `_text(result)` | 78 |  |

Tests (12): `test_us0101_mcp_create_y_errores_explicitos`, `test_us0106_ca01_herramientas_de_proyecto_exigen_project_id`, `test_us0106_ca02_respuestas_incluyen_project_id`, `test_us0106_ca03_project_id_desconocido_error_explicito`, `test_us0106_ca04_instructions_explican_project_id`, `test_us1405_ca01_ca02_descubrir_herramientas`, `test_us1405_ca03_herramientas_de_proyecto_declaran_project_id`, `test_us1406_ca01_operacion_persiste`, `test_us1406_ca02_operacion_rechazada_sin_efectos`, `test_us1407_varios_proyectos_misma_instancia`, `test_us1409_ca01_sin_project_id_no_reutiliza_el_anterior`, `test_us1409_ca02_proyecto_ajeno_rechazado_sin_efectos`

### `tests/test_migrations.py`

US-18.03 — Gestionar migraciones (ver control/01_PRODUCTO/refinements/US-18.03.md).

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `CATALOG` | 18 | |
| función | `_versions(db)` | 25 |  |
| función | `_migrate_worker(path)` | 95 |  |

Tests (7): `test_us1803_ca01_cada_migracion_tiene_version`, `test_us1803_ca02_se_ejecutan_en_orden`, `test_us1803_ca03_migracion_fallida_no_queda_marcada`, `test_us1803_ca04_version_actual_consultable`, `test_us1803_catalogo_invalido_rechazado`, `test_us1803_base_de_version_futura_rechazada`, `test_us1803_migracion_concurrente_una_sola_vez`

### `tests/test_projects.py`

US-01.01, US-01.02, US-01.03 — ver control/01_PRODUCTO/refinements/.

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| función | `_registered(data_dir)` | 17 |  |

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
| constante | `ENDPOINTS` | 369 | |

Tests (25): `test_us0602_ca01_ca02_cambio_permitido_y_registrado`, `test_us0602_ca03_transiciones_no_permitidas`, `test_us0602_done_solo_tras_verificar`, `test_us0602_ca04_el_tablero_refleja_el_estado`, `test_us0601_ca01_ca02_una_columna_por_historia_con_datos`, `test_us0601_ca03_solo_el_contexto_seleccionado_y_varios_a_la_vez`, `test_us0601_ca03_proyecto_ajeno_no_se_muestra`, `test_us0601_ca04_historia_inexistente_no_aparece`, `test_us2101_ca01_ca02_cambio_genera_evento_con_contexto`, `test_us2101_ca03_operacion_revertida_no_publica`, `test_us0603_ca01_ca02_agente_cambia_y_los_clientes_lo_reciben`, `test_us0603_agente_por_stdio_en_otro_proceso`, `test_us0603_ca04_evento_duplicado_no_modifica_dos_veces`, `test_us2102_ca01_ca02_solo_proyectos_autorizados`, `test_us2102_actividad_solo_para_admin`, `test_us2102_ca03_desconexion_libera_la_suscripcion`, `test_us2102_ws_exige_autenticacion`, `test_us2103_ca01_ca02_ca03_ca04_reanuda_sin_perder_ni_duplicar`, `test_us2103_resync_si_los_eventos_ya_no_estan`, `test_us2103_eventos_por_rest`, `test_us3001_ca01_us3002_contrato_documentado`, `test_us3001_ca02_ca04_entradas_invalidas_formato_consistente`, `test_us3001_ca03_autorizacion_aplicada`, `test_us3003_ca01_ca02_ca03_version_en_la_ruta`, `test_us3001_lectura_completa_del_proyecto`

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

Tests (25): `test_us1501_ca01_id_y_version`, `test_us1501_ca02_ca03_capacidades_y_dependencias`, `test_us1501_ca04_skill_invalida_no_se_activa`, `test_us1501_ca04_rechazo_en_cascada`, `test_us1504_ca01_instructions_piden_cargar_skills`, `test_us1504_ca02_capacidades_declaradas`, `test_us1504_ca03_skills_list`, `test_us1505_ca01_leer_cada_archivo_y_verificar_digest`, `test_us1505_ca02_skills_get_y_error`, `test_us1505_ca03_herramientas_de_respaldo`, `test_us1506_ca01_version_en_frontmatter`, `test_us1506_ca02_digest_cambia_solo_si_cambia_el_contenido`, `test_us1506_ca03_notificacion_al_cambiar_catalogo`, `test_us1506_recargar_requiere_admin`, `test_us1507_ca01_skills_oficiales_versionadas_con_el_codigo`, `test_us1507_ca02_skill_retirada_desaparece`, `test_us1507_ca03_descargas_auditadas`, `test_us1508_ca01_acm_schema_valida`, `test_us1508_ca02_ca03_documenta_exactamente_las_herramientas`, `test_us1508_ca04_modelo_y_flujo`, `test_us1509_ca01_acm_invest_valida`, `test_us1509_ca02_ca03_invest_y_criterios_binarios`, `test_us1509_us1510_ca04_solo_herramientas_existentes`, `test_us1510_ca01_acm_discovery_valida`, `test_us1510_ca02_ca03_preguntas_y_registro`

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
| constante | `MVP_EPICS` | 120 | |
| constante | `POST_MVP_A_STORIES` | 122 | |
| constante | `B_MVP_EPICS` | 135 | |
| constante | `B_POST_MVP_FEATURES` | 136 | |
| constante | `DUP_THRESHOLD` | 141 | |
| clase | `Story` (—) | 146 |  |
| clase | `Feature` (—) | 166 |  |
| clase | `Epic` (—) | 174 |  |
| clase | `Item` (—) | 184 |  |
| constante | `A_EPIC` | 191 | |
| constante | `A_FEAT` | 192 | |
| constante | `A_US` | 193 | |
| constante | `A_CA` | 194 | |
| constante | `A_SECTION` | 195 | |
| constante | `A_ROLE` | 196 | |
| función | `parse_a(text)` | 199 |  |
| constante | `B_EPIC` | 247 | |
| constante | `B_FEAT` | 248 | |
| constante | `B_US` | 249 | |
| constante | `B_TECH` | 250 | |
| constante | `B_SPIKE` | 251 | |
| constante | `BOLD` | 252 | |
| función | `parse_b(text)` | 255 |  |
| constante | `STOP` | 305 | |
| función | `words(s)` | 310 |  |
| función | `jaccard(a, b)` | 316 |  |
| función | `unify(a_epics, b_epics)` | 320 |  |
| función | `apply_dedupe(epics, errors)` | 389 |  |
| función | `load_refinements(epics, errors)` | 413 |  |
| constante | `REPO_ROOT` | 445 | |
| constante | `TEST_REF` | 446 | |
| función | `check_test_refs(epics, errors)` | 449 | Trazabilidad historia → test: cada test citado en "Pruebas" debe existir en el repositorio. |
| función | `missing_sections(s)` | 462 |  |
| función | `status_of(s)` | 466 | Estado efectivo: explícito en item_status.json > fusionada (CANCELLED) > READY calculado > PLANNED. |
| constante | `HEADER` | 478 | |
| función | `stories_of(e)` | 482 |  |
| función | `active(stories)` | 486 | Historias vivas: excluye las fusionadas por duplicado (sus criterios ya están en la historia destino). |
| función | `epic_scope(e)` | 491 |  |
| función | `feat_scope(f)` | 495 |  |
| función | `origin_label(e)` | 499 |  |
| función | `render_epics(epics)` | 505 |  |
| función | `render_features(epics)` | 523 |  |
| función | `render_stories(epics)` | 535 |  |
| función | `render_backlog(epics, techs, spikes)` | 581 |  |
| función | `render_tech(techs, spikes)` | 617 |  |
| función | `render_mapping(b_epics, mapping)` | 627 |  |
| función | `main()` | 643 |  |

### `control/tools/evidence.py`

Genera la matriz de evidencia criterio de aceptación ↔ test de un sprint.

| Tipo | Nombre | Línea | Descripción |
|------|--------|-------|-------------|
| constante | `REF_LINE` | 25 | |
| constante | `PENDING_LINE` | 26 | |
| constante | `CA_CODE` | 27 | |
| función | `junit_results(path)` | 30 | ({'módulo::test': 'PASS'/'FAIL'/'SKIP'}, nº de casos). Un test parametrizado falla si falla un caso. |
| función | `main(sprint, junit)` | 47 |  |

