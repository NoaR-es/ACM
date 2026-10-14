# Evidencia de SPRINT-001 — criterios de aceptación ↔ tests

Generado el 2026-09-30 a partir de `pytest --junitxml` (50 tests) y de las secciones *Pruebas* de `01_PRODUCTO/refinements/`.
Instantánea: se regenera al cerrar el sprint. Comando: `.venv/bin/pytest -q`.

## US-01.01

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Dado un usuario autorizado, cuando introduce datos válidos y confirma, entonces se crea exactamente un proyecto. | `test_projects::test_us0101_ca01_crea_exactamente_un_proyecto`<br>`test_projects::test_us0101_ca05_proyecto_creado_se_abre_desde_listado`<br>`test_projects::test_us0101_contexto_fisico_creado` | PASS |
| CA-02 | Si el nombre obligatorio está vacío, entonces el sistema impide la creación e identifica el campo. | `test_projects::test_us0101_ca02_nombre_vacio_rechazado_identifica_campo` | PASS |
| CA-03 | Si ya existe un proyecto con el identificador correspondiente, entonces no se crea un duplicado. | `test_projects::test_us0101_ca03_duplicado_no_se_crea`<br>`test_projects::test_us0101_ca03_creacion_concurrente_mismo_key` | PASS |
| CA-04 | Si falla el almacenamiento, entonces el proyecto no queda registrado parcialmente y se muestra un error recuperable. | `test_projects::test_us0101_ca04_fallo_de_almacenamiento_no_deja_registro_parcial` | PASS |
| CA-05 | Tras una creación correcta, el proyecto puede abrirse desde el listado. | `test_projects::test_us0101_ca05_proyecto_creado_se_abre_desde_listado` | PASS |
| CA-01.04-01 | El sistema permite introducir nombre e identificador. (de B:US-01.01, fusionada) | `test_projects::test_us0101_ca01_crea_exactamente_un_proyecto` | PASS |
| CA-01.04-02 | Se crea el contexto físico del proyecto. (de B:US-01.01, fusionada) | `test_projects::test_us0101_contexto_fisico_creado` | PASS |
| CA-01.04-03 | Se crea su base SQLite. (de B:US-01.01, fusionada) | `test_projects::test_us0101_ca01_crea_exactamente_un_proyecto` | PASS |
| CA-01.04-04 | El proyecto queda disponible para consulta. (de B:US-01.01, fusionada) | `test_projects::test_us0101_ca05_proyecto_creado_se_abre_desde_listado` | PASS |
| — | precondición | `test_projects::test_us0101_no_admin_no_puede_crear` | PASS |
| — | frontera MCP, GAP-007 | `test_mcp::test_us0101_mcp_create_y_errores_explicitos` | PASS |

## US-01.02

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Solo aparecen proyectos a los que el usuario tiene acceso. | `test_projects::test_us0102_ca01_listado_solo_proyectos_con_acceso` | PASS |
| CA-02 | Al seleccionar un proyecto se carga su contexto. | `test_projects::test_us0102_ca02_abrir_carga_contexto` | PASS |
| CA-03 | El proyecto activo queda identificado visualmente. | — | PENDIENTE (sin test en SPRINT-001) |
| CA-04 | Si el proyecto ya no existe, se informa del error y se limpia la selección. | `test_projects::test_us0102_ca04_proyecto_inexistente_o_sin_base` | PASS |
| CA-05 | Cambiar de proyecto no mezcla datos del proyecto anterior con el nuevo. | `test_projects::test_us0102_ca05_cambiar_de_proyecto_no_mezcla_datos` | PASS |
| — | regla de no revelar | `test_projects::test_us0102_no_miembro_recibe_not_found` | PASS |

> **US-01.02:** CA-03 y la parte "se limpia la selección" de CA-04 dependen de la interfaz web (TASK-000-07); el test de CA-04 cubre solo la parte del servidor. Por eso la historia queda IMPLEMENTED, no VERIFIED.

## US-01.03

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Los parámetros modificables se muestran con su valor actual. | `test_projects::test_us0103_ca01_parametros_con_valor_actual` | PASS |
| CA-02 | Los valores inválidos son rechazados antes de guardar. | `test_projects::test_us0103_ca02_invalidos_rechazados_sin_guardar` | PASS |
| CA-03 | Una configuración válida queda persistida. | `test_projects::test_us0103_ca03_configuracion_persistida` | PASS |
| CA-04 | Los cambios que requieran reinicio o recarga quedan identificados. | `test_projects::test_us0103_ca04_cambios_que_requieren_recarga` | PASS |
| CA-05 | La configuración pertenece exclusivamente al proyecto seleccionado. | `test_projects::test_us0103_ca05_configuracion_exclusiva_del_proyecto` | PASS |
| — | precondición | `test_projects::test_us0103_member_no_puede_modificar` | PASS |

## US-01.06

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Toda herramienta MCP que opera sobre un proyecto exige el parámetro `project_id`; sin él, la llamada se rechaza antes de ejecutar nada. (definido en refinamiento) | `test_mcp::test_us0106_ca01_herramientas_de_proyecto_exigen_project_id` | PASS |
| CA-02 | Toda respuesta de una herramienta de proyecto incluye el `project_id` sobre el que actuó. (definido en refinamiento) | `test_mcp::test_us0106_ca02_respuestas_incluyen_project_id` | PASS |
| CA-03 | Un `project_id` inexistente o no accesible produce un error explícito (`NOT_FOUND`) con el motivo legible por el agente, y no modifica ningún proyecto. (definido en refinamiento) | `test_mcp::test_us0106_ca03_project_id_desconocido_error_explicito` | PASS |
| CA-04 | Las `instructions` del servidor MCP indican al agente que debe pasar `project_id` en cada llamada y cómo obtenerlo (`acm_project_list`). (definido en refinamiento) | `test_mcp::test_us0106_ca04_instructions_explican_project_id` | PASS |

## US-18.01

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | El estado relevante queda almacenado. | `test_db::test_us1801_ca01_estado_relevante_almacenado` | PASS |
| CA-02 | Un reinicio no elimina información persistente. | `test_db::test_us1801_ca02_ca03_reinicio_reconstruye_desde_sqlite` | PASS |
| CA-03 | El proyecto puede reconstruirse desde la persistencia. | `test_db::test_us1801_ca02_ca03_reinicio_reconstruye_desde_sqlite` | PASS |
| CA-04 | Una escritura fallida no deja datos inconsistentes. | `test_db::test_us1801_ca04_escritura_fallida_no_deja_inconsistencias` | PASS |
| — | caso límite | `test_db::test_us1801_transaccion_no_confirmada_desaparece_si_el_proceso_muere` | PASS |
| — | reglas | `test_db::test_pragmas_adr013_activos` | PASS |

## US-18.02

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Una operación completamente válida se confirma. | `test_db::test_us1802_ca01_operacion_valida_se_confirma` | PASS |
| CA-02 | Un fallo durante la transacción revierte los cambios afectados. | `test_db::test_us1802_ca02_ca03_fallo_revierte_todo` | PASS |
| CA-03 | No quedan registros parcialmente creados. | `test_db::test_us1802_ca02_ca03_fallo_revierte_todo` | PASS |
| — | regla | `test_db::test_us1802_anidamiento_detectado` | PASS |
| — | caso límite | `test_db::test_us1802_escritores_concurrentes_sin_perdidas` | PASS |
| — | errores | `test_db::test_us1802_reintento_ante_bloqueo_transitorio` | PASS |

## US-18.03

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Cada migración tiene versión. | `test_migrations::test_us1803_ca01_cada_migracion_tiene_version` | PASS |
| CA-02 | Las migraciones se ejecutan en orden. | `test_migrations::test_us1803_ca02_se_ejecutan_en_orden` | PASS |
| CA-03 | Una migración fallida no deja el esquema marcado como completado. | `test_migrations::test_us1803_ca03_migracion_fallida_no_queda_marcada` | PASS |
| CA-04 | La versión actual puede consultarse. | `test_migrations::test_us1803_ca04_version_actual_consultable` | PASS |
| — | validaciones | `test_migrations::test_us1803_catalogo_invalido_rechazado` | PASS |
| — | errores | `test_migrations::test_us1803_base_de_version_futura_rechazada` | PASS |
| — | caso límite | `test_migrations::test_us1803_migracion_concurrente_una_sola_vez` | PASS |

## Resumen

| Historia | Todos los CA con test en PASS | CA pendientes |
|----------|------------------------------|---------------|
| US-01.01 | sí | — |
| US-01.02 | no | CA-03 |
| US-01.03 | sí | — |
| US-01.06 | sí | — |
| US-18.01 | sí | — |
| US-18.02 | sí | — |
| US-18.03 | sí | — |
