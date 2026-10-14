# Criterios de aceptación

Los criterios viven junto a cada historia en `user_stories.md` (generado).

Medido el 2026-10-06 (SPRINT-008) sobre `user_stories.md`; historias activas (sin las fusionadas por duplicado):

| Origen | Historias | Con criterios | Criterios |
|--------|-----------|---------------|-----------|
| A (`backlog_completo_v1.md`) | 132 | 132 | 519 (incluye los absorbidos de B en fusiones) |
| B (`product_definition_v5.md`, v1.4) | 351 | 64 (fuente o refinamiento) | 192 |
| **Total** | **483** | **196** | **711** (coincide con `derive_backlog.py`: `criteria=711`) |

## Definición de READY (fuente A, *Regla de aceptación del backlog*)
Requisito → épica → feature → historia → actor → valor → precondiciones → flujo → alternativas → errores → reglas → validaciones → casos límite → criterios de aceptación → tareas → pruebas.
Historias con la cadena completa (refinamiento en `refinements/`): 98, marcadas «completo (regla READY de A)» en `user_stories.md`. El resto sigue incompleto (GAP-001).

## Definición de DONE (fuente A + CLAUDE.md §4)
Implementado + tests ejecutados + todos los CA en PASS + sin bloqueos + trazabilidad actualizada + documentación actualizada.
