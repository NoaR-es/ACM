# Trabajo pendiente (ordenado)

1. Comprobar la CI en GitHub del commit de SPRINT-004.
2. **Operador:** ejecutar SPIKE-005 con un Ollama real (IMP-004) → US-22.01/22.03 a VERIFIED y diseño de `OllamaDecisionEngine`.
3. **Propuesta de SPRINT-005: "Watchdog de calidad del backlog" (EPIC-13).** Primer consumidor autónomo de la interfaz de decisión: revisa historias (INVEST, criterios verificables) con el motor de reglas y marca "revisar" cuando el motor no está calibrado. Cerraría US-35.11 CA-01.
   - Alternativa: interfaz web (TASK-000-07 + EPIC-30), que cerraría US-01.02 CA-03.
4. Eventos en tiempo real (EPIC-21) → US-24.03 CA-02.
5. Adaptador JEV (EPIC-50) cuando haya acceso a Ollaya/TypeSafe (SPIKE-006).
6. Seguridad pendiente: US-20.07 (limitar herramientas visibles por rol), expiración de tokens, retención de la auditoría (EPIC-44), VULN-002 (TLS en un proxy).
7. Skills acm-error-analysis y acm-documentation (US-15.11/15.12) cuando existan EPIC-29 y EPIC-25.
8. TD-001: auditoría atómica con la operación.
9. Resto de solapamientos A↔B (GAP-006) y refinamientos (GAP-001).
10. Automatizar las pruebas de mutación.
11. Más adelante: orquestador interno (CONF-003).
