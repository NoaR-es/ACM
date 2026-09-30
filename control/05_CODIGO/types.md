# Interfaces y tipos

Actualizado: 2026-09-30 (SPRINT-007).

## Contratos entre backend y frontend
El frontend (TypeScript) y el backend (Python) comparten el contrato de la API REST v1, no el código (ADR-005: lenguajes distintos).

| Tipo TS (`web/src/types.ts`) | Ruta REST | Origen en Python |
|------------------------------|-----------|------------------|
| `Me` | `GET /me` | `IdentityService.get_principal` |
| `PortfolioProject`, `Governance` | `GET /projects`, `GET /projects/{p}/governance` | `web_api.portfolio_entry`, `WatchdogService.status/history` |
| `Backlog`, `Requirement`, `Epic`, `Feature`, `Story`, `Criterion`, `Gaps` | `GET /projects/{p}/backlog` | `BacklogService.list_requirements/list_epics/list_stories/audit` |
| `StoryDetail` | `GET /projects/{p}/stories/{s}` | `get_story` + `status_history` + `STORY_TRANSITIONS` |
| `Kanban`, `Card` | `GET /kanban` | `web_api.kanban` |
| `WatchdogRun`, `Finding`, `Semaphore` | `GET /projects/{p}/governance` | `WatchdogService.run/history` |
| `AcmEvent` | `WS /ws`, `GET /events` | `EventStore.after` |

**Riesgo registrado:** no hay generación automática de tipos desde OpenAPI. Un cambio de forma en la API que no se refleje en `types.ts` lo detectan los e2e, no el compilador (candidato a deuda técnica si crece la API).

## Tipos y protocolos del backend
- Puertos de inferencia (`inference/ports.py`): `DecisionEngine`, `GenerationEngine` (Protocol, `runtime_checkable`) y dataclasses del contrato de decisión y generación. Ver `classes.md`.
- Estados de historia: `backlog.STORY_STATUSES` / `STORY_TRANSITIONS` ↔ `theme.STATUS_ORDER` en el frontend. El frontend no los inventa: el flujo lo toma de `/meta` y del Kanban.
- Errores: `AcmError.code` ↔ `ApiError.code` en el frontend (mismo texto).
