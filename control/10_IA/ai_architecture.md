# Arquitectura IA

IMPLEMENTED en parte (SPRINT-003 y SPRINT-008). ACM actúa como **segundo cerebro** del agente IA (ADR-012): usa modelos locales para ahorrar tokens al agente.

| Capacidad | Motor | Épica | Alcance |
|-----------|-------|-------|---------|
| Generación | Ollama | EPIC-22 | MVP (básico) |
| Decisión tipada — interfaz común | Reglas · Ollama · JEV | US-35.11, US-47.01 | MVP (reglas + Ollama), preparada para JEV |
| Decisión tipada — adaptador JEV | Ollaya local | EPIC-50 | IMPLEMENTED en SPRINT-008 (sin Ollaya real); TypeSafe cloud PLANNED |
| Decisión tipada — Ollama sin calibrar | Ollama (esquema JSON) | US-22.04 | IMPLEMENTED en SPRINT-008 |
| Supervisor ágil autónomo | Reglas + JEV/Ollama + informe Ollama | FEAT-10.04 (US-13.14/13.15) | IMPLEMENTED en SPRINT-008 (ADR-020) |
| Agente interno con hilos | Ollama con *tool calling* | FEAT-23.05 (US-22.10/22.11) | IMPLEMENTED en SPRINT-008 (ADR-022) |
| Contexto compacto y tokens ahorrados | Ollama + RAG | FEAT-35.05 | MVP |
| Decisiones delegadas por el agente | Interfaz de decisión | FEAT-35.06 | MVP |
| Recuperación semántica | Vector store + RAG | EPIC-16 | MVP (básico) |
| Catálogo y selección de modelos por propósito | `ModelService` | FEAT-24.05 (US-50.09/50.10) | IMPLEMENTED en SPRINT-008 (ADR-021); registro avanzado EPIC-38/39 POST-MVP |
| Gobernanza de inferencia (consumo, límites) | — | EPIC-23 | POST-MVP |

En el MVP, el razonamiento principal lo aportan los agentes externos conectados por MCP (ADR-010), y ACM les ahorra tokens con modelos locales (ADR-012). El orquestador interno queda aplazado (CONF-003). Desde SPRINT-008, ACM también usa sus modelos **por sí mismo**: el supervisor revisa el trabajo ágil y el agente interno responde sobre el proyecto (`agents.md`).
