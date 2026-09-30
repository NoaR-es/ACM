# Glosario

| Término | Definición |
|---------|------------|
| ACM | Agile Context Manager, el producto de este repositorio. |
| control/ | Fuente de verdad operacional del proyecto (Markdown). |
| Constitución | `/CLAUDE.md`: reglas de funcionamiento del agente. |
| Watchdog | Agente/subsistema inspector que valida, audita y bloquea operaciones (ACT-05, EPIC-13). |
| INVEST | Independent, Negotiable, Valuable, Estimable, Small, Testable — criterios de calidad de historias. |
| ADR | Architecture Decision Record. |
| MCP | Model Context Protocol: interfaz por la que los agentes invocan herramientas de ACM. |
| RAG | Retrieval-Augmented Generation: recuperación semántica de contexto. |
| Ollama | Motor de inferencia de modelos locales. |
| JEV / Jev | Modelos de decisión "System One" (TypeSafe) servidos en local por Ollaya: estado + preguntas tipadas → respuestas con probabilidades calibradas, sin generar texto. Se integrarán (EPIC-50); la interfaz de decisión existe desde el MVP (ADR-006, ADR-012). |
| Interfaz de decisión | Puerto único del núcleo por el que Watchdog, gates y router piden decisiones tipadas; implementaciones: reglas, Ollama y JEV (US-35.11, ADR-012). |
| Segundo cerebro | Papel de ACM respecto al agente IA: contexto compacto y decisiones resueltas con modelos locales para que el agente gaste menos tokens (definición §1.2, ADR-012). |
| Preparado para JEV | Diseño en el que conectar el adaptador JEV no requiere cambiar a los consumidores (US-47.01). |
| Ollaya | Runtime local tipo Ollama para modelos de decisión estilo Jev (puerto 11435). |
| choice / score / noul | Tipos de pregunta de un modelo de decisión: categoría, puntuación, sí/no. |
| Walkthrough | Secuencia de pasos (algunos ejecutables) que evidencia que una funcionalidad funciona (EPIC-28). |
| Done-Done | Código terminado **y** verificado con evidencia. |
| Snapshot | Estado coordinado SQLite + Git restaurable (EPIC-12). |
| DocuTwin | Documentación viva sincronizada con el sistema real (EPIC-25). |
| Historia técnica (TECH-NNN) | Trabajo técnico transversal necesario para el producto (no es deuda). |
| TD-NNN | Deuda técnica registrada. |
| GAP-NNN | Hueco/inconsistencia detectado en el sistema de control o backlog. |
| MVP / POST-MVP | Clasificación de alcance (ADR-010). |
| Fuente A / Fuente B | A = `backlog_completo_v1.md` (columna vertebral del backlog); B = `product_definition_v3.md` (definición v1.2). ADR-010. |
| Backlog unificado | Backlog generado a partir de A y B con IDs sin colisiones; traducción de IDs de B en `id_mapping.md`. |
| CA-NN | Criterio de aceptación binario PASS/FAIL de una historia. |
| CONF-NNN | Conflicto de requisitos entre fuentes que requiere decisión del operador. |
| Orquestador | Componente de ACM que asigna trabajo a agentes internos (EPIC-07, POST-MVP). |
| Skill | Paquete de instrucciones (`SKILL.md` con frontmatter YAML) que enseña a un agente a realizar una tarea; ACM sirve las suyas por MCP (ADR-008). |
| Extensión MCP Skills | SEP-2640, `io.modelcontextprotocol/skills`: estándar para descubrir y distribuir skills por MCP (`skills/list`, `skills/get`, URIs `skill://`). |
