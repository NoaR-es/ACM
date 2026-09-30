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
