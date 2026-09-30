# Estado actual

LAST_UPDATED: 2026-09-30
LOCK: none

| Pregunta | Respuesta |
|----------|-----------|
| ¿Dónde estamos? | **Identidad real.** Cada petición MCP por HTTP se autentica con un token de ACM y actúa con los permisos de su principal (usuario o agente). Roles y tokens se gestionan por MCP con efecto inmediato. ACM ya puede exponerse detrás de un proxy TLS. Sin interfaz web. |
| ¿Sprint activo? | SPRINT-004 — entregado, pendiente de revisión del operador (`02_AGILE/sprint.md`) |
| ¿Story activa? | Ninguna en curso |
| ¿Task activa? | Ninguna en curso |
| ¿Qué se acaba de terminar? | SPRINT-004: US-20.01, 20.02, 20.03, 20.04, 20.05, 20.08 VERIFIED. 198 tests PASS. Evidencia: `12_TESTING/sprint_004_evidence.md` |
| ¿Qué está bloqueado? | SPIKE-005 (IMP-004): sin Ollama real en el entorno cloud |
| ¿Qué queda? | `03_ESTADO/pending_work.md` |
| ¿Siguiente acción? | Operador: revisar y fusionar (cambio incompatible: el HTTP exige token). CI en verde (run #8). Agente: proponer SPRINT-005. |
| ¿Salud? | WARNING — ver `project_health.md` |
