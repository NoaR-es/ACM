# Árbol de fuentes

Actualizado: 2026-09-30 (SPRINT-007). Cada archivo de código tiene su fila en `file_inventory.md` (lo exige `control/tools/code_inventory.py --check` en la CI); los símbolos públicos, en `code_reference.md` (generado).

```text
/
├── CLAUDE.md                        # Constitución del agente
├── README.md                        # Instalar, probar, ejecutar
├── pyproject.toml                   # Paquete `acm` y dependencias fijadas (dependencies.md)
├── .github/workflows/ci.yml         # CI: job `test` (ruff, pytest + e2e obligatorios, derive_backlog/code_inventory --check) y job `web` (vitest, build, bundle al día)
├── src/acm/                         # BACKEND DE PRODUCTO (modules.md)
│   ├── __init__.py                  # versión
│   ├── __main__.py                  # CLI: `acm serve`, `acm mcp-stdio`
│   ├── config.py                    # Settings (variables ACM_*)
│   ├── app.py                       # Composición FastAPI: /api/health, /api/v1 (REST+WS), /mcp, / (interfaz)
│   ├── auth.py                      # BearerAuth y principal por petición (ADR-017)
│   ├── events.py                    # EventStore: eventos de dominio (ADR-018)
│   ├── web_api.py                   # REST v1 + WebSocket de eventos
│   ├── webui_app.py                 # SecureStatic: sirve la interfaz con CSP (ADR-019)
│   ├── webui/                       # BUILD GENERADO de web/ (no editar a mano; la CI verifica que está al día)
│   ├── mcp_server.py                # Servidor MCP: 65 herramientas, 2 prompts, extensión Skills, auditoría
│   ├── skills_catalog.py            # Catálogo de skills validado
│   ├── sessions.py                  # Identidad de los agentes locales: principal y sesión (ADR-023)
│   ├── local.py                     # Modo local: interfaz en segundo plano, sesión local, `acm stop` (ADR-023)
│   ├── skills/                      # Skills oficiales (acm-schema, acm-invest, acm-discovery)
│   ├── inference/                   # ports, rules, router, ollama, jev (Ollaya), selection, ollaya_models (ADR-015/016/021)
│   ├── db/                          # connection (ADR-013), migrations, schema (global v8, proyecto v5)
│   └── domain/                      # errors, config_schema, projects, backlog, sprints, audit, identity, context, watchdog,
│                                    #   supervisor (ADR-020), models (ADR-021), chat (ADR-022)
├── web/                             # FRONTEND (frontend.md)
│   ├── package.json, package-lock.json, tsconfig.json, vite.config.ts, index.html
│   └── src/
│       ├── main.tsx, App.tsx        # proveedores y rutas
│       ├── api.ts, auth.tsx, live.tsx, liveCore.ts, prefs.tsx   # cliente, sesión, tiempo real, preferencias
│       ├── theme.ts, kanban.ts, markdown.ts, types.ts           # lógica pura y tipos (con *.test.ts)
│       ├── components.tsx, forms.tsx, KanbanBoard.tsx, styles.css   # componentes y formularios compartidos
│       └── pages/                   # Login, Dashboard, KanbanPage, Project, Story, Activity, Docs, System,
│                                    #   BacklogForms, Sprints, Supervisor, Assistant, Models
├── tests/                           # pytest (tests.md): unitarios, integración HTTP/MCP, e2e con Chromium
├── control/                         # Sistema de control (fuente de verdad del desarrollo)
│   └── tools/                       # derive_backlog.py, evidence.py, code_inventory.py (utilities.md)
└── spikes/                          # Experimentos; no es producto
```
