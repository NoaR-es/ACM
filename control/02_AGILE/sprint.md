# Sprint activo

## SPRINT-002 — Skills y backlog por MCP

| Campo | Valor |
|-------|-------|
| Sprint ID | SPRINT-002 |
| Objetivo | Que un agente que se conecta a ACM aprenda a usarlo (skills servidas por MCP) y pueda construir un backlog trazable en la SQLite del proyecto |
| Inicio | 2026-09-30 |
| Fin | Al cumplir el Sprint Goal (sin timebox; desarrollo por agente) |
| Sprint Goal | **Un agente IA que se conecta al servidor MCP de ACM descarga las skills oficiales (acm-schema, acm-invest, acm-discovery) y, con ellas, registra requisitos, épicas, features, historias y criterios de aceptación en la base SQLite del proyecto, con trazabilidad requisito ↔ historia, aislamiento entre proyectos y auditoría de cada invocación, con cada CA verificado por tests automáticos.** |
| Historias | US-03.03, US-04.01, US-04.02, US-04.03, US-14.04, US-14.05, US-14.06, US-14.07, US-14.09, US-14.10, US-14.11, US-15.01, US-15.04..US-15.10, US-24.01, US-24.03 (21; refinamientos en `01_PRODUCTO/refinements/`) |
| Dependencias | ADR-008, ADR-011, ADR-013, ADR-014; SPRINT-001 |
| Riesgos | Extensión Skills (SEP-2640) sin soporte nativo en el SDK: implementada con `Extension`; no sabemos qué clientes cargan skills automáticamente (SPIKE-002 P4 UNKNOWN) |
| Impedimentos | Ninguno |
| Fuera de alcance | Skills acm-error-analysis y acm-documentation (US-15.11/15.12: necesitan EPIC-29/25); eventos en tiempo real (EPIC-21, US-24.03 CA-02); redacción de secretos en la auditoría (EPIC-44); autenticación (EPIC-20); US-14.08 fusionada en US-01.06 |
| Velocidad | No se mide |

### Tasks

| ID | Tipo | Título | Historias | Estado |
|----|------|--------|-----------|--------|
| TASK-000-10 | DOCUMENTATION | Depurar solapamientos de EPIC-04 y EPIC-14 (7 fusiones más en `tools/dedupe.json`, una entre épicas) | GAP-006 | VERIFIED (parcial: 13 fusiones en total; siguen señales en otras épicas) |
| TASK-002-01 | TASK | Esquema v2 de proyecto (requisitos, épicas, features, historias, CA) y `BacklogService` | US-03.03, US-04.01..03, US-24.01, US-24.03 | VERIFIED |
| TASK-002-02 | TASK | Herramientas MCP de backlog (15) con `project_id` explícito | US-14.05..07, US-14.09 | VERIFIED |
| TASK-002-03 | TASK | Auditoría de invocaciones MCP (`mcp_audit`, esquema global v2, `acm_audit_list`) | US-14.10, US-14.11 | VERIFIED (TD-001 registrada) |
| TASK-002-04 | TASK | Catálogo de skills, extensión MCP Skills (`skills/list`, `skills/get`, `skill://`), herramientas de respaldo, recarga con notificación y las 3 skills oficiales | US-15.01, US-15.04..10 | VERIFIED |
| TASK-002-05 | TEST | Tests por CA (72 nuevos) y matriz de evidencia generada (`tools/evidence.py`) | todas | VERIFIED (122 tests; 6/6 mutaciones detectadas) |
| BUG-001 | BUG | `database is locked` al abrir una base nueva desde varios procesos (CI run #2 en rojo) | US-18.01, US-18.03 | VERIFIED (test de regresión) |
| TASK-000-07 | DECISION | Decidir tooling del frontend React (GAP-002) | — | PLANNED (arrastrada) |

SPRINT-001 cerrado y archivado en `99_ARCHIVO/historical/sprint_001.md`.

### Estado de las historias (2026-09-30)

| Historia | Estado | Evidencia / nota |
|----------|--------|------------------|
| US-03.03, US-04.01, US-04.02, US-04.03 | VERIFIED | `12_TESTING/sprint_002_evidence.md` |
| US-14.04, US-14.05, US-14.06, US-14.07, US-14.09, US-14.10, US-14.11 | VERIFIED | idem; US-14.11 con TD-001 (auditoría no atómica con la operación) |
| US-15.01, US-15.04..US-15.10 | VERIFIED | idem |
| US-24.01 | VERIFIED | idem |
| US-24.03 | IMPLEMENTED | CA-02 (eventos de B no llegan al cliente de A) requiere EPIC-21 |

VERIFIED = todos los CA con test automático en PASS. DONE requiere además la revisión del operador (merge del PR).
