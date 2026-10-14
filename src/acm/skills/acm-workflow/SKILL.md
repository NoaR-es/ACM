---
name: acm-workflow
description: Proceso completo para trabajar con ACM desde cualquier agente - elegir o unirse a un proyecto, pedir trabajo a ACM, hacerlo, registrarlo y repetir, colaborando con otros agentes sin pisarse.
version: 1.0.0
capabilities: [agile-workflow, multi-agent-collaboration]
dependencies: [acm-schema]
---

# Trabajar con ACM

ACM lleva el proceso ágil del proyecto (backlog, sprints, Kanban, trazabilidad y gobernanza). **Tú haces el trabajo;
ACM decide qué toca, lo asigna y lo registra.** Si hay más agentes en el mismo proyecto, ACM reparte el trabajo para que
nadie haga lo mismo que otro. No necesitas coordinarte con ellos: solo con ACM.

## 1. Elegir proyecto (una vez por conversación)
1. `acm_project_directory`: lista los proyectos, tu rol en cada uno (`your_role`) y tus peticiones (`join_request`).
2. Si ya eres miembro del proyecto de la conversación, úsalo. Si no, **pregunta a la persona** con la que trabajas:
   - **Proyecto nuevo:** `acm_project_create` (no necesita aprobación; quedas como owner).
   - **Unirte a uno existente:** `acm_project_join(project_id, access_level)`. La petición queda `PENDING` hasta que
     una persona la apruebe en la interfaz de ACM (Panel → Solicitudes de acceso). Díselo a la persona y consulta
     `acm_project_join_status` cuando te avise. Hasta entonces el proyecto no es accesible para ti.
3. Desde aquí, pasa **siempre** `project_id` en cada herramienta.

## 2. Bucle de trabajo
Repite hasta que `acm_next_work` responda `idle` o la persona te pare:

1. `acm_next_work(project_id)` y haz lo que indique `action`, siguiendo sus `steps`:
   - `build_backlog`: construye el backlog con la persona (usa la skill acm-discovery si el producto no está claro):
     `acm_requirement_create`, `acm_epic_create`, `acm_feature_create`, `acm_story_create` con criterios.
   - `refine`: completa la historia hasta que pase el gate (`acm_story_add_criteria`, criterios binarios; skill
     acm-invest) y `acm_story_mark_ready`.
   - `plan_sprint`: `acm_sprint_create` con objetivo, `acm_sprint_add_stories` con historias READY y `acm_sprint_start`.
   - `start_sprint`: revisa el plan (`acm_sprint_get`) y `acm_sprint_start`.
   - `implement`: `acm_context_compact` para el contexto mínimo; `acm_story_set_status` a `IN_PROGRESS`; implementa en
     el repositorio; al terminar, `IMPLEMENTED`.
   - `verify`: comprueba **cada** criterio con pruebas reales; `TESTING` y después `VERIFIED` o `FAILED` explicando
     qué falla. Nunca marques `DONE`: lo decide una persona tras revisar.
   - `close_sprint`: `acm_sprint_close`.
2. Vuelve a pedir `acm_next_work`. Tocar la historia y pedir trabajo renueva tu asignación; si dejas un trabajo a
   medias, libéralo con `acm_work_release` para que otro lo coja.
3. Cada cierto tiempo (por ejemplo, al cerrar un sprint), `acm_watchdog_run` y corrige lo que señale el supervisor
   (`findings` e informe): historias mal escritas, sprints sobrecargados, trabajo estancado…

## 3. Reglas
- Una historia asignada a otro agente no se toca: ACM lo rechaza y te dice a quién pertenece. Pide otro trabajo.
- `acm_work_list` muestra quién trabaja en qué.
- Ahorra tokens: `acm_context_compact` en vez de leer el backlog entero; `acm_decide` para clasificar, filtrar o validar
  (sí/no, elegir, puntuar) sin razonarlo tú.
- No inventes estados: un cambio de estado sin el trabajo hecho es un error de trazabilidad.
- Si una herramienta devuelve un error, su código y su motivo dicen qué corregir; no reintentes lo mismo sin cambiar
  nada.
