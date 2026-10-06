# Sprint activo

## SPRINT-008 — ACM operable desde la interfaz, sprints y segundo cerebro autónomo

Contexto: el operador pide dejar ACM **totalmente funcional** tras esta iteración y un README bilingüe para GitHub. Además pide que ACM use JEV (Ollaya) y Ollama **por sí mismo**: para supervisar el trabajo ágil, informar de incoherencias y tomar decisiones sobre documentación, sprints y Kanban. También pide descubrir y seleccionar los modelos (uno de Ollama y varios de Ollaya según el propósito), una guía de uso de cada familia de Ollaya y un agente interno de Ollama con hilos de conversación que pueda revisar el proyecto. Decisiones del operador (2026-09-30): los sprints se añaden en esta iteración; el supervisor puede «aplicar cambios seguros».

| Campo | Valor |
|-------|-------|
| Sprint ID | SPRINT-008 |
| Objetivo | Operar ACM entero desde el navegador y que ACM supervise su trabajo ágil con sus propios modelos |
| Inicio | 2026-09-30 |
| Fin | Al cumplir el Sprint Goal (sin timebox; desarrollo por agente) |
| Sprint Goal | **Todo lo que se puede hacer por MCP se puede hacer desde la interfaz (proyectos, backlog, criterios, sprints, miembros, principales, tokens, configuración y modelos). ACM gestiona sprints completos. Un supervisor autónomo revisa cada proyecto con JEV y Ollama, informa y aplica solo cambios seguros y reversibles. El operador elige los modelos de cada propósito y conversa con un agente interno de solo lectura que conserva el hilo.** |
| Historias | US-31.09..31.12; US-05.02..05.09; US-13.14, 13.15; US-04.10, 04.14, 04.15, 43.08; US-50.01..50.04, 50.09, 50.10; US-22.04, 22.06, 22.07, 22.10, 22.11 |
| Dependencias | SPRINT-007 (interfaz), ADR-016/018/019; nuevas ADR-020, ADR-021, ADR-022 |
| Riesgos | Sin Ollama ni Ollaya reales en el entorno (IMP-004): adaptadores probados contra servidores simulados con el contrato documentado. Calidad de las decisiones de los modelos no medida |
| Impedimentos | IMP-004 (abierto) |
| Fuera de alcance | Dependencias entre historias (US-05.02 CA-03); tareas, documentos, ADR y bugs de los proyectos gestionados; evaluación de modelos con datos reales |
| Velocidad | No se mide |

### Tasks

| ID | Tipo | Título | Historias | Estado |
|----|------|--------|-----------|--------|
| TASK-008-01 | DOCUMENTATION | Definición de producto v1.4 (`product_definition_v5.md`): FEAT-19.07, FEAT-10.04, FEAT-23.05, FEAT-24.05; refinamientos | todas | VERIFIED |
| TASK-008-02 | TASK | API REST de escritura completa (54 rutas HTTP, 28 de escritura) con actividad en tiempo real | US-31.09..31.12 | VERIFIED |
| TASK-008-03 | TASK | Formularios en la interfaz (`forms.tsx`): proyectos, backlog, criterios, miembros, principales, tokens, configuración | US-31.09..31.12 | VERIFIED |
| TASK-008-04 | TASK | Sprints: esquema de proyecto v4, `SprintService`, MCP, REST, vista y tablero del sprint | US-05.02..05.09 | VERIFIED (US-05.02 CA-03 pendiente) |
| TASK-008-05 | TASK | Motores JEV (`OllayaClient`, `JevDecisionEngine`) y `OllamaDecisionEngine` | US-50.01..50.04, US-22.04 | IMPLEMENTED (sin runtime real, IMP-004) |
| TASK-008-06 | TASK | Supervisor ágil autónomo (`AgileSupervisor`) integrado en el Watchdog: reglas de flujo, revisión INVEST, informe, acciones seguras con deshacer | US-13.14, 13.15, 04.10, 04.14, 04.15, 43.08, 22.06, 22.07 | VERIFIED |
| TASK-008-07 | TASK | Catálogo y selección de modelos (`ModelService`, `ModelSelection`, guía de Ollaya) | US-50.09, 50.10 | IMPLEMENTED (sin runtime real) |
| TASK-008-08 | TASK | Agente interno de Ollama con 7 herramientas de solo lectura e hilos persistentes (esquema de proyecto v5) | US-22.10, 22.11 | IMPLEMENTED (sin runtime real) |
| TASK-008-09 | TEST | 105 tests Python nuevos (380 en total; 13 e2e nuevos) y 1 vitest, matriz de evidencia, 10 mutaciones | todas | VERIFIED |
| TASK-008-10 | DOCUMENTATION | README bilingüe EN/ES y cierre de `control/` | — | VERIFIED |

SPRINT-007 cerrado y archivado en `99_ARCHIVO/historical/sprint_007.md` (CI runs #13 y #14 en verde).

### Estado de las historias (2026-10-06)

| Historia | Estado | Evidencia |
|----------|--------|-----------|
| US-31.09..31.12, US-05.03..05.09, US-13.14, 13.15, US-04.10, 04.14, 04.15, US-43.08, US-50.04, US-22.06, 22.07 | VERIFIED | `12_TESTING/sprint_008_evidence.md` |
| US-05.02 | IMPLEMENTED | CA-01, CA-02 y CA-04 en PASS; CA-03 (detección de dependencias) PENDIENTE: el producto no modela dependencias entre historias |
| US-50.01, 50.02, 50.03, 50.09, 50.10, US-22.04, 22.10, 22.11 | IMPLEMENTED | Todos sus CA en PASS contra Ollaya/Ollama simulados; falta verificarlos con runtimes reales (IMP-004) |

VERIFIED = todos los CA con test automático en PASS. DONE requiere además la revisión del operador (merge del PR).
