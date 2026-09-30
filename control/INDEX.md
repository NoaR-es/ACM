# control/ — Índice maestro

Proyecto: **Agile Context Manager (ACM)** · Constitución: `/CLAUDE.md` · Actualizado: 2026-09-30

## Flujo de lectura
`/CLAUDE.md` → este índice → `03_ESTADO/current_state.md` → `03_ESTADO/active_context.md` → índice del área → documento → `RELATIONSHIPS.md`

## Áreas
| Área | Responde a | Salud |
|------|-----------|-------|
| `00_GOBIERNO/` | Qué estamos construyendo y con qué reglas | OK |
| `01_PRODUCTO/` | Qué debemos hacer | WARNING — backlog unificado; solo las historias de SPRINT-001/002 refinadas (GAP-001); solapamientos pendientes fuera de EPIC-01/04/14/24 (GAP-006) |
| `02_AGILE/` | Sprint, Kanban e impedimentos | WARNING — IMP-004 abierto |
| `03_ESTADO/` | Dónde estamos | OK |
| `04_ARQUITECTURA/` | Cómo está diseñado | OK — topología, SQLite e interfaces de inferencia (ADR-013..016), implementadas |
| `05_CODIGO/` | Dónde está implementado | OK — `src/acm` (SPRINT-006) |
| `06_API/` | Cómo funcionan las APIs | OK — MCP: proyectos, backlog, auditoría, extensión Skills, segundo cerebro, identidad y Watchdog; API REST v1 y WebSocket (SPRINT-006) |
| `07_DATOS/` | Cómo se almacenan los datos | OK — SQLite global v6 + por proyecto v3 (SPRINT-006) |
| `08_INFRAESTRUCTURA/` | Cómo se ejecuta | OK — ejecución local (`acm serve`/`mcp-stdio`) |
| `09_MENSAJERIA/` | Cómo se comunican los componentes | OK — eventos persistidos y WebSocket (ADR-018) |
| `10_IA/` | Qué IA utilizamos | WARNING — reglas y adaptador Ollama implementados; Ollama sin verificar en real (IMP-004); JEV pendiente (EPIC-50) |
| `11_SEGURIDAD/` | Cómo se protege | WARNING — tokens y RBAC implementados (VULN-001 resuelta); sin TLS propio (VULN-002) |
| `12_TESTING/` | Cómo se prueba | OK — 251 tests de producto en PASS |
| `13_BUGS/` | Qué problemas existen | WARNING — 4 gaps abiertos, TD-001, BUG-001 corregido; conflictos resueltos o aplazados (CONF-003) |
| `14_DECISIONES/` | Por qué se tomaron decisiones | OK |
| `15_CAMBIOS/` | Qué ha cambiado | OK |
| `16_DOCUMENTACION/` | Cómo está documentado | N/A |
| `17_GIT/` | Cómo se versiona el código | OK |
| `18_CICD/` | Cómo se despliega | OK — CI en verde; sin CD |
| `19_OBSERVABILIDAD/` | Cómo se observa | WARNING — salud por componente y Watchdog; sin métricas ni alertas externas |
| `20_PERFORMANCE/` | Cómo rinde | OK — SPIKE-001 medido |
| `21_COMPLIANCE/` | Cumple normativa | N/A |
| `99_ARCHIVO/` | Documentación histórica, deprecada y supersedida | OK — 2 documentos supersedidos, 6 sprints históricos |

## Transversales
- `RELATIONSHIPS.md` — grafo de relaciones entre elementos.
- `tools/` — tooling del sistema de control (`derive_backlog.py`, `evidence.py`).
