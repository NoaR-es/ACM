# Endpoints HTTP (SPRINT-006)

| Método | Ruta | Propósito | Autenticación | Tests |
|--------|------|-----------|---------------|-------|
| GET | `/api/health` | Salud mínima pública | Ninguna | `tests/test_app.py` |
| POST/GET | `/mcp/` | Servidor MCP (Streamable HTTP) | Bearer (ADR-017) | `tests/test_app.py`, `tests/test_auth.py` |
| * | `/api/v1/...` | API REST v1 (`rest_api.md`) | Bearer | `tests/test_realtime.py` |
| WS | `/api/v1/ws` | Eventos en tiempo real (`09_MENSAJERIA/event_schemas.md`) | Primer mensaje con token | `tests/test_realtime.py` |
