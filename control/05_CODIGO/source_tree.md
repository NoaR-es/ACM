# Árbol de fuentes

```text
/
├── CLAUDE.md                      # Constitución del agente
├── README.md                      # Cómo instalar, probar y ejecutar
├── pyproject.toml                 # Paquete `acm` y dependencias fijadas (ADR-014)
├── .github/workflows/ci.yml       # CI: ruff + pytest + derive_backlog --check
├── src/acm/                       # CÓDIGO DE PRODUCTO (ver 05_CODIGO/modules.md)
│   ├── __init__.py                # versión
│   ├── __main__.py                # CLI: `acm serve`, `acm mcp-stdio`
│   ├── config.py                  # Settings del proceso (variables ACM_*)
│   ├── app.py                     # FastAPI: /api/health + MCP montado en /mcp (ADR-014), con BearerAuth
│   ├── auth.py                    # Autenticación HTTP por token (ADR-017)
│   ├── events.py                  # Eventos de dominio persistidos (ADR-018)
│   ├── web_api.py                 # API REST v1 y WebSocket de eventos
│   ├── mcp_server.py              # Servidor MCP propio: herramientas, extensión Skills, auditoría
│   ├── skills_catalog.py          # Catálogo de skills validado (US-15.01)
│   ├── inference/                 # Puertos, reglas, registro/router y adaptador Ollama (ADR-015/016)
│   ├── skills/                    # Skills oficiales: acm-schema, acm-invest, acm-discovery
│   ├── db/
│   │   ├── connection.py          # Database: PRAGMAs, write()/read(), reintentos (ADR-013)
│   │   ├── migrations.py          # Migrador versionado (US-18.03)
│   │   └── schema.py              # Catálogos GLOBAL y PROJECT (v2)
│   └── domain/
│       ├── errors.py              # Errores de dominio con código estable
│       ├── config_schema.py       # Parámetros de configuración de proyecto (US-01.03)
│       ├── projects.py            # ProjectService (US-01.01..03, US-01.06)
│       ├── backlog.py             # BacklogService (EPIC-03/04, US-24.01/03)
│       ├── audit.py               # AuditService (US-14.10/11)
│       ├── identity.py            # IdentityService: principales, roles, tokens (EPIC-20)
│       ├── context.py             # ContextService: contexto compacto y ahorro (US-35.08/09)
│       └── watchdog.py            # WatchdogService: gobernanza e integridad (EPIC-13)
├── tests/                         # pytest: un test por CA (nombres test_usNNNN_caNN_*)
├── control/                       # Sistema de control (fuente de verdad del desarrollo)
└── spikes/                        # Experimentos, no es producto
```
