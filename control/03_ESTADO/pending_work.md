# Trabajo pendiente (ordenado)

1. Comprobar la CI en GitHub del commit de SPRINT-002.
2. **Propuesta de SPRINT-003: "Segundo cerebro: contexto compacto y decisiones delegadas"**
   - Interfaces de inferencia (ADR-015) con `RulesDecisionEngine` determinista (US-35.11, US-47.01).
   - Contexto compacto del proyecto para el agente con presupuesto de tokens (FEAT-35.05: US-35.08, US-35.09).
   - Validación INVEST en servidor (hoy solo existe como skill): candidata a la primera decisión delegada.
   - Antes: refinamiento a READY y depuración de solapamientos de EPIC-35/47.
3. Autenticación con tokens y RBAC (EPIC-20): sustituye al principal por configuración. Necesaria antes de exponer HTTP fuera de 127.0.0.1 (VULN-001).
4. Tooling del frontend React (TASK-000-07) → interfaz web; cerraría US-01.02 CA-03.
5. Eventos en tiempo real (EPIC-21) → cerraría US-24.03 CA-02.
6. Skills acm-error-analysis y acm-documentation (US-15.11/15.12) cuando existan EPIC-29 y EPIC-25.
7. TD-001: auditoría atómica con la operación (o registro previo "en curso").
8. Resto de solapamientos A↔B (GAP-006) y refinamientos (GAP-001).
9. Automatizar las pruebas de mutación de invariantes críticas (retrospectivas SPRINT-001/002).
10. SPIKE-005 (Ollama) y SPIKE-006 (Ollaya).
11. Más adelante: orquestador interno (CONF-003).
