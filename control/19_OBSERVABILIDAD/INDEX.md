# 19_OBSERVABILIDAD — Observabilidad

**Responde a:** Cómo se observa

**Salud:** WARNING — salud por componente y Watchdog implementados (SPRINT-005); sin métricas, trazas ni alertas externas

| Documento | Estado |
|-----------|--------|
| `logging.md` | ACTIVE |
| `metrics.md` | ACTIVE |
| `tracing.md` | N/A (no existe aún; revisado en SPRINT-007) |
| `alerting.md` | N/A (no existe aún; revisado en SPRINT-007) |
| `dashboards.md` | ACTIVE |

Implementado (SPRINT-005):
- **Salud por componente:** `acm_health` (admin; bases, skills, motores), recalculada en cada llamada; `/api/health` público mínimo.
- **Gobernanza:** Watchdog periódico con semáforo e histórico por proyecto (`acm_governance_status`, `acm_watchdog_history`).
- **Registros en SQLite:** `mcp_audit` (invocaciones), `inference_calls`, `context_deliveries`, `watchdog_runs`.
- **Log del proceso:** logger `acm` (rondas fallidas del Watchdog). Sin formato ni destino definidos (MISSING).
- **Alertas externas:** MISSING (un semáforo RED no avisa a nadie fuera de ACM).

Documentos históricos: ninguno (ver `99_ARCHIVO/`).
Relaciones: `../RELATIONSHIPS.md`.
