# API REST v1 (SPRINT-006; escritura y nuevas rutas en SPRINT-008)

- **Base:** `/api/v1`. **Autenticación:** `Authorization: Bearer acm_…` (ADR-017).
- **Contrato:** `/api/v1/openapi.json` y `/api/v1/docs`, generados del código (US-30.02).
- **Errores:** `{"error": {"code", "message", "field"}}`:
  - 400 INVALID_ARGUMENT (incluye JSON inválido);
  - 401 UNAUTHENTICATED;
  - 403 FORBIDDEN;
  - 404 NOT_FOUND;
  - 409 FAILED_PRECONDITION / ALREADY_EXISTS / DATA_INTEGRITY;
  - 502/503 motores.
- **Versionado:** en la ruta. Un cambio incompatible crea `/api/v2` (US-30.03).

| Método | Ruta | Devuelve | Quién |
|--------|------|----------|-------|
| GET | `/me` | Principal, rol, proyectos, tokens activos | cualquiera |
| GET | `/meta` | Versión, estados, transiciones, columnas Kanban, último `seq`, suscripciones activas | cualquiera |
| GET | `/projects` | Cartera: proyectos accesibles con semáforo y recuento por estado | cualquiera |
| GET | `/projects/{p}` | Metadatos, rol y configuración | miembros |
| GET | `/projects/{p}/backlog` | Requisitos, épicas (features e historias), historias completas, huecos | miembros |
| GET | `/projects/{p}/stories/{s}` | Historia con criterios, requisitos, historial y transiciones permitidas | miembros |
| POST | `/projects/{p}/stories/{s}/status` | `{status, reason?}` → historia actualizada | miembros |
| POST | `/projects/{p}/stories/{s}/ready` | Gate READY → historia | miembros |
| GET | `/projects/{p}/requirements/{r}/trace` | Traza requisito → épicas → features → historias | miembros |
| GET | `/projects/{p}/context/{s}` | Contexto compacto (US-35.08) | miembros |
| GET | `/projects/{p}/members` · `/config` | Miembros · configuración | miembros |
| GET | `/projects/{p}/governance` | Semáforo, integridad e histórico del Watchdog | miembros |
| POST | `/projects/{p}/watchdog` | Ejecuta una auditoría | miembros |
| GET | `/kanban?projects=a,b` | Columnas, transiciones y tarjetas de uno o varios proyectos | miembros de cada proyecto |
| GET | `/events?after=` | Eventos visibles posteriores a `after` | cualquiera (filtrado) |
| GET | `/activity` | Auditoría (US-14.10) | admin |
| GET | `/health` · `/savings` · `/principals` | Salud por componente · ahorro de tokens · principales | admin |
| GET | `/engines` · `/skills` · `/skills/{name}` | Motores · catálogo de skills · archivos de una skill | cualquiera |
| GET | `/tokens` | Tokens sin secreto | los propios; los de todos, admin |

Las mutaciones REST se auditan como `rest:*` en `mcp_audit`.

## Escritura y nuevas rutas (SPRINT-008)
54 rutas HTTP (28 de escritura; 59 y 31 tras SPRINT-009) más el WebSocket, medidas sobre `src/acm/web_api.py`. Cada escritura llama al mismo servicio de dominio que su herramienta MCP, con la misma autorización, validación y errores. Además emite su evento de actividad (`emit_activity`).

| Método | Ruta | Cuerpo → respuesta | Quién | MCP equivalente |
|--------|------|--------------------|-------|-----------------|
| POST | `/projects` | `{key, name, description?}` → proyecto | según `acm_project_create` | `acm_project_create` |
| PATCH | `/projects/{p}/config` | `{changes: {clave: valor}}` → configuración | admin del proyecto | `acm_project_config_set` |
| POST | `/projects/{p}/requirements` · `/epics` · `/features` · `/stories` | entidad del backlog | miembros | `acm_requirement_create`, `acm_epic_create`, `acm_feature_create`, `acm_story_create` |
| POST | `/projects/{p}/epics/{e}/requirements` · `/epics/{e}/confirm-coverage` | vincular requisitos · confirmar cobertura | miembros | `acm_epic_link_requirements`, `acm_epic_confirm_coverage` |
| POST | `/projects/{p}/features/{f}/split` | `{parts}` → división de una feature | miembros | `acm_feature_split` |
| POST | `/projects/{p}/stories/{s}/criteria` | `{criteria:[…]}` → historia | miembros | `acm_story_add_criteria` |
| GET/POST | `/projects/{p}/sprints` · GET `/sprints/{id}` | listar · crear `{name, goal, start_date, end_date, capacity?}` | miembros | `acm_sprint_list`, `_get`, `_create` |
| POST/DELETE | `/projects/{p}/sprints/{id}/stories` · `/stories/{s}` | planificar `{story_ids}` (devuelve `warnings`) · quitar | miembros | `acm_sprint_add_stories` / `_remove_story` |
| POST | `/projects/{p}/sprints/{id}/start` · `/close` · `/cancel` | `{force?}` · `{carry_over_to?}` · — | miembros | `acm_sprint_start` / `_close` / `_cancel` |
| PUT/DELETE | `/projects/{p}/members/{principal}` | `{role}` · — | admin u owner | `acm_member_set` / `acm_member_remove` |
| POST | `/principals` · PUT `/principals/{id}/role` | `{principal_id, kind, role?}` · `{role}` | admin | `acm_principal_create` / `_set_role` |
| POST/DELETE | `/tokens` · `/tokens/{id}` | `{principal_id, name}` emitir (secreto solo en esta respuesta) · revocar | emitir: admin; revocar: propios o admin | `acm_token_create` / `_revoke` |
| POST | `/engines/refresh` | redetecta motores y modelos | admin | `acm_engines_refresh` |
| GET/PUT | `/models` | catálogo con guía de uso · `{ollama_model?, jev_default_model?, jev_models_by_purpose?, jev_model_notes?}` selección por propósito (ADR-021) | GET cualquiera; PUT admin | `acm_models_list` / `_select` |
| GET | `/projects/{p}/chat/threads` · `/chat/threads/{TH}` | hilos · mensajes de un hilo | miembros | `acm_chat_threads` / `_get` |
| POST | `/projects/{p}/chat` | `{message, thread_id?, title?}` → respuesta, hilo y herramientas usadas (ADR-022) | miembros | `acm_chat` |
| GET | `/kanban?projects=a&sprint=SP-001` | tablero filtrado por sprint (un solo proyecto) | miembros | — |

Los nombres exactos de las herramientas MCP están en `mcp_server.md`. Tests: `tests/test_rest_write.py`, `tests/test_sprints.py`, `tests/test_models_chat.py`, `tests/test_realtime.py` (toda ruta exige autenticación).

## Agentes: unión con aprobación y trabajo (SPRINT-009)
59 rutas HTTP (31 de escritura), medidas sobre `src/acm/web_api.py`.

| Método | Ruta | Cuerpo → respuesta | Quién | MCP equivalente |
|--------|------|--------------------|-------|-----------------|
| GET | `/join-requests?status=PENDING` | peticiones que el actor puede decidir (+ `can_decide`) | admin: todas; owner: las suyas | — |
| POST | `/join-requests/{id}/approve` | `{role?}` (member \| viewer) → petición | persona admin u owner | — (solo personas) |
| POST | `/join-requests/{id}/reject` | — → petición | persona admin u owner | — (solo personas) |
| GET | `/projects/{p}/work` | asignaciones vigentes (`agent` = principal#sesión) | miembros | `acm_work_list` |
| DELETE | `/projects/{p}/work/{item}` | libera una asignación | quien la tiene; una persona, cualquiera | `acm_work_release` |
| GET | `/kanban` | cada tarjeta incluye `assigned_to` | miembros | — |
| GET | `/api/local-session` (fuera de `/api/v1`) | `{"token": ...}` o `{"token": null}` | solo este equipo, con `X-ACM-Local: 1` y `Host` local | — |

Retirar a un agente: `DELETE /projects/{p}/members/{principal}` (ya existía). Eventos nuevos: `join.requested`, `join.decided`, `work.claimed`, `work.released` (`09_MENSAJERIA/events.md`). Tests: `tests/test_access.py`, `tests/test_work.py`, `tests/test_webui_agents.py`, `tests/test_realtime.py` (contrato y autenticación de toda ruta).
