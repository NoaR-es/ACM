# Hooks y proveedores de estado (`web/src`)

Actualizado: 2026-09-30 (SPRINT-008).

| Hook / proveedor | Archivo | Devuelve | Efectos | Invariantes |
|------------------|---------|----------|---------|-------------|
| `AuthProvider` / `useAuth()` | `auth.tsx` | `token`, `bootstrapping`, `me`, `isAdmin`, `login(token)`, `logout()`; en modo local pide un token a `/api/local-session` al arrancar (no tras salir a propósito) | `login` valida el token con `/me` antes de guardarlo; `logout` borra token y caché. Escucha `acm:unauthenticated` (401 de la API o cierre 4401 del WebSocket) | el token solo vive en sessionStorage |
| `LiveProvider` / `useLive()` | `live.tsx` | `status` (offline/connecting/live/reconnecting), `events` (últimos 300), `lastSeq`, `changedAt(p, id)`, `announcement` | abre el WebSocket con el token; reconecta con backoff y `after`; invalida en react-query las claves que afecta cada evento (`liveCore.affectedKeys`); `resync` → invalida todo | eventos aplicados en orden, sin duplicados (`liveCore.receive`) |
| `PrefsProvider` / `usePrefs()` | `prefs.tsx` | `mode` (system/light/dark), `theme`, `setMode` | aplica las variables CSS de `theme.ts` en `<html>`; recuerda la elección en localStorage; sigue al sistema en modo `system` | solo colores de la paleta verificada |
| `useBacklog(projectId)` | `pages/Project.tsx` | query del backlog completo | GET `/projects/{id}/backlog` (clave `["project", id, "backlog"]`) | — |
| `useNow(ms)` (interno) | `KanbanBoard.tsx` | reloj para caducar el resaltado | intervalo | — |
| `useAction(fn, keys)` | `forms.tsx` | mutación de react-query | invalida `keys` al terminar bien; el error conserva código y campo | lo escrito no se pierde si falla |
| `useSprints(projectId)` | `pages/Sprints.tsx` | query de sprints | GET `/projects/{id}/sprints` (clave `["sprints", id]`) | — |

Claves de react-query y quién las invalida: `["projects"]`, `["kanban", …]`, `["project", id, …]`, `["story", id, story]`, `["governance", id]`, `["members", id]`, `["activity", …]`, `["me"]`, `["principals"]`, `["sprints", id]`, `["models"]`, `["engines"]`, `["chat", id, …]`, `["tokens"]` — invalidadas por eventos (`liveCore.affectedKeys`) y por las mutaciones de cada página. Refresco periódico de seguridad: 120 s (TD-003).
