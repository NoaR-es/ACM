# ACM — Agile Context Manager

Memoria de estado, gobernanza y trazabilidad Agile para agentes IA, servida por su propio servidor MCP.

- **Visión y estado del proyecto:** `control/INDEX.md` (fuente de verdad del desarrollo).
- **Constitución del agente de desarrollo:** `CLAUDE.md`.

## Desarrollo

```bash
uv venv .venv --python 3.11
uv pip install --python .venv/bin/python -e ".[dev]"
.venv/bin/pytest                       # tests
.venv/bin/ruff check src tests         # lint
python3 control/tools/derive_backlog.py --check   # integridad del backlog
```

## Ejecutar

```bash
.venv/bin/acm serve --data-dir ./.acm-data        # http://127.0.0.1:8765/api/health y MCP en /mcp/
.venv/bin/acm mcp-stdio --data-dir ./.acm-data    # MCP por stdio para agentes locales
```

Sin autenticación hasta EPIC-20: por defecto solo escucha en 127.0.0.1 y el principal es `ACM_PRINCIPAL` (por defecto `local-admin`).
