# Sprint Reviews

## SPRINT-000 — Inception (2026-09-30)
- **Goal:** reconstruibilidad total del proyecto desde `control/`. **Cumplido.** `control/` completo, backlog unificado y verificable, 15 ADRs, spikes con evidencia.
- **Entregado:** TASK-000-01..06, 08, 09, 11, 12, 13, SPIKE-001, SPIKE-002. Todo VERIFIED y pendiente de revisión del operador (merge).
- **No entregado:** TASK-000-07 (tooling frontend) y TASK-000-10 (solapamientos). Pasan a SPRINT-001; TASK-000-10 se hace de forma parcial.
- **Producto:** sin código de producto (esperado en un sprint de arranque).

## SPRINT-001 — Esqueleto del backend y núcleo de proyecto (2026-09-30)
- **Goal:** cumplido en el backend. Un agente MCP (HTTP o stdio) crea, lista, abre y configura proyectos, cada uno con su base SQLite.
- **Entregado:** 6 historias VERIFIED (US-01.01, 01.03, 01.06, 18.01, 18.02, 18.03) y 1 IMPLEMENTED (US-01.02, falta la UI). TASK-001-01..06.
- **Evidencia:** 50 tests en PASS; matriz CA↔test en `12_TESTING/sprint_001_evidence.md`; 6 mutaciones del código detectadas por los tests.
- **No entregado:** interfaz web (TASK-000-07); la primera ejecución de la CI en GitHub está pendiente de comprobar.
