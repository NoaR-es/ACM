# Sprint Reviews

## SPRINT-000 — Inception (2026-09-30)
- **Goal:** reconstruibilidad total del proyecto desde `control/`. **Cumplido.** `control/` completo, backlog unificado y verificable, 15 ADRs, spikes con evidencia.
- **Entregado:** TASK-000-01..06, 08, 09, 11, 12, 13, SPIKE-001, SPIKE-002. Todo VERIFIED y pendiente de revisión del operador (merge).
- **No entregado:** TASK-000-07 (tooling frontend) y TASK-000-10 (solapamientos). Pasan a SPRINT-001; TASK-000-10 se hace de forma parcial.
- **Producto:** sin código de producto (esperado en un sprint de arranque).

## SPRINT-001 — Esqueleto del backend y núcleo de proyecto (2026-09-30)
- **Goal:** cumplido en el backend. Un agente MCP (HTTP o stdio) crea, lista, abre y configura proyectos, cada uno con su base SQLite.
- **Entregado:** 6 historias VERIFIED (US-01.01, 01.03, 01.06, 18.01, 18.02, 18.03) y 1 IMPLEMENTED (US-01.02, falta la UI). TASK-001-01..06.
- **Evidencia:** 50 tests en PASS; matriz CA↔test en `12_TESTING/sprint_001_evidence.md`; 6 mutaciones del código detectadas por los tests.
- **No entregado:** interfaz web (TASK-000-07). CI en GitHub: success (run #1).

## SPRINT-002 — Skills y backlog por MCP (2026-09-30)
- **Goal:** cumplido. Un agente conectado por MCP obtiene las `instructions`, lista y descarga las 3 skills oficiales (extensión Skills o herramientas de respaldo) y crea requisitos, épicas, features, historias y CA en la SQLite del proyecto; cada invocación queda auditada.
- **Entregado:** 20 historias VERIFIED y 1 IMPLEMENTED (US-24.03, CA-02 depende de EPIC-21). TASK-002-01..05. 7 fusiones de duplicados más (TASK-000-10).
- **Evidencia:** 122 tests en PASS (72 nuevos); matriz CA↔test generada en `12_TESTING/sprint_002_evidence.md`; 6/6 mutaciones detectadas.
- **No entregado:** skills acm-error-analysis y acm-documentation (US-15.11/15.12, dependen de EPIC-29/25); interfaz web.

## SPRINT-003 — Segundo cerebro (2026-09-30)
- **Goal:** cumplido en el núcleo. `acm_decide` responde decisiones tipadas con el motor que decidió, calibración y fallback. `acm_context_compact` entrega el contexto de una historia por secciones con fuentes (medido: 3382 tokens frente a 7780 del equivalente completo en el caso de prueba; 275 con resumen). El gate READY decide a través de la interfaz común.
- **Entregado:** US-35.08, 35.09, 35.10, 47.01 VERIFIED; US-35.11, 22.01, 22.03 IMPLEMENTED. TASK-003-01..06. ADR-016.
- **Evidencia:** 172 tests en PASS (49 nuevos); `12_TESTING/sprint_003_evidence.md`; 8/8 mutaciones detectadas.
- **No entregado:** verificación con un Ollama real (IMP-004); `OllamaDecisionEngine` (depende de SPIKE-005); Watchdog.

## SPRINT-004 — Autenticación y RBAC (2026-09-30)
- **Goal:** cumplido. `/mcp` exige un token Bearer de ACM y cada petición actúa con su principal. Tokens por usuario o agente, solo hash en la base, redactados en la auditoría y revocables al instante. Roles globales y de proyecto gestionables por MCP.
- **Entregado:** US-20.01, 20.02, 20.03, 20.04, 20.05, 20.08 VERIFIED. TASK-004-01..05. ADR-017. VULN-001 resuelta; TD-002 detectada y resuelta (`ACM_ALLOWED_HOSTS`).
- **Evidencia:** 198 tests en PASS (27 nuevos, contra ACM real por HTTP); `12_TESTING/sprint_004_evidence.md`; 8/8 mutaciones de seguridad detectadas.
- **Cambio incompatible:** los clientes HTTP necesitan token (ver `README.md`).
- **No entregado:** TLS propio (VULN-002: se delega en un proxy); US-20.07 y US-20.12..14.

## SPRINT-005 — Watchdog de gobernanza (2026-09-30)
- **Goal:** cumplido. `acm_watchdog_run` y la auditoría periódica comprueban integridad, calidad de historias (vía la interfaz de decisión) y estructura; semáforo e histórico; cuarentena sin escrituras de un proyecto dañado; `acm_health` por componente.
- **Entregado:** US-13.03, 13.05, 13.06, 13.07, 13.10, 13.11, 13.12, 13.13 VERIFIED; US-35.11 pasa a VERIFIED (CA-01). TASK-005-01..04.
- **Evidencia:** 220 tests en PASS (22 nuevos, uno con corrupción real de la base); `12_TESTING/sprint_005_evidence.md`; 8/8 mutaciones detectadas.
- **No entregado:** US-13.01, 13.02, 13.08 y 13.09 (sin entidades que vigilar); vista del semáforo (EPIC-30).

## SPRINT-006 — Plataforma de tiempo real (2026-09-30)
- **Goal:** cumplido. La API REST v1 lee todo lo que guarda ACM. Las historias tienen flujo de estados con historial. Los cambios llegan por WebSocket a los clientes autorizados, incluidos los de un agente stdio en otro proceso, con reanudación sin pérdidas ni duplicados.
- **Entregado:** US-06.01, 06.02, 06.03, 21.01, 21.02, 21.03, 30.01, 30.02, 30.03 VERIFIED. TASK-006-01..04. ADR-018.
- **Evidencia:** 251 tests en PASS (31 nuevos); `12_TESTING/sprint_006_evidence.md`; 8/8 mutaciones detectadas.
- **Siguiente:** SPRINT-007, la interfaz web sobre esta plataforma.
