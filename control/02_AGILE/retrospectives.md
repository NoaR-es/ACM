# Retrospectivas

## SPRINT-000 — Inception (2026-09-30)
**Bien**
- Todas las decisiones de alcance quedaron trazadas en ADRs, con evidencia cuando hubo spike.
- Los inventarios generados por script con `--check` evitaron errores de transcripción en casi 500 historias.
- Las ediciones masivas de `control/` pasaron a validarse antes de escribir (desde 0.0.3), tras un commit parcial en 0.0.2.

**Mal**
- Commit parcial por un script de edición que abortó a mitad (0.0.2).
- Se subió `__pycache__` al repositorio (c0d9482). Corregido con `.gitignore`.
- Tres ejecuciones defectuosas del banco de SPIKE-001 antes de obtener datos válidos. Se detectaron y documentaron, pero habrían producido conclusiones falsas si no se hubieran revisado.
- Se marcó SPIKE-002 como VERIFIED antes de responder su pregunta principal (aislamiento). Se corrigió en la misma iteración.

**Acciones**
- Toda edición multiarchivo: validar todo y después escribir (práctica ya en uso).
- Comprobar `git status` y artefactos antes de cada commit.
- Antes de marcar un SPIKE o una historia como VERIFIED, volver a leer su pregunta o sus CA literales y comprobar la evidencia de cada uno.

## SPRINT-001 (2026-09-30)
**Bien**
- Refinamientos con la regla READY de A y un script que calcula READY y comprueba que cada test citado existe: la trazabilidad historia → test se verifica automáticamente.
- Pruebas de mutación manuales: confirman que los tests detectan los errores que protegen (BEGIN IMMEDIATE, foreign_keys, atomicidad, validación, errores MCP, migración concurrente).
- La validación previa de las ediciones de `control/` abortó sin escribir nada cuando una edición no coincidía.

**Mal**
- Una de las mutaciones estaba mal escrita (error de sintaxis) y habría pasado por una "detección" falsa; se repitió bien.

**Acciones**
- Automatizar las pruebas de mutación de las invariantes críticas (candidato a TECH) en lugar de hacerlas a mano.
- Comprobar la CI remota tras el push.
