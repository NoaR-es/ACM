# Trabajo pendiente (ordenado)

1. **Comprobar la primera ejecución de la CI en GitHub** (`.github/workflows/ci.yml`).
2. **Propuesta de SPRINT-002: "Skills y backlog por MCP"**
   - Servidor MCP: extensión Skills en producto (FEAT-15.02, US-15.04..07) con las 5 skills oficiales (FEAT-15.03, US-15.08..12).
   - Núcleo de backlog en SQLite del proyecto: épicas, features, historias y CA (EPIC-04 y US-24.01/24.03, para verificar backlog y memoria independientes por proyecto).
   - Antes: refinamiento a READY y depuración de solapamientos de EPIC-04, 15 y 24.
3. Autenticación con tokens y RBAC (EPIC-20): sustituye al principal por configuración. Necesaria antes de exponer HTTP fuera de 127.0.0.1 (VULN-001).
4. Tooling del frontend React (TASK-000-07) → interfaz web; cerraría US-01.02 CA-03.
5. Interfaces de inferencia (ADR-015) con `RulesDecisionEngine` y Ollama (US-35.11, US-47.01, EPIC-22).
6. Resto de solapamientos A↔B (35, GAP-006) y refinamientos (GAP-001).
7. Automatizar las pruebas de mutación de invariantes críticas (retrospectiva SPRINT-001).
8. SPIKE-005 (Ollama) y SPIKE-006 (Ollaya).
9. Más adelante: orquestador interno (CONF-003).
