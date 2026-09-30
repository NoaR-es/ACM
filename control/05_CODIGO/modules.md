# Módulos de `src/acm` (SPRINT-001, 2026-09-30)

| Módulo | Responsabilidad | Entradas | Salidas / efectos | Invariantes | Historias | Tests |
|--------|-----------------|----------|-------------------|-------------|-----------|-------|
| `acm.config` | Configuración del proceso desde el entorno (`ACM_DATA_DIR`, `ACM_PRINCIPAL`, `ACM_HOST`, `ACM_PORT`, `ACM_SQLITE_SYNCHRONOUS`) | variables de entorno, argumentos del CLI | `Settings` inmutable | host por defecto 127.0.0.1 (sin autenticación) | — | `test_app.py` |
| `acm.db.connection` | `Database`: una conexión por hilo con PRAGMAs de ADR-013; `write()` (BEGIN IMMEDIATE, COMMIT/ROLLBACK, 3 reintentos); `read()` | ruta de la base | ficheros `.db`/`-wal`/`-shm` | WAL y `foreign_keys` verificados al abrir; `write()` no anidable | US-18.01, US-18.02 | `test_db.py` |
| `acm.db.migrations` | Catálogo validado y aplicación en orden, cada migración en su transacción junto con su registro | `Database`, catálogo | tabla `schema_migrations` | versiones consecutivas desde 1; base de versión futura rechazada | US-18.03 | `test_migrations.py` |
| `acm.db.schema` | Catálogos `GLOBAL` (principales, proyectos, pertenencias) y `PROJECT` (metadatos, config) | — | — | migraciones publicadas inmutables | US-18.03 | `test_migrations.py` |
| `acm.domain.errors` | Jerarquía `AcmError` con `code` estable (`INVALID_ARGUMENT`, `NOT_FOUND`, `ALREADY_EXISTS`, `FORBIDDEN`, `STORAGE_ERROR`, `DATA_INTEGRITY`, `MIGRATION_ERROR`) | — | `str(err)` = `CODE: [campo: ]motivo` | — | GAP-007 | `test_mcp.py` |
| `acm.domain.config_schema` | Parámetros de proyecto v1 y su validación | cambios `{parámetro: valor}` | valores validados; `DataIntegrityError` si la base tiene un valor corrupto | validar todo antes de guardar | US-01.03 | `test_projects.py` |
| `acm.domain.projects` | `ProjectService`: crear (atómico), listar por acceso, abrir, leer/modificar configuración, `system_info` | principal, `project_id`, datos | `acm.db`, `projects/<id>/project.db` | `project_id` = `key` inmutable; no revela proyectos ajenos (NOT_FOUND) | US-01.01..03, US-18.01 | `test_projects.py`, `test_db.py` |
| `acm.mcp_server` | Servidor MCP: 6 herramientas, `instructions`, errores de dominio convertidos en `ToolError` y servicio ejecutado en hilos | llamadas MCP | respuestas con `project_id` | toda herramienta de proyecto exige `project_id` | US-01.06, ADR-014 | `test_mcp.py`, `test_app.py` |
| `acm.app` | Composición FastAPI: `/api/health` y MCP montado en `/mcp` (lifespan del gestor de sesiones MCP) | `Settings` | aplicación ASGI | un proceso (ADR-014) | ADR-014 | `test_app.py` |
| `acm.__main__` | CLI `acm serve` / `acm mcp-stdio` | argumentos | proceso uvicorn o servidor stdio | — | TECH-029 (parcial) | `test_app.py::test_modo_stdio_del_cli` |
