# Registro de modelos

Actualizado: 2026-09-30 (SPRINT-003).

| Motor | Provider | Modelo | Tipo | Uso | Configuración | Calibrado | Estado |
|-------|----------|--------|------|-----|---------------|-----------|--------|
| `rules` | rules (en proceso) | — (sin modelo) | decisión | Gate READY y `acm_decide` para `story.quality` | Siempre registrado | Sí (respuestas exactas) | IMPLEMENTED (VERIFIED por tests) |
| `ollama:<ACM_OLLAMA_MODEL>` | Ollama | El que configure el operador: **ninguno fijado en el código ni verificado** | generación | Resumen del contexto compacto (`context.compact`) | `ACM_OLLAMA_URL` + `ACM_OLLAMA_MODEL` | No aplica (generación) | IMPLEMENTED — solo probado contra un Ollama simulado (IMP-004, SPIKE-005) |
| `jev:<modelo>` | Ollaya / TypeSafe | Por decidir (candidatos en `models.md`) | decisión | Decisiones calibradas | EPIC-50 | Sí (según ADR-006) | PLANNED |

Regla: ACM solo considera sano un motor Ollama si su modelo aparece en `GET /api/tags` (US-22.01 CA-04); los modelos detectados se guardan en `inference_engines` y se consultan con `acm_engines_list`.
Coste: los motores locales no tienen coste por token; los tokens que Ollama informa se registran en `inference_calls` (`cost_tracking.md`).
