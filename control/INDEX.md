# control/ — Índice maestro

Proyecto: **Agile Context Manager (ACM)** · Constitución: `/CLAUDE.md` · Actualizado: 2026-09-30

## Flujo de lectura
`/CLAUDE.md` → este índice → `03_ESTADO/current_state.md` → `03_ESTADO/active_context.md` → índice del área → documento → `RELATIONSHIPS.md`

## Áreas
| Área | Responde a | Salud |
|------|-----------|-------|
| `00_GOBIERNO/` | Qué estamos construyendo y con qué reglas | OK |
| `01_PRODUCTO/` | Qué debemos hacer | WARNING — 351/356 historias sin criterios de aceptación (GAP-001) |
| `02_AGILE/` | Sprint, Kanban e impedimentos | OK |
| `03_ESTADO/` | Dónde estamos | OK |
| `04_ARQUITECTURA/` | Cómo está diseñado | WARNING — arquitectura objetivo conceptual; backend Python (ADR-005), framework pendiente |
| `05_CODIGO/` | Dónde está implementado | OK — solo existe tooling de control |
| `06_API/` | Cómo funcionan las APIs | OK — servidor MCP planificado (ADR-008) |
| `07_DATOS/` | Cómo se almacenan los datos | N/A — modelo conceptual en data_architecture.md |
| `08_INFRAESTRUCTURA/` | Cómo se ejecuta | N/A |
| `09_MENSAJERIA/` | Cómo se comunican los componentes | N/A — WebSockets previstos (EPIC-21) |
| `10_IA/` | Qué IA utilizamos | OK — JEV definido (ADR-006); nada integrado |
| `11_SEGURIDAD/` | Cómo se protege | N/A |
| `12_TESTING/` | Cómo se prueba | OK — solo test de integridad del backlog |
| `13_BUGS/` | Qué problemas existen | WARNING — 4 gaps abiertos; conflictos resueltos o aplazados (CONF-003) |
| `14_DECISIONES/` | Por qué se tomaron decisiones | OK |
| `15_CAMBIOS/` | Qué ha cambiado | OK |
| `16_DOCUMENTACION/` | Cómo está documentado | N/A |
| `17_GIT/` | Cómo se versiona el código | OK |
| `18_CICD/` | Cómo se despliega | MISSING — no existe pipeline |
| `19_OBSERVABILIDAD/` | Cómo se observa | N/A |
| `20_PERFORMANCE/` | Cómo rinde | N/A |
| `21_COMPLIANCE/` | Cumple normativa | N/A |
| `99_ARCHIVO/` | Documentación histórica, deprecada y supersedida | OK — 2 documentos supersedidos |

## Transversales
- `RELATIONSHIPS.md` — grafo de relaciones entre elementos.
- `tools/` — tooling del sistema de control (`derive_backlog.py`).
