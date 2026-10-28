# Evidencia de SPRINT-007 — criterios de aceptación ↔ tests

Generado el 2026-09-30 por `control/tools/evidence.py` a partir de `pytest --junitxml` (275 casos) y de las secciones *Pruebas* de `01_PRODUCTO/refinements/`.
Instantánea: se regenera al cerrar el sprint.

## US-06.06

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Pulsar una tarjeta del Kanban abre la ficha de su historia. (definido en refinamiento) | `test_webui::test_us0606_ca01_ca02_ca03_abrir_tarjeta_con_contexto` | PASS |
| CA-02 | La ficha muestra enunciado, criterios, requisitos, épica, feature y estado. (definido en refinamiento) | `test_webui::test_us0606_ca01_ca02_ca03_abrir_tarjeta_con_contexto` | PASS |
| CA-03 | Desde la ficha se puede generar el contexto compacto con su estimación de ahorro. (definido en refinamiento) | `test_webui::test_us0606_ca01_ca02_ca03_abrir_tarjeta_con_contexto` | PASS |

## US-06.07

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | El operador elige qué proyectos aparecen en el tablero: uno o varios. | `test_webui::test_us0607_ca01_elegir_proyectos` | PASS |
| CA-02 | Cada tarjeta indica a qué proyecto pertenece con su color y su nombre. | `test_webui::test_us0607_ca02_color_y_nombre_del_proyecto` | PASS |
| CA-03 | Los proyectos pueden verse mezclados o en un carril por proyecto. | `test_webui::test_us0607_ca03_mezclados_o_por_carril` | PASS |
| CA-04 | Una tarjeta se puede mover a otro estado permitido arrastrándola o con teclado; un movimiento no permitido se rechaza con un mensaje. | `test_webui::test_us0607_ca04_arrastrar_permitido_y_rechazo`<br>`test_webui::test_us3107_ca04_mover_con_teclado` | PASS |

## US-21.09

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | El feed muestra el nombre de la herramienta invocada y el proyecto sobre el que actúa. (definido en refinamiento) | `test_webui::test_us3104_us2109_feed_en_vivo_de_herramientas` | PASS |

## US-31.01

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Se muestran eventos relevantes. | `test_webui::test_us3101_us3102_consola_filtrable`<br>`test_webui::test_us3104_us2109_feed_en_vivo_de_herramientas` | PASS |
| CA-02 | Los eventos incluyen timestamp. | `test_webui::test_us3101_us3102_consola_filtrable` | PASS |
| CA-03 | Pueden filtrarse por proyecto/agente. | `test_webui::test_us3101_us3102_consola_filtrable` | PASS |
| CA-04 | Un error aparece claramente diferenciado. | `test_webui::test_us3101_us3102_consola_filtrable`<br>`test_webui::test_us3104_us2109_feed_en_vivo_de_herramientas` | PASS |

## US-31.02

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | El filtro se aplica al conjunto de eventos. | `test_webui::test_us3101_us3102_consola_filtrable` | PASS |
| CA-02 | Los resultados coinciden con los filtros. | `test_webui::test_us3101_us3102_consola_filtrable` | PASS |
| CA-03 | Limpiar filtros restaura la vista completa. | `test_webui::test_us3101_us3102_consola_filtrable` | PASS |

## US-31.04

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Cada invocación de un agente aparece en el feed sin recargar. (definido en refinamiento) | `test_webui::test_us3104_us2109_feed_en_vivo_de_herramientas` | PASS |
| CA-02 | Una invocación fallida se distingue visualmente y con texto. (definido en refinamiento) | `test_webui::test_us3104_us2109_feed_en_vivo_de_herramientas` | PASS |

## US-31.06

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Cada tipo de dato que ACM guarda de un proyecto (requisitos, épicas, features, historias, criterios de aceptación, trazabilidad, estados e historial, gobernanza, miembros y configuración) tiene una vista en la interfaz. | `test_webui::test_us3106_ca01_cada_dato_tiene_vista` | PASS |
| CA-02 | Desde una historia se puede navegar a su épica, feature, requisitos y criterios. | `test_webui::test_us3106_ca02_navegar_desde_una_historia` | PASS |
| CA-03 | La documentación de ACM (skills, flujo de estados y referencia de la API) se puede consultar en la interfaz. | `test_webui::test_us3106_ca03_documentacion_de_acm` | PASS |
| CA-04 | Solo se muestran los proyectos y datos a los que el usuario tiene acceso. | `test_webui::test_us3106_ca04_solo_lo_accesible` | PASS |

## US-31.07

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Todo texto tiene un contraste mínimo de 4.5:1 sobre su fondo (WCAG 2.1 AA), en tema claro y en tema oscuro. | `test_webui::test_us3107_ca01_contraste_aa_en_ambos_temas` | PASS |
| CA-02 | El estado nunca se comunica solo con color: siempre va acompañado de texto o de un símbolo. | `test_webui::test_us3107_ca02_nunca_solo_color` | PASS |
| CA-03 | El usuario puede elegir tema claro, oscuro o el del sistema. | `test_webui::test_us3107_ca03_elegir_tema` | PASS |
| CA-04 | Las acciones de la interfaz pueden realizarse con teclado. | `test_webui::test_us3107_ca04_mover_con_teclado` | PASS |

## US-31.08

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Un cambio hecho por un agente aparece en la interfaz sin recargar la página. | `test_webui::test_us3108_ca01_cambio_de_agente_sin_recargar` | PASS |
| CA-02 | La interfaz indica si está conectada en tiempo real. | `test_webui::test_us3108_ca02_indicador_de_conexion` | PASS |
| CA-03 | Tras perder la conexión, la interfaz se reconecta y recupera los cambios ocurridos mientras tanto. | `test_webui::test_us3108_ca03_reconexion_recupera_los_cambios` | PASS |

## US-45.02

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Cada elemento navegable abre su detalle. | `test_webui::test_us4502_acceder_a_elementos_desde_el_panel` | PASS |
| CA-02 | Se conserva el contexto del proyecto. | `test_webui::test_us4502_acceder_a_elementos_desde_el_panel` | PASS |
| CA-03 | Un elemento inexistente muestra error controlado. | `test_webui::test_us4502_acceder_a_elementos_desde_el_panel` | PASS |

## US-45.03

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | El panel muestra cada proyecto accesible con su semáforo de gobernanza y su reparto de estados. (definido en refinamiento) | `test_webui::test_us4503_panel_global_de_varios_proyectos` | PASS |
| CA-02 | Los cambios de cualquier proyecto aparecen en el panel en tiempo real. (definido en refinamiento) | `test_webui::test_us4503_panel_global_de_varios_proyectos` | PASS |
| CA-03 | Desde el panel se abre el Kanban de todos los proyectos. (definido en refinamiento) | `test_webui::test_us4503_panel_global_de_varios_proyectos` | PASS |

# Anexo — historia de un sprint anterior cerrada en SPRINT-007

## US-01.02 (SPRINT-001)

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Solo aparecen proyectos a los que el usuario tiene acceso. | `test_projects::test_us0102_ca01_listado_solo_proyectos_con_acceso` | PASS |
| CA-02 | Al seleccionar un proyecto se carga su contexto. | `test_projects::test_us0102_ca02_abrir_carga_contexto` | PASS |
| CA-03 | El proyecto activo queda identificado visualmente. | `test_webui::test_us0102_ca03_proyecto_activo_identificado` | PASS |
| CA-04 | Si el proyecto ya no existe, se informa del error y se limpia la selección. | `test_projects::test_us0102_ca04_proyecto_inexistente_o_sin_base`<br>`test_webui::test_us0102_ca04_proyecto_inexistente_informa_y_no_queda_seleccionado` | PASS |
| CA-05 | Cambiar de proyecto no mezcla datos del proyecto anterior con el nuevo. | `test_projects::test_us0102_ca05_cambiar_de_proyecto_no_mezcla_datos` | PASS |
| — | regla de no revelar | `test_projects::test_us0102_no_miembro_recibe_not_found` | PASS |
