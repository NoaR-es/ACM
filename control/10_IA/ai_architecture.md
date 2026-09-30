# Arquitectura IA

PLANNED. Tres capacidades separadas:

| Capacidad | Motor | Épica | Alcance |
|-----------|-------|-------|---------|
| Generación | Ollama | EPIC-22 | MVP (básico) |
| Decisión tipada | Ollaya local / TypeSafe (JEV) | EPIC-50 | POST-MVP (ADR-006) |
| Recuperación semántica | Vector store + RAG | EPIC-16 | MVP (básico) |
| Registro y selección de modelos, fallback | Model registry | EPIC-38, EPIC-39 | POST-MVP |
| Gobernanza de inferencia (consumo, límites) | — | EPIC-23 | POST-MVP |

En el MVP, el razonamiento lo aportan los agentes externos conectados por MCP (ADR-010).
