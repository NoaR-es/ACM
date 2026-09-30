# 05_CODIGO — Código

**Responde a:** Dónde está implementado y cómo está organizado el código.

**Salud:** OK — 75 archivos de código, todos con fila en `file_inventory.md` y cabecera; `code_inventory.py --check` en la CI lo exige (SPRINT-007).

## Cómo mantenerlo
Archivo nuevo → fila en `file_inventory.md` + cabecera + `python3 control/tools/code_inventory.py`. Qué más actualizar según el cambio: `file_documentation.md`.

| Documento | Contenido | Estado |
|-----------|-----------|--------|
| `source_tree.md` | Árbol del repositorio (backend, frontend, tests, herramientas) | ACTIVE |
| `file_inventory.md` | Cada archivo de código: propósito, historias, tests (medidos) | ACTIVE (verificado por CI) |
| `code_reference.md` | Símbolos públicos, herramientas MCP y rutas REST por archivo | GENERADO (verificado por CI) |
| `file_documentation.md` | Convenciones de documentación y qué documento tocar según el cambio | ACTIVE |
| `modules.md` | Módulos backend: responsabilidad, entradas, efectos, invariantes | ACTIVE |
| `services.md` | Servicios de dominio: operaciones, permisos, eventos | ACTIVE |
| `classes.md` | Clases y protocolos del backend | ACTIVE |
| `functions.md` | Funciones relevantes (backend y frontend) | ACTIVE |
| `utilities.md` | Herramientas de control y módulos puros del frontend | ACTIVE |
| `frontend.md` | Arquitectura de `web/`: proveedores, datos, tiempo real, tema, build, seguridad | ACTIVE |
| `components.md` | Páginas y componentes React | ACTIVE |
| `hooks.md` | Hooks y proveedores React | ACTIVE |
| `types.md` | Tipos TS ↔ API REST ↔ Python | ACTIVE |
| `tests.md` | Código de tests: convenciones, fixtures, dobles, ejecución | ACTIVE |
| `dependencies.md` | Paquetes Python y npm fijados y para qué | ACTIVE |
| `dead_code.md` | Revisión de código muerto | ACTIVE (ninguno) |

Relacionados: arquitectura `../04_ARQUITECTURA/`, API `../06_API/`, estrategia y resultados de tests `../12_TESTING/`.
Documentos históricos: ninguno (ver `../99_ARCHIVO/`). Relaciones: `../RELATIONSHIPS.md`.
