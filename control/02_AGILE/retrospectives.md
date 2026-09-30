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

## SPRINT-003 (2026-09-30)
**Bien**
- Se comprobó el entorno (acceso a Ollama y a modelos) antes de fijar el alcance, y las historias de Ollama quedaron IMPLEMENTED, no VERIFIED, al no poder probarse contra una instancia real.
- El Ollama simulado es un servidor HTTP real: cubre errores de conexión, HTTP 404/500 y respuestas incompletas.
- Las mutaciones marcan ahora un timeout como INVALID, no como detección (acción de SPRINT-002).
- Se vio en la matriz que citar un test como "CA-01 parcial" habría marcado CA-01 como PASS; se cambió la cita para que quede PENDIENTE.

**Mal**
- Un primer borrador del router extraía el nombre del motor separando por `:`, lo que rompía `ollama:<modelo>`. Se detectó al revisar el código, antes de los tests.
- El cliente HTTP de Ollama no se cerraba al apagar ACM; se corrigió en el mismo sprint.
- Los tests async del nuevo archivo mixto fallaron por no llevar la marca `anyio`.

**Acciones**
- Ejecutar SPIKE-005 en una máquina con Ollama (operador) antes de construir `OllamaDecisionEngine`.
- Automatizar las mutaciones (sigue pendiente).

## SPRINT-004 (2026-09-30)
**Bien**
- Se comprobó con un experimento (8 identidades, 200 llamadas concurrentes, 0 mezclas) que la identidad de la petición llega a la herramienta antes de basar el diseño en ello.
- Los tests de seguridad van contra ACM real por HTTP, no contra el dominio aislado.
- Revisando el SDK se encontró TD-002 (421 con otro Host), que habría impedido exponer ACM, el objetivo del sprint. Se verificó con una petición real antes de registrarlo y se corrigió.
- El secreto del token se redacta en la auditoría: un test lo comprobó y una mutación confirmó que el test lo protege.

**Mal**
- En SPRINT-002 se añadió al glosario una definición de TD-NNN que ya existía (se corrigió en SPRINT-003).
- La primera versión del CLI dejaba la base abierta si fallaba la operación; se corrigió antes de los tests.

**Acciones**
- Buscar en el SDK las suposiciones que dependen del despliegue (host, TLS, proxy) cuando se toque la red.
- Automatizar las mutaciones (sigue pendiente).

## SPRINT-005 (2026-09-30)
**Bien**
- Antes de escribir el test de corrupción se probó qué detecta de verdad `integrity_check`. Sobrescribir contenido de celdas no se detecta; dañar la cabecera de una página sí, 5 de 5 veces. El test usa lo que funciona y el refinamiento documenta el límite.
- El Watchdog es el tercer consumidor de la interfaz de decisión, y con él se cerró US-35.11 CA-01 con un test real en lugar de declararlo.
- El histórico y el estado de integridad viven en la base global: siguen disponibles aunque la base del proyecto esté dañada.

**Mal**
- Una edición multiarchivo del código abortó a medias (el primer archivo se escribió, los siguientes no) porque un ancla no coincidía. Se detectó y se completó, pero la práctica "validar todo antes de escribir" solo se aplicaba a `control/`.

**Acciones**
- Aplicar también a las ediciones de código en varios archivos la validación previa de todas las anclas.
- Medir la duración de la auditoría con proyectos grandes antes de bajar el intervalo por defecto.

## SPRINT-006 (2026-09-30)
**Bien**
- Persistir los eventos en SQLite resolvió de una vez tres problemas: agentes en otros procesos, reanudación tras reconexión y deduplicación por `seq`. Lo demuestra un test con un agente stdio real.
- Revisando el código del test se vio que `{"type": "event", **event}` dejaba que el `type` del evento pisara el del mensaje. Se corrigió el protocolo (evento anidado) antes de que nadie lo consumiera.
- Los errores de validación de FastAPI (422 con otro formato) se unificaron con el resto al escribir el test de formato consistente.

**Mal**
- Un primer borrador del helper de eventos del test salió con condiciones sin sentido. Se detectó al releerlo y se reescribió antes de ejecutarlo.
- El fixture de ACM real se importaba entre módulos de test (avisos de ruff); se movió a `tests/live.py`.

- Por segunda vez se añadió al glosario un término que ya existía (Watchdog, en SPRINT-005). Se unificó.

**Acciones**
- Releer cada helper de test antes de ejecutarlo, no solo el código de producto.
- Buscar el término en el glosario antes de añadirlo.
