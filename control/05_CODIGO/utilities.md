# Utilidades

Actualizado: 2026-09-30 (SPRINT-007).

## Herramientas de control (`control/tools/`)

### `control/tools/derive_backlog.py`
- **Entradas:** `01_PRODUCTO/backlog_completo_v1.md` (fuente A) y `01_PRODUCTO/product_definition_v4.md` (fuente B, v1.3); `refinements/`, `tools/dedupe.json`, `tools/item_status.json`.
- **Unificación:** `FEATURE_MAP` (feature B → épica unificada), `NEW_EPICS` (49..53), solapamientos por Jaccard (`DUP_THRESHOLD`), fusiones (`dedupe.json`, con `cross_epic`), refinamientos (READY calculado), estados validados.
- **Salida:** `epics.md`, `features.md`, `user_stories.md`, `backlog.md`, `technical_stories.md`, `id_mapping.md`.
- **Modos:** sin argumentos regenera; `--check` compara sin escribir (en CI).
- **Códigos de salida:** 0 OK; 1 inventarios desincronizados; 2 violación de integridad (IDs duplicados, épica o feature vacía, `FEATURE_MAP` incompleto, historia MVP en épica no MVP, test citado inexistente, estado no permitido…).
- **Dependencias:** solo la biblioteca estándar.

### `control/tools/evidence.py`
- `python3 control/tools/evidence.py SPRINT-00N junit.xml > 12_TESTING/sprint_00N_evidence.md`: matriz CA ↔ test con resultado de cada caso (PASS, FAIL, AUSENTE, SIN TEST, PENDIENTE). Sale con 1 si algún test citado falla o falta.

### `control/tools/code_inventory.py`
- Genera `05_CODIGO/code_reference.md` desde el código (ast para Python; exportaciones para TypeScript) y, con `--check` (en CI), exige que esté al día y que **cada archivo de código tenga fila en `file_inventory.md`**.

## Módulos puros del frontend (`web/src`) — probados con vitest

| Módulo | Funciones | Uso |
|--------|-----------|-----|
| `theme.ts` | `PALETTES`, `STATUS_ORDER`, `STATUS_LABEL`, `luminance`, `contrast`, `projectIndex`, `cssVariables` | paleta con contraste WCAG AA verificado; color estable por proyecto |
| `kanban.ts` | `visibleColumns`, `matches`, `groupByColumn`, `targets`, `canMove`, `applyStatus`, `TERMINAL` | agrupar tarjetas (una columna por historia), filtros, transiciones (READY por el gate) |
| `liveCore.ts` | `receive`, `authMessage`, `backoff`, `affectedKeys` | orden por `seq`, duplicados, reanudación, resync, qué datos recargar |
| `markdown.ts` | `renderMarkdown`, `splitFrontmatter` | Markdown saneado (sin HTML ejecutable) |
| `api.ts` | `api`, `post`, `ApiError`, `tokenStore` | cliente REST v1 con token; 401 → evento `acm:unauthenticated` |
