# Permisos por herramienta MCP (SPRINT-004; ampliado en SPRINT-008)

| Herramientas | Quién |
|--------------|-------|
| `acm_project_create`, `acm_principal_create`, `acm_principal_list`, `acm_principal_set_role`, `acm_token_create`, `acm_audit_list`, `acm_skills_reload`, `acm_engines_refresh`, `acm_savings_report` | admin |
| `acm_member_set`, `acm_member_remove`, `acm_project_config_set` | admin u owner del proyecto |
| `acm_health` | admin |
| `acm_watchdog_run`, `acm_watchdog_history`, `acm_governance_status` | cualquier miembro del proyecto (o admin) |
| Herramientas de backlog, contexto y decisión (`acm_requirement_*`, `acm_epic_*`, `acm_feature_*`, `acm_story_*`, `acm_backlog_audit`, `acm_context_compact`, `acm_decide`), `acm_project_open`, `acm_project_config_get`, `acm_member_list` | cualquier miembro del proyecto (o admin) |
| `acm_project_list` | cualquiera (solo ve sus proyectos; un admin, todos) |
| `acm_token_list`, `acm_token_revoke` | los propios; los ajenos, admin |
| `acm_whoami`, `acm_system_info`, `acm_skills_list`, `acm_skill_get`, `acm_engines_list`, `acm_models_list` | cualquier principal autenticado |
| `acm_models_select` | admin (SPRINT-008) |
| `acm_sprint_*` | cualquier miembro del proyecto (o admin) (SPRINT-008) |
| `acm_chat` | cualquier miembro del proyecto (o admin); el agente interno solo lee y actúa con los permisos de quien pregunta (ADR-022) |
| `acm_chat_threads`, `acm_chat_get` | los hilos propios; los de todos, admin |

La API REST v1 aplica las mismas reglas: cada ruta llama al mismo servicio de dominio que su herramienta MCP (`06_API/rest_api.md`).

## Principal interno `acm-supervisor` (ADR-020)
Agente con rol admin que ACM da de alta al arrancar el supervisor. Sus acciones se limitan en el código a `story.mark_ready`, `story.back_to_planned` y `sprint.remove_story` (`SAFE_ACTIONS`); cualquier otro tipo se rechaza con FAILED_PRECONDITION. Todo queda auditado como `supervisor:*` y se puede deshacer. No tiene token: no se puede usar desde fuera de ACM.

Pendiente (US-20.07): la lista de herramientas (`tools/list`) es la misma para todos; el control se aplica al invocarlas.
