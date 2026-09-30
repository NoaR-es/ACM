# Sprint activo

## SPRINT-007 — Interfaz web completa en tiempo real

Contexto: el operador pide una interfaz **completa**, no mínima. Debe mostrar toda la documentación, los artefactos ágiles, las especificaciones, los criterios y los tableros Kanban de uno o varios proyectos, en tiempo real y con colores de buen contraste. SPRINT-006 dejó la plataforma (API REST v1, eventos, WebSocket); este sprint construye la interfaz. A mitad del sprint, el operador pidió además llevar un control completo del código en `control/05_CODIGO/`.

| Campo | Valor |
|-------|-------|
| Sprint ID | SPRINT-007 |
| Objetivo | Interfaz web con la que el operador revisa todo lo que guarda ACM y ve el trabajo moverse en tiempo real |
| Inicio | 2026-09-30 |
| Fin | Al cumplir el Sprint Goal (sin timebox; desarrollo por agente) |
| Sprint Goal | **Desde el navegador, con un token de ACM, el operador revisa todo lo que ACM guarda de sus proyectos y su documentación. Mueve historias en un Kanban de uno o varios proyectos (con ratón o teclado) y ve al instante los cambios de cualquier agente, con contraste WCAG AA en tema claro y oscuro. Cada CA está verificado por tests e2e en un navegador real contra ACM real, obligatorios en la CI.** |
| Historias | US-06.06, US-06.07, US-31.01, US-31.02, US-31.04, US-31.06, US-31.07, US-31.08, US-21.09, US-45.02, US-45.03; cierra US-01.02 (CA-03 y la parte cliente de CA-04). Fusiones: US-31.05 → US-31.01; US-21.04 y US-21.06 → US-31.08 |
| Dependencias | SPRINT-006 (API REST v1, ADR-018), ADR-017, ADR-019 (nueva) |
| Riesgos | Tipos TS mantenidos a mano frente a la API (`05_CODIGO/types.md`); bundle de 423 kB sin dividir |
| Impedimentos | IMP-004 sigue abierto (no afecta) |
| Fuera de alcance | Edición de backlog desde la interfaz (solo cambio de estado y gate READY); tareas, sprints, documentos, ADR y bugs de los proyectos (aún no existen en el producto); presencia de agentes (US-21.10/11) |
| Velocidad | No se mide |

### Tasks

| ID | Tipo | Título | Historias | Estado |
|----|------|--------|-----------|--------|
| TASK-000-07 | DECISION | Tooling del frontend: React + TypeScript + Vite, build versionado en `src/acm/webui`, servido con CSP (ADR-019) | GAP-002 | VERIFIED |
| TASK-007-01 | INFRASTRUCTURE | Proyecto `web/`, build reproducible, `SecureStatic` con cabeceras de seguridad, job `web` en la CI | ADR-019 | VERIFIED |
| TASK-007-02 | TASK | Sesión con token y cliente REST (`auth.tsx`, `api.ts`), pantalla de acceso | US-31.06 CA-04 | VERIFIED |
| TASK-007-03 | TASK | Canal en vivo: WebSocket, reanudación por `seq`, `resync`, recarga selectiva, indicador de conexión | US-31.08, US-31.04 | VERIFIED |
| TASK-007-04 | TASK | Kanban de uno o varios proyectos: colores por proyecto, carriles, arrastrar y teclado, rechazo explicado | US-06.07, US-06.06 | VERIFIED |
| TASK-007-05 | TASK | Vistas de proyecto (resumen, backlog, trazabilidad, gobernanza, miembros, configuración) y ficha de historia | US-31.06, US-06.06, US-01.02 | VERIFIED |
| TASK-007-06 | TASK | Actividad (feed y consola filtrable) y panel global | US-31.01, 31.02, 31.04, 21.09, 45.02, 45.03 | VERIFIED |
| TASK-007-07 | TASK | Documentación (skills, flujo de estados, OpenAPI) y sistema (salud, motores, ahorro, principales, tokens) | US-31.06 CA-03 | VERIFIED |
| TASK-007-08 | TASK | Tema claro/oscuro/sistema, paleta AA verificada, estado nunca solo por color | US-31.07 | VERIFIED |
| TASK-007-09 | TEST | 24 e2e con Chromium contra ACM real (obligatorios en CI), 25 unitarios vitest, matriz de evidencia | todas | VERIFIED |
| TASK-007-10 | DOCUMENTATION | Control del código: `05_CODIGO/` completo y `code_inventory.py --check` en la CI (petición del operador) | — | VERIFIED |
| TASK-000-10 | DOCUMENTATION | Fusiones US-31.05, US-21.04, US-21.06 | GAP-006 | VERIFIED (parcial: 23 fusiones en total) |

SPRINT-006 cerrado y archivado en `99_ARCHIVO/historical/sprint_006.md` (CI run #12 en verde).

### Estado de las historias (2026-09-30)

| Historia | Estado | Evidencia |
|----------|--------|-----------|
| US-06.06, 06.07, 31.01, 31.02, 31.04, 31.06, 31.07, 31.08, 21.09, 45.02, 45.03 | VERIFIED | `12_TESTING/sprint_007_evidence.md` |
| US-01.02 (SPRINT-001) | VERIFIED | CA-03 y la parte cliente de CA-04 cerrados por la interfaz; anexo de `12_TESTING/sprint_007_evidence.md` |

VERIFIED = todos los CA con test automático en PASS. DONE requiere además la revisión del operador (merge del PR).
