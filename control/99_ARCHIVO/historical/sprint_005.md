# Sprint archivado (cerrado el 2026-09-30, al abrir SPRINT-006)

## SPRINT-005 — Watchdog de gobernanza

| Campo | Valor |
|-------|-------|
| Sprint ID | SPRINT-005 |
| Objetivo | Que ACM vigile por sí mismo la salud de cada proyecto: integridad de sus datos, calidad del backlog y estado de sus componentes, y que no opere sobre un estado corrupto |
| Inicio | 2026-09-30 |
| Fin | Al cumplir el Sprint Goal (sin timebox; desarrollo por agente) |
| Sprint Goal | **ACM audita cada proyecto (a demanda y periódicamente): integridad SQLite, calidad de cada historia evaluada a través de la interfaz de decisión común, y estructura del backlog. Resume el resultado en un semáforo con histórico, pone en cuarentena (sin escrituras) un proyecto con la base dañada hasta que se repare, e informa de la salud de cada componente. Cada CA verificado por tests automáticos.** |
| Historias | US-13.03, US-13.05, US-13.06, US-13.07, US-13.10, US-13.11, US-13.12, US-13.13 (refinamientos en `01_PRODUCTO/refinements/`); US-13.04 fusionada en US-13.03; cierra US-35.11 CA-01 |
| Dependencias | ADR-015 (el Watchdog consume la interfaz de decisión), ADR-011 (SQLite), SPRINT-004 |
| Riesgos | La auditoría periódica corre en el mismo proceso: con muchos proyectos grandes, `integrity_check` puede tardar (sin medir) |
| Impedimentos | IMP-004 sigue abierto (no afecta a este sprint) |
| Fuera de alcance | US-13.01/13.02 (ejecuciones de agentes: no existen); US-13.08 (el producto no tiene entidad "tarea"); US-13.09 (cambios no trazables más allá de las historias sin requisito); interfaz visual del semáforo (EPIC-30) |
| Velocidad | No se mide |

### Tasks

| ID | Tipo | Título | Historias | Estado |
|----|------|--------|-----------|--------|
| TASK-005-01 | TASK | `WatchdogService`: integridad SQLite, calidad de historias vía `EngineRouter`, estructura, semáforo, histórico (`watchdog_runs`), cuarentena y `ensure_writable`; esquema global v5 | US-13.05, 13.07, 13.10..13.13, US-35.11 | VERIFIED |
| TASK-005-02 | TASK | Auditoría periódica en el ciclo de vida de la app (`ACM_WATCHDOG_INTERVAL_S`) | US-13.06 | VERIFIED |
| TASK-005-03 | TASK | `acm_health` y herramientas MCP `acm_watchdog_run`, `acm_watchdog_history`, `acm_governance_status`; skill acm-schema 1.3.0 | US-13.03, 13.10, 13.12, 13.13 | VERIFIED |
| TASK-005-04 | TEST | Tests por CA (22 nuevos), corrupción real de la base y matriz de evidencia | todas | VERIFIED (220 tests; 8/8 mutaciones detectadas) |
| TASK-000-10 | DOCUMENTATION | Fusión US-13.04 → US-13.03 | GAP-006 | VERIFIED (parcial: 19 fusiones en total) |
| TASK-000-07 | DECISION | Decidir tooling del frontend React (GAP-002) | — | PLANNED (arrastrada) |

SPRINT-004 cerrado y archivado en `99_ARCHIVO/historical/sprint_004.md`.

### Estado de las historias (2026-09-30)

| Historia | Estado | Evidencia |
|----------|--------|-----------|
| US-13.03, 13.05, 13.06, 13.07, 13.10, 13.11, 13.12, 13.13 | VERIFIED | `12_TESTING/sprint_005_evidence.md` |
| US-35.11 (SPRINT-003) | VERIFIED | CA-01 cerrado por el Watchdog; ver el anexo de `12_TESTING/sprint_005_evidence.md` |

VERIFIED = todos los CA con test automático en PASS. DONE requiere además la revisión del operador (merge del PR).
