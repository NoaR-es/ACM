# Agentes

Actualizado: 2026-10-06 (SPRINT-008). ADR-020, ADR-022.

| Agente | Qué es | Motor | Qué puede hacer | Identidad | Código | Estado |
|--------|--------|-------|-----------------|-----------|--------|--------|
| Agentes externos | Agentes IA (Claude, etc.) conectados por MCP | Los suyos | Las 59 herramientas MCP según su rol (ADR-017) | Su principal y token | `mcp_server.py` | IMPLEMENTED |
| Supervisor ágil (`acm-supervisor`) | Revisión autónoma de cada proyecto, dentro de cada ejecución del Watchdog (a demanda y periódica) | Reglas de flujo (sin modelo) + decisiones por `agile.story_review` / `agile.sprint_review` (JEV u Ollama) + informe por `agile.report` (Ollama) | Detectar incongruencias (sprint sobrecargado, vacío, con historias canceladas o no READY, vencido, en riesgo, WIP excedido, historias estancadas, trabajo fuera de sprint) y revisar INVEST, criterios verificables y tamaño. Solo aplica 3 acciones seguras y reversibles (`story.mark_ready`, `story.back_to_planned`, `sprint.remove_story`), con confianza ≥ `supervisor.min_confidence_pct` y `supervisor.mode = apply_safe`. Lo demás queda como propuesta | Principal `acm-supervisor` (agente, admin), auditado como `supervisor:*` | `domain/supervisor.py` | VERIFIED con motores simulados; calidad con modelos reales sin medir (IMP-004) |
| Agente interno de Ollama | Conversación de una persona o agente con el modelo local sobre un proyecto | Ollama (`agent.chat`) con *tool calling* | Solo lectura: 7 herramientas (`tools.md`). Máximo 5 rondas de herramientas por mensaje; historial de 30 mensajes; resultados de herramienta recortados a 6000 caracteres | Actúa con los permisos de quien pregunta | `domain/chat.py` | IMPLEMENTED (sin Ollama real) |

El supervisor nunca borra, nunca cambia el alcance y nunca marca nada como DONE. Cada acción aplicada se puede deshacer desde la interfaz (Gobernanza → Supervisor).
