# Trabajo pendiente (ordenado)

1. Comprobar la CI en GitHub del commit de SPRINT-003.
2. **Operador:** ejecutar SPIKE-005 con un Ollama real (IMP-004). Con él, US-22.01 y US-22.03 pueden pasar a VERIFIED y se puede diseñar `OllamaDecisionEngine`.
3. **Propuesta de SPRINT-004: "Autenticación y RBAC" (EPIC-20).** Sustituye al principal por configuración por tokens; requisito para exponer HTTP fuera de 127.0.0.1 (VULN-001). Ahora que ACM guarda backlog, auditoría y ahorro por agente, la identidad real es lo que más riesgo reduce.
   - Alternativa: Watchdog (EPIC-13) sobre la interfaz de decisión, que cerraría US-35.11 CA-01.
4. Tooling del frontend React (TASK-000-07) → interfaz web; cerraría US-01.02 CA-03.
5. Eventos en tiempo real (EPIC-21) → cerraría US-24.03 CA-02.
6. Adaptador JEV (EPIC-50) cuando haya acceso a Ollaya/TypeSafe (SPIKE-006).
7. Skills acm-error-analysis y acm-documentation (US-15.11/15.12) cuando existan EPIC-29 y EPIC-25.
8. TD-001: auditoría atómica con la operación.
9. Resto de solapamientos A↔B (GAP-006) y refinamientos (GAP-001).
10. Automatizar las pruebas de mutación.
11. Más adelante: orquestador interno (CONF-003).
