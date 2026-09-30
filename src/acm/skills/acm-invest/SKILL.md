---
name: acm-invest
description: Método para redactar y validar historias de usuario con INVEST y criterios de aceptación binarios antes de pedir en ACM que pasen a READY.
version: 1.0.0
capabilities: [invest-validation, acceptance-criteria]
dependencies: [acm-schema]
---

# Historias INVEST y criterios binarios en ACM

## Antes de crear la historia
Cada historia tiene **actor** (`as_a`), **acción** (`i_want`) y **valor** (`so_that`), y al menos un
**requisito de origen** (`requirement_ids`). Si es trabajo técnico sin valor directo para un usuario, no la
disfraces de historia: usa `kind="technical"` con `technical_reason` explícita, o regístrala como tarea.

## Comprobación INVEST (todas deben cumplirse)
| Letra | Pregunta | Si falla |
|-------|----------|----------|
| I — Independiente | ¿Se puede implementar y probar sin esperar a otra historia? | Reordena o separa la dependencia |
| N — Negociable | ¿Describe el qué y el para qué, no una solución cerrada? | Quita detalles de implementación |
| V — Valiosa | ¿El `so_that` expresa un beneficio para el actor? | Reescribe el valor o cuestiona la historia |
| E — Estimable | ¿Se entiende lo suficiente para estimarla? | Pregunta o crea un spike |
| S — Pequeña | ¿Cabe en un sprint? | Divídela; si su feature crece demasiado, `acm_feature_split` |
| T — Testeable | ¿Cada criterio se puede evaluar como PASS/FAIL? | Reescribe los criterios |

## Criterios de aceptación binarios
- Un criterio es válido solo si dos personas distintas llegarían al mismo PASS/FAIL sin interpretar.
- Usa el formato "Dado… cuando… entonces…" o una afirmación comprobable ("Un nombre vacío se rechaza e identifica el campo").
- Evita palabras vagas: "rápido", "fácil", "adecuado", "correctamente" sin métrica.
- Incluye los casos de error relevantes, no solo el camino feliz.

## En ACM
1. `acm_story_create` con `acceptance_criteria` (o `acm_story_add_criteria` después).
2. `acm_story_get` para revisar la historia completa.
3. `acm_story_mark_ready`: ACM rechaza con `FAILED_PRECONDITION` y la lista de huecos si falta actor, acción,
   valor, requisito de origen o criterios.
4. `acm_backlog_audit` para ver historias sin criterios en todo el proyecto.
