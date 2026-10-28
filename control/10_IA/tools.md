# Tools

Actualizado: 2026-10-06 (SPRINT-008).

## Herramientas que ACM ofrece a agentes externos
65 herramientas MCP. Lista generada en `../05_CODIGO/code_reference.md` (sección `mcp_server.py`); contrato en `../06_API/mcp_server.md` y en la skill `acm-schema`.

## Herramientas del agente interno de Ollama (ADR-022)
Definidas en `src/acm/domain/chat.py` (`TOOLS`). Todas son de solo lectura y se ejecutan con los permisos de quien conversa.

| Herramienta | Devuelve |
|-------------|----------|
| `backlog_overview` | Requisitos, épicas con sus features e historias con estado y sprint |
| `get_story` | Una historia completa: enunciado, criterios, requisitos, estado e historial |
| `search_stories` | Historias que contienen un texto (y, opcionalmente, en un estado) |
| `trace_requirement` | Épicas e historias que implementan un requisito |
| `list_sprints` | Sprints con objetivo, fechas, estado, historias, carga y resumen de cierre |
| `governance` | Última auditoría: semáforo, hallazgos, acciones e informe del supervisor |
| `story_context` | Contexto compacto de una historia: épica, feature, requisitos y hermanas (US-35.08) |
