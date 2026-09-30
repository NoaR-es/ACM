# Arquitectura IA

PLANNED. ACM actúa como **segundo cerebro** del agente IA (ADR-012): usa modelos locales para ahorrar tokens al agente.

| Capacidad | Motor | Épica | Alcance |
|-----------|-------|-------|---------|
| Generación | Ollama | EPIC-22 | MVP (básico) |
| Decisión tipada — interfaz común | Reglas · Ollama · JEV | US-35.11, US-47.01 | MVP (reglas + Ollama), preparada para JEV |
| Decisión tipada — adaptador JEV | Ollaya local / TypeSafe | EPIC-50 | Tras el MVP (ADR-006, ADR-012) |
| Contexto compacto y tokens ahorrados | Ollama + RAG | FEAT-35.05 | MVP |
| Decisiones delegadas por el agente | Interfaz de decisión | FEAT-35.06 | MVP |
| Recuperación semántica | Vector store + RAG | EPIC-16 | MVP (básico) |
| Registro y selección de modelos, fallback | Model registry | EPIC-38, EPIC-39 | POST-MVP |
| Gobernanza de inferencia (consumo, límites) | — | EPIC-23 | POST-MVP |

En el MVP, el razonamiento principal lo aportan los agentes externos conectados por MCP (ADR-010), y ACM les ahorra tokens con modelos locales (ADR-012). El orquestador interno queda aplazado (CONF-003).
