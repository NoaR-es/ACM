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

Modelo local opcional (Ollama) para resumir el contexto: `ACM_OLLAMA_URL=http://127.0.0.1:11434 ACM_OLLAMA_MODEL=<modelo instalado>`.
Sin él, ACM funciona con su motor de reglas y entrega el contexto sin resumir.

### Acceso por HTTP: tokens (ADR-017)

`/mcp` exige `Authorization: Bearer acm_…`. Crea el primer token en el servidor (se muestra una sola vez):

```bash
.venv/bin/acm token create local-admin --name mi-portatil --data-dir ./.acm-data
.venv/bin/acm principal create bot-ci --kind agent --data-dir ./.acm-data   # un agente con sus propias credenciales
.venv/bin/acm token create bot-ci --name ci --data-dir ./.acm-data
```

Después, un admin gestiona principales, miembros y tokens desde MCP (`acm_principal_*`, `acm_member_*`,
`acm_token_*`). En stdio no hay red: el principal es `ACM_PRINCIPAL` (por defecto `local-admin`).

Por defecto `acm serve` escucha en 127.0.0.1. Para exponerlo, ponlo detrás de un proxy con TLS (el tráfico lleva el
token; VULN-002) y declara su nombre con `ACM_ALLOWED_HOSTS=acm.midominio.com`; sin él, el SDK MCP responde 421.
