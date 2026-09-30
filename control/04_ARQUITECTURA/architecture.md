# Arquitectura

> **Estado: PLANNED (objetivo conceptual).** No existe ninguna implementación. Fuente: definición §1, §6, §14, §18 y ADR-001.

## Vista objetivo

```text
Humanos ──(Web React / CLI / MCP)──► ACM Core (Governance + State)
                                        │
                ┌───────────────────────┼───────────────────────┐
         SQLite (por proyecto)     Vector DB + RAG          Git / Código
                └───────────────────────┼───────────────────────┘
                                 Agent Orchestrator
                          ┌─────────────┼─────────────┐
                        Ollama        JEV*      Agentes externos (MCP)
                                        │
                                  Watchdog (gates)
                                        │
                                  Estado verificado
                  * JEV: POST-MVP, sin definir (GAP-003)
```

## Componentes previstos
| Componente | Épicas | Estado |
|-----------|--------|--------|
| Núcleo de estado (SQLite por proyecto) | EPIC-01, 34, TECH-003..009 | PLANNED |
| Servidor MCP multi-proyecto | EPIC-15, TECH-010/011 | PLANNED |
| Motor de eventos + bus WebSocket | EPIC-18, TECH-001/002 | PLANNED |
| Frontend React (Kanban, actividad, grafos) | EPIC-19, 20, 46 | PLANNED |
| Watchdog | EPIC-05, 10, 36, 42 | PLANNED |
| RAG / Vector store | EPIC-21, TECH-015..017, SPIKE-003/004 | PLANNED |
| Adaptador Ollama + router de modelos | EPIC-23, TECH-018/019 | PLANNED |
| Snapshot engine (SQLite+Git) | EPIC-13, TECH-021/022 | PLANNED |
| Auth/RBAC/tokens | EPIC-16, TECH-012/013 | PLANNED |
| Auditoría/telemetría | EPIC-27, TECH-014/027 | PLANNED |
| CLI | EPIC-31, TECH-029 | PLANNED (POST-MVP completa) |

## Decisiones abiertas
- Runtime/lenguaje backend (IMP-001).
- Proceso único vs. servicios separados (MCP / API / WS) — pendiente tras IMP-001.
- Vector store concreto (SPIKE-003 propone evaluar ChromaDB).
