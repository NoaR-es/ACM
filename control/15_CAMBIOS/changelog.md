# Changelog

## [0.0.3] — 2026-09-30 — SPRINT-000
- **Cambio:** ADR-006 (JEV = modelos de decisión servidos localmente con Ollaya; adaptador único contra el contrato TypeSafe System One). ADR-007 (MVP final; supersede ADR-003): FEAT-02.03 y FEAT-07.02 pasan a POST-MVP. Backlog regenerado. IMP-002 y GAP-003 cerrados.
- **Motivo:** Aclaración y delegación del operador.
- **Archivos:** `control/14_DECISIONES/`, `10_IA/`, `tools/derive_backlog.py`, `01_PRODUCTO/` (generados), `02_AGILE/`, `03_ESTADO/`, `13_BUGS/`, `00_GOBIERNO/`, `04_ARQUITECTURA/`, `RELATIONSHIPS.md`, `INDEX.md`.
- **Impacto:** Alcance MVP reducido en 2 features. Sin código de producto.
- **Tests:** TEST-CTRL-001 PASS.
- **Breaking change:** no.

## [0.0.2] — 2026-09-30 — SPRINT-000
- **Cambio:** ADR-005 — backend en Python ≥ 3.11. IMP-001 cerrado; GAP-002 reducido a tooling frontend (TASK-000-07).
- **Motivo:** Decisión del operador.
- **Archivos:** `control/14_DECISIONES/`, `02_AGILE/`, `03_ESTADO/`, `04_ARQUITECTURA/`, `13_BUGS/`, `12_TESTING/`, `RELATIONSHIPS.md`, `INDEX.md`.
- **Impacto:** Desbloquea SPIKE-001/002 y el esqueleto del backend.
- **Tests:** TEST-CTRL-001 PASS.
- **Breaking change:** no.

## [0.0.1] — 2026-09-30 — SPRINT-000
- **Cambio:** Arranque del sistema de control `control/`; definición de producto v1; backlog derivado (48 EPIC / 150 FEAT / 352 US / 30 TECH / 12 SPIKE); ADR-001..004; `control/tools/derive_backlog.py`.
- **Motivo:** CLAUDE.md §42 (arranque de proyecto).
- **Archivos:** `control/**`.
- **Impacto:** Solo documentación y tooling. Sin código de producto.
- **Tests:** TEST-CTRL-001 PASS.
- **Documentación:** toda `control/`.
- **Breaking change:** no.
