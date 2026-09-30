# Glosario

| Término | Definición |
|---------|------------|
| ACM | Agile Context Manager, el producto de este repositorio. |
| control/ | Fuente de verdad operacional del proyecto (Markdown). |
| Constitución | `/CLAUDE.md`: reglas de funcionamiento del agente. |
| Watchdog | Agente/subsistema inspector que valida, audita y bloquea operaciones (ACT-05, EPIC-10). |
| INVEST | Independent, Negotiable, Valuable, Estimable, Small, Testable — criterios de calidad de historias. |
| ADR | Architecture Decision Record. |
| MCP | Model Context Protocol: interfaz por la que los agentes invocan herramientas de ACM. |
| RAG | Retrieval-Augmented Generation: recuperación semántica de contexto. |
| Ollama | Motor de inferencia de modelos locales. |
| JEV / Jev | Modelos de decisión "System One" (TypeSafe): estado + preguntas tipadas → respuestas con probabilidades calibradas, sin generar texto. POST-MVP (ADR-006). |
| Ollaya | Runtime local tipo Ollama para modelos de decisión estilo Jev (puerto 11435). |
| choice / score / noul | Tipos de pregunta de un modelo de decisión: categoría, puntuación, sí/no. |
| Walkthrough | Secuencia de pasos (algunos ejecutables) que evidencia que una funcionalidad funciona (EPIC-09). |
| Done-Done | Código terminado **y** verificado con evidencia. |
| Snapshot | Estado coordinado SQLite + Git restaurable (EPIC-13). |
| DocuTwin | Documentación viva sincronizada con el sistema real (EPIC-14). |
| Historia técnica (TECH-NNN) | Trabajo técnico transversal necesario para el producto (no es deuda). |
| TD-NNN | Deuda técnica registrada. |
| GAP-NNN | Hueco/inconsistencia detectado en el sistema de control o backlog. |
| MVP / POST-MVP | Clasificación de alcance (ADR-007). |
