# Inventario de archivos

| Path | Propósito | Tipo | Consumidores | Tests | Estado |
|------|-----------|------|--------------|-------|--------|
| CLAUDE.md | Constitución del agente | Doc | Todo agente | — | ACTIVE |
| control/01_PRODUCTO/product_definition_v1.md | Fuente de alcance del producto | Doc | derive_backlog.py | — | ACTIVE |
| control/tools/derive_backlog.py | Genera inventarios de backlog y valida integridad | Python 3.11 script (stdlib) | Agentes, futura CI | TEST-CTRL-001 | IMPLEMENTED |
