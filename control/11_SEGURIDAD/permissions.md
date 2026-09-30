# Permisos por herramienta MCP (SPRINT-004)

| Herramientas | Quién |
|--------------|-------|
| `acm_project_create`, `acm_principal_create`, `acm_principal_list`, `acm_principal_set_role`, `acm_token_create`, `acm_audit_list`, `acm_skills_reload`, `acm_engines_refresh`, `acm_savings_report` | admin |
| `acm_member_set`, `acm_member_remove`, `acm_project_config_set` | admin u owner del proyecto |
| Herramientas de backlog, contexto y decisión (`acm_requirement_*`, `acm_epic_*`, `acm_feature_*`, `acm_story_*`, `acm_backlog_audit`, `acm_context_compact`, `acm_decide`), `acm_project_open`, `acm_project_config_get`, `acm_member_list` | cualquier miembro del proyecto (o admin) |
| `acm_project_list` | cualquiera (solo ve sus proyectos; un admin, todos) |
| `acm_token_list`, `acm_token_revoke` | los propios; los ajenos, admin |
| `acm_whoami`, `acm_system_info`, `acm_skills_list`, `acm_skill_get`, `acm_engines_list` | cualquier principal autenticado |

Pendiente (US-20.07): la lista de herramientas (`tools/list`) es la misma para todos; el control se aplica al invocarlas.
