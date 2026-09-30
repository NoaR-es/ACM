# Resultados

| Fecha | Test | Resultado | Salida |
|-------|------|-----------|--------|
| 2026-09-30 | TEST-CTRL-001 | PASS | `epics=48 features=150 stories=352 tech=30 spikes=12` / `OK (check)` |
| 2026-09-30 | Verificación cruzada manual | PASS | `grep -c` sobre la fuente: 48 EPIC, 150 FEAT, 352 US, 30 TECH, 12 SPIKE; 0 IDs de historia duplicados |
| 2026-09-30 | TEST-CTRL-001 (tras definición v1.1) | PASS | `epics=48 features=151 stories=356 tech=30 spikes=12` / `OK (check)` |
| 2026-09-30 | TEST-CTRL-001 (backlog unificado) | PASS | `epics=53 features=199 stories=488 (A=132 B=356) criteria=531 mvp=228 overlaps=37` / `OK (check)` |
| 2026-09-30 | Verificación cruzada fuente A | PASS | `grep -c`: 48 `# EPIC-`, 48 FEAT, 132 `### US-`, 515 `CA-`; 0 IDs de historia duplicados (coincide con el parser) |
| 2026-09-30 | TEST-CTRL-001 (definición v1.2 + ADR-012) | PASS | `epics=53 features=201 stories=492 (A=132 B=360) criteria=543 mvp=233 overlaps=37` / `OK (check)` |
