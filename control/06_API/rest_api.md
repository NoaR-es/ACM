# API REST v1 (SPRINT-006)

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
