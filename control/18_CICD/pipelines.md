# Pipelines

## CI — `.github/workflows/ci.yml` (2026-09-30)
Disparadores: `push` y `pull_request`. Pasos:
1. `uv` + Python 3.11.
2. `pip install -e .[dev]`.
3. `ruff check src tests`.
4. `pytest -q`.
5. `python3 control/tools/derive_backlog.py --check`.

Estado: primera ejecución en GitHub **success** ([run #1](https://github.com/NoaR-es/ACM/actions/runs/36758248042), commit `04f32c3`).
CD: MISSING (sin despliegue).
