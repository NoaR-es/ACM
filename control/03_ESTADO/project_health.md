# Salud del proyecto — 2026-10-28

**Global: WARNING**

| Área | Estado | Motivo |
|------|--------|--------|
| Control | OK | Índices y relaciones al día; `05_CODIGO/` verificado por CI (`code_inventory --check`); backlog verificado (`derive_backlog --check`) |
| Producto | WARNING | Definición v1.5 (`product_definition_v6.md`): 287/489 historias sin criterios; 104 con refinamiento completo (GAP-001); solapamientos pendientes (GAP-006); CONF-003 aplazado |
| Arquitectura | OK | ADR-013..025 implementadas; estados por componente en `04_ARQUITECTURA/architecture.md` |
| IA | WARNING | Motores JEV y Ollama (decisión y generación), selección por propósito, supervisor y agente interno implementados (ADR-020..022), pero solo probados contra servidores simulados: sin Ollama ni Ollaya reales (IMP-004). Calidad de decisión no medida |
| Código | OK | Backend `src/acm` y frontend `web/`: lint y tipos limpios; archivos inventariados con cabecera; deuda TD-001, TD-003 |
| Testing | OK | 431 tests Python (con e2e en Chromium) + 27 vitest en PASS; matrices CA↔test por sprint; mutaciones SPRINT-009: 12/12 detectadas |
| CI/CD | OK | CI en verde hasta SPRINT-008 (runs #15 y #16); los commits parciales de SPRINT-009 la dejaron en rojo por un test existente, corregido en `b93b1fb` (pendiente de comprobar); sin CD |
| Seguridad | WARNING | Token y RBAC (ADR-017); escritura REST con la misma autorización que MCP; claves de Ollaya solo por entorno (ADR-021); el supervisor actúa como principal propio y auditado (ADR-020). Sin TLS propio: exponer solo tras un proxy TLS (VULN-002). Modo local: los agentes se ejecutan como el usuario del sistema, la aprobación de acceso es una salvaguarda y no una barrera (VULN-005); el token de la interfaz local está mitigado (VULN-006) |
