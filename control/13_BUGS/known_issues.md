# Problemas conocidos

| ID | Fecha | Descripción | Impacto | Severidad | Estado |
|----|-------|-------------|---------|-----------|--------|
| GAP-001 | 2026-09-30 | Backlog unificado (2026-09-30): 137 de 488 historias tienen criterios (132 de A + 5 de B); 351 (todas de origen B) no. Además, ninguna cumple la *Regla de aceptación del backlog* de A para READY (precondiciones, flujo, alternativas, errores, reglas, validaciones, casos límite, tareas, pruebas). | Ninguna historia puede pasar a READY hasta refinarse. | ALTA | OPEN |
| GAP-002 | 2026-09-30 | La definición no fija runtime/lenguaje del backend ni del servidor MCP, ni tooling del frontend React. | Backend resuelto 2026-09-30 (Python, ADR-005). Queda abierto el tooling del frontend (TASK-000-07); no bloquea el backend. | BAJA | PARTIALLY_RESOLVED |
| GAP-003 | 2026-09-30 | "JEV" no está definido (naturaleza, contrato, proveedor). | Resuelto 2026-09-30: aclaración del operador + investigación (ADR-006). | MEDIA | RESOLVED |
| GAP-004 | 2026-09-30 | 47 de 53 épicas unificadas no declaran objetivo explícito (sí EPIC-01 y EPIC-49..53); lista en `01_PRODUCTO/epics.md`. | Priorización por valor limitada. | BAJA | OPEN |
| GAP-005 | 2026-09-30 | El modelo de datos conceptual (§6) no cubre auditoría, tokens, snapshots, sesiones ni locks exigidos por el MVP. | Diseño de datos incompleto. | MEDIA | OPEN |
| GAP-006 | 2026-09-30 | Solapamientos entre historias de A y B tras la unificación: 37 marcados por heurística (Jaccard ≥ 0,20), con falsos positivos y omisiones conocidas. | Backlog con historias redundantes; riesgo de implementar dos veces. | MEDIA | IN_PROGRESS — 2026-09-30: 18 fusionadas en EPIC-01/04/14/20/22/24 (`tools/dedupe.json`); quedan señales en otras épicas |

## Deuda técnica

| ID | Fecha | Descripción | Motivo | Impacto | Riesgo | Prioridad | Dependencias | Estado |
|----|-------|-------------|--------|---------|--------|-----------|--------------|--------|
| TD-001 | 2026-09-30 | La auditoría MCP (`mcp_audit`, en `acm.db`) se escribe después de la operación, que confirma en `project.db`: no hay transacción común. Si falla la escritura de auditoría, el agente recibe `STORAGE_ERROR` pero la operación ya está confirmada y queda sin auditar. | Bases SQLite separadas (ADR-013); SQLite no ofrece commit atómico entre archivos en WAL | Operación sin rastro de auditoría en un fallo de disco | BAJO (requiere fallo de escritura en `acm.db` justo tras la operación) | MEDIA | EPIC-44 | OPEN — documentado en US-14.11 |
| TD-002 | 2026-09-30 | El SDK MCP activa por defecto la protección DNS rebinding solo con Host locales: servido con otro nombre (proxy, IP pública), ACM respondía 421. | `streamable_http_app` sin `transport_security` | Impedía exponer ACM (objetivo de EPIC-20) | ALTO para el despliegue | ALTA | — | RESOLVED en SPRINT-004: `ACM_ALLOWED_HOSTS` (`tests/test_auth.py::test_td002_host_permitido_por_configuracion`) |

## Conflictos de requisitos (CLAUDE.md §35 — requieren decisión del operador)

| ID | Fecha | Conflicto | Propuesta del agente | Estado |
|----|-------|-----------|----------------------|--------|
| CONF-001 | 2026-09-30 | **JEV.** A (EPIC-47) trata "JEV" como un futuro *entorno de ejecución* virtual; el operador aclaró que JEV son *modelos de decisión servidos por Ollaya* (ADR-006). | Operador (2026-09-30): JEV = modelos de decisión en Ollaya, a integrar; todo se diseña preparado para ello. EPIC-47 = preparación (abstracción, US-47.01 en MVP); EPIC-50 = adaptador JEV. | RESOLVED (ADR-012) |
| CONF-002 | 2026-09-30 | **Fuente de verdad del producto ACM.** A (EPIC-02) define `control/` como "memoria y fuente de verdad" de cada proyecto; B y ADR-001 establecen SQLite como núcleo de persistencia (A EPIC-18 también). | Operador (2026-09-30): `control/` es la fuente de verdad del **desarrollo** (el agente la mantiene siempre al día); en el **producto ACM** la fuente de verdad es SQLite y todo se aloja ahí (EPIC-02 = memoria de proyecto en SQLite). | RESOLVED (ADR-011) |
| CONF-003 | 2026-09-30 | **Orquestador interno en el MVP.** A es un "Sistema Autónomo" con orquestador y agentes propios (EPIC-07/08/09/46); ADR-007/010 dejan eso POST-MVP y basan el MVP en agentes externos vía MCP. | Operador (2026-09-30): se deja para más adelante, pero teniendo siempre en cuenta Ollama y JEV locales, que hacen de ACM un segundo cerebro del agente. | DEFERRED (ADR-012) |
| CONF-004 | 2026-09-30 | **MCP.** A (EPIC-14) describe ACM como *cliente* que registra servidores MCP externos; ADR-008 lo describe como *servidor* MCP propio. | No es excluyente: ACM es servidor MCP para agentes (MVP) y cliente MCP para sus agentes internos (POST-MVP). | RESOLVED por el agente (ADR-010) |

## Hallazgos técnicos de spikes

| ID | Fecha | Descripción | Impacto | Severidad | Estado |
|----|-------|-------------|---------|-----------|--------|
| GAP-007 | 2026-09-30 | SDK `mcp` 2.2.0: una excepción genérica en una herramienta llega al agente como "Error executing tool …", sin el motivo (visto en TEST-SPIKE-002c). | El agente no sabía por qué se rechazaba la operación. | MEDIA | RESOLVED en ACM (2026-09-30): errores de dominio → `ToolError` con `CODE: motivo` (`test_mcp.py`) |
