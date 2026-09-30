# Salud del proyecto — 2026-09-30

**Global: WARNING**

| Área | Estado | Motivo |
|------|--------|--------|
| Control | OK | Estructura completa, índices y relaciones creados |
| Producto | WARNING | Backlog unificado (ADR-010/012): 351/492 historias sin criterios, ninguna READY (GAP-001); 37 solapamientos (GAP-006); conflictos resueltos, CONF-003 aplazado |
| Arquitectura | OK | Topología (ADR-014), SQLite (ADR-013) e interfaces de inferencia (ADR-015) decididas con evidencia de spikes |
| IA | WARNING | Interfaz de decisión, reglas y adaptador Ollama implementados (ADR-015/016); Ollama sin verificar contra una instancia real (IMP-004); JEV sin integrar (EPIC-50) |
| Código | OK | Paquete `src/acm` (SPRINT-006): lint limpio, 251 tests en verde; deuda TD-001, TD-003 |
| Testing | OK | 251 tests de producto en PASS; matrices CA↔test de SPRINT-001 y SPRINT-002; integridad del backlog con `--check` |
| CI/CD | OK | CI en verde en GitHub (run #10, commit `cc2b9a8`); run #2 falló por BUG-001, ya corregido; sin CD |
| Seguridad | WARNING | Autenticación por token y RBAC implementados (ADR-017, VULN-001 resuelta). Sin TLS propio: exponer solo tras un proxy TLS (VULN-002) |
