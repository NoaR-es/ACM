# Estado actual

LAST_UPDATED: 2026-10-06
LOCK: none

| Pregunta | Respuesta |
|----------|-----------|
| ¿Dónde estamos? | **ACM operable entero desde la interfaz y con supervisor autónomo.** Todo lo que se hace por MCP se hace también desde el navegador: proyectos, backlog, criterios, sprints, miembros, principales, tokens, configuración y modelos. ACM gestiona sprints completos. Un supervisor ágil revisa cada proyecto con JEV (Ollaya) y Ollama dentro del Watchdog y aplica solo cambios seguros y reversibles. El operador elige modelos por propósito y conversa con un agente interno de solo lectura que conserva el hilo. Por debajo: API REST v1, eventos en tiempo real, Watchdog, tokens y RBAC, segundo cerebro, skills y backlog por MCP (59 herramientas). |
| ¿Sprint activo? | SPRINT-008 — entregado, pendiente de CI en GitHub y de revisión del operador |
| ¿Story activa? | Ninguna en curso |
| ¿Task activa? | Ninguna en curso |
| ¿Qué se acaba de terminar? | SPRINT-008: 20 historias VERIFIED y 9 IMPLEMENTED (US-05.02 por CA-03; 8 a falta de runtimes reales). 380 tests Python (37 e2e) y 26 vitest en PASS; 10 mutaciones (9 detectadas, 1 equivalente); BUG-002 corregido. README bilingüe. Evidencia: `12_TESTING/sprint_008_evidence.md` |
| ¿Qué está bloqueado? | Verificación con Ollama y Ollaya reales (IMP-004) |
| ¿Qué queda? | `03_ESTADO/pending_work.md` |
| ¿Siguiente acción? | Agente: comprobar la CI del commit de SPRINT-008. Operador: revisar la interfaz y el README; ejecutar SPIKE-005 con Ollama y Ollaya reales; decidir el siguiente sprint (propuesta en `pending_work.md`). |
| ¿Salud? | WARNING — ver `project_health.md` |
