# Inventario de archivos

Actualizado: 2026-09-30 (SPRINT-007). **Regla:** todo archivo de código (`src/acm`, `web/src`, `tests`, `control/tools`) tiene aquí su fila; `control/tools/code_inventory.py --check` (en CI) falla si falta alguno. Detalle por símbolo: `code_reference.md` (generado).

## Backend — `src/acm` (Python 3.11)

| Path | Propósito | Capa | Depende de | Lo usan | Tests | Estado |
|------|-----------|------|------------|---------|-------|--------|
| `src/acm/__init__.py` | Versión del paquete (`__version__`) | paquete | — | app, MCP, API | — | ACTIVE |
| `src/acm/__main__.py` | CLI: `acm serve`, `acm mcp-stdio`, `acm principal create`, `acm token create` | entrada | config, app, identity, audit | operador | `test_app.py`, `test_auth.py::test_cli_*` | IMPLEMENTED |
| `src/acm/config.py` | `Settings`: configuración del proceso desde variables `ACM_*` | configuración | — | app, CLI | `test_app.py`, `test_watchdog.py` | IMPLEMENTED |
| `src/acm/app.py` | Composición ASGI: FastAPI + `/api/health` + `/api/v1` + `/api/v1/ws` + `/mcp` + interfaz en `/`; tareas de fondo (Watchdog, purga de eventos) | composición | todos los servicios, auth, web_api, webui_app, mcp_server | `acm serve`, tests | `test_app.py`, `test_auth.py`, `test_realtime.py`, `test_webui.py` | IMPLEMENTED |
| `src/acm/auth.py` | `BearerAuth`: autenticación HTTP por token y contexto de identidad por petición (ADR-017) | seguridad | identity, audit | app | `test_auth.py` | IMPLEMENTED |
| `src/acm/events.py` | `EventStore`: eventos de dominio persistidos (ADR-018) | mensajería | db.connection | ProjectService (y por él todos los servicios), web_api, mcp_server | `test_realtime.py` | IMPLEMENTED |
| `src/acm/web_api.py` | API REST v1 (24 rutas), WebSocket de eventos, `Access` | API | servicios de dominio, events, auth | app | `test_realtime.py`, `test_webui.py` | IMPLEMENTED |
| `src/acm/webui_app.py` | `SecureStatic`: sirve la interfaz compilada con cabeceras de seguridad (ADR-019) | web | starlette | app | `test_webui.py` | IMPLEMENTED |
| `src/acm/mcp_server.py` | Servidor MCP: 46 herramientas, extensión Skills, auditoría y eventos `activity` | API (agentes) | servicios de dominio, skills_catalog, inference | app, CLI stdio | `test_mcp.py`, `test_skills.py`, `test_audit.py`, `test_auth.py` | IMPLEMENTED |
| `src/acm/skills_catalog.py` | `SkillCatalog`: carga, valida y sirve las skills (US-15.01) | catálogo | — | mcp_server, web_api, watchdog.health | `test_skills.py` | IMPLEMENTED |
| `src/acm/db/connection.py` | `Database`: conexión SQLite por hilo, PRAGMAs, `write()`/`read()` con reintentos (ADR-013) | datos | sqlite3 | ProjectService, EventStore | `test_db.py` | IMPLEMENTED |
| `src/acm/db/migrations.py` | `Migration`, `migrate`: migraciones versionadas (US-18.03) | datos | connection | ProjectService | `test_migrations.py` | IMPLEMENTED |
| `src/acm/db/schema.py` | Catálogos `GLOBAL` (v6) y `PROJECT` (v3) | datos | migrations | ProjectService | `test_migrations.py` y todos | IMPLEMENTED |
| `src/acm/domain/errors.py` | Jerarquía `AcmError` con códigos estables | dominio | — | todo el backend | todos | IMPLEMENTED |
| `src/acm/domain/config_schema.py` | Parámetros de configuración de proyecto y su validación | dominio | errors | ProjectService | `test_projects.py` | IMPLEMENTED |
| `src/acm/domain/projects.py` | `ProjectService`: proyectos, principales, pertenencias, configuración, cuarentena | dominio | db, schema, config_schema, events | todos los servicios | `test_projects.py`, `test_db.py` | IMPLEMENTED |
| `src/acm/domain/backlog.py` | `BacklogService`: requisitos, épicas, features, historias, CA, gate READY, estados | dominio | projects, inference.router | mcp_server, web_api, context, watchdog | `test_backlog.py`, `test_isolation.py`, `test_realtime.py` | IMPLEMENTED |
| `src/acm/domain/identity.py` | `IdentityService`: principales, roles, miembros, tokens | dominio | projects | auth, mcp_server, web_api, CLI | `test_auth.py` | IMPLEMENTED |
| `src/acm/domain/audit.py` | `AuditService`: auditoría de invocaciones con redacción de secretos | dominio | projects | mcp_server, web_api, auth, CLI | `test_audit.py`, `test_auth.py` | IMPLEMENTED |
| `src/acm/domain/context.py` | `ContextService`: contexto compacto y ahorro de tokens | dominio | backlog, inference.router | mcp_server, web_api | `test_context.py` | IMPLEMENTED |
| `src/acm/domain/watchdog.py` | `WatchdogService`: integridad, calidad, semáforo, histórico, salud | dominio | backlog, inference.router, projects | mcp_server, web_api, app | `test_watchdog.py` | IMPLEMENTED |
| `src/acm/inference/__init__.py` | Paquete de inferencia | inferencia | — | — | — | ACTIVE |
| `src/acm/inference/ports.py` | Contratos de decisión y generación (ADR-015/016) | inferencia | errors | todos los consumidores de inferencia | `test_inference.py` | IMPLEMENTED |
| `src/acm/inference/rules.py` | `RulesDecisionEngine` (sin modelo) | inferencia | ports | router | `test_inference.py` | IMPLEMENTED |
| `src/acm/inference/router.py` | `EngineRegistry`, `EngineRouter`, `require_calibrated` | inferencia | ports, rules, projects | backlog, context, watchdog, mcp_server | `test_inference.py` | IMPLEMENTED |
| `src/acm/inference/ollama.py` | Adaptador Ollama (`/api/tags`, `/api/chat`) | inferencia | httpx, ports | app.build_engines | `test_inference.py`, `test_context.py` (Ollama simulado) | IMPLEMENTED (sin Ollama real, IMP-004) |
| `src/acm/skills/*/SKILL.md` | Skills oficiales (acm-schema 1.4.0, acm-invest 1.0.0, acm-discovery 1.0.0) | contenido | — | SkillCatalog | `test_skills.py` | ACTIVE |
| `src/acm/webui/**` | **Generado**: interfaz compilada por `npm run build` (no editar) | web | web/src | SecureStatic | job `web` de CI (bundle al día) | GENERATED |

## Frontend — `web/` (React 19 + TypeScript 7 + Vite 8; ADR-019)

| Path | Propósito | Tipo | Depende de | Lo usan | Tests | Estado |
|------|-----------|------|------------|---------|-------|--------|
| `web/package.json` / `web/package-lock.json` | Dependencias fijadas y scripts (`build`, `test`, `typecheck`) | config | — | npm, CI | — | ACTIVE |
| `web/vite.config.ts` | Build a `src/acm/webui`, proxy de desarrollo, vitest | config | — | vite | — | ACTIVE |
| `web/tsconfig.json` | TypeScript estricto | config | — | tsc | — | ACTIVE |
| `web/index.html` | Documento raíz (favicon SVG en línea) | html | — | vite | — | ACTIVE |
| `web/src/main.tsx` | Arranque: QueryClient, proveedores y HashRouter | entrada | App, auth, live, prefs | navegador | e2e | IMPLEMENTED |
| `web/src/App.tsx` | Cabecera, navegación, indicador en vivo, rutas | shell | pages, auth, live, prefs | main | e2e | IMPLEMENTED |
| `web/src/api.ts` | Cliente REST v1, `ApiError`, almacén del token | datos | fetch | todas las páginas, auth | e2e | IMPLEMENTED |
| `web/src/auth.tsx` | `AuthProvider`/`useAuth`: sesión con token, `/me`, cierre de sesión | estado | api, react-query | App, pages | e2e | IMPLEMENTED |
| `web/src/live.tsx` | `LiveProvider`/`useLive`: WebSocket, reanudación, invalidación de datos | tiempo real | liveCore, auth, react-query | App, Dashboard, Activity, KanbanBoard | `liveCore.test.ts`, e2e | IMPLEMENTED |
| `web/src/liveCore.ts` | Lógica pura del canal en vivo (seq, duplicados, resync, backoff, claves afectadas) | lógica | types | live | `liveCore.test.ts` | IMPLEMENTED |
| `web/src/prefs.tsx` | `PrefsProvider`/`usePrefs`: tema claro/oscuro/sistema | estado | theme | main, App | `test_webui.py::test_us3107_*` | IMPLEMENTED |
| `web/src/theme.ts` | Paleta con contraste verificado, `contrast`, `cssVariables`, colores de proyecto | lógica | — | prefs, components, KanbanBoard | `theme.test.ts` | IMPLEMENTED |
| `web/src/kanban.ts` | Lógica pura del Kanban: agrupar, filtrar, transiciones | lógica | theme, types | KanbanBoard | `kanban.test.ts` | IMPLEMENTED |
| `web/src/markdown.ts` | Markdown saneado (marked + DOMPurify) y frontmatter | lógica | marked, dompurify | components.Markdown, Docs | `markdown.test.ts` | IMPLEMENTED |
| `web/src/types.ts` | Tipos de la API REST v1 | tipos | theme | todo el frontend | tsc | IMPLEMENTED |
| `web/src/components.tsx` | Componentes comunes (badges, chips, secciones, estados de carga/error, Markdown, barra de estados) | UI | theme, markdown, auth | pages, KanbanBoard | e2e | IMPLEMENTED |
| `web/src/KanbanBoard.tsx` | Tablero Kanban: columnas, carriles, arrastrar/soltar, «Mover a…», resaltado en vivo | UI | kanban, live, api, components | KanbanPage, Project | `kanban.test.ts`, e2e | IMPLEMENTED |
| `web/src/pages/Login.tsx` | Entrada con token | página | auth | App | e2e | IMPLEMENTED |
| `web/src/pages/Dashboard.tsx` | Panel: cartera de proyectos y cambios en vivo | página | api, live, components | App | e2e | IMPLEMENTED |
| `web/src/pages/KanbanPage.tsx` | Kanban de uno o varios proyectos (selección en la URL) | página | KanbanBoard, api | App | e2e | IMPLEMENTED |
| `web/src/pages/Project.tsx` | Proyecto: resumen, backlog, requisitos, historias, Kanban, gobernanza, miembros, configuración; `useBacklog` | página | api, components, KanbanBoard | App, Story | e2e | IMPLEMENTED |
| `web/src/pages/Story.tsx` | Detalle de historia: enunciado, CA, trazabilidad, estado, historial, contexto compacto | página | api, Project.useBacklog | App | e2e | IMPLEMENTED |
| `web/src/pages/Activity.tsx` | Actividad en vivo y auditoría filtrable (admin) | página | api, live | App | e2e | IMPLEMENTED |
| `web/src/pages/Docs.tsx` | Documentación: skills, flujo de estados, referencia de la API | página | api, markdown | App | e2e | IMPLEMENTED |
| `web/src/pages/System.tsx` | Sistema: salud, motores, ahorro, principales, tokens (admin) | página | api | App | e2e | IMPLEMENTED |
| `web/src/theme.test.ts` | Contraste WCAG AA de toda la paleta en ambos temas | test | theme | vitest | — | ACTIVE |
| `web/src/kanban.test.ts` | Agrupación, filtros y transiciones del Kanban | test | kanban | vitest | — | ACTIVE |
| `web/src/liveCore.test.ts` | Orden, duplicados, reanudación y resync del canal en vivo | test | liveCore | vitest | — | ACTIVE |
| `web/src/markdown.test.ts` | Renderizado y saneado (XSS) del Markdown | test | markdown | vitest | — | ACTIVE |
| `web/src/styles.css` | Estilos (solo variables de la paleta; foco visible; movimiento reducido) | estilos | theme (variables) | main | contraste e2e | ACTIVE |

## Tests — `tests/` (pytest; detalle en `tests.md`)

Recuentos medidos con `pytest --collect-only` el 2026-09-30 (casos = funciones × parametrizaciones): 241 funciones, 275 casos.

| Path | Qué prueba | Funciones / casos | Estado |
|------|------------|-------------------|--------|
| `tests/conftest.py` | Fixtures `data_dir`, `service`; `add_member`; registra `tests.live` | — | ACTIVE |
| `tests/live.py` | Fixture `acm`: ACM real por HTTP (uvicorn en hilo); `mcp()` cliente con token | — | ACTIVE |
| `tests/fake_ollama.py` | Ollama simulado (servidor HTTP real) | — | ACTIVE |
| `tests/test_db.py` | US-18.01/02, BUG-001 | 11 / 12 | ACTIVE |
| `tests/test_migrations.py` | US-18.03 | 7 / 10 | ACTIVE |
| `tests/test_projects.py` | US-01.01..03 | 20 / 22 | ACTIVE |
| `tests/test_mcp.py` | US-01.06, US-14.05..09 (frontera MCP) | 12 / 12 | ACTIVE |
| `tests/test_app.py` | ADR-014: HTTP + MCP en un proceso; modo stdio | 2 / 2 | ACTIVE |
| `tests/test_backlog.py` | US-03.03, US-04.01..03 | 19 / 23 | ACTIVE |
| `tests/test_isolation.py` | US-24.01, US-24.03 | 6 / 6 | ACTIVE |
| `tests/test_audit.py` | US-14.10, US-14.11 | 7 / 7 | ACTIVE |
| `tests/test_skills.py` | US-15.01, US-15.04..10 | 25 / 29 | ACTIVE |
| `tests/test_inference.py` | US-35.10/11, US-47.01, US-22.01/03 | 25 / 32 | ACTIVE |
| `tests/test_context.py` | US-35.08/09 | 13 / 17 | ACTIVE |
| `tests/test_auth.py` | EPIC-20, TD-002 | 24 / 26 | ACTIVE |
| `tests/test_watchdog.py` | EPIC-13, US-35.11 CA-01 | 22 / 22 | ACTIVE |
| `tests/test_realtime.py` | EPIC-06, EPIC-21, EPIC-30 | 25 / 31 | ACTIVE |
| `tests/test_webui.py` | Interfaz web e2e (Chromium) | 23 / 24 | ACTIVE |

## Herramientas de control — `control/tools/`

| Path | Propósito | Entradas | Salidas | En CI | Estado |
|------|-----------|----------|---------|-------|--------|
| `control/tools/derive_backlog.py` | Unifica fuentes A y B del backlog, aplica fusiones, refinamientos y estados; comprueba integridad y referencias a tests | `01_PRODUCTO/backlog_completo_v1.md`, `product_definition_v4.md`, `refinements/`, `dedupe.json`, `item_status.json` | `epics.md`, `features.md`, `user_stories.md`, `backlog.md`, `technical_stories.md`, `id_mapping.md` | `--check` | IMPLEMENTED |
| `control/tools/evidence.py` | Matriz CA ↔ test de un sprint | refinamientos + JUnit | `12_TESTING/sprint_00N_evidence.md` | — (al cerrar sprint) | IMPLEMENTED |
| `control/tools/code_inventory.py` | Referencia de código generada y control de que cada archivo está inventariado | código | `05_CODIGO/code_reference.md` | `--check` | IMPLEMENTED |
| `control/tools/dedupe.json` | Fusiones de historias duplicadas (GAP-006) | — | — | vía derive | ACTIVE |
| `control/tools/item_status.json` | Estados de historias/TECH/SPIKE distintos de PLANNED | — | — | vía derive | ACTIVE |

## Configuración e infraestructura

| Path | Propósito | Estado |
|------|-----------|--------|
| `pyproject.toml` | Paquete `acm`, dependencias fijadas (`dependencies.md`), pytest y ruff | ACTIVE |
| `.github/workflows/ci.yml` | CI: job `web` (vitest, build, bundle al día) y job `test` (ruff, pytest con e2e obligatorios, `derive_backlog --check`, `code_inventory --check`) | ACTIVE |
| `.gitignore` | Cachés, `.venv/`, `.acm-data/`, `web/node_modules/` | ACTIVE |
| `README.md` | Instalación, ejecución, tokens, Watchdog, interfaz | ACTIVE |
| `CLAUDE.md` | Constitución del agente | ACTIVE |
| `spikes/**` | Experimentos de SPIKE-001/002 (no es producto) | SPIKE |
| `control/01_PRODUCTO/backlog_completo_v1.md` | Fuente A del backlog | ACTIVE |
| `control/01_PRODUCTO/product_definition_v4.md` | Fuente B: definición de producto v1.3 | ACTIVE |
| `control/99_ARCHIVO/superseded/product_definition_v{1,2,3}.md` | Definiciones v1.0, v1.1, v1.2 | SUPERSEDED |
