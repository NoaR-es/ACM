# Inventario de archivos

| Path | Propósito | Tipo | Consumidores | Tests | Estado |
|------|-----------|------|--------------|-------|--------|
| CLAUDE.md | Constitución del agente | Doc | Todo agente | — | ACTIVE |
| control/01_PRODUCTO/backlog_completo_v1.md | Fuente A del backlog (columna vertebral) | Doc | derive_backlog.py | — | ACTIVE |
| control/01_PRODUCTO/product_definition_v3.md | Fuente B: definición v1.2 (visión, TECH, SPIKE, épicas integradas) | Doc | derive_backlog.py | — | ACTIVE |
| control/99_ARCHIVO/superseded/product_definition_v2.md | Definición v1.1 | Doc | — | — | SUPERSEDED |
| .gitignore | Excluye cachés de Python, `.venv/` y `.acm-data/` | Config | git | — | ACTIVE |
| pyproject.toml | Paquete `acm`, dependencias fijadas, pytest y ruff | Config | uv/pip, CI | todos | ACTIVE |
| README.md | Instalación, pruebas y ejecución | Doc | desarrolladores | — | ACTIVE |
| .github/workflows/ci.yml | CI: ruff, pytest, derive_backlog --check | CI | GitHub Actions | — | ACTIVE (run #1 success) |
| src/acm/** | Código de producto (detalle en `modules.md`) | Python | — | tests/** | IMPLEMENTED (SPRINT-001..004) |
| src/acm/skills/*/SKILL.md | Skills oficiales servidas por MCP | Markdown | agentes MCP, `SkillCatalog` | `test_skills.py` | ACTIVE (acm-schema 1.2.0; resto 1.0.0) |
| tests/fake_ollama.py | Ollama simulado (servidor HTTP real) para los tests de EPIC-22 | Python | `test_inference.py`, `test_context.py` | — | ACTIVE |
| control/tools/evidence.py | Genera la matriz CA ↔ test de un sprint desde los refinamientos y un JUnit de pytest | Python 3.11 script (stdlib) | agentes al cerrar sprint | reproducida la matriz de SPRINT-001 | IMPLEMENTED |
| tests/** | Tests pytest, un test por CA | Python | CI | — | ACTIVE |
| control/tools/dedupe.json | Fusión de historias duplicadas (GAP-006) | Datos | derive_backlog.py | TEST-CTRL-001 | ACTIVE |
| control/01_PRODUCTO/refinements/*.md | Refinamientos READY por historia | Doc | derive_backlog.py | TEST-CTRL-001 (refs a tests) | ACTIVE |
| control/tools/item_status.json | Estados de historias/TECH/SPIKE distintos de PLANNED; validado por derive_backlog.py | Datos | derive_backlog.py | TEST-CTRL-001 | ACTIVE |
| spikes/spike_001_sqlite/bench.py | SPIKE-001: banco de concurrencia SQLite (E1–E5) | Python (stdlib) | — | autoverificable | SPIKE |
| spikes/spike_001_sqlite/results.json | Datos brutos de SPIKE-001 | Datos | 20_PERFORMANCE/benchmarks.md | — | SPIKE |
| spikes/spike_002_mcp/acm_mcp_proto.py | SPIKE-002: prototipo de servidor MCP con extensión Skills | Python (mcp 2.2.0) | tests del spike | TEST-SPIKE-002a..c | SPIKE |
| control/99_ARCHIVO/superseded/product_definition_v1.md | Definición v1.0 | Doc | — | — | SUPERSEDED |
| control/tools/derive_backlog.py | Unifica las fuentes A y B, genera los inventarios de backlog y valida integridad | Python 3.11 script (stdlib) | Agentes, futura CI | TEST-CTRL-001 | IMPLEMENTED |
