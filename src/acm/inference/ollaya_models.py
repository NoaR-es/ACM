"""Guía de modelos de Ollaya (JEV) para operadores y agentes (US-50.10).

Qué es cada familia, para qué sirve y cuándo elegirla. Los datos (tamaños, precisión en «typed-decisions», latencias)
proceden del README del repositorio github.com/ollaya-dev/ollaya, consultado el 2026-09-30; no se han medido en ACM
(SPIKE-006). Las sugerencias por propósito de ACM (`ACM_SUGGESTIONS`) son criterio de ACM, no del fabricante.

El catálogo (`domain/models.py`) adjunta a cada modelo detectado la entrada de su etiqueta exacta o, si no la hay, la
de su familia (lo que va antes de `:`).
"""

from __future__ import annotations

from typing import Any

SOURCE = "https://github.com/ollaya-dev/ollaya (README), consultado el 2026-09-30"
ALL_TYPES = ["choice", "score", "noul"]


def _m(summary: str, best_for: str, size: str = "", notes: str = "", types: list[str] | None = None) -> dict[str, Any]:
    return {"summary": summary, "best_for": best_for, "size": size, "notes": notes, "types": types or ALL_TYPES}


GUIDE: dict[str, dict[str, Any]] = {
    "winnow:e4b": _m(
        "Winnow-E4B (ajuste de Gemma 4). Modelo recomendado por Ollaya: 0,722 en typed-decisions (Jev de "
        "TypeSafe: 0,738); 89 ms para cinco preguntas en una RTX 4090.",
        "Modelo por defecto si hay GPU: la mejor precisión general para choice, score y noul.",
        "4B",
    ),
    "winnow": _m(
        "Winnow-12B, hermano mayor de winnow:e4b: 0,702 en typed-decisions.",
        "Solo si sobra GPU; winnow:e4b es más preciso y ligero según Ollaya.",
        "12B",
    ),
    "laya": _m(
        "Enrutador: detecta el idioma de cada petición y responde con laya:en o laya:multilingual.",
        "Sin GPU: responde en fracciones de segundo en CPU (Ollaya recomienda empezar por él). Textos en español.",
        "322M–421M",
    ),
    "laya:en": _m(
        "Modelo de decisión en inglés (ModernBERT-large, 421M). El más rápido: 8–10 ms para cinco preguntas en una "
        "RTX 4090.",
        "Estados en inglés cuando importa la latencia.",
        "421M",
        "Solo inglés.",
    ),
    "laya:multilingual": _m(
        "Modelo de decisión multilingüe, más de 100 idiomas (mmBERT-base, 322M).",
        "Estados en español u otros idiomas sin GPU.",
        "322M",
    ),
    "laya:typed-decisions": _m(
        "Laya ajustado sobre los flujos de typed-decisions.", "Decisiones tipadas generales en CPU.", ""
    ),
    "decider": _m(
        "Decodificadores Qwen3.5 de Mapika: 2B (por defecto), 4B y 0.8B. 0,680 en typed-decisions (4B), 0,591 (2B).",
        "Alternativa general; decider:0.8b si el hardware es muy limitado.",
        "0.8B / 2B / 4B",
    ),
    "decider:2b-vision": _m(
        "Decider visión-lenguaje (Qwen3.5-2B): preguntas sobre una imagen además del estado.",
        "Decisiones sobre imágenes (capturas, diagramas).",
        "2B",
        "ACM todavía no envía imágenes en acm_decide: hoy solo sirve con texto.",
    ),
    "kev": _m(
        "Kev de Jared Palmer: LoRA y cabeza puntero sobre Qwen3.5 (4B por defecto, 0.8B, 9B), calibrado. "
        "kev:4b 0,669 y kev:9b 0,722 en typed-decisions.",
        "Cuando importan probabilidades fiables: gates, validaciones y umbrales de confianza.",
        "0.8B / 4B / 9B",
    ),
    "decision": _m(
        "Decision 1.0 Eos (vLLM Semantic Router): Qwen3.5-0.8B con cabeza de endpoint y filas de 16k tokens.",
        "Estados largos (hasta 16k tokens) con un modelo pequeño.",
        "0.8B",
    ),
    "qwen3guard": _m(
        "Qwen3Guard-Gen-0.6B, guarda de seguridad con preguntas integradas: seguro, controvertido o inseguro, y la "
        "categoría.",
        "Filtrar contenido potencialmente inseguro antes de procesarlo.",
        "0.6B",
        "Sus preguntas son fijas: no es un decisor general.",
    ),
    "nli": _m(
        "Clasificadores zero-shot NLI de Moritz Laurer (DeBERTa-v3-large, ModernBERT-large).",
        "Etiquetar texto libre con categorías que no ha visto al entrenar (choice, noul).",
        "large",
        types=["choice", "noul"],
    ),
    "gliclass": _m(
        "Clasificador zero-shot que sigue instrucciones (Knowledgator, DeBERTa-v3-large).",
        "Clasificación zero-shot guiada por instrucciones.",
        "large",
        types=["choice", "noul"],
    ),
    "von": _m(
        "Von 1.1 (ModernBERT-large): puntúa cada opción en su propio marcador; contexto de 8k tokens.",
        "Estados medianos con varias opciones puntuadas por separado.",
        "large",
    ),
    "clm": _m(
        "CLM-v0.1-8B (encoder Qwen3-8B y dos cabezas de proyección): puntúa opciones por similitud, con caché.",
        "Estados de agentes, juegos y tool-calling. Precisión baja en typed-decisions (0,357).",
        "8B",
    ),
    "jevk5": _m("JevK5 v0.3 (Qwen3.5-4B, GGUF Q8_0), hasta 16 opciones.", "Decisiones con hasta 16 opciones.", "4B"),
    "nimble": _m(
        "Nimble v2 (Bespoke Labs): LoRA sobre Qwen3.5-9B que lee la petición como esquema JSON; 0,665 en "
        "typed-decisions; hasta 255 opciones; ~2,3 s para cinco preguntas en una RTX 4090.",
        "Muchas opciones (más de 16), cuando la latencia no importa.",
        "9B",
    ),
    "jeb": _m(
        "Jebadiah (AINode): LoRAs sobre Qwen3.5 (9B por defecto, 4B) y 27B; jeb:9b responde cinco preguntas en "
        "124 ms en una RTX 4090.",
        "Alternativa general con GPU.",
        "4B / 9B / 27B",
    ),
    "cygnet": _m(
        "Cygnet (blockbrain-ai): Gemma 4 12B IT congelado con lectura por letras; 0,683 en typed-decisions, 202 ms.",
        "Alternativa general con GPU.",
        "12B",
    ),
}

# Criterio de ACM (no del fabricante): qué familia encaja con cada propósito que usa ACM por sí mismo.
ACM_SUGGESTIONS: dict[str, str] = {
    "agile.story_review": "Con GPU, winnow:e4b; sin GPU, laya (las historias suelen estar en español).",
    "agile.sprint_review": "kev (probabilidades calibradas para el riesgo) o winnow:e4b.",
    "story.quality": "Lo responden las reglas; no necesita modelo.",
    "clasificar texto en etiquetas": "nli o gliclass (zero-shot).",
    "más de 16 opciones": "nimble (hasta 255).",
    "contenido potencialmente inseguro": "qwen3guard.",
}
CHOOSING = [
    "Con GPU, empieza por winnow:e4b (recomendado por Ollaya). Sin GPU, empieza por laya.",
    "Si necesitas probabilidades en las que confiar para un umbral (gates), prefiere kev.",
    "Para etiquetar texto libre con categorías nuevas, nli o gliclass.",
    "Asigna modelos por propósito en ACM (Sistema → Modelos o acm_models_select) y deja uno por defecto.",
]


def guide_for(name: str) -> dict[str, Any] | None:
    """Entrada de la guía para un modelo instalado: su etiqueta exacta (sin `:latest`) o, si no, su familia."""
    tag = name.removesuffix(":latest")
    for suffix in ("-fp32", "-fp16"):  # Ollaya: las etiquetas laya-fp32/-fp16 solo fijan la precisión
        tag = tag.replace(suffix, "")
    return GUIDE.get(tag) or GUIDE.get(tag.split(":")[0])


def overview() -> dict[str, Any]:
    return {"source": SOURCE, "families": GUIDE, "choosing": CHOOSING, "acm_suggestions": ACM_SUGGESTIONS}
