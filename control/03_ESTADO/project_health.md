# Salud del proyecto — 2026-09-30

**Global: WARNING**

| Área | Estado | Motivo |
|------|--------|--------|
| Control | OK | Índices y relaciones al día; en SPRINT-007 se corrigieron 55 documentos marcados «no existe implementación» y el estado de componentes de la arquitectura (`recovery_log.md`); `05_CODIGO/` verificado por CI |
| Producto | WARNING | Backlog unificado (ADR-010/012/v1.3): 304/473 historias sin criterios; 69 con refinamiento completo (GAP-001); 29 solapamientos (GAP-006); conflictos resueltos, CONF-003 aplazado |
| Arquitectura | OK | ADR-013..019 implementadas; estados por componente en `04_ARQUITECTURA/architecture.md` |
| IA | WARNING | Interfaz de decisión, reglas y adaptador Ollama implementados (ADR-015/016); Ollama sin verificar contra una instancia real (IMP-004); JEV sin integrar (EPIC-50) |
| Código | OK | Backend `src/acm` y frontend `web/` (SPRINT-007): lint y tipos limpios; 75 archivos inventariados con cabecera; deuda TD-001, TD-003 |
| Testing | OK | 275 tests Python (24 e2e en Chromium) + 25 vitest en PASS; matrices CA↔test por sprint; 8/8 mutaciones en SPRINT-007 |
| CI/CD | OK | CI en verde en GitHub hasta SPRINT-006 (run #12, commit `4bc3e3a`); SPRINT-007 pendiente de comprobar; sin CD |
| Seguridad | WARNING | Autenticación por token y RBAC implementados (ADR-017, VULN-001 resuelta); interfaz con CSP (VULN-004 mitigada). Sin TLS propio: exponer solo tras un proxy TLS (VULN-002) |
