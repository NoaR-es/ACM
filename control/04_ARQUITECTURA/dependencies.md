# Dependencias

Estado: versiones **validadas en spikes** (2026-09-30); aún no hay `pyproject.toml` de producto. Se fijarán al crear el esqueleto.

| Dependencia | Versión probada | Uso | Decisión | Validada en |
|-------------|-----------------|-----|----------|-------------|
| Python | 3.11.15 | Runtime backend | ADR-005 | SPIKE-001/002 |
| SQLite (vía `sqlite3` stdlib) | 3.45.1 | Persistencia, fuente de verdad del producto | ADR-001, ADR-011, ADR-013 | SPIKE-001 |
| mcp (SDK oficial) + mcp-types | 2.2.0 | Servidor MCP propio, extensión Skills | ADR-008, ADR-014 | SPIKE-002 |
| starlette | 1.7.0 | ASGI (montaje de MCP, rutas, WebSocket) | ADR-014 | SPIKE-002 |
| uvicorn | 0.54.0 | Servidor ASGI | ADR-014 | SPIKE-002 |
| httpx | 0.28.1 | Cliente HTTP (tests; adaptadores Ollama/Ollaya) | ADR-014/015 | SPIKE-002 |
| websockets | 17.1 | Soporte WebSocket de uvicorn y cliente de tests | ADR-014 | SPIKE-002 |
| pydantic | 2.13.5 | Modelos (dependencia del SDK) | — | SPIKE-002 |
| anyio | 4.15.1 | Concurrencia (dependencia del SDK; `to_thread` para SQLite) | ADR-013 | SPIKE-002 (sin medir con SQLite) |
| FastAPI | — (no probada) | API HTTP con OpenAPI | ADR-014 | Pendiente (esqueleto) |

Frontend: pendiente (TASK-000-07, GAP-002).
