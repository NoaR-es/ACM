---
name: acm-schema
description: Explica qué es ACM, su modelo de datos (proyecto, requisito, épica, feature, historia, criterio de aceptación) y qué herramienta MCP usar en cada paso. Léela antes de operar sobre cualquier proyecto ACM.
version: 1.3.0
capabilities: [acm-model, acm-tools, acm-workflow, acm-second-brain, acm-identity, acm-governance]
dependencies: []
---

# ACM — modelo y herramientas

ACM (Agile Context Manager) es la memoria de estado y gobernanza de tus proyectos. Todo lo que registras queda
en SQLite: es la fuente de verdad. Úsalo para no tener que recordar el proyecto en tu propio contexto.

## Reglas de uso
1. **No existe "proyecto activo".** Pasa `project_id` en cada herramienta de proyecto; compruébalo en la respuesta.
2. **Los errores empiezan por un código** (`INVALID_ARGUMENT`, `NOT_FOUND`, `ALREADY_EXISTS`, `FORBIDDEN`,
   `FAILED_PRECONDITION`, `STORAGE_ERROR`, `ENGINE_UNAVAILABLE`, `ENGINE_ERROR`, `UNAUTHENTICATED`) seguido del campo y el motivo. Corrige la llamada según el motivo.
3. **Todo queda auditado** (quién, con qué token, qué, argumentos, resultado, duración). Los secretos se redactan.
4. **Nada se inventa:** una historia solo pasa a READY con actor, acción, valor, requisito de origen y criterios.
5. **Identidad:** por HTTP te identifica tu token (`Authorization: Bearer acm_…`); tus permisos son los de tu
   principal. `acm_whoami` te dice quién eres, tu rol global y en qué proyectos puedes trabajar.

## Modelo
```text
Proyecto (project_id)
└── Requisito REQ-NNN
    ↑ (origen)
└── Épica EPIC-NN (objetivo, alcance, requisitos asociados)
    └── Feature FEAT-NN.MM (ACTIVE | SPLIT)
        └── Historia US-NN.MM (como / quiero / para, requisitos de origen, estado)
            └── Criterio de aceptación CA-NN (binario, PASS/FAIL)
```

## Flujo recomendado
1. `acm_project_list` → elige `project_id` (o `acm_project_create`).
2. `acm_requirement_create` por cada requisito del producto.
3. `acm_epic_create` (objetivo + alcance + `requirement_ids`).
4. `acm_feature_create` dentro de cada épica; si una feature crece demasiado, `acm_feature_split`.
5. `acm_story_create` con `as_a`, `i_want`, `so_that`, `requirement_ids` y `acceptance_criteria`
   (ver la skill `acm-invest`). Añade criterios con `acm_story_add_criteria`.
6. `acm_story_mark_ready` cuando la historia esté completa.
7. `acm_epic_confirm_coverage` cuando las features cubran el objetivo de la épica.
8. `acm_backlog_audit` y `acm_requirement_trace` para detectar huecos de trazabilidad.

## Segundo cerebro: ahorra tus tokens
- **Contexto de una historia:** en lugar de leer historia, épica, requisitos e historias hermanas por separado, pide
  `acm_context_compact(project_id, story_id, budget_tokens?)`. Recibes secciones (`story`, `acceptance_criteria`,
  `requirements`, `feature`, `epic`, `related_stories`), cada una con sus `sources`. La historia y sus criterios van
  siempre literales; el resto puede venir resumido por un modelo local (`summarized: true`). Si no hay modelo,
  `not_summarized_reason` lo dice. La respuesta indica `delivered_tokens`, `full_equivalent_tokens` y el
  `estimation_method` (`chars/4@v1`: estimación, no el tokenizador de tu modelo).
- **Decisiones delegadas:** `acm_decide(project_id, purpose, questions, state)`. Tipos de pregunta:
  `noul` (sí/no → `value` = P(sí)), `choice` (`criteria` = {opción: descripción} → `value` = opción) y `score`
  (`criteria` = [nivel, …] de 2 a 10 → `value` = 1..n). La respuesta dice qué motor decidió (`engine`), si sus
  probabilidades son reales (`calibrated`) y si hubo `fallback_from`. Con `calibrated: false` trata la confianza
  como orientativa, no como probabilidad.
- **Qué cubren las reglas (sin modelo):** `acm_engines_list` devuelve el catálogo `rules`. Hoy: purpose
  `story.quality` con `state` = la historia de `acm_story_get` y preguntas `has_statement`, `has_requirements`,
  `has_acceptance_criteria`, `technical_reason_ok` (noul), `readiness` (choice `ready`/`not_ready`) y `completeness`
  (score de 5 niveles). Otras preguntas necesitan un motor con modelo; si no hay, `ENGINE_UNAVAILABLE`.

## Gobernanza (Watchdog)
- `acm_governance_status(project_id)` antes de trabajar: si el semáforo está en RED o `writable` es false, el proyecto
  está en cuarentena por integridad y **no admite escrituras** (`DATA_INTEGRITY`). Avisa al operador; no intentes
  sortearlo.
- `acm_watchdog_run(project_id)` audita el proyecto: integridad SQLite (CRITICAL), calidad de cada historia
  evaluada por el motor de decisión (WARNING si el motor es calibrado; REVIEW si no), y huecos de estructura (INFO).
  Corrige los WARNING antes de marcar historias como READY. `acm_watchdog_history` guarda cada auditoría.

## Herramientas
| Herramienta | Para qué |
|-------------|----------|
| `acm_skills_list` | Lista las skills de ACM (respaldo si tu cliente no soporta la extensión Skills) |
| `acm_skill_get` | Descarga todos los archivos de una skill (respaldo) |
| `acm_skills_reload` | (admin) Relee el catálogo de skills |
| `acm_system_info` | Estado de la plataforma, versión y skills activas |
| `acm_audit_list` | (admin) Consulta la auditoría de invocaciones |
| `acm_project_create` | Crea un proyecto con su propia base SQLite |
| `acm_project_list` | Proyectos a los que tienes acceso |
| `acm_project_open` | Contexto de un proyecto: metadatos, rol, configuración |
| `acm_project_config_get` | Parámetros de configuración del proyecto |
| `acm_project_config_set` | Modifica parámetros (valida todo antes de guardar) |
| `acm_requirement_create` | Registra un requisito |
| `acm_requirement_list` | Lista requisitos |
| `acm_requirement_trace` | Requisito → épicas → features → historias |
| `acm_epic_create` | Crea una épica con objetivo y alcance |
| `acm_epic_link_requirements` | Asocia requisitos a una épica |
| `acm_epic_get` | Épica con sus features e historias |
| `acm_epic_list` | Todas las épicas del proyecto |
| `acm_epic_confirm_coverage` | Confirma que las features cubren el objetivo de la épica |
| `acm_feature_create` | Crea una feature en una épica |
| `acm_feature_split` | Divide una feature en varias repartiendo sus historias |
| `acm_story_create` | Crea una historia de usuario (o técnica con razón explícita) |
| `acm_story_add_criteria` | Añade criterios de aceptación |
| `acm_story_get` | Historia con requisitos y criterios |
| `acm_story_mark_ready` | PLANNED → READY si la historia está completa |
| `acm_backlog_audit` | Huecos: requisitos huérfanos, épicas/features vacías, historias sin criterios |
| `acm_context_compact` | Contexto compacto de una historia, con fuentes y tokens ahorrados |
| `acm_decide` | Decisión tipada (noul, choice, score) delegada en el motor de decisión |
| `acm_engines_list` | Motores de inferencia, su estado, modelos detectados y reglas disponibles |
| `acm_engines_refresh` | (admin) Comprueba los motores y detecta modelos |
| `acm_savings_report` | (admin) Tokens ahorrados por agente y proyecto |
| `acm_whoami` | Tu identidad, rol global, proyectos y tokens activos |
| `acm_principal_create` | (admin) Alta de un usuario o agente |
| `acm_principal_list` | (admin) Principales y roles disponibles |
| `acm_principal_set_role` | (admin) Cambia el rol global |
| `acm_member_set` | (admin/owner) Añade un miembro al proyecto o cambia su rol |
| `acm_member_remove` | (admin/owner) Retira a un miembro del proyecto |
| `acm_member_list` | Miembros del proyecto |
| `acm_token_create` | (admin) Crea un token; el secreto solo se muestra una vez |
| `acm_token_list` | Tokens sin secreto: prefijo, estado y uso |
| `acm_token_revoke` | Revoca un token al instante |
| `acm_watchdog_run` | Audita integridad, calidad de historias y estructura; semáforo y hallazgos |
| `acm_watchdog_history` | Histórico de auditorías del proyecto |
| `acm_governance_status` | Semáforo de la última auditoría, integridad y si admite escrituras |
| `acm_health` | (admin) Salud de bases, catálogo de skills y motores |
