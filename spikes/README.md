# spikes/

Experimentos de investigación (tipo SPIKE del backlog). **No es código de producto**: no se importa desde ACM y puede
borrarse cuando sus conclusiones estén incorporadas a ADRs y al código real. Sus resultados se registran en `control/`.

| Spike | Carpeta | Cómo ejecutar | Informe |
|-------|---------|---------------|---------|
| SPIKE-001 — Concurrencia SQLite en Python | `spike_001_sqlite/` | `python3 spikes/spike_001_sqlite/bench.py` (solo stdlib; ~1 min) | `control/20_PERFORMANCE/benchmarks.md`, ADR-013 |
| SPIKE-002 — Servidor MCP propio (SDK Python) | `spike_002_mcp/` | ver abajo | `control/06_API/mcp_server.md`, ADR-014 |

SPIKE-002 necesita un entorno virtual (ignorado por Git):

```bash
uv venv spikes/.venv --python 3.11
uv pip install --python spikes/.venv/bin/python "mcp==2.2.0" uvicorn httpx websockets
spikes/.venv/bin/python spikes/spike_002_mcp/test_proto.py              # extensión Skills, instructions, stdio
spikes/.venv/bin/python spikes/spike_002_mcp/test_asgi_topology.py      # MCP + API + WebSocket en un proceso
spikes/.venv/bin/python spikes/spike_002_mcp/test_session_isolation.py  # aislamiento multi-proyecto
```
