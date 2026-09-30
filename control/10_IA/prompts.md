# Prompts

| ID | Versión | Dónde | Motor | Propósito | Entrada | Salida esperada | Estado |
|----|---------|-------|-------|-----------|---------|-----------------|--------|
| PROMPT-001 `context.compact` | v1 (2026-09-30) | `src/acm/domain/context.py` (`ContextService._summarize`) | Generación (hoy `ollama:<modelo>`) | Resumir una sección de apoyo del contexto compacto (requisitos, feature, épica, historias hermanas) | Mensaje de sistema con el límite de palabras (≈ ¾ de los tokens objetivo), la orden de conservar literalmente los identificadores (REQ-, EPIC-, FEAT-, US-, CA-) y la de no añadir nada; mensaje de usuario con el texto de la sección | Texto más corto que el original; si no lo es, se descarta | IMPLEMENTED — calidad **sin evaluar** con un modelo real (IMP-004) |

Las fuentes de cada sección las añade ACM de forma determinista; no dependen de que el modelo conserve los identificadores.
