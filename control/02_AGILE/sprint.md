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
| Impedimentos | IMP-001, IMP-002 (ver impediments.md) |
| Velocidad | No se mide |

### Tasks

| ID | Tipo | Título | Estado |
|----|------|--------|--------|
| TASK-000-01 | DOCUMENTATION | Crear estructura `control/` e índices | VERIFIED |
| TASK-000-02 | DOCUMENTATION | Registrar definición de producto v1 y derivar backlog con script verificable | VERIFIED |
| TASK-000-03 | DOCUMENTATION | Registrar ADRs iniciales (001–004) | VERIFIED |
| TASK-000-04 | DECISION | Decidir runtime/lenguaje backend y frontend tooling | BLOCKED (IMP-001, decisión del operador) |
| TASK-000-05 | RESEARCH | Aclarar qué es JEV (GAP-003) | BLOCKED (IMP-002) |
| TASK-000-06 | DOCUMENTATION | Validar con operador clasificación MVP (ADR-003) y mapeo REQ-F → épicas | READY |

VERIFIED = comprobado en sistema de archivos y con `derive_backlog.py --check`. No se marcan DONE hasta la revisión del operador (merge).
