# Problemas conocidos

| ID | Fecha | Descripción | Impacto | Severidad | Estado |
|----|-------|-------------|---------|-----------|--------|
| GAP-001 | 2026-09-30 | 351 de 352 historias carecen de criterios de aceptación (solo US-01.01 los tiene). | Ninguna historia salvo US-01.01 puede pasar a READY (Regla 3). | ALTA | OPEN |
| GAP-002 | 2026-09-30 | La definición no fija runtime/lenguaje del backend ni del servidor MCP, ni tooling del frontend React. | Backend resuelto 2026-09-30 (Python, ADR-005). Queda abierto el tooling del frontend (TASK-000-07); no bloquea el backend. | BAJA | PARTIALLY_RESOLVED |
| GAP-003 | 2026-09-30 | "JEV" no está definido (naturaleza, contrato, proveedor). | Resuelto 2026-09-30: aclaración del operador + investigación (ADR-006). | MEDIA | RESOLVED |
| GAP-004 | 2026-09-30 | Épicas EPIC-03..48 no declaran Objetivo/Valor explícitos (solo EPIC-01 y 02). | Priorización por valor limitada. | BAJA | OPEN |
| GAP-005 | 2026-09-30 | El modelo de datos conceptual (§6) no cubre auditoría, tokens, snapshots, sesiones ni locks exigidos por el MVP. | Diseño de datos incompleto. | MEDIA | OPEN |
