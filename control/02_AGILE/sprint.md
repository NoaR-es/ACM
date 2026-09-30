# Sprint activo

## SPRINT-000 — Inception

| Campo | Valor |
|-------|-------|
| Sprint ID | SPRINT-000 |
| Objetivo | Establecer el sistema de control y la línea base del backlog de ACM |
| Inicio | 2026-09-30 |
| Fin | Al completar sus tareas (sprint de arranque, sin timebox) |
| Sprint Goal | Que cualquier agente pueda reconstruir qué es ACM, qué hay que hacer y qué decisiones faltan leyendo `control/` |
| Historias | Ninguna de producto (trabajo de tipo DOCUMENTATION/INFRASTRUCTURE) |
| Riesgos | Decisiones de stack no tomadas; historias sin criterios |
| Impedimentos | IMP-003 abierto (conflictos de requisitos); IMP-001 e IMP-002 cerrados |
| Velocidad | No se mide |

### Tasks

| ID | Tipo | Título | Estado |
|----|------|--------|--------|
| TASK-000-01 | DOCUMENTATION | Crear estructura `control/` e índices | VERIFIED |
| TASK-000-02 | DOCUMENTATION | Registrar definición de producto v1 y derivar backlog con script verificable | VERIFIED |
| TASK-000-03 | DOCUMENTATION | Registrar ADRs iniciales (001–004) | VERIFIED |
| TASK-000-04 | DECISION | Decidir runtime/lenguaje backend | VERIFIED (Python, ADR-005) |
| TASK-000-07 | DECISION | Decidir tooling del frontend React (GAP-002) | PLANNED |
| TASK-000-08 | DOCUMENTATION | Incorporar el cambio de alcance "servidor MCP propio + skills" (definición v1.1, ADR-008, ADR-009) | VERIFIED |
| TASK-000-09 | DOCUMENTATION | Registrar el backlog completo (fuente A) y unificarlo con la definición v1.1 (ADR-010) | VERIFIED |
| TASK-000-10 | DOCUMENTATION | Revisar los 37 solapamientos A↔B y fusionar o descartar duplicados (GAP-006) | PLANNED |
| TASK-000-11 | DECISION | Resolver CONF-001 (JEV en EPIC-47) y CONF-002 (fuente de verdad) con el operador | BLOCKED (IMP-003) |
| TASK-000-05 | RESEARCH | Aclarar qué es JEV (GAP-003) | VERIFIED (ADR-006) |
| TASK-000-06 | DECISION | Cerrar alcance MVP (delegado por el operador) | VERIFIED (ADR-007) |

VERIFIED = comprobado en sistema de archivos y con `derive_backlog.py --check`. No se marcan DONE hasta la revisión del operador (merge).
