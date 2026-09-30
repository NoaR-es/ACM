# Sprint archivado (cerrado el 2026-09-30, al abrir SPRINT-007)

## SPRINT-006 — Plataforma de tiempo real para la interfaz web

Contexto: el operador pide una interfaz web **completa** (toda la documentación, artefactos ágiles, especificaciones, criterios y tableros Kanban de uno o varios proyectos, en tiempo real y con colores de buen contraste). Se divide en dos sprints: SPRINT-006 (plataforma: eventos, WebSocket, API REST, estados de historia) y SPRINT-007 (interfaz React).

| Campo | Valor |
|-------|-------|
| Sprint ID | SPRINT-006 |
| Objetivo | Dar a la interfaz web todo lo que necesita del servidor: lectura completa por API, cambios de estado de las historias y eventos en tiempo real, también de agentes en otros procesos |
| Inicio | 2026-09-30 |
| Fin | Al cumplir el Sprint Goal (sin timebox; desarrollo por agente) |
| Sprint Goal | **Todo lo que guarda ACM se lee por una API REST v1 autenticada, versionada y documentada. Las historias se mueven por un flujo de estados con historial, y cada cambio confirmado (de cualquier agente o proceso) llega en tiempo real por WebSocket a los clientes autorizados, que pueden reconectarse sin perder ni duplicar eventos. Cada CA verificado por tests automáticos contra ACM real.** |
| Historias | US-06.01, US-06.02, US-06.03, US-21.01, US-21.02, US-21.03, US-30.01, US-30.02, US-30.03 (refinamientos en `01_PRODUCTO/refinements/`); US-06.05 fusionada en US-06.03 |
| Dependencias | ADR-014, ADR-017, ADR-018 (nueva) |
| Riesgos | Polling de eventos por conexión (0,2 s): suficiente para el MVP, sin medir con muchos clientes |
| Impedimentos | IMP-004 sigue abierto (no afecta) |
| Fuera de alcance | La interfaz (SPRINT-007); tareas, sprints, documentos, ADR y bugs de los proyectos (aún no existen en el producto: EPIC-05, 10, 25, 29); presencia de agentes (US-21.10/11) |
| Velocidad | No se mide |

### Tasks

| ID | Tipo | Título | Historias | Estado |
|----|------|--------|-----------|--------|
| TASK-006-01 | TASK | Flujo de estados de historias (`STORY_TRANSITIONS`), historial (`story_status_history`, esquema de proyecto v3), `acm_story_set_status`, `acm_story_history` | US-06.02 | VERIFIED |
| TASK-006-02 | TASK | Eventos de dominio persistidos (`events`, esquema global v6), emisión desde el dominio, WebSocket `/api/v1/ws` con visibilidad, reanudación, `resync` y purga | US-06.03, US-21.01..03 | VERIFIED |
| TASK-006-03 | TASK | API REST v1 (24 rutas), formato de error único, OpenAPI con errores, Kanban de uno o varios proyectos | US-06.01, US-30.01..03 | VERIFIED |
| TASK-006-04 | TEST | Tests por CA contra ACM real (31 nuevos, incluido un agente stdio en otro proceso) y matriz de evidencia | todas | VERIFIED (251 tests; 8/8 mutaciones detectadas) |
| TASK-000-10 | DOCUMENTATION | Fusión US-06.05 → US-06.03 | GAP-006 | VERIFIED (parcial: 20 fusiones en total) |
| TASK-000-07 | DECISION | Tooling del frontend React (GAP-002) | — | PLANNED → SPRINT-007 (resuelta allí con ADR-019) |

SPRINT-005 cerrado y archivado en `99_ARCHIVO/historical/sprint_005.md`.

### Estado de las historias (2026-09-30)

| Historia | Estado | Evidencia |
|----------|--------|-----------|
| US-06.01, 06.02, 06.03, 21.01, 21.02, 21.03, 30.01, 30.02, 30.03 | VERIFIED | `12_TESTING/sprint_006_evidence.md` |

VERIFIED = todos los CA con test automático en PASS. DONE requiere además la revisión del operador (merge del PR).

CI en GitHub del commit 4bc3e3a: success (run #12).
