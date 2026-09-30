# Funciones públicas (backend)

Actualizado: 2026-09-30 (SPRINT-007). Métodos de servicios: `services.md`. Herramientas MCP (46): `06_API/mcp_server.md`. Rutas REST (24): `06_API/rest_api.md`. Todas las firmas: `code_reference.md`.

| Función | Archivo | Entrada → salida | Efectos secundarios / errores |
|---------|---------|------------------|-------------------------------|
| `main(argv)` | `__main__.py` | argumentos CLI → código de salida | arranca uvicorn o stdio; `principal`/`token create` escriben en la base y se auditan (`cli:*`) |
| `build_service(settings)` | `app.py` | `Settings` → `ProjectService` | crea/migra la base global; da de alta `ACM_PRINCIPAL` como admin |
| `build_engines(service, settings)` | `app.py` | → `EngineRouter` | registra reglas y, si hay `ACM_OLLAMA_URL`+`MODEL`, Ollama; INVALID_ARGUMENT si solo uno |
| `transport_security(settings)` | `app.py` | → `TransportSecuritySettings` | Host/Origin permitidos: locales + `ACM_ALLOWED_HOSTS` (TD-002) |
| `create_app(settings)` | `app.py` | → FastAPI | monta `/api/health`, `/api/v1/ws`, `/api/v1`, `/mcp`, `/`; tareas de fondo en el lifespan |
| `scheduled_watchdog`, `prune_events` (async) | `app.py` | — | bucles de fondo; un fallo va al log y no detiene el bucle |
| `request_principal()`, `request_token()` | `auth.py` | → identidad de la petición HTTP | UNAUTHENTICATED fuera de una petición autenticada |
| `validate_catalog`, `current_version`, `migrate(db, catalog)` | `db/migrations.py` | catálogo → versiones aplicadas | MIGRATION_ERROR si la base es de una versión futura o el catálogo no es consecutivo |
| `validate_project_id(value, field)` | `domain/projects.py` | → id válido | INVALID_ARGUMENT |
| `validate_changes(changes)`, `check_stored(key, value)` | `domain/config_schema.py` | cambios → cambios validados | INVALID_ARGUMENT; DATA_INTEGRITY si lo guardado es inválido |
| `redact(value)` | `domain/audit.py` | valor → copia con `token`/`secret`/`password` = `[REDACTED]` | puro |
| `hash_secret(secret)` | `domain/identity.py` | → sha256 hex | puro |
| `estimate_tokens(value)` | `domain/context.py` | texto o JSON → ⌈caracteres/4⌉ (`chars/4@v1`) | puro |
| `semaphore(findings)` | `domain/watchdog.py` | hallazgos → GREEN/AMBER/RED | puro |
| `noul`, `choice`, `score`, `story_checks` | `inference/rules.py` | → `Answer` exacta / comprobaciones de una historia | INVALID_ARGUMENT si el estado no es una historia |
| `require_calibrated(result, consumer)` | `inference/router.py` | resultado → — | FAILED_PRECONDITION si alguna respuesta no es calibrada |
| `build_mcp_server(service, principal, catalog?, engines?, token_id?)` | `mcp_server.py` | → `MCPServer` con 46 herramientas | cada invocación: auditoría + evento `activity` |
| `build_api(service, engines, catalog)` | `web_api.py` | → (sub-app REST, router WS) | — |
| `error_response(exc)` | `web_api.py` | `AcmError` → JSON + código HTTP | puro |
| `parse_frontmatter(text)` | `skills_catalog.py` | SKILL.md → frontmatter | SkillError si es inválido |
| `webui_available()` | `webui_app.py` | → ¿existe la interfaz compilada? | — |
