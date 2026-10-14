---
name: acm-discovery
description: Discovery socrático para entender un producto antes de crear backlog, registrando en ACM requisitos, épicas y supuestos de forma trazable.
version: 1.0.0
capabilities: [product-discovery, requirements-capture]
dependencies: [acm-schema]
---

# Discovery socrático con ACM

Tú (el agente) haces el razonamiento; ACM guarda el resultado de forma trazable. No pases a historias hasta
entender el producto.

## 1. Preguntas antes de escribir nada
- **Visión:** ¿qué problema resuelve y para quién? ¿Cómo sabremos que funciona?
- **Actores:** ¿quién lo usa, quién lo administra, qué sistemas externos intervienen?
- **Alcance:** ¿qué está fuera? ¿Qué es imprescindible en la primera versión?
- **Restricciones:** técnicas, legales, de coste, de plazo, de datos.
- **Dependencias ocultas:** ¿qué debe existir antes? ¿Qué decisiones condicionan a otras?
- **Riesgos y supuestos:** ¿qué estamos dando por hecho? ¿Qué pasaría si fuera falso?
- **Conflictos:** ¿hay requisitos que se contradicen?

Haz las preguntas al humano cuando la respuesta no esté en la documentación. No inventes respuestas.

## 2. Registrar en ACM
1. Cada necesidad confirmada → `acm_requirement_create` (título breve; descripción con el porqué y la fuente).
2. Agrupa requisitos en capacidades → `acm_epic_create` con `objective`, `scope` y `requirement_ids`.
3. Supuestos y conflictos sin resolver: anótalos en la descripción del requisito afectado y pregunta al humano;
   no los conviertas en historias.
4. Comprueba con `acm_backlog_audit` que no quedan requisitos huérfanos antes de planificar un sprint, y con
   `acm_requirement_trace` que cada requisito llega hasta historias.

## 3. Cuándo parar
El discovery termina cuando cada requisito confirmado está en al menos una épica y no quedan conflictos abiertos
sin decisión humana. Después usa la skill `acm-invest` para escribir las historias.
