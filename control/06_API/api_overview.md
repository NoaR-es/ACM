# API — visión general (SPRINT-007)

| Interfaz | Consumidor | Documento | Estado |
|----------|-----------|-----------|--------|
| Servidor MCP propio (+ skills) | Agentes IA | `mcp_server.md` | IMPLEMENTED |
| API REST `/api/v1` | Interfaz web, integraciones | `rest_api.md`, contrato en `/api/v1/openapi.json` | IMPLEMENTED (SPRINT-006) |
| WebSocket `/api/v1/ws` | Interfaz web | `09_MENSAJERIA/event_schemas.md` | IMPLEMENTED (SPRINT-006) |
| Interfaz web `/` | Personas (navegador) | `../05_CODIGO/frontend.md`, `../16_DOCUMENTACION/user_documentation.md` | IMPLEMENTED (SPRINT-007, ADR-019); consume REST v1 y WS |
| `/api/health` | Comprobaciones de salud | `endpoints.md` | IMPLEMENTED (público) |
