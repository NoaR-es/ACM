# Arquitectura

> **Estado: PLANNED (objetivo conceptual).** No existe ninguna implementación. Fuentes: definición §1, §6, §14, §18 (fuente B), backlog unificado (ADR-010) y ADR-001/005/006/008.

## Vista objetivo

```text
Humanos ──(Web React / CLI / MCP)──► ACM Core (Governance + State)
                                        │
                ┌───────────────────────┼───────────────────────┐
         SQLite (por proyecto)     Vector DB + RAG          Git / Código
                └───────────────────────┼───────────────────────┘
                                 Agent Orchestrator
                          ┌─────────────┼─────────────┐
                        Ollama    Ollaya/JEV*   Agentes externos (MCP)
                                        │
                                  Watchdog (gates)
                                        │
                                  Estado verificado
                  * JEV: modelos de decisión servidos por Ollaya; se conectan a la interfaz de decisión del núcleo (ADR-006, ADR-012)
```

## Componentes previstos
| Componente | Épicas | Estado |
|-----------|--------|--------|
| Núcleo de estado (SQLite por proyecto; fuente de verdad del producto, ADR-011) | EPIC-01, 18, 24, TECH-003..009 | VERIFIED en parte (US-01.01..03/06, 18.01..03, 24.01; US-24.03 IMPLEMENTED); resto PLANNED |
| Memoria de proyecto (estructura "control/" persistida en SQLite; exportación a archivos no autoritativa, ADR-011) | EPIC-02 | PLANNED |
| Servidor MCP propio multi-proyecto + distribución de skills | EPIC-14 (FEAT-14.02..04), EPIC-15 (FEAT-15.01..03), TECH-010/011, ADR-008 | VERIFIED (SPRINT-001/002; 46 herramientas) |
| Cliente MCP para agentes internos | EPIC-14 (US-14.01..03) | PLANNED (POST-MVP) |
| Orquestador interno, instancias e hilos, roles IA | EPIC-07, 08, 09, 41, 46 | PLANNED (POST-MVP, CONF-003) |
| Motor de eventos + WebSocket (eventos persistidos, ADR-018) | EPIC-21, TECH-001/002 | VERIFIED (SPRINT-006: US-21.01..03) |
| Frontend React (Kanban, consola, dashboard, grafos) | EPIC-06, 31, 45, 17, ADR-019 | VERIFIED (SPRINT-007: Kanban, consola, panel, vistas); grafos (EPIC-17) PLANNED |
| Watchdog | EPIC-13, 19, 27, 48 | VERIFIED en EPIC-13 (SPRINT-005); resto PLANNED |
| RAG / Vector store | EPIC-16, TECH-015..017, SPIKE-003/004 | PLANNED |
| Adaptador Ollama + router de modelos | EPIC-22, 38, 39, TECH-018/019 | IMPLEMENTED (sin Ollama real, IMP-004); router VERIFIED |
| Interfaz de decisión (reglas · Ollama · JEV) | US-35.11, US-47.01, ADR-012, ADR-015 | VERIFIED (reglas; Ollama IMPLEMENTED) |
| Servicio de contexto compacto + medición de tokens ahorrados (segundo cerebro) | FEAT-35.05, EPIC-16, EPIC-22 | PLANNED (MVP) |
| Adaptador de decisión JEV (Ollaya/TypeSafe) | EPIC-50, TECH-020, ADR-006 | PLANNED (tras el MVP; la interfaz ya existe) |
| Snapshot engine (SQLite+Git) | EPIC-12, TECH-021/022 | PLANNED |
| Auth/RBAC/tokens | EPIC-20, 44, TECH-012/013 | VERIFIED en EPIC-20 (SPRINT-004); resto PLANNED |
| Auditoría/telemetría | EPIC-26, 44, TECH-014/027 | PLANNED |
| API HTTP | EPIC-30 | VERIFIED (REST v1, SPRINT-006) |
| Sandbox / entornos de ejecución | EPIC-47, 51, TECH-023 | PLANNED (POST-MVP) |
| CLI | EPIC-52, TECH-029 | PLANNED (POST-MVP) |

## Decisiones abiertas
- ~~Runtime/lenguaje backend (IMP-001)~~ → **Python ≥ 3.11 (ADR-005)**.
- ~~Proceso único vs. servicios separados~~ → **un proceso ASGI (uvicorn) con MCP `/mcp`, API `/api` y WebSocket `/ws`, más stdio para agentes locales (ADR-014)**.
- ~~Framework HTTP/WebSocket y acceso SQLite~~ → **FastAPI/Starlette (ADR-014); SQLite en WAL con `BEGIN IMMEDIATE`, FULL y claves foráneas por conexión (ADR-013)**.
- ~~Interfaces de inferencia~~ → **DecisionEngine y GenerationEngine con router (ADR-015, `inference_ports.md`)**.
- ~~Tooling del frontend React (GAP-002)~~ → **React + TypeScript + Vite, build en `src/acm/webui` servido en `/` con CSP (ADR-019, `05_CODIGO/frontend.md`)**.
- Vector store concreto (SPIKE-003 propone evaluar ChromaDB).

## Topología de ejecución (ADR-014)

Actualizado en SPRINT-007: el WebSocket lee la tabla `events` (ADR-018, sustituye al bus en memoria previsto por ADR-014).

```text
                         ┌──────────────── proceso ACM (uvicorn, Python ≥ 3.11) ────────────────┐
 Agente IA ── HTTP ────► │ /mcp  Servidor MCP propio (SDK mcp 2.2.x) + extensión Skills (SEP-2640) │
 Agente IA ── stdio ───► │        (mismo servidor lanzado por stdio)                              │
 Navegador ─ HTTP ─────► │ /     interfaz React compilada (SecureStatic + CSP, ADR-019)           │
 Navegador ─ HTTP ─────► │ /api/v1  REST (BearerAuth)                                             │
 Navegador ─ WS ───────► │ /api/v1/ws ◄── tabla events (SQLite) ◄── dominio, cualquier proceso    │
                         │        servicios ──► DecisionEngine / GenerationEngine (ADR-015)       │
                         │        repositorios ──► SQLite WAL (1 base por proyecto + 1 global)    │
                         └────────────────────────────────────────────────────────────────────────┘
                                        │ HTTP                           │ HTTP
                                    Ollama (local)               Ollaya / TypeSafe (JEV, EPIC-50)
```
