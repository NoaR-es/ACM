# Mensajería (ADR-018)

| Elemento | Valor |
|----------|-------|
| Broker | Ninguno: tabla `events` de la base global SQLite |
| Productores | El dominio de cualquier proceso de ACM (HTTP, stdio, CLI) tras cada COMMIT; el servidor MCP (`activity`) |
| Consumidores | Conexiones WebSocket `/api/v1/ws`; `GET /api/v1/events` |
| Orden | Total, por `seq` (AUTOINCREMENT) |
| Entrega | Al menos una vez al reconectar con `after`; el cliente descarta `seq` ≤ último aplicado |
| Retención | Últimos `ACM_EVENTS_KEEP` (10 000); más atrás → `resync` |
| Reintentos | No aplica (el cliente vuelve a pedir desde su `seq`) |
| Dead Letter Queue | No aplica |
| Latencia | ≤ ~0,2 s (consulta por conexión) |
| Seguridad | WebSocket autenticado con el primer mensaje (token de ACM); visibilidad por principal |
