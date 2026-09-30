# Inventario de archivos

| Path | Propósito | Tipo | Consumidores | Tests | Estado |
|------|-----------|------|--------------|-------|--------|
| CLAUDE.md | Constitución del agente | Doc | Todo agente | — | ACTIVE |
| control/01_PRODUCTO/backlog_completo_v1.md | Fuente A del backlog (columna vertebral) | Doc | derive_backlog.py | — | ACTIVE |
| control/01_PRODUCTO/product_definition_v3.md | Fuente B: definición v1.2 (visión, TECH, SPIKE, épicas integradas) | Doc | derive_backlog.py | — | ACTIVE |
| control/99_ARCHIVO/superseded/product_definition_v2.md | Definición v1.1 | Doc | — | — | SUPERSEDED |
| .gitignore | Excluye cachés de Python (`__pycache__/`, `*.pyc`) y `.venv/` | Config | git | — | ACTIVE |
| control/tools/item_status.json | Estados de historias/TECH/SPIKE distintos de PLANNED; validado por derive_backlog.py | Datos | derive_backlog.py | TEST-CTRL-001 | ACTIVE |
| spikes/spike_001_sqlite/bench.py | SPIKE-001: banco de concurrencia SQLite (E1–E5) | Python (stdlib) | — | autoverificable | SPIKE |
| spikes/spike_001_sqlite/results.json | Datos brutos de SPIKE-001 | Datos | 20_PERFORMANCE/benchmarks.md | — | SPIKE |
| spikes/spike_002_mcp/acm_mcp_proto.py | SPIKE-002: prototipo de servidor MCP con extensión Skills | Python (mcp 2.2.0) | tests del spike | TEST-SPIKE-002a..c | SPIKE |
| control/99_ARCHIVO/superseded/product_definition_v1.md | Definición v1.0 | Doc | — | — | SUPERSEDED |
| control/tools/derive_backlog.py | Unifica las fuentes A y B, genera los inventarios de backlog y valida integridad | Python 3.11 script (stdlib) | Agentes, futura CI | TEST-CTRL-001 | IMPLEMENTED |
