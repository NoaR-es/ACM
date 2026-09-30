# Sprint activo

## SPRINT-004 — Autenticación y RBAC

| Campo | Valor |
|-------|-------|
| Sprint ID | SPRINT-004 |
| Objetivo | Identidad real: cada petición HTTP se autentica con un token de ACM y actúa con los permisos de su principal, para poder exponer ACM fuera de 127.0.0.1 (VULN-001) |
| Inicio | 2026-09-30 |
| Fin | Al cumplir el Sprint Goal (sin timebox; desarrollo por agente) |
| Sprint Goal | **Ninguna petición MCP por HTTP se ejecuta sin un token de ACM válido. Cada usuario o agente tiene sus propias credenciales, revocables al instante, cuyo secreto nunca se guarda ni se audita. Los roles globales y de proyecto se gestionan por MCP con efecto inmediato, y todo intento queda auditado con su token. Cada CA verificado por tests automáticos contra ACM real por HTTP.** |
| Historias | US-20.01, US-20.02, US-20.03, US-20.04, US-20.05, US-20.08 (refinamientos en `01_PRODUCTO/refinements/`); fusionadas: US-20.06 → 20.01; US-20.09, 20.10, 20.11 → 20.03 |
| Dependencias | ADR-014 (MCP sin estado), ADR-017 (nueva); SPRINT-003 |
| Riesgos | Cambio incompatible: el HTTP ahora exige token; sin TLS propio (VULN-002) |
| Impedimentos | IMP-004 sigue abierto (no afecta a este sprint) |
| Fuera de alcance | Operaciones sensibles con autorización adicional (US-20.12..14: no existen purga ni rollback); limitar la lista de herramientas por rol (US-20.07); OAuth; expiración de tokens; revocación de un principal completo (US-20.15, POST-MVP) |
| Velocidad | No se mide |

### Tasks

| ID | Tipo | Título | Historias | Estado |
|----|------|--------|-----------|--------|
| TASK-004-01 | TASK | Esquema global v4 (`principals.kind`, `api_tokens`, `mcp_audit.token_id`) e `IdentityService` | US-20.01, 20.03, 20.04 | VERIFIED |
| TASK-004-02 | TASK | 10 herramientas MCP de identidad (`acm_whoami`, `acm_principal_*`, `acm_member_*`, `acm_token_*`) y skill acm-schema 1.2.0 | US-20.01..04, 20.08 | VERIFIED |
| TASK-004-03 | TASK | `BearerAuth` en `/mcp`, CLI de arranque (`acm principal create`, `acm token create`) y `ACM_ALLOWED_HOSTS` (TD-002) | US-20.03, 20.05 | VERIFIED |
| TASK-004-04 | TASK | Auditoría con `token_id` y redacción de secretos; owners gestionan miembros; nunca sin admin ni owner | US-20.01, 20.02, 20.03 | VERIFIED |
| TASK-004-05 | TEST | Tests por CA contra ACM real por HTTP (27 nuevos) y matriz de evidencia | todas | VERIFIED (198 tests; 8/8 mutaciones detectadas) |
| TASK-000-10 | DOCUMENTATION | 4 fusiones en EPIC-20 | GAP-006 | VERIFIED (parcial: 18 fusiones en total) |
| TASK-000-07 | DECISION | Decidir tooling del frontend React (GAP-002) | — | PLANNED (arrastrada) |

SPRINT-003 cerrado y archivado en `99_ARCHIVO/historical/sprint_003.md`.

### Estado de las historias (2026-09-30)

| Historia | Estado | Evidencia |
|----------|--------|-----------|
| US-20.01, US-20.02, US-20.03, US-20.04, US-20.05, US-20.08 | VERIFIED | `12_TESTING/sprint_004_evidence.md` |

VERIFIED = todos los CA con test automático en PASS. DONE requiere además la revisión del operador (merge del PR).
