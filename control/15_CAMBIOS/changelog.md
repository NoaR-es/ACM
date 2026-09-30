# Changelog

## [0.2.0.dev0] — 2026-09-30 — SPRINT-002 — skills y backlog por MCP
- **Cambio:**
  - Esquema v2:
    - global: `mcp_audit`;
    - proyecto: requisitos, épicas, features, historias y CA.
  - `BacklogService` (`domain/backlog.py`) y `AuditService` (`domain/audit.py`); nuevo error `FAILED_PRECONDITION`.
  - Servidor MCP: 19 herramientas nuevas (25 en total), extensión Skills (`skills/list`, `skills/get`, `skill://acm/...`), recarga del catálogo con notificación y auditoría de toda invocación.
  - `SkillCatalog` y 3 skills oficiales: acm-schema, acm-invest, acm-discovery.
  - `control/`:
    - 21 refinamientos;
    - 7 fusiones de duplicados (una entre épicas, `cross_epic`);
    - `tools/evidence.py`;
    - SPRINT-001 archivado y SPRINT-002 abierto y cerrado;
    - TD-001 registrada.
- **Stories:**
  - VERIFIED: US-03.03, 04.01..03, 14.04..07, 14.09..11, 15.01, 15.04..10, 24.01;
  - IMPLEMENTED: US-24.03 (CA-02 → EPIC-21).
- **Archivos:** `src/acm/{db/schema.py, domain/backlog.py, domain/audit.py, domain/errors.py, skills_catalog.py, skills/**, mcp_server.py, __init__.py}`, `pyproject.toml`, `tests/test_{backlog,isolation,audit,skills,mcp}.py`, `control/**`.
  - BUG-001 corregido: activación de WAL con reintentos en `db/connection.py`.
- **Tests:** 123/123 PASS (incluye la regresión de BUG-001); 6/6 mutaciones detectadas.
- **Migración:** las bases existentes suben a v2 al abrirse (migraciones aditivas).
- **Breaking change:** no.

## [0.1.0.dev0] — 2026-09-30 — SPRINT-001 — primer código de producto
- **Cambio:**
  - Paquete `acm`:
    - SQLite según ADR-013 (`db/`);
    - `ProjectService` para crear, listar, abrir y configurar proyectos;
    - servidor MCP con 6 herramientas y errores explícitos;
    - FastAPI con `/api/health` y `/mcp`;
    - CLI `serve`/`mcp-stdio`.
  - 50 tests y CI de GitHub Actions.
  - En `control/`:
    - refinamientos READY de 7 historias;
    - 6 fusiones de duplicados;
    - el script calcula READY y verifica que existen los tests citados;
    - SPRINT-000 cerrado y SPRINT-001 abierto;
    - VULN-001 registrada y GAP-007 resuelto en ACM.
- **Stories:**
  - VERIFIED: US-01.01, US-01.03, US-01.06, US-18.01, US-18.02, US-18.03;
  - IMPLEMENTED: US-01.02 (falta la UI).
- **Archivos:** `pyproject.toml`, `README.md`, `src/acm/**`, `tests/**`, `.github/workflows/ci.yml`, `.gitignore`, `control/**`.
- **Tests:** 50/50 PASS; 6/6 mutaciones detectadas.
- **Breaking change:** no.

## [0.0.7] — 2026-09-30 — SPRINT-000
- **Cambio:**
  - SPIKE-001: banco de concurrencia SQLite y resultados.
  - SPIKE-002: prototipo del servidor MCP propio con extensión Skills y 3 suites de pruebas.
  - ADR-013 (SQLite), ADR-014 (topología y MCP) y ADR-015 (interfaces de inferencia) con `inference_ports.md`.
  - `item_status.json`: estados reales de SPIKE/TECH/historias en los inventarios.
  - GAP-007.
- **Motivo:** Fase 0 del roadmap.
- **Archivos:** `spikes/**`, `control/tools/`, `control/14_DECISIONES/`, `04_ARQUITECTURA/`, `06_API/`, `07_DATOS/`, `08_INFRAESTRUCTURA/`, `10_IA/`, `12_TESTING/`, `13_BUGS/`, `20_PERFORMANCE/`, `02_AGILE/`, `03_ESTADO/`, `05_CODIGO/`, `00_GOBIERNO/`, `RELATIONSHIPS.md`, `INDEX.md`, `/.gitignore`.
- **Impacto:** Decisiones técnicas con evidencia; sin código de producto.
- **Tests:** TEST-SPIKE-001, TEST-SPIKE-002a (11/11), 002b (4/4), 002c (3/3) y TEST-CTRL-001: PASS.
- **Breaking change:** no.

## [0.0.6] — 2026-09-30 — SPRINT-000
- **Cambio:**
  - Definición v1.2 (`product_definition_v3.md`; v1.1 archivada): JEV a integrar con la arquitectura preparada desde el inicio; ACM como segundo cerebro del agente (4 historias nuevas con CA: US-35.08..US-35.11).
  - ADR-011: `control/` es la fuente de verdad del desarrollo y SQLite la del producto.
  - ADR-012: interfaz de decisión común desde el MVP; US-47.01 al MVP; CONF-003 aplazado. MVP = 233 historias.
  - REQ-F-41/42. IMP-003 cerrado.
  - Retirado `control/tools/__pycache__` (subido por error en c0d9482) y añadido `.gitignore`.
- **Motivo:** Respuesta del operador a CONF-001..003.
- **Archivos:** `control/01_PRODUCTO/`, `99_ARCHIVO/`, `14_DECISIONES/`, `13_BUGS/`, `02_AGILE/`, `03_ESTADO/`, `00_GOBIERNO/`, `04_ARQUITECTURA/`, `07_DATOS/`, `10_IA/`, `05_CODIGO/`, `12_TESTING/`, `tools/derive_backlog.py`, `RELATIONSHIPS.md`, `INDEX.md`, `/.gitignore`.
- **Impacto:** MVP +5 historias; sin código de producto.
- **Tests:** TEST-CTRL-001 PASS.
- **Breaking change:** no.

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
