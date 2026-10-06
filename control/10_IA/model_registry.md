# Registro de modelos

Actualizado: 2026-10-06 (SPRINT-008).

| Motor | Provider | Modelo | Tipo | Propósitos | Configuración | Calibrado | Estado |
|-------|----------|--------|------|------------|---------------|-----------|--------|
| `rules` | rules (en proceso) | — (sin modelo) | decisión | `story.quality` (gate READY) | Siempre registrado | Sí (respuestas exactas) | VERIFIED |
| `jev:<modelo>` | Ollaya (JEV) | El elegido por propósito o por defecto: **ninguno fijado en el código** | decisión | `agile.story_review`, `agile.sprint_review` y cualquier `acm_decide` | `ACM_JEV_URL` (+ `ACM_JEV_API_KEY`) y selección en `inference_settings` o `ACM_JEV_MODEL` | Sí (según el fabricante; ADR-006) | IMPLEMENTED — solo contra un Ollaya simulado (IMP-004) |
| `ollama-decide:<modelo>` | Ollama | El modelo de Ollama elegido | decisión (respuesta restringida por esquema JSON) | Respaldo de las decisiones cuando no hay JEV | `ACM_OLLAMA_URL` + modelo elegido | **No** (`calibrated=false`; confianza 1.0 nominal) | IMPLEMENTED — solo contra un Ollama simulado |
| `ollama:<modelo>` | Ollama | El modelo de Ollama elegido | generación (y *tool calling*) | `context.compact`, `agile.report`, `agent.chat` | `ACM_OLLAMA_URL` + modelo elegido | No aplica | IMPLEMENTED — solo contra un Ollama simulado (IMP-004, SPIKE-005) |

## Reglas
- **Selección (ADR-021):** el modelo elegido en ACM (`inference_settings`, Sistema → Modelos o `acm_models_select`) tiene prioridad sobre `ACM_OLLAMA_MODEL`/`ACM_JEV_MODEL`. Solo se pueden elegir modelos detectados en el servidor. JEV admite un modelo por propósito (`jev.models_by_purpose`) y uno por defecto; `acm_decide` acepta además `model` explícito.
- **Salud:** un motor está sano si su modelo aparece en `GET /api/tags` (`laya` ≡ `laya:latest`). Los modelos detectados se guardan en `inference_engines`.
- **Enrutado de decisiones:** propósito con regla → reglas; si no, JEV; si no hay JEV, Ollama sin calibrar. El fallo de un motor pasa al siguiente y queda en `fallback_from`.
- **Supervisor:** sus acciones automáticas exigen confianza ≥ `supervisor.min_confidence_pct`. Con Ollama (sin calibrar) la confianza es nominal, por eso el umbral solo protege de verdad con JEV.
- **Coste:** motores locales, sin coste por token; tokens informados en `inference_calls` (`cost_tracking.md`).
