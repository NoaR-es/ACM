# Clases (backend y dobles de test)

Actualizado: 2026-09-30 (SPRINT-007). Los servicios de dominio están en `services.md`; aquí el resto. Líneas exactas: `code_reference.md`.

## Infraestructura y composición

| Clase | Archivo | Responsabilidad | Invariantes / notas |
|-------|---------|-----------------|---------------------|
| `Settings` (dataclass inmutable) | `config.py` | Configuración del proceso: `data_dir`, `principal`, `host`, `port`, `sqlite_synchronous`, `ollama_url`, `ollama_model`, `events_keep`, `watchdog_interval_s`, `allowed_hosts`. `from_env(**overrides)` lee `ACM_*` | host por defecto 127.0.0.1 |
| `Database` | `db/connection.py` | Una conexión SQLite por hilo; `write()` (BEGIN IMMEDIATE, COMMIT/ROLLBACK, 3 reintentos), `read()`, `pragmas()`, `set_synchronous()`, `close()` | WAL y `foreign_keys` verificados al abrir; activación de WAL con reintentos (BUG-001); `write()` no anidable |
| `NestedTransactionError` | `db/connection.py` | `write()` dentro de otra transacción | error de programación, no de dominio |
| `Migration` (dataclass) | `db/migrations.py` | `version`, `name`, `statements` | publicadas = inmutables; versiones consecutivas |
| `BearerAuth` | `auth.py` | Middleware ASGI: token Bearer → identidad en variables de contexto; 401 y auditoría si falla | ninguna petición sin token válido llega a la app envuelta |
| `SecureStatic` | `webui_app.py` | Sirve la interfaz compilada con CSP, `nosniff`, `no-referrer`, `DENY` | `connect-src` limitado al propio host |
| `Access` | `web_api.py` | Qué eventos puede ver un principal (`can_see`, `age`) | admin ve todo; `activity` y eventos sin proyecto solo admin |
| `StatusChange` (Pydantic) | `web_api.py` | Cuerpo de `POST …/status`: `status`, `reason` | validación → 400 INVALID_ARGUMENT |
| `SkillsListParams`, `SkillsGetParams` | `mcp_server.py` | Parámetros de `skills/list` y `skills/get` (SEP-2640) | — |
| `AcmSkillsExtension` (interna) | `mcp_server.py` | Extensión MCP Skills | `-32602` si la skill no existe |

## Errores (`domain/errors.py`, `inference/ports.py`)

`AcmError(message, field=None)` → `str()` = `CODE: [campo: ]motivo`. Subclases y código: `InvalidArgument` (INVALID_ARGUMENT), `NotFound` (NOT_FOUND), `AlreadyExists` (ALREADY_EXISTS), `Forbidden` (FORBIDDEN), `StorageError` (STORAGE_ERROR), `DataIntegrityError` (DATA_INTEGRITY), `MigrationError` (MIGRATION_ERROR), `FailedPrecondition` (FAILED_PRECONDITION), `Unauthenticated` (UNAUTHENTICATED), `EngineUnavailable` (ENGINE_UNAVAILABLE), `EngineError` (ENGINE_ERROR). La frontera MCP los convierte en `ToolError` (GAP-007); la REST en `{"error": {...}}` con el código HTTP de `web_api.HTTP_STATUS`.

## Configuración de proyecto (`domain/config_schema.py`)

| Clase | Responsabilidad |
|-------|-----------------|
| `Parameter` (dataclass) | Definición de un parámetro: clave, tipo, defecto, permitido, `requires_reload`, descripción, consumidor, validador; `describe(current)` |

## Inferencia (`inference/`)

| Clase | Archivo | Responsabilidad | Invariantes |
|-------|---------|-----------------|-------------|
| `Question`, `DecisionRequest`, `Answer`, `DecisionResult` (dataclasses inmutables) | `ports.py` | Contrato de decisión (espejo de Ollaya, ADR-006/015) | `DecisionRequest` se valida al construirse |
| `GenerationRequest`, `GenerationResult`, `EngineHealth` | `ports.py` | Contrato de generación y salud | — |
| `DecisionEngine`, `GenerationEngine` (Protocol) | `ports.py` | Puertos síncronos (ADR-016) | `runtime_checkable` |
| `Rule` (dataclass), `RulesDecisionEngine` | `rules.py` | Reglas deterministas por `purpose` (hoy `story.quality`) | respuestas exactas, `calibrated=True` |
| `OllamaClient`, `OllamaGenerationEngine` | `ollama.py` | HTTP a Ollama y motor de generación | sano solo si el modelo está instalado; respuesta vacía = ENGINE_ERROR |
| `Routed` (dataclass) | `router.py` | Resultado + `call_id` | — |

## Skills (`skills_catalog.py`)

| Clase | Responsabilidad |
|-------|-----------------|
| `SkillFile` (dataclass) | Archivo: nombre, URI, texto, digest sha256, tamaño |
| `Skill` (dataclass) | Skill: nombre, frontmatter, archivos; `uri`, `entry()` |
| `SkillError` | Motivo de rechazo de una skill |

## Dobles de test (`tests/`)

| Clase | Archivo | Qué simula |
|-------|---------|-----------|
| `FakeOllama`, `FakeOllamaState` | `fake_ollama.py` | Ollama como servidor HTTP real (modos `ok`, `empty`, `not_done`, `error500`, `not_json`) |
| `Acm` | `live.py` | ACM real por HTTP con acceso a los datos (`token()`, `audit()`) |
| `FakeJev` | `test_inference.py` | Motor de decisión con el contrato de JEV (calibrado o no, que falla o no) |
| `SpyGen` | `test_context.py` | Motor de generación que registra peticiones |
