# Salud del proyecto — 2026-09-30

**Global: WARNING**

| Área | Estado | Motivo |
|------|--------|--------|
| Control | OK | Estructura completa, índices y relaciones creados |
| Producto | WARNING | Backlog unificado (ADR-010/012): 351/492 historias sin criterios, ninguna READY (GAP-001); 37 solapamientos (GAP-006); conflictos resueltos, CONF-003 aplazado |
| Arquitectura | OK | Topología (ADR-014), SQLite (ADR-013) e interfaces de inferencia (ADR-015) decididas con evidencia de spikes |
| IA | OK | JEV definido (ADR-006); nada integrado |
| Código | OK | Paquete `src/acm` (SPRINT-002): lint limpio, 122 tests en verde; deuda TD-001 |
| Testing | OK | 122 tests de producto en PASS; matrices CA↔test de SPRINT-001 y SPRINT-002; integridad del backlog con `--check` |
| CI/CD | OK | CI en verde en GitHub ([run #1](https://github.com/NoaR-es/ACM/actions/runs/36758248042)); sin CD |
| Seguridad | WARNING | Sin autenticación hasta EPIC-20: el HTTP escucha en 127.0.0.1 por defecto (VULN-001) |
