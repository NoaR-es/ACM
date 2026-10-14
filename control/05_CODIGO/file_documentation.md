# Convenciones de documentación del código

Actualizado: 2026-09-30 (SPRINT-007). Aplicación automática: `control/tools/code_inventory.py --check` (CI).

## Qué se exige a cada archivo de código
| Regla | Python | TypeScript | Verificación |
|-------|--------|------------|--------------|
| Cabecera: para qué existe el archivo, qué historias o ADR cubre | docstring de módulo | comentario en la primera línea (`//` o `/* */`) | `code_inventory --check` (CI) |
| Fila en `file_inventory.md` (propósito, historias, tests) | sí | sí | `code_inventory --check` (CI) |
| Símbolos públicos con descripción | docstring (primera línea: qué hace) | nombre explícito + comentario cuando no es obvio | `code_reference.md` (generado) lo hace visible |
| Rutas REST con docstring | la primera línea sale en OpenAPI y en `code_reference.md` | — | revisión |
| Herramientas MCP con docstring | es la descripción que ven los agentes | — | `test_skills.py` (acm-schema coincide con las herramientas) |

Excepción: `__init__.py` vacíos o de solo versión.

## Qué documento actualizar según el cambio
| Cambio | Documento de `05_CODIGO/` |
|--------|---------------------------|
| Archivo nuevo, movido o borrado | `file_inventory.md` (obligatorio), `source_tree.md` y regenerar `code_reference.md` |
| Módulo backend nuevo o con otra responsabilidad | `modules.md` |
| Servicio de dominio, método público o invariante | `services.md`, `classes.md` |
| Función auxiliar relevante | `functions.md` o `utilities.md` |
| Componente o página React | `components.md` (+ `frontend.md` si cambia la arquitectura) |
| Hook o proveedor | `hooks.md` |
| Tipo compartido con la API | `types.md` |
| Dependencia nueva o de otra versión | `dependencies.md` |
| Fixture o doble de test | `tests.md` |
| Código eliminado o sin uso | `dead_code.md` |

## Tests
Nombre `test_usNNNN_caNN_<qué>`: la historia y el criterio que prueba (ver `tests.md`). Los tests son la documentación ejecutable de cada CA.

## Documentación generada vs. narrativa
- `code_reference.md` es **generado**: no editar a mano; se regenera con `python3 control/tools/code_inventory.py`.
- El resto es **narrativo**: explica responsabilidades, invariantes, efectos y el porqué, que el código no dice por sí solo.
