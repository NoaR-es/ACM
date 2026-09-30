# Trabajo pendiente (ordenado)

1. **Preparar SPRINT-001 — "Esqueleto del backend y núcleo de proyecto"** (propuesta):
   a. TASK-000-10: depurar los solapamientos A↔B de EPIC-01, 18 y 24 (GAP-006).
   b. Refinar a READY las historias de EPIC-01 (proyecto), EPIC-18 (SQLite) y EPIC-24 (multiproyecto) con la regla de A (GAP-001).
   c. Implementar el esqueleto:
      - `pyproject.toml` con dependencias fijadas;
      - paquete `acm/` con capa de datos según ADR-013;
      - proceso ASGI según ADR-014 (FastAPI + MCP `/mcp` + `/ws` + stdio);
      - interfaces de ADR-015 con `RulesDecisionEngine`;
      - pytest y CI mínima.
2. Configurar CI que ejecute `derive_backlog.py --check` y los tests (18_CICD MISSING).
3. Completar el modelo de datos en SQLite (GAP-005).
4. Redactar las 5 skills oficiales (FEAT-15.03) sobre el esqueleto.
5. GAP-007: errores de herramienta explícitos en el servidor MCP.
6. Decidir el tooling del frontend React (TASK-000-07, GAP-002).
7. SPIKE-005 (Ollama: concurrencia, log-probabilidades y salida estructurada) y SPIKE-006 (Ollaya en hardware real).
8. Más adelante: orquestador interno (CONF-003, aplazado).

Histórico: runtime → ADR-005; JEV → ADR-006 → ADR-012; MCP + skills → ADR-008 → ADR-014; MVP → ADR-007 → 009 → 010 → 012; backlog → ADR-010; fuente de verdad → ADR-011; SQLite → ADR-013; inferencia → ADR-015.
