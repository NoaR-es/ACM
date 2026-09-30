# Inventario de archivos

| Path | Propósito | Tipo | Consumidores | Tests | Estado |
|------|-----------|------|--------------|-------|--------|
| CLAUDE.md | Constitución del agente | Doc | Todo agente | — | ACTIVE |
| control/01_PRODUCTO/backlog_completo_v1.md | Fuente A del backlog (columna vertebral) | Doc | derive_backlog.py | — | ACTIVE |
| control/01_PRODUCTO/product_definition_v3.md | Fuente B: definición v1.2 (visión, TECH, SPIKE, épicas integradas) | Doc | derive_backlog.py | — | ACTIVE |
| control/99_ARCHIVO/superseded/product_definition_v2.md | Definición v1.1 | Doc | — | — | SUPERSEDED |
| .gitignore | Excluye cachés de Python (`__pycache__/`, `*.pyc`) | Config | git | — | ACTIVE |
| control/99_ARCHIVO/superseded/product_definition_v1.md | Definición v1.0 | Doc | — | — | SUPERSEDED |
| control/tools/derive_backlog.py | Unifica las fuentes A y B, genera los inventarios de backlog y valida integridad | Python 3.11 script (stdlib) | Agentes, futura CI | TEST-CTRL-001 | IMPLEMENTED |
