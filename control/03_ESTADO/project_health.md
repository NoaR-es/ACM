# Salud del proyecto — 2026-10-06

**Global: WARNING**

| Área | Estado | Motivo |
|------|--------|--------|
| Control | OK | Índices y relaciones al día; `05_CODIGO/` verificado por CI (`code_inventory --check`); backlog verificado (`derive_backlog --check`) |
| Producto | WARNING | Definición v1.4 (`product_definition_v5.md`): 287/483 historias sin criterios; 98 con refinamiento completo (GAP-001); solapamientos pendientes (GAP-006); CONF-003 aplazado |
| Arquitectura | OK | ADR-013..022 implementadas; estados por componente en `04_ARQUITECTURA/architecture.md` |
| IA | WARNING | Motores JEV y Ollama (decisión y generación), selección por propósito, supervisor y agente interno implementados (ADR-020..022), pero solo probados contra servidores simulados: sin Ollama ni Ollaya reales (IMP-004). Calidad de decisión no medida |
| Código | OK | Backend `src/acm` y frontend `web/`: lint y tipos limpios; archivos inventariados con cabecera; deuda TD-001, TD-003 |
| Testing | OK | 380 tests Python (37 e2e en Chromium) + 26 vitest en PASS; matrices CA↔test por sprint; mutaciones SPRINT-008: 9/10 detectadas + 1 equivalente |
| CI/CD | OK | CI en verde hasta SPRINT-007 (runs #13 y #14); SPRINT-008 pendiente de comprobar; sin CD |
| Seguridad | WARNING | Token y RBAC (ADR-017); escritura REST con la misma autorización que MCP; claves de Ollaya solo por entorno (ADR-021); el supervisor actúa como principal propio y auditado (ADR-020). Sin TLS propio: exponer solo tras un proxy TLS (VULN-002) |
