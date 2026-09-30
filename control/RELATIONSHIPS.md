# Relaciones

LAST_UPDATED: 2026-09-30

## Sprint → Tasks
```
SPRINT-000
├── TASK-000-01 → control/** (estructura)
├── TASK-000-02 → control/01_PRODUCTO/product_definition_v1.md, control/tools/derive_backlog.py, TEST-CTRL-001, ADR-004
├── TASK-000-03 → control/14_DECISIONES/decisions.md (ADR-001..004)
├── TASK-000-04 → IMP-001, GAP-002 → (futuro ADR-005)
├── TASK-000-05 → IMP-002, GAP-003, EPIC-24, SPIKE-006
└── TASK-000-06 → ADR-003, control/01_PRODUCTO/requirements.md
```

## Código → origen
```
control/tools/derive_backlog.py
├── TASK-000-02
├── ADR-003 (constantes MVP)
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
GAP-002 → IMP-001, TASK-000-04, ADR-001
GAP-003 → IMP-002, EPIC-24, SPIKE-006, TECH-020
GAP-004 → EPIC-03..EPIC-48
GAP-005 → 07_DATOS/data_architecture.md, EPIC-13, 16, 17, 27
```
