# Sprint activo

## SPRINT-003 — Segundo cerebro: decisiones delegadas y contexto compacto

| Campo | Valor |
|-------|-------|
| Sprint ID | SPRINT-003 |
| Objetivo | Que ACM ahorre tokens al agente: decisiones tipadas delegadas y contexto compacto, con un núcleo preparado para JEV (ADR-012, ADR-015) |
| Inicio | 2026-09-30 |
| Fin | Al cumplir el Sprint Goal (sin timebox; desarrollo por agente) |
| Sprint Goal | **Un agente conectado a ACM puede delegar decisiones tipadas (noul, choice, score) y pedir el contexto compacto de una historia con fuentes y tokens ahorrados medidos. Toda decisión pasa por una interfaz común con un motor de reglas que funciona sin modelos, Ollama puede conectarse por configuración y JEV podrá conectarse sin cambiar a los consumidores. Cada CA verificado por tests automáticos.** |
| Historias | US-35.08, US-35.09, US-35.10, US-35.11, US-47.01, US-22.01, US-22.03 (refinamientos en `01_PRODUCTO/refinements/`); US-22.05 fusionada en US-22.01 |
| Dependencias | ADR-006, ADR-012, ADR-015; ADR-016 (nueva); SPRINT-002 |
| Riesgos | Sin Ollama real en el entorno (IMP-004): el adaptador solo se prueba contra un Ollama simulado; la estimación de tokens es aproximada (`chars/4@v1`) |
| Impedimentos | IMP-004 (SPIKE-005 bloqueado en el entorno cloud) |
| Fuera de alcance | `OllamaDecisionEngine` (depende de SPIKE-005); adaptador JEV (EPIC-50); Watchdog (EPIC-13); RAG (EPIC-16); fallback autorizado por modelo (US-39.02) |
| Velocidad | No se mide |

### Tasks

| ID | Tipo | Título | Historias | Estado |
|----|------|--------|-----------|--------|
| TASK-003-01 | TASK | `acm.inference`: puertos (ADR-015, síncronos por ADR-016), `RulesDecisionEngine`, `EngineRegistry`, `EngineRouter` con fallback y registro de llamadas; esquema global v3 | US-35.10, US-35.11, US-47.01 | VERIFIED |
| TASK-003-02 | TASK | Adaptador Ollama: detección de modelos (`/api/tags`) y generación (`/api/chat`); configuración `ACM_OLLAMA_URL`/`ACM_OLLAMA_MODEL` | US-22.01, US-22.03 | IMPLEMENTED (solo contra Ollama simulado; IMP-004) |
| TASK-003-03 | TASK | El gate READY (`mark_ready`) consume la interfaz de decisión común | US-35.11 | VERIFIED |
| TASK-003-04 | TASK | `ContextService`: contexto compacto con fuentes, estimación `chars/4@v1`, registro y agregado del ahorro | US-35.08, US-35.09 | VERIFIED |
| TASK-003-05 | TASK | 5 herramientas MCP (`acm_decide`, `acm_context_compact`, `acm_engines_list`, `acm_engines_refresh`, `acm_savings_report`) y skill acm-schema 1.1.0 | US-35.08..10, US-22.01 | VERIFIED |
| TASK-003-06 | TEST | Tests por CA (49 nuevos), Ollama simulado y matriz de evidencia | todas | VERIFIED (172 tests; 8/8 mutaciones detectadas) |
| TASK-000-10 | DOCUMENTATION | Fusión US-22.05 → US-22.01 | GAP-006 | VERIFIED (parcial: 14 fusiones en total) |
| TASK-000-07 | DECISION | Decidir tooling del frontend React (GAP-002) | — | PLANNED (arrastrada) |

SPRINT-002 cerrado y archivado en `99_ARCHIVO/historical/sprint_002.md`.

### Estado de las historias (2026-09-30)

| Historia | Estado | Evidencia / nota |
|----------|--------|------------------|
| US-35.08, US-35.09, US-35.10, US-47.01 | VERIFIED | `12_TESTING/sprint_003_evidence.md` |
| US-35.11 | IMPLEMENTED | CA-01 nombra al Watchdog (EPIC-13), que no existe; consumen la interfaz el gate READY y `acm_decide` |
| US-22.01, US-22.03 | IMPLEMENTED | Todos los CA en PASS contra un Ollama simulado; falta verificar contra un Ollama real (SPIKE-005, IMP-004) |

VERIFIED = todos los CA con test automático en PASS. DONE requiere además la revisión del operador (merge del PR).
