# Trabajo pendiente (ordenado)

1. **[Operador]** Resolver CONF-001 (¿"entorno JEV" en EPIC-47 significa algo distinto de los modelos de decisión?) y CONF-002 (SQLite frente a `control/` como fuente de verdad). Confirmar o cambiar CONF-003 (orquestador interno fuera del MVP).
2. SPIKE-001 (concurrencia SQLite/WAL en Python) y SPIKE-002 (servidor MCP propio + extensión Skills, preguntas en `06_API/mcp_server.md`) → ADRs de framework y topología de procesos.
3. TASK-000-10: revisar los 37 solapamientos A↔B (GAP-006) y fusionar duplicados.
4. Refinar a READY (regla de A) las historias de EPIC-01, 02 y 18 (GAP-001).
5. Configurar CI mínima que ejecute `derive_backlog.py --check` (18_CICD MISSING).
6. Decidir tooling del frontend React (TASK-000-07, GAP-002).
7. Completar modelo de datos (GAP-005), ahora también con instancias, hilos, ejecuciones y lecciones (fuente A).
8. Redactar las 5 skills oficiales (FEAT-15.03) en cuanto exista el esqueleto del backend.
9. POST-MVP: SPIKE-006 (Ollaya en hardware real, ADR-006).

Histórico: runtime → ADR-005; JEV → ADR-006; servidor MCP + skills → ADR-008; MVP → ADR-007 → ADR-009 → ADR-010; backlog unificado → ADR-010.
