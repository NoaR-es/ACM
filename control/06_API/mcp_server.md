# Servidor MCP de ACM

Estado: **PLANNED** — nada implementado en producto; **prototipo validado en SPIKE-002** (`spikes/spike_002_mcp/`). Decisión de topología: ADR-014. Decisiones: ADR-005 (Python) y ADR-008 (servidor propio + skills). Historias (numeración unificada, ADR-010): servidor propio FEAT-14.02..14.04 (US-14.04..US-14.11); registro y versionado de skills FEAT-15.01 (US-15.01, US-15.03); distribución FEAT-15.02 (US-15.04..US-15.07); catálogo FEAT-15.03 (US-15.08..US-15.12). ACM como *cliente* MCP (US-14.01..14.03) es POST-MVP.

## Principio
El servidor MCP **es ACM**: los agentes IA se conectan a él para operar sobre los proyectos. Al conectarse, reciben las instrucciones y las skills necesarias para usar ACM correctamente.

## Flujo de conexión previsto
1. Conexión → el servidor declara `resources`, `tools` y la extensión `io.modelcontextprotocol/skills` (`directoryRead=false`), y devuelve `instructions` que piden cargar las skills de ACM. `prompts`: por decidir.
2. El agente llama a `skills/list` → recibe el catálogo (`skill://acm/...`) con `digest` y `size` por archivo.
3. El agente descarga cada archivo con `resources/read` (o con `skills/get`).
4. El agente opera mediante herramientas MCP indicando **`project_id` en cada llamada** (US-14.08). No existe "proyecto seleccionado" por sesión (ADR-014, prueba D1).
5. Si el catálogo cambia → notificación de cambio de lista de recursos; el agente compara `digest` y vuelve a descargar lo que haya cambiado.

Clientes sin extensión de skills: herramientas de respaldo `acm_skills_list` y `acm_skill_get` (validadas en el prototipo).

## Catálogo inicial de skills (FEAT-22.01) — PLANNED
| Skill | URI | Historia | Propósito |
|-------|-----|----------|-----------|
| acm-schema | `skill://acm/acm-schema/SKILL.md` | US-15.08 | Modelo de datos y flujo de trabajo de ACM: qué entidades hay, cómo se relacionan y qué herramientas usar en cada paso |
| acm-invest | `skill://acm/acm-invest/SKILL.md` | US-15.09 | Validar historias según INVEST y criterios binarios |
| acm-discovery | `skill://acm/acm-discovery/SKILL.md` | US-15.10 | Discovery Socrático antes de crear backlog |
| acm-error-analysis | `skill://acm/acm-error-analysis/SKILL.md` | US-15.11 | Análisis de errores y causa raíz con registro en ACM |
| acm-documentation | `skill://acm/acm-documentation/SKILL.md` | US-15.12 | Documentación viva enlazada a requisitos y evidencias |

Frontmatter obligatorio: `name`, `description`, `version`. Ubicación en el código: directorio de skills del paquete Python de ACM (ruta exacta al crear el esqueleto).

## Límites de la extensión (SEP-2640)
- Hasta 512 recursos y 16 MiB por skill.
- Error `-32602` si la skill no existe; `-32603` para errores internos.

## Seguridad
- Las skills se sirven como contenido de solo lectura.
- No se incluyen scripts ejecutables en el MVP.
- Acceso autenticado (EPIC-16) y descargas auditadas (US-14.11).

## Resultados de SPIKE-002 (2026-09-30, SDK `mcp` 2.2.0)

| # | Pregunta | Respuesta | Evidencia |
|---|----------|-----------|-----------|
| 1 | ¿El SDK soporta `2026-07-28` y la extensión Skills? | Soporta y negocia `2026-07-28`. **No trae** la extensión Skills, pero su API `Extension` (métodos, recursos y ajustes propios) permite implementarla: `skills/list`, `skills/get`, recursos `skill://acm/...` con digest sha256, error `-32602` para skill inexistente. | `test_proto.py` 11/11 PASS |
| 2 | ¿Transporte y convivencia con API y WebSocket? | Streamable HTTP montado en `/mcp` de una app Starlette junto a `/api/health` y `/ws`, en un solo proceso uvicorn (el `session_manager.run()` del SDK se arranca en el lifespan de la app). stdio también funciona con el mismo servidor. Una herramienta MCP publicó un evento que recibió el WebSocket. | `test_asgi_topology.py` 4/4, `test_proto.py` (stdio) |
| 3 | ¿Aislamiento multi-proyecto por sesión? | Con `2026-07-28` cada petición HTTP es autocontenida: el servidor **no conservó** el proyecto seleccionado entre dos llamadas del mismo cliente (el `ctx.session` era distinto en cada una). El proyecto explícito en cada llamada, validado contra el alcance del llamante, aísla y rechaza el acceso cruzado. | `test_session_isolation.py` 3/3 |
| 4 | ¿Qué clientes cargan automáticamente las skills servidas? | **UNKNOWN.** No verificable en este entorno. Mitigación: `instructions` + herramientas de respaldo. | — |

Hallazgo adicional: el SDK devuelve al agente "Error executing tool …" ante excepciones genéricas y oculta el motivo (GAP-007). El producto debe emitir errores de herramienta con mensaje explícito.

## Fuentes
- https://github.com/modelcontextprotocol/ext-skills (especificación estable `skills.mdx`)
- https://modelcontextprotocol.io/seps/2640-skills-extension
- https://devblogs.microsoft.com/agent-framework/discover-agent-skills-from-mcp-servers-in-net/
