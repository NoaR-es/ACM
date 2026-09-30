# Utilidades

## control/tools/derive_backlog.py
- **Entradas:** `control/01_PRODUCTO/backlog_completo_v1.md` (fuente A) y `control/01_PRODUCTO/product_definition_v2.md` (fuente B).
- **Unificación:** `FEATURE_MAP` (feature B → épica unificada), `NEW_EPICS` (49..53), marca de solapamientos por Jaccard (`DUP_THRESHOLD`).
- **Salida:** `epics.md`, `features.md`, `user_stories.md`, `backlog.md`, `technical_stories.md`, `id_mapping.md` en `01_PRODUCTO/`.
- **Modos:** sin argumentos regenera; `--check` compara sin escribir.
- **Exit codes:** 0 OK · 1 inventarios desincronizados · 2 violación de integridad (IDs duplicados, historia o feature fuera de su épica, épica o feature vacía, historia sin enunciado, `FEATURE_MAP` incompleto, historia MVP de B en épica no MVP, A sin 48 épicas).
- **Efectos secundarios:** sobrescribe los 5 archivos generados (solo en modo regenerar).
- **Dependencias:** solo stdlib de Python ≥ 3.10.
- **Invariante:** la clasificación MVP está en `MVP_EPICS`/`POST_MVP_FEATURES` (ADR-010).
