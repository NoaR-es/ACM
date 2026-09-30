# Trabajo pendiente (ordenado)

1. SPIKE-001 (concurrencia SQLite/WAL en Python) y SPIKE-002 (servidor MCP propio + extensión Skills, preguntas en `06_API/mcp_server.md`) → ADRs de framework y topología de procesos.
2. Diseño de las interfaces de inferencia del núcleo: decisión (US-35.11, contrato de ADR-006) y generación (Ollama), preparadas para JEV (US-47.01, ADR-012).
3. TASK-000-10: revisar los 37 solapamientos A↔B (GAP-006) y fusionar duplicados.
4. Refinar a READY (regla de A) las historias de EPIC-01, 02 y 18 (GAP-001).
5. Completar el modelo de datos en SQLite (GAP-005): memoria de proyecto de EPIC-02 (ADR-011), instancias, hilos, ejecuciones, lecciones y registro de tokens ahorrados (US-35.09).
6. Configurar CI mínima que ejecute `derive_backlog.py --check` (18_CICD MISSING).
7. Decidir tooling del frontend React (TASK-000-07, GAP-002).
8. Redactar las 5 skills oficiales (FEAT-15.03) en cuanto exista el esqueleto del backend.
9. SPIKE-005 (Ollama multiagente) y SPIKE-006 (Ollaya en hardware real), priorizados por ADR-012.
10. Más adelante: orquestador interno (CONF-003, aplazado).

Histórico: runtime → ADR-005; JEV → ADR-006 → ADR-012; servidor MCP + skills → ADR-008; MVP → ADR-007 → ADR-009 → ADR-010 → ADR-012; backlog unificado → ADR-010; fuente de verdad → ADR-011.
