# Relaciones

LAST_UPDATED: 2026-09-30

## Sprint → Tasks
```
SPRINT-000
├── TASK-000-01 → control/** (estructura)
├── TASK-000-02 → control/01_PRODUCTO/product_definition_v1.md (ahora en 99_ARCHIVO), control/tools/derive_backlog.py, TEST-CTRL-001, ADR-004
├── TASK-000-03 → control/14_DECISIONES/decisions.md (ADR-001..004)
├── TASK-000-04 → IMP-001 (CLOSED), GAP-002 → ADR-005
├── TASK-000-07 → GAP-002 (tooling frontend)
├── TASK-000-05 → IMP-002, GAP-003 → ADR-006
├── TASK-000-06 → ADR-003 (SUPERSEDED) → ADR-007 (SUPERSEDED) → ADR-009, control/tools/derive_backlog.py
├── TASK-000-08 → product_definition_v2.md, ADR-008, ADR-009, 06_API/mcp_server.md
├── TASK-000-09 → backlog_completo_v1.md, ADR-010, id_mapping.md, tools/derive_backlog.py
├── TASK-000-10 → GAP-006
├── TASK-000-11 → IMP-003, CONF-001 → ADR-012, CONF-002 → ADR-011
└── TASK-000-12 → product_definition_v3.md, ADR-012, US-35.08..US-35.11, US-47.01
```

## Código → origen
```
control/tools/derive_backlog.py
├── TASK-000-02
├── ADR-010 (FEATURE_MAP, NEW_EPICS, constantes MVP; antes ADR-009, ADR-007, ADR-003)
├── ADR-004
└── TEST-CTRL-001
```

## Producto
- Backlog unificado (ADR-010) = fuente A `01_PRODUCTO/backlog_completo_v1.md` + fuente B `01_PRODUCTO/product_definition_v3.md` (v1.2, que supersede a v1.1 y v1.0 en `99_ARCHIVO/superseded/`). Traducción de IDs de B: `01_PRODUCTO/id_mapping.md`.
- Épica → Feature → Historia: generado en `01_PRODUCTO/features.md` y `01_PRODUCTO/user_stories.md` (bidireccional por ID).
- Requisito funcional → Épica: `01_PRODUCTO/requirements.md` (REQ-F-01..40).
- Épica → Componente arquitectónico: `04_ARQUITECTURA/architecture.md`.
- Historia → Código / Test / API: bloques SPRINT-001 y SPRINT-002 al final de este documento; matrices CA ↔ test en `12_TESTING/sprint_00N_evidence.md`.

## Gaps → afectados
```
GAP-001 → 351 US (todas salvo US-01.01 y US-15.09..12)
GAP-002 → IMP-001, TASK-000-04, TASK-000-07, ADR-001, ADR-005
GAP-003 (RESOLVED) → IMP-002, ADR-006, EPIC-24, SPIKE-006, TECH-020
GAP-004 → EPIC-03..EPIC-48
GAP-005 → 07_DATOS/data_architecture.md, EPIC-13, 16, 17, 27
```

## Decisiones → alcance
```
ADR-005 (Python backend)
├── EPIC-01, 15, 18, 21, 23 (todo el backend)
├── SPIKE-001, SPIKE-002, SPIKE-005
└── 06_API/contract_tests.md (contrato React ↔ Python)
```

```
ADR-006 (JEV vía Ollaya)
├── EPIC-24, TECH-020, SPIKE-006
├── US-24.03 (router Ollama ↔ Ollaya), US-24.07 (Watchdog JEV)
└── 10_IA/inference_engines.md, providers.md, models.md

ADR-007 (MVP, SUPERSEDED por ADR-009)
├── supersede ADR-003
├── control/tools/derive_backlog.py (MVP_EPICS, POST_MVP_FEATURES)
└── 01_PRODUCTO/backlog.md, epics.md, features.md, user_stories.md
```

```
ADR-008 (servidor MCP propio + skills)
├── EPIC-15: FEAT-15.04 (US-15.09, US-15.10, US-15.11, US-15.12), US-15.08 (auditoría de descargas)
├── EPIC-22: FEAT-22.01 (US-22.01..05) → catálogo skill://acm/*
├── TECH-010, TECH-011, SPIKE-002
├── ADR-005 (Python)
└── 06_API/mcp_server.md, 04_ARQUITECTURA/architecture.md

ADR-009 (MVP v2)
├── supersede ADR-007
└── control/tools/derive_backlog.py (MVP_EPICS incluye 22; FEAT-22.02/03/04 POST-MVP)
```

```
ADR-010 (backlog unificado + MVP v3)
├── supersede ADR-009
├── fuentes: backlog_completo_v1.md (A), product_definition_v3.md (B, antes v2)
├── genera: epics.md, features.md, user_stories.md, backlog.md, technical_stories.md, id_mapping.md
├── nuevas épicas: EPIC-49 (deuda), EPIC-50 (JEV ← ADR-006), EPIC-51 (sandbox), EPIC-52 (CLI), EPIC-53 (extensiones)
└── conflictos: CONF-001 (EPIC-47 ↔ EPIC-50), CONF-002 (EPIC-02 ↔ EPIC-18), CONF-003 (EPIC-07/08/09/46), CONF-004 (EPIC-14)

Servidor MCP propio (ADR-008) en numeración unificada
├── FEAT-14.02..14.04 (US-14.04..US-14.11) ← B:FEAT-15.01..15.03
├── FEAT-15.02 (US-15.04..US-15.07) ← B:FEAT-15.04
└── FEAT-15.03 (US-15.08..US-15.12) ← B:FEAT-22.01 → catálogo skill://acm/*
```

```
ADR-011 (fuente de verdad por nivel)
├── desarrollo → control/ (00_GOBIERNO/agent_operating_rules.md regla 6)
└── producto → SQLite: EPIC-18, EPIC-02 (memoria de proyecto), 07_DATOS/data_architecture.md

ADR-012 (JEV preparado + segundo cerebro)
├── interfaz de decisión: US-35.11 (← B:US-43.09), US-47.01 → adaptador EPIC-50 / TECH-020 (ADR-006)
├── contexto compacto + tokens ahorrados: FEAT-35.05 (US-35.08, US-35.09) ← B:FEAT-43.04
├── decisiones delegadas: FEAT-35.06 (US-35.10, US-35.11) ← B:FEAT-43.05
├── REQ-F-41, REQ-F-42
└── CONF-003 aplazado → EPIC-07/08/09/46
```

```
SPIKE-001 → spikes/spike_001_sqlite/bench.py, results.json → 20_PERFORMANCE/benchmarks.md → ADR-013
        ADR-013 → EPIC-18 (US-18.01..03), EPIC-19 (US-19.01, US-19.03), US-39.01, TECH-003..008, 07_DATOS/data_architecture.md

SPIKE-002 → spikes/spike_002_mcp/{acm_mcp_proto.py, test_proto.py, test_asgi_topology.py, test_session_isolation.py}
        → 06_API/mcp_server.md (resultados) → ADR-014
        ADR-014 → EPIC-14 (FEAT-14.02..04), EPIC-15 (FEAT-15.02/03), EPIC-21, EPIC-24, EPIC-30, TECH-001/002/010/011, GAP-007

TASK-000-13 → 04_ARQUITECTURA/inference_ports.md → ADR-015
        ADR-015 → US-35.08..US-35.11, US-47.01, EPIC-22, EPIC-50, TECH-018..020, 10_IA/inference_engines.md
```

```
SPRINT-001
├── US-01.01 → src/acm/domain/projects.py (create), mcp_server.py (acm_project_create) → tests/test_projects.py::test_us0101_*, tests/test_mcp.py::test_us0101_*
├── US-01.02 → projects.py (list_for, open), mcp_server.py (acm_project_list/open) → tests/test_projects.py::test_us0102_*   [CA-03: pendiente UI]
├── US-01.03 → domain/config_schema.py, projects.py (get_config/set_config), mcp_server.py (acm_project_config_*) → tests/test_projects.py::test_us0103_*
├── US-01.06 → mcp_server.py (project_id obligatorio, instructions, ToolError) → tests/test_mcp.py::test_us0106_*
├── US-18.01 → db/connection.py, db/schema.py → tests/test_db.py::test_us1801_*
├── US-18.02 → db/connection.py (write/read, reintentos) → tests/test_db.py::test_us1802_*
├── US-18.03 → db/migrations.py, db/schema.py → tests/test_migrations.py::test_us1803_*
├── ADR-013 → db/connection.py ; ADR-014 → app.py, mcp_server.py, __main__.py → tests/test_app.py
├── GAP-007 (RESOLVED en ACM) → mcp_server.py call() → tests/test_mcp.py
└── VULN-001 → config.py (DEFAULT_HOST=127.0.0.1)

Código → historias: projects.py ← US-01.01/02/03, US-18.01 · connection.py ← US-18.01/02, ADR-013 · migrations.py ← US-18.03 · mcp_server.py ← US-01.06, ADR-014, GAP-007
```

```
SPRINT-002
├── US-03.03 → domain/backlog.py (trace_requirement, audit), mcp_server.py (acm_requirement_*, acm_backlog_audit) → tests/test_backlog.py::test_us0303_*
├── US-04.01 → backlog.py (create_epic, link_epic_requirements), acm_epic_* → tests/test_backlog.py::test_us0401_*
├── US-04.02 → backlog.py (create_feature, split_feature, confirm_epic_coverage), acm_feature_* → tests/test_backlog.py::test_us0402_*
├── US-04.03 → backlog.py (create_story, add_criteria, mark_ready), acm_story_* → tests/test_backlog.py::test_us0403_*
├── US-14.04 → app.py, __main__.py → tests/test_app.py
├── US-14.05/06/07/09 → mcp_server.py → tests/test_mcp.py::test_us1405_*, test_us1406_*, test_us1407_*, test_us1409_*
├── US-14.10/11 → domain/audit.py, db/schema.py (GLOBAL v2 mcp_audit), mcp_server.py audited() → tests/test_audit.py   [TD-001]
├── US-15.01/06/07 → skills_catalog.py → tests/test_skills.py::test_us1501_*, test_us1506_*, test_us1507_*
├── US-15.04/05 → mcp_server.py (AcmSkillsExtension, skill_file, acm_skills_*) → tests/test_skills.py::test_us1504_*, test_us1505_*
├── US-15.08/09/10 → skills/acm-schema, skills/acm-invest, skills/acm-discovery → tests/test_skills.py::test_us1508_*..test_us1510_*
├── US-24.01/03 → backlog.py (_db: acceso por proyecto), una project.db por proyecto → tests/test_isolation.py   [US-24.03 CA-02 → EPIC-21]
├── TASK-000-10 → tools/dedupe.json (US-04.04/05 → 04.01; 04.07/08/11/13 → 04.03; US-14.08 → US-01.06)
├── TASK-002-05 → tools/evidence.py → 12_TESTING/sprint_002_evidence.md
└── BUG-001 → src/acm/db/connection.py (_enable_wal) → tests/test_db.py::test_bug001_apertura_concurrente_de_base_nueva; afecta a US-18.01, US-18.03

SPRINT-003
├── US-35.08 → domain/context.py (compact, _summarize), mcp_server.py (acm_context_compact) → tests/test_context.py::test_us3508_*
├── US-35.09 → domain/context.py (savings_report), db/schema.py (context_deliveries), acm_savings_report → tests/test_context.py::test_us3509_*
├── US-35.10 → inference/ports.py, inference/router.py (decide, _log), acm_decide → tests/test_inference.py::test_us3510_*
├── US-35.11 → domain/backlog.py (mark_ready, READY_GATE_*), inference/rules.py, router.require_calibrated → tests/test_inference.py::test_us3511_*   [CA-01: Watchdog, EPIC-13]
├── US-47.01 → inference/router.py (EngineRegistry), inference/ports.py → tests/test_inference.py::test_us4701_*
├── US-22.01 → inference/ollama.py (list_models, health), app.build_engines, acm_engines_* → tests/test_inference.py::test_us2201_*   [IMP-004]
├── US-22.03 → inference/ollama.py (generate), router.generate → tests/test_inference.py::test_us2203_*   [IMP-004]
├── ADR-016 → inference/ports.py (firmas síncronas)
├── PROMPT-001 → domain/context.py (_summarize) → 10_IA/prompts.md
└── IMP-004 → SPIKE-005, US-22.01, US-22.03

Código → historias: inference/** ← US-35.10, 35.11, 47.01, 22.01, 22.03, ADR-015/016 · context.py ← US-35.08/09, PROMPT-001 · backlog.py (gate) ← US-35.11
Modelo IA → uso: rules → gate READY, acm_decide · ollama:<modelo> → PROMPT-001 (context.compact) · jev → EPIC-50 (pendiente)

Código → historias: backlog.py ← US-03.03, 04.01..03, 24.01, 24.03 · audit.py ← US-14.10/11, TD-001 · skills_catalog.py ← US-15.01, 15.06, 15.07 · skills/** ← US-15.08..10 · mcp_server.py ← US-14.04..11, US-15.04..07
```
