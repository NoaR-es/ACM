# Endpoints HTTP (SPRINT-009)

| Método | Ruta | Propósito | Autenticación | Tests |
|--------|------|-----------|---------------|-------|
| GET | `/api/health` | Salud mínima pública | Ninguna | `tests/test_app.py` |
| POST/GET | `/mcp/` | Servidor MCP (Streamable HTTP) | Bearer (ADR-017) | `tests/test_app.py`, `tests/test_auth.py` |
| * | `/api/v1/...` | API REST v1, 59 rutas (`rest_api.md`) | Bearer | `tests/test_realtime.py`, `tests/test_rest_write.py` |
| GET | `/api/local-session` | Token efímero de la interfaz local (solo `acm serve --local`): `{"token": ...}` o `{"token": null}` | Solo peticiones de este equipo con `X-ACM-Local: 1` y `Host` local | `tests/test_local_mode.py`, `tests/test_webui_agents.py` |
| WS | `/api/v1/ws` | Eventos en tiempo real (`09_MENSAJERIA/event_schemas.md`) | Primer mensaje con token | `tests/test_realtime.py` |
| GET | `/` (y `/assets/*`) | Interfaz web compilada (ADR-019) con CSP; las rutas de la app van tras `#` | Pública (los datos exigen token vía API) | `tests/test_webui.py` |
