# Código muerto

Revisión: 2026-09-30 (SPRINT-007). Resultado: **ninguno detectado**.

- `ruff check` (F401/F811/F841) sin avisos en `src/`, `tests/` y `control/tools/`.
- TypeScript estricto con `noUnusedLocals`/`noUnusedParameters` en `web/`: `tsc --noEmit` sin errores.
- Parámetros de configuración: `context.max_tokens` lo consume `ContextService` (`domain/context.py`) y `decision.engine_order` lo consume `EngineRouter` (`inference/router.py`). La nota anterior («sin consumidor») quedó obsoleta en SPRINT-004/005 y se corrige aquí.
- `spikes/` no es código muerto: son experimentos documentados que `src/acm` no importa.
- `src/acm/webui/` es un artefacto generado (no código fuente): lo regenera `npm run build`.

Limitación: no hay una herramienta automática de cobertura ni de símbolos sin uso entre módulos (p. ej. `vulture`). La revisión es manual más lint; queda como mejora posible, no como deuda registrada.
