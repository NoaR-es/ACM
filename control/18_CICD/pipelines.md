# Pipelines

## CI — `.github/workflows/ci.yml` (actualizado 2026-09-30, SPRINT-007)
Disparadores: `push` y `pull_request`. Dos jobs en paralelo:

**`web`** (Node 22, directorio `web/`, ADR-019):
1. `npm ci`.
2. `npm test` (vitest).
3. `npm run build` (typecheck + build a `src/acm/webui`).
4. Bundle versionado al día: falla si el build deja cambios o archivos nuevos en `src/acm/webui` (`git status --porcelain`).

**`test`** (Python 3.11):
1. `uv` + `pip install -e .[dev]`.
2. `playwright install --with-deps chromium`.
3. `ruff check src tests`.
4. `pytest -q` con `ACM_E2E_REQUIRED=1` (los e2e no pueden saltarse).
5. `derive_backlog.py --check`.
6. `code_inventory.py --check` (control del código, petición del operador en SPRINT-007).

Historial de ejecuciones: `12_TESTING/test_results.md`.
CD: MISSING (sin despliegue).
