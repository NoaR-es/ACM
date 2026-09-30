# Problemas conocidos

| ID | Fecha | Descripción | Impacto | Severidad | Estado |
|----|-------|-------------|---------|-----------|--------|
| GAP-001 | 2026-09-30 | 351 de 356 historias carecen de criterios de aceptación (solo US-01.01 y US-15.09..12 los tienen). | Solo esas 5 historias pueden pasar a READY (Regla 3). | ALTA | OPEN |
| GAP-002 | 2026-09-30 | La definición no fija runtime/lenguaje del backend ni del servidor MCP, ni tooling del frontend React. | Backend resuelto 2026-09-30 (Python, ADR-005). Queda abierto el tooling del frontend (TASK-000-07); no bloquea el backend. | BAJA | PARTIALLY_RESOLVED |
| GAP-003 | 2026-09-30 | "JEV" no está definido (naturaleza, contrato, proveedor). | Resuelto 2026-09-30: aclaración del operador + investigación (ADR-006). | MEDIA | RESOLVED |
| GAP-004 | 2026-09-30 | 44 de 48 épicas no declaran Objetivo/Valor explícitos (sí EPIC-01, 02, 15, 22; lista en `01_PRODUCTO/epics.md`). | Priorización por valor limitada. | BAJA | OPEN |
| GAP-005 | 2026-09-30 | El modelo de datos conceptual (§6) no cubre auditoría, tokens, snapshots, sesiones ni locks exigidos por el MVP. | Diseño de datos incompleto. | MEDIA | OPEN |
