# Services

**Estado del área:** ACTIVE (SPRINT-008). Un solo servicio desplegable: el proceso `acm serve` (ADR-014), con interfaz `/`, REST `/api/v1`, WebSocket `/api/v1/ws` y MCP `/mcp`; `acm mcp-stdio` es el mismo servidor MCP sobre stdio. El Watchdog periódico (con el supervisor ágil) corre dentro de `acm serve`. Servicios de dominio internos: `../05_CODIGO/services.md`.
