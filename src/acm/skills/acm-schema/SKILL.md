---
name: acm-schema
description: Explica qué es ACM, su modelo de datos (proyecto, requisito, épica, feature, historia, criterio de aceptación) y qué herramienta MCP usar en cada paso. Léela antes de operar sobre cualquier proyecto ACM.
version: 1.0.0
capabilities: [acm-model, acm-tools, acm-workflow]
dependencies: []
---

# ACM — modelo y herramientas

ACM (Agile Context Manager) es la memoria de estado y gobernanza de tus proyectos. Todo lo que registras queda
en SQLite: es la fuente de verdad. Úsalo para no tener que recordar el proyecto en tu propio contexto.

## Reglas de uso
1. **No existe "proyecto activo".** Pasa `project_id` en cada herramienta de proyecto; compruébalo en la respuesta.
2. **Los errores empiezan por un código** (`INVALID_ARGUMENT`, `NOT_FOUND`, `ALREADY_EXISTS`, `FORBIDDEN`,
   `FAILED_PRECONDITION`, `STORAGE_ERROR`) seguido del campo y el motivo. Corrige la llamada según el motivo.
3. **Todo queda auditado** (quién, qué, argumentos, resultado, duración).
4. **Nada se inventa:** una historia solo pasa a READY con actor, acción, valor, requisito de origen y criterios.

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
