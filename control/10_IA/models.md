# Modelos

Actualizado: 2026-10-06 (SPRINT-008). Ningún modelo está fijado en el código ni evaluado con hardware real (IMP-004).

ACM descubre los modelos instalados (`GET /api/tags` de Ollama y de Ollaya) y el operador elige uno de Ollama y varios de Ollaya por propósito (ADR-021, `model_registry.md`).

## Guía de modelos de Ollaya (para el agente)
Fuente: README de github.com/ollaya-dev/ollaya, consultado el 2026-09-30. Vive en `src/acm/inference/ollaya_models.py` (`GUIDE`) y se sirve a los agentes con `acm_models_list` y en Sistema → Modelos. Familias: `winnow:e4b` (recomendado por Ollaya: 0,722 en typed-decisions), `winnow` (12B), `laya` (enrutador por idioma, CPU) con `laya:en` (421M) y `laya:multilingual` (322M), `laya:typed-decisions`, `decider` (2b/4b/0.8b) y `decider:2b-vision`, `kev` (calibrado), `decision`, `qwen3guard` (seguridad), `nli` y `gliclass` (zero-shot), `von`, `clm`, `jevk5` (≤ 16 opciones), `nimble` (≤ 255 opciones), `jeb` y `cygnet`.

## Sugerencias de ACM por propósito (criterio de ACM, no del fabricante)
| Propósito | Sugerencia |
|-----------|------------|
| `agile.story_review` | Con GPU, `winnow:e4b`; sin GPU, `laya` (las historias suelen estar en español) |
| `agile.sprint_review` | `kev` (probabilidades calibradas para el riesgo) o `winnow:e4b` |
| `story.quality` | Reglas; no necesita modelo |
| Clasificar texto en etiquetas | `nli` o `gliclass` |
| Más de 16 opciones | `nimble` |
| Contenido potencialmente inseguro | `qwen3guard` |

Las cifras de rendimiento son las publicadas por Ollaya; ACM no las ha medido (SPIKE-006).
