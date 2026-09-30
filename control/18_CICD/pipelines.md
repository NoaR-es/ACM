# Pipelines

## CI — `.github/workflows/ci.yml` (2026-09-30)
Disparadores: `push` y `pull_request`. Pasos:
1. `uv` + Python 3.11.
2. `pip install -e .[dev]`.
3. `ruff check src tests`.
4. `pytest -q`.
5. `python3 control/tools/derive_backlog.py --check`.

Estado: los pasos 3–5 se ejecutaron en local (PASS). **La primera ejecución en GitHub está pendiente de comprobar.**
CD: MISSING (sin despliegue).
