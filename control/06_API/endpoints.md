# Endpoints HTTP

| Método | Ruta | Propósito | Autenticación | Respuesta | Tests |
|--------|------|-----------|---------------|-----------|-------|
| GET | `/api/health` | Salud: versión, versión del esquema global, nº de proyectos y PRAGMAs de SQLite; `status` = `ok` si WAL y foreign_keys están activos, si no `degraded` | Ninguna (EPIC-20); escucha en 127.0.0.1 | 200 JSON | `tests/test_app.py::test_fastapi_sirve_api_y_mcp_en_un_proceso` |
| POST/GET | `/mcp/` | Servidor MCP (Streamable HTTP) | Ninguna (EPIC-20) | protocolo MCP | idem |

Actualizado: 2026-09-30 (SPRINT-001). La API REST de proyectos es EPIC-30.
