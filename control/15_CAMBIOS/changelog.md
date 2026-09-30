# Changelog

## [0.0.5] — 2026-09-30 — SPRINT-000
- **Cambio:** Registro íntegro del backlog completo del operador (fuente A). Unificación con la definición v1.1 (fuente B) en un backlog de 53 épicas, 199 features, 488 historias y 531 criterios, con `id_mapping.md`. ADR-010 (supersede a ADR-009; MVP v3 = 228 historias). Nuevas épicas EPIC-49..53. Conflictos CONF-001..004, GAP-006 e IMP-003. Documentos activos traducidos a la numeración unificada.
- **Motivo:** El operador aporta el prompt inicial completo.
- **Archivos:** `control/01_PRODUCTO/` (fuente A, fuentes y generados), `tools/derive_backlog.py` (reescrito), `14_DECISIONES/`, `13_BUGS/`, `02_AGILE/`, `03_ESTADO/`, `04_ARQUITECTURA/`, `06_API/`, `07_DATOS/`, `10_IA/`, `00_GOBIERNO/`, `05_CODIGO/`, `12_TESTING/`, `RELATIONSHIPS.md`, `INDEX.md`.
- **Impacto:** Cambian los IDs de las historias de la definición v1.1; tabla de traducción en `id_mapping.md`.
- **Tests:** TEST-CTRL-001 PASS.
- **Breaking change:** sí, para referencias a IDs de B (documental; no hay código de producto).

## [0.0.4] — 2026-09-30 — SPRINT-000
- **Cambio:** Definición de producto v1.1: ACM implementa y gestiona su propio servidor MCP y distribuye por él sus skills (nueva FEAT-15.04 con US-15.09..12, con criterios de aceptación; objetivos de EPIC-15 y EPIC-22; punto 27 del MVP). ADR-008 (extensión oficial MCP Skills SEP-2640 + `instructions` + herramientas de respaldo). ADR-009 (EPIC-22/FEAT-22.01 al MVP; supersede ADR-007). v1.0 archivada en `99_ARCHIVO/superseded/`. Nuevo `06_API/mcp_server.md`.
- **Motivo:** Aclaración del operador.
- **Archivos:** `control/01_PRODUCTO/` (v2 + generados), `99_ARCHIVO/`, `14_DECISIONES/`, `06_API/`, `tools/derive_backlog.py`, `00_GOBIERNO/`, `02_AGILE/`, `03_ESTADO/`, `04_ARQUITECTURA/`, `05_CODIGO/`, `RELATIONSHIPS.md`, `INDEX.md`.
- **Impacto:** +4 historias (356). MVP ampliado (EPIC-22 con FEAT-22.01; FEAT-15.04).
- **Tests:** TEST-CTRL-001 PASS.
- **Breaking change:** no.

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
