# Sprint activo

## SPRINT-001 — Esqueleto del backend y núcleo de proyecto

| Campo | Valor |
|-------|-------|
| Sprint ID | SPRINT-001 |
| Objetivo | Primer código de producto: esqueleto Python de ACM y núcleo de proyectos sobre SQLite, accesible por MCP |
| Inicio | 2026-09-30 |
| Fin | Al cumplir el Sprint Goal (sin timebox; desarrollo por agente) |
| Sprint Goal | **Un agente IA puede crear, listar, abrir y configurar proyectos ACM, cada uno con su propia base SQLite, a través del servidor MCP de ACM, con cada criterio de aceptación verificado por tests automáticos.** |
| Historias | US-01.01, US-01.02, US-01.03, US-01.06, US-18.01, US-18.02, US-18.03 (READY; refinamientos en `01_PRODUCTO/refinements/`) |
| Dependencias | ADR-011, ADR-013, ADR-014 |
| Riesgos | Sin autenticación hasta EPIC-20 (HTTP ligado a 127.0.0.1 por defecto); FastAPI aún no probado con el montaje MCP (ADR-014); el SDK MCP es muy reciente |
| Impedimentos | Ninguno |
| Fuera de alcance | Interfaz web (US-01.02 CA-03), autenticación (EPIC-20), skills en producto (FEAT-15.02/03), WebSocket/eventos (EPIC-21), API REST de proyectos (EPIC-30), interfaces de inferencia (ADR-015) |
| Velocidad | No se mide |

### Tasks

| ID | Tipo | Título | Historias | Estado |
|----|------|--------|-----------|--------|
| TASK-000-10 | DOCUMENTATION | Depurar solapamientos de EPIC-01/18/24 (6 fusiones en `tools/dedupe.json`); resto de épicas pendiente | GAP-006 | VERIFIED (parcial: 35 solapamientos siguen pendientes en otras épicas) |
| TASK-001-01 | INFRASTRUCTURE | Esqueleto: `pyproject.toml`, paquete `src/acm`, CLI, configuración, CI | todas | VERIFIED (CI en GitHub: success, [run #1](https://github.com/NoaR-es/ACM/actions/runs/36758248042)) |
| TASK-001-02 | TASK | Capa de datos: conexión (ADR-013), transacciones, migrador y catálogos v1 | US-18.01..03 | VERIFIED |
| TASK-001-03 | TASK | `ProjectService`: crear, listar, abrir, configurar; principales y pertenencias | US-01.01..03 | VERIFIED |
| TASK-001-04 | TASK | Servidor MCP: herramientas de proyecto, `instructions`, errores explícitos (GAP-007) | US-01.01..03, US-01.06 | VERIFIED |
| TASK-001-05 | TASK | App ASGI: FastAPI + `/mcp` + `/api/health` y modo stdio (verifica ADR-014 con FastAPI) | US-01.06, US-18.01 | VERIFIED (ADR-014 comprobado con FastAPI) |
| TASK-001-06 | TEST | Tests automáticos que verifican cada CA | todas | VERIFIED (50 tests; 6 mutaciones detectadas) |
| TASK-000-07 | DECISION | Decidir tooling del frontend React (GAP-002) | — | PLANNED (arrastrada de SPRINT-000) |

SPRINT-000 cerrado y archivado en `99_ARCHIVO/historical/sprint_000.md`.

### Estado de las historias (2026-09-30)

| Historia | Estado | Evidencia |
|----------|--------|-----------|
| US-01.01 | VERIFIED | `12_TESTING/sprint_001_evidence.md` |
| US-01.02 | IMPLEMENTED | CA-03 y la parte de cliente de CA-04 requieren la interfaz web |
| US-01.03 | VERIFIED | idem |
| US-01.06 | VERIFIED | idem |
| US-18.01 | VERIFIED | idem |
| US-18.02 | VERIFIED | idem |
| US-18.03 | VERIFIED | idem |

VERIFIED = todos los CA con test automático en PASS. DONE requiere además la revisión del operador (merge del PR).
