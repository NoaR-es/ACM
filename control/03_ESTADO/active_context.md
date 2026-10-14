TASK: SPRINT-009 PAUSADO (2026-10-14, a petición del operador)
STORY: US-14.12..14.17 (IN_PROGRESS: tests nuevos en PASS en local; falta la suite completa, evidencia, control y CI)
SPRINT: SPRINT-009 — Conexión universal de agentes, unión con aprobación y colaboración

PARA REANUDAR:
1. Ejecutar la suite completa: ACM_E2E_REQUIRED=1 .venv/bin/pytest -q (esperado 431 casos) y ruff.
2. Generar 12_TESTING/sprint_009_evidence.md con tools/evidence.py y pasar las historias a VERIFIED si todo pasa.
3. Actualizar control/: 03_ESTADO, 06_API (65 herramientas, rutas /join-requests y /work), 07_DATOS (global v9, proyecto v6),
   08 environment, 09 events (join.*, work.*), 10_IA, 11_SEGURIDAD, 12_TESTING, 15_CAMBIOS (0.9.0.dev0), RELATIONSHIPS, INDEX, glossary.
4. Commit, push y comprobar la CI.

RELEVANT DOCUMENTS:
01_PRODUCTO/product_definition_v6.md · 02_AGILE/sprint.md · 14_DECISIONES/decisions.md (ADR-023..025)

LOCK: none
LAST_UPDATED: 2026-10-14
