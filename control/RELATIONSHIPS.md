# Relaciones

LAST_UPDATED: 2026-09-30

## Sprint → Tasks
```
SPRINT-000
├── TASK-000-01 → control/** (estructura)
├── TASK-000-02 → control/01_PRODUCTO/product_definition_v1.md, control/tools/derive_backlog.py, TEST-CTRL-001, ADR-004
├── TASK-000-03 → control/14_DECISIONES/decisions.md (ADR-001..004)
├── TASK-000-04 → IMP-001 (CLOSED), GAP-002 → ADR-005
├── TASK-000-07 → GAP-002 (tooling frontend)
├── TASK-000-05 → IMP-002, GAP-003 → ADR-006
└── TASK-000-06 → ADR-003 (SUPERSEDED) → ADR-007, control/tools/derive_backlog.py
```

## Código → origen
```
control/tools/derive_backlog.py
├── TASK-000-02
├── ADR-007 (constantes MVP; antes ADR-003)
├── ADR-004
└── TEST-CTRL-001
```

## Producto
- Épica → Feature → Historia: generado en `01_PRODUCTO/features.md` y `01_PRODUCTO/user_stories.md` (bidireccional por ID).
- Requisito funcional → Épica: `01_PRODUCTO/requirements.md` (REQ-F-01..40).
- Épica → Componente arquitectónico: `04_ARQUITECTURA/architecture.md`.
- Historia → Código / Test / API: **ninguna todavía** (no hay implementación).

## Gaps → afectados
```
GAP-001 → 351 US (todas salvo US-01.01)
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

ADR-007 (MVP)
├── supersede ADR-003
├── control/tools/derive_backlog.py (MVP_EPICS, POST_MVP_FEATURES)
└── 01_PRODUCTO/backlog.md, epics.md, features.md, user_stories.md
```
