# Motores de inferencia

> Los consumidores del núcleo acceden a estos motores solo a través de las interfaces de `04_ARQUITECTURA/inference_ports.md` (ADR-015, ADR-016).
>
> Implementado en SPRINT-003: `RulesDecisionEngine` y `OllamaGenerationEngine` (`src/acm/inference/`). Registro de modelos: `model_registry.md`.

Estado: **PLANNED** — ninguno integrado ni probado en este entorno. Información de fuentes públicas consultadas el 2026-09-30.

## Ollama (generativo) — EPIC-22, TECH-018
Modelos locales generativos. Detalle pendiente de SPIKE-005.

## Ollaya (decisional, "JEV") — EPIC-50, TECH-020, ADR-006

> CONF-001 resuelto (ADR-012): JEV = estos modelos de decisión; se integrarán y el núcleo expone desde el MVP una interfaz de decisión común (US-35.11) en la que el adaptador Ollaya/TypeSafe se enchufa sin cambiar a los consumidores.

| Campo | Valor |
|-------|-------|
| Qué es | Runtime local "tipo Ollama" para modelos de decisión estilo Jev |
| Repositorio | github.com/ollaya-dev/ollaya — Apache-2.0 |
| Versión observada | v0.7.5 (2026-09-28); proyecto muy reciente, varias versiones al día |
| Puerto por defecto | 11435 |
| CLI | `ollaya serve`, `pull`, `run`, `list`, `ps`, `show`, `rm`, `cp`, `stop`, `create` |
| Backend | ONNX Runtime; CPU, NVIDIA CUDA, Apple MLX; Docker `ghcr.io/ollaya-dev/ollaya:cuda` |
| Variables | `OLLAYA_HOST`, `OLLAYA_MODELS`, `OLLAYA_KEEP_ALIVE`, `OLLAYA_DEVICE`, `OLLAYA_API_KEY` |
| Compatibilidad | `TYPESAFE_BASE_URL=http://localhost:11435` → los SDK oficiales de TypeSafe funcionan sin cambios |

### Endpoints
| Método | Ruta | Uso |
|--------|------|-----|
| POST | `/v1/systemone` | Compatible TypeSafe (wire idéntico) |
| POST | `/v1/decisions` | Compatible TypeSafe |
| GET | `/v1/models` | Compatible TypeSafe |
| POST | `/api/decide` | Nativo: añade `routing` y tiempos (ns) |
| POST | `/api/pull` | Descarga de modelos (NDJSON) |
| GET | `/api/tags`, `/api/show`, `/api/ps` | Gestión de modelos |

### Contrato (resumen de `docs/api.md` del repositorio)
Petición: `model`, `state` (texto o JSON), `questions` (mapa nombre → `{type, instructions, criteria}`), `keep_alive` opcional.
Tipos: `choice` (categoría + `probabilities`, `confidence`), `score` (valor continuo sobre niveles + `probabilities`), `noul` (probabilidad sí/no).
Respuesta: `answers`, `usage` (`output_tokens` siempre 0); en `/api/decide` además `routing`, `total_duration`, `eval_duration`.
Límites: 1–256 preguntas; 2–255 opciones por `choice`; 2–10 niveles por `score`; estado ≤ 65 536 tokens; cuerpo ≤ 8 MiB.
Errores: `INVALID_REQUEST`/`INPUT_TOO_LONG`/`STATE_TRUNCATED`/`TOO_MANY_OPTIONS` (422), `MODEL_NOT_FOUND` (404), `QUEUE_FULL` (503 + `Retry-After`), `MODEL_LOAD_FAILED` (500).

### Usos previstos en ACM (segundo cerebro, ADR-012)
- Decisiones delegadas por el agente externo vía MCP (US-35.10), para ahorrarle tokens.
- Watchdog: ¿historia INVEST? (`noul` por criterio), ¿criterio verificable? (US-04.15), severidad de bug (`score`), ¿cambio viola ADR? (US-50.07).
- Router: tarea generativa → Ollama, decisión → Ollaya (US-50.03).

### SPIKE-006 (refinado)
Validar en hardware real: instalación Docker fijada, latencia y calibración de `laya`/`decider` con preguntas de gobernanza ACM, estabilidad del contrato entre versiones, comportamiento con `QUEUE_FULL`.

## Fuentes
- https://github.com/ollaya-dev/ollaya (README, `docs/api.md`, releases)
- https://www.marktechpost.com/2026/09/19/typesafe-ai-releases-jev/
- https://www.datacamp.com/blog/system-one-models-jev
