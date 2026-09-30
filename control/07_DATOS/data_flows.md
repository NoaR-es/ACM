# Data flows

**Estado del área:** ACTIVE (SPRINT-007).

```text
Agente (MCP HTTP/stdio) ─┐
Navegador (REST v1) ─────┼─► servicios de dominio ─► project.db / acm.db (COMMIT)
CLI ─────────────────────┘            │
                                      └─► tabla events (acm.db, tras el COMMIT) ─► WebSocket ─► navegador (invalida y relee por REST)
Cada invocación MCP/REST ─► mcp_audit (acm.db)
```
Bases y tablas: `databases.md`. Eventos: `../09_MENSAJERIA/events.md`.
