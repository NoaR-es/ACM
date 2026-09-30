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
| GAP-NNN | Hueco/inconsistencia detectado en el sistema de control o backlog. |
| MVP / POST-MVP | Clasificación de alcance (ADR-010). |
| Fuente A / Fuente B | A = `backlog_completo_v1.md` (columna vertebral del backlog); B = `product_definition_v3.md` (definición v1.2). ADR-010. |
| Backlog unificado | Backlog generado a partir de A y B con IDs sin colisiones; traducción de IDs de B en `id_mapping.md`. |
| CA-NN | Criterio de aceptación binario PASS/FAIL de una historia. |
| CONF-NNN | Conflicto de requisitos entre fuentes que requiere decisión del operador. |
| Orquestador | Componente de ACM que asigna trabajo a agentes internos (EPIC-07, POST-MVP). |
| Skill | Paquete de instrucciones (`SKILL.md` con frontmatter YAML) que enseña a un agente a realizar una tarea; ACM sirve las suyas por MCP (ADR-008). |
| Extensión MCP Skills | SEP-2640, `io.modelcontextprotocol/skills`: estándar para descubrir y distribuir skills por MCP (`skills/list`, `skills/get`, URIs `skill://`). |
| WAL | Write-Ahead Logging de SQLite: los lectores no se bloquean con un escritor activo (ADR-013). |
| BEGIN IMMEDIATE | Transacción SQLite que toma el lock de escritura al empezar; obligatoria para escrituras en ACM (ADR-013). |
| Streamable HTTP | Transporte HTTP de MCP; ACM lo sirve en `/mcp` (ADR-014). |
| 2026-07-28 | Revisión del protocolo MCP con peticiones autocontenidas (sin handshake ni sesión); impide el estado de "proyecto seleccionado" por sesión (ADR-014). |
| DecisionEngine / GenerationEngine | Interfaces de inferencia del núcleo (ADR-015). |
| Spike | Experimento acotado para responder una pregunta técnica; su código vive en `spikes/` y no es producto. |
| Principal | Identidad que llama a ACM, de tipo `user` o `agent`. Rol global `admin`/`user`. Por HTTP la fija su token (ADR-017); en stdio y CLI, `ACM_PRINCIPAL`. |
| Token de ACM | Credencial `acm_…` de un principal. Se muestra una vez; ACM guarda su hash y un prefijo. Revocable al instante. |
| owner / member | Roles de pertenencia a un proyecto: owner modifica la configuración y gestiona miembros; member lee y escribe el backlog. |
| Refinamiento | Documento `01_PRODUCTO/refinements/US-NN.MM.md` con las secciones de la regla READY de la fuente A. |
| Fusión (dedupe) | Marcar una historia como duplicado de otra (`tools/dedupe.json`): queda CANCELLED y sus CA pasan a la destino. `cross_epic: true` permite fusionar entre épicas. |
| Skill | Paquete de instrucciones en Markdown (`SKILL.md` con frontmatter) que ACM sirve por MCP para que el agente sepa usarlo. Oficiales en `src/acm/skills/`. |
| Extensión Skills | Extensión MCP `io.modelcontextprotocol/skills` (SEP-2640): métodos `skills/list` y `skills/get`, archivos como recursos `skill://`. |
| Digest | `sha256:<hex>` del contenido de un archivo de skill; cambia solo si cambia el contenido (US-15.06). |
| Auditoría MCP | Registro en `mcp_audit` de cada invocación: principal, operación, argumentos, estado, error, resultado (truncado) y duración. |
| Motor de decisión | Implementación del puerto `DecisionEngine` (reglas, Ollama, JEV). Responde preguntas `noul`, `choice` o `score`. |
| Router de inferencia | `EngineRouter`: elige motor según `decision.engine_order`, aplica fallback y registra cada llamada. Los consumidores solo hablan con él. |
| Calibrado | Respuesta cuyas probabilidades son reales (reglas exactas, JEV). La de un LLM generativo no lo es: un gate no la acepta. |
| purpose | Para qué se pide una decisión o generación (p. ej. `story.quality`, `context.compact`); sirve para enrutar y auditar. |
| Contexto compacto | Contexto de una historia por secciones con fuentes, resumido si supera el presupuesto (US-35.08). |
| chars/4@v1 | Método versionado de estimación de tokens: ⌈caracteres / 4⌉ del JSON entregado (US-35.09). |
| TD-NNN | Deuda técnica detectada durante el desarrollo (`13_BUGS/known_issues.md`); distinta de las historias TECH-NNN del backlog. |
