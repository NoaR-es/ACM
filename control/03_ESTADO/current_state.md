# Estado actual

LAST_UPDATED: 2026-10-28
LOCK: none

| Pregunta | Respuesta |
|----------|-----------|
| ¿Dónde estamos? | **Cualquier agente MCP se conecta a ACM con una única entrada stdio** (`uvx --from git+https://github.com/NoaR-es/ACM acm mcp-stdio`), sin instalar ni crear tokens. Cada agente es un principal (`<cliente>.<equipo>`) con una sesión por conexión. Crea un proyecto o pide unirse a uno, y una persona aprueba desde la interfaz local, que arranca sola y entra sin token. Varios agentes colaboran: ACM les reparte el trabajo con `acm_next_work` sin solapes. Por debajo: sprints, supervisor ágil autónomo con JEV y Ollama, selección de modelos, agente interno, API REST v1 (59 rutas), eventos en tiempo real, RBAC y 65 herramientas MCP. |
| ¿Sprint activo? | SPRINT-009 — entregado, CI en verde (runs #27 y #28, commit `0ccd71c`); pendiente de revisión del operador |
| ¿Story activa? | Ninguna en curso |
| ¿Task activa? | Ninguna en curso |
| ¿Qué se acaba de terminar? | SPRINT-009: US-14.12..14.17 VERIFIED (21 CA en PASS). 431 tests Python y 27 vitest en PASS; 12/12 mutaciones. Evidencia: `12_TESTING/sprint_009_evidence.md` |
| ¿Qué está bloqueado? | Verificación con Ollama y Ollaya reales (IMP-004) y con los agentes concretos (Antigravity, Codex, Hermes, Cursor) |
| ¿Qué queda? | `03_ESTADO/pending_work.md` |
| ¿Siguiente acción? | Operador: revisar el README y probar la entrada con su agente; decidir el siguiente sprint (propuesta en `pending_work.md`). |
| ¿Salud? | WARNING — ver `project_health.md` |
