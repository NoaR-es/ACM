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
- **No entregado:** interfaz web (TASK-000-07). CI en GitHub: success (run #1).

## SPRINT-002 — Skills y backlog por MCP (2026-09-30)
- **Goal:** cumplido. Un agente conectado por MCP obtiene las `instructions`, lista y descarga las 3 skills oficiales (extensión Skills o herramientas de respaldo) y crea requisitos, épicas, features, historias y CA en la SQLite del proyecto; cada invocación queda auditada.
- **Entregado:** 20 historias VERIFIED y 1 IMPLEMENTED (US-24.03, CA-02 depende de EPIC-21). TASK-002-01..05. 7 fusiones de duplicados más (TASK-000-10).
- **Evidencia:** 122 tests en PASS (72 nuevos); matriz CA↔test generada en `12_TESTING/sprint_002_evidence.md`; 6/6 mutaciones detectadas.
- **No entregado:** skills acm-error-analysis y acm-documentation (US-15.11/15.12, dependen de EPIC-29/25); interfaz web.
