# Utilidades

## control/tools/derive_backlog.py
- **Entrada:** `control/01_PRODUCTO/product_definition_v2.md`.
- **Salida:** `epics.md`, `features.md`, `user_stories.md`, `backlog.md`, `technical_stories.md` en `01_PRODUCTO/`.
- **Modos:** sin argumentos regenera; `--check` compara sin escribir.
- **Exit codes:** 0 OK · 1 inventarios desincronizados · 2 violación de integridad (IDs duplicados, historia fuera de su épica, épica/feature vacía, historia sin enunciado).
- **Efectos secundarios:** sobrescribe los 5 archivos generados (solo en modo regenerar).
- **Dependencias:** solo stdlib de Python ≥ 3.10.
- **Invariante:** la clasificación MVP está en `MVP_EPICS`/`POST_MVP_FEATURES` (ADR-009).
