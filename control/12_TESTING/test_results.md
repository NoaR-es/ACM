# Resultados

| Fecha | Test | Resultado | Salida |
|-------|------|-----------|--------|
| 2026-09-30 | TEST-CTRL-001 | PASS | `epics=48 features=150 stories=352 tech=30 spikes=12` / `OK (check)` |
| 2026-09-30 | Verificación cruzada manual | PASS | `grep -c` sobre la fuente: 48 EPIC, 150 FEAT, 352 US, 30 TECH, 12 SPIKE; 0 IDs de historia duplicados |
| 2026-09-30 | TEST-CTRL-001 (tras definición v1.1) | PASS | `epics=48 features=151 stories=356 tech=30 spikes=12` / `OK (check)` |
| 2026-09-30 | TEST-CTRL-001 (backlog unificado) | PASS | `epics=53 features=199 stories=488 (A=132 B=356) criteria=531 mvp=228 overlaps=37` / `OK (check)` |
| 2026-09-30 | Verificación cruzada fuente A | PASS | `grep -c`: 48 `# EPIC-`, 48 FEAT, 132 `### US-`, 515 `CA-`; 0 IDs de historia duplicados (coincide con el parser) |
| 2026-09-30 | TEST-CTRL-001 (definición v1.2 + ADR-012) | PASS | `epics=53 features=201 stories=492 (A=132 B=360) criteria=543 mvp=233 overlaps=37` / `OK (check)` |
| 2026-09-30 | TEST-SPIKE-001 | PASS (datos obtenidos) | Ver `20_PERFORMANCE/benchmarks.md`; 2 ejecuciones anteriores descartadas por defectos del experimento (documentados) |
| 2026-09-30 | TEST-SPIKE-002a | PASS 11/11 | Protocolo negociado 2026-07-28 |
| 2026-09-30 | TEST-SPIKE-002b | PASS 4/4 | — |
| 2026-09-30 | TEST-SPIKE-002c | PASS 3/3 | D1 sin estado entre llamadas; D2 aísla |
| 2026-09-30 | TEST-CTRL-001 (con `item_status.json`) | PASS | Prueba negativa: estado `FINISHED` e ID inexistente → exit 2 |
| 2026-09-30 | TEST-PROD-S01 | PASS 50/50 | `pytest -q` en 4,9 s; `ruff check` limpio |
| 2026-09-30 | Mutación manual (6 invariantes) | 6/6 detectadas | BEGIN DEFERRED, foreign_keys=OFF, sin limpieza atómica, sin validar rango, error no traducido a ToolError, migración sin re-comprobar |
| 2026-09-30 | TEST-CTRL-001 (refs a tests) | PASS | 41 referencias válidas; prueba negativa con un test inventado → exit 2 |
| 2026-09-30 | CI GitHub Actions (ruff + pytest + derive_backlog --check) | PASS | [run #1](https://github.com/NoaR-es/ACM/actions/runs/36758248042), commit `04f32c3` |
| 2026-09-30 | CI GitHub Actions run #2 | **FAIL** | [run #2](https://github.com/NoaR-es/ACM/actions/runs/36758383579), commit `445f09c`: `test_us1803_migracion_concurrente_una_sola_vez` → `database is locked` (BUG-001) |
| 2026-09-30 | CI GitHub Actions runs #3 y #4 | PASS | [run #3](https://github.com/NoaR-es/ACM/actions) commit `7f12a6d` (SPRINT-002); run #4 commit `2cb7de7` (BUG-001) |
| 2026-09-30 | BUG-001 regresión | PASS | `test_bug001_apertura_concurrente_de_base_nueva`: 3/3 FAIL sin la corrección y 3/3 PASS con ella; estrés local 0/480 fallos (antes 13/480) |
| 2026-09-30 | TEST-PROD-S02 | PASS 122/122 (123 con BUG-001) | `pytest -q` en 9,5 s; `ruff check` limpio; 72 tests nuevos (backlog, aislamiento, auditoría, skills, frontera MCP) |
| 2026-09-30 | Mutación manual SPRINT-002 (6 invariantes) | 6/6 detectadas | auditoría solo admin, truncado del resultado, aislamiento de backlog por proyecto, READY solo desde PLANNED, rechazo en cascada por dependencias, recarga solo admin. Un primer mutante inválido (bucle infinito) se descartó |
| 2026-09-30 | TEST-CTRL-001 (SPRINT-002) | PASS | `stories=479 merged=13 test_refs=106`; `OK (check)` |
| 2026-09-30 | TEST-PROD-S03 | PASS 172/172 | 49 tests nuevos (`test_inference.py`, `test_context.py`); Ollama simulado como servidor HTTP real |
| 2026-09-30 | Mutación manual SPRINT-003 (8 invariantes) | 8/8 detectadas | gate acepta motor no calibrado; router ignora `supports()`; fallback sin indicar; Ollama sano sin el modelo; Ollama acepta respuesta vacía; historia resumible; gate sin re-comprobar; ahorro sin admin |
| 2026-09-30 | Ollama real | NO EJECUTADO | Sin acceso a Ollama ni a modelos (IMP-004) |
| 2026-09-30 | `tools/evidence.py` | PASS | SPRINT-002: 21 historias, solo US-24.03 CA-02 PENDIENTE; SPRINT-001 reproducida (solo US-01.02 CA-03 sin test) |
