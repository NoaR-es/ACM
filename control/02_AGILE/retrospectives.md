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

## SPRINT-002 (2026-09-30)
**Bien**
- La matriz de evidencia pasa a generarse con un script permanente (`tools/evidence.py`) que cruza refinamientos y JUnit; se comprobó que reproduce la de SPRINT-001.
- Los tests de skills trabajan sobre una copia temporal del catálogo: recarga, retirada y notificación se prueban sin tocar las skills oficiales.
- Las skills se prueban contra el servidor real: acm-schema documenta exactamente las herramientas publicadas y las demás solo citan herramientas existentes.

**Mal**
- Un refinamiento (US-14.11) afirmaba que ninguna operación podía quedar sin auditar; no era cierto (bases distintas, sin transacción común). Se corrigió y se registró TD-001.
- Un mutante estaba mal planteado (dejaba un bucle infinito) y habría contado como detección por timeout; se sustituyó por uno válido.
- `create_feature` devolvía la épica entera en lugar de la feature; lo detectó un test.
- No se comprobó la CI del commit `445f09c` (run #2, en rojo por BUG-001) aunque la retrospectiva anterior lo pedía. Se detectó al comprobar la CI de SPRINT-002.

**Acciones**
- Al redactar un refinamiento, contrastar cada garantía con el diseño real antes de escribirla.
- Automatizar las mutaciones (sigue pendiente de SPRINT-001) y limitarlas con un timeout que las marque como inválidas, no como detectadas.
- Comprobar la CI después de cada push, incluidos los commits solo de documentación.
