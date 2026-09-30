# Eventos de dominio (SPRINT-006)

| Tipo | Entidad | Emisor | `data` | Visible para |
|------|---------|--------|--------|--------------|
| `project.created` | project | `ProjectService.create` | `name` | miembros del proyecto, admin |
| `project.config_changed` | project | `ProjectService.set_config` | `changed` | miembros, admin |
| `requirement.created` | requirement | `BacklogService` | `title` | miembros, admin |
| `epic.created` / `epic.updated` | epic | `BacklogService` | `title` / `requirement_ids` o `coverage_confirmed` | miembros, admin |
| `feature.created` / `feature.split` | feature | `BacklogService` | `epic_id` / `split_into` | miembros, admin |
| `story.created` / `story.updated` | story | `BacklogService` | `status`, `feature_id`, `epic_id`, `i_want`, `kind` | miembros, admin |
| `story.status_changed` | story | `mark_ready`, `set_status` | lo anterior + `from` | miembros, admin |
| `member.changed` | member | `IdentityService` | `role` (null si se retira) | miembros, admin |
| `principal.changed` | principal | `IdentityService` | `kind`, `role` | admin |
| `watchdog.run` | project | `WatchdogService.run` | `run_id`, `semaphore`, `integrity`, `counts` | miembros, admin |
| `activity` | operation | servidor MCP (cada invocación) | `status`, `error` | admin |

Los tokens nunca aparecen en eventos.
