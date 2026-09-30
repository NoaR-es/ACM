# Problemas conocidos

| ID | Fecha | Descripción | Impacto | Severidad | Estado |
|----|-------|-------------|---------|-----------|--------|
| GAP-001 | 2026-09-30 | Backlog unificado (2026-09-30): 137 de 488 historias tienen criterios (132 de A + 5 de B); 351 (todas de origen B) no. Además, ninguna cumple la *Regla de aceptación del backlog* de A para READY (precondiciones, flujo, alternativas, errores, reglas, validaciones, casos límite, tareas, pruebas). | Ninguna historia puede pasar a READY hasta refinarse. | ALTA | OPEN |
| GAP-002 | 2026-09-30 | La definición no fija runtime/lenguaje del backend ni del servidor MCP, ni tooling del frontend React. | Backend resuelto 2026-09-30 (Python, ADR-005). Queda abierto el tooling del frontend (TASK-000-07); no bloquea el backend. | BAJA | PARTIALLY_RESOLVED |
| GAP-003 | 2026-09-30 | "JEV" no está definido (naturaleza, contrato, proveedor). | Resuelto 2026-09-30: aclaración del operador + investigación (ADR-006). | MEDIA | RESOLVED |
| GAP-004 | 2026-09-30 | 47 de 53 épicas unificadas no declaran objetivo explícito (sí EPIC-01 y EPIC-49..53); lista en `01_PRODUCTO/epics.md`. | Priorización por valor limitada. | BAJA | OPEN |
| GAP-005 | 2026-09-30 | El modelo de datos conceptual (§6) no cubre auditoría, tokens, snapshots, sesiones ni locks exigidos por el MVP. | Diseño de datos incompleto. | MEDIA | OPEN |
| GAP-006 | 2026-09-30 | Solapamientos entre historias de A y B tras la unificación: 37 marcados por heurística (Jaccard ≥ 0,20), con falsos positivos y omisiones conocidas (p. ej. B:US-04.01 ↔ US-04.01 no se marca). | Backlog con historias redundantes; riesgo de implementar dos veces. | MEDIA | OPEN (TASK-000-10) |

## Conflictos de requisitos (CLAUDE.md §35 — requieren decisión del operador)

| ID | Fecha | Conflicto | Propuesta del agente | Estado |
|----|-------|-----------|----------------------|--------|
| CONF-001 | 2026-09-30 | **JEV.** A (EPIC-47) trata "JEV" como un futuro *entorno de ejecución* virtual; el operador aclaró que JEV son *modelos de decisión servidos por Ollaya* (ADR-006). | Mantener ambas épicas: EPIC-47 = abstracción de entornos de ejecución (su contenido es válido sin la palabra JEV) y EPIC-50 = modelos de decisión JEV. Confirmar si "entorno JEV" en EPIC-47 tiene otro significado. | OPEN |
| CONF-002 | 2026-09-30 | **Fuente de verdad del producto ACM.** A (EPIC-02) define `control/` como "memoria y fuente de verdad" de cada proyecto; B y ADR-001 establecen SQLite como núcleo de persistencia (A EPIC-18 también). | SQLite = estado operacional autoritativo; `control/` = proyección documental versionada en Git que ACM genera y mantiene sincronizada (legible por humanos y agentes). Si se edita `control/` a mano, ACM detecta la divergencia (US-25.03). | OPEN |
| CONF-003 | 2026-09-30 | **Orquestador interno en el MVP.** A es un "Sistema Autónomo" con orquestador y agentes propios (EPIC-07/08/09/46); ADR-007/010 dejan eso POST-MVP y basan el MVP en agentes externos vía MCP. | Mantener ADR-010: primero ACM útil con agentes externos (Claude Code, etc.) y después el orquestador interno sobre la misma base. El operador puede adelantarlo. | OPEN (decisión delegada; revisable) |
| CONF-004 | 2026-09-30 | **MCP.** A (EPIC-14) describe ACM como *cliente* que registra servidores MCP externos; ADR-008 lo describe como *servidor* MCP propio. | No es excluyente: ACM es servidor MCP para agentes (MVP) y cliente MCP para sus agentes internos (POST-MVP). | RESOLVED por el agente (ADR-010) |
