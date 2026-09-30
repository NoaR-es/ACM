# Servidor MCP de ACM

Estado: **PLANNED** — nada implementado. Decisiones: ADR-005 (Python) y ADR-008 (servidor propio + skills). Historias (numeración unificada, ADR-010): servidor propio FEAT-14.02..14.04 (US-14.04..US-14.11); registro y versionado de skills FEAT-15.01 (US-15.01, US-15.03); distribución FEAT-15.02 (US-15.04..US-15.07); catálogo FEAT-15.03 (US-15.08..US-15.12). ACM como *cliente* MCP (US-14.01..14.03) es POST-MVP.

## Principio
El servidor MCP **es ACM**: los agentes IA se conectan a él para operar sobre los proyectos. Al conectarse, reciben las instrucciones y las skills necesarias para usar ACM correctamente.

## Flujo de conexión previsto
1. Inicialización MCP → el servidor declara `resources`, `tools`, `prompts` (por decidir) y la extensión `io.modelcontextprotocol/skills`, y devuelve `instructions` que piden cargar las skills de ACM.
2. El agente llama a `skills/list` → recibe el catálogo (`skill://acm/...`) con `digest` y `size` por archivo.
3. El agente descarga cada archivo con `resources/read` (o con `skills/get`).
4. El agente selecciona el proyecto de forma explícita (US-14.08) y opera mediante herramientas MCP.
5. Si el catálogo cambia → notificación de cambio de lista de recursos; el agente compara `digest` y vuelve a descargar lo que haya cambiado.

Clientes sin extensión de skills: herramientas de respaldo para listar y obtener skills (nombres por fijar en el diseño de TECH-010/011).

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

## Preguntas para SPIKE-002
1. ¿Soporta el SDK MCP de Python la revisión `2026-07-28` y los métodos `skills/list`/`skills/get`? Si no, ¿cómo se añaden?
2. Transporte: stdio y/o HTTP en streaming, y cómo convive con la API web y los WebSockets en el mismo proceso.
3. Aislamiento multi-proyecto por sesión (US-14.08, US-14.09).
4. ¿Qué clientes MCP actuales cargan automáticamente las skills servidas?

## Fuentes
- https://github.com/modelcontextprotocol/ext-skills (especificación estable `skills.mdx`)
- https://modelcontextprotocol.io/seps/2640-skills-extension
- https://devblogs.microsoft.com/agent-framework/discover-agent-skills-from-mcp-servers-in-net/
