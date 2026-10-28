# Evidencia de SPRINT-009 — criterios de aceptación ↔ tests

Generado el 2026-10-28 por `control/tools/evidence.py` a partir de `pytest --junitxml` (431 casos) y de las secciones *Pruebas* de `01_PRODUCTO/refinements/`.
Instantánea: se regenera al cerrar el sprint.

## US-14.12

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Existe una entrada stdio estándar (`command` + `args`) que arranca ACM sin pasos previos ni tokens. | `test_local_mode::test_us1412_ca01_flujo_completo_sin_pasos_previos`<br>`test_app::test_modo_stdio_del_cli` | PASS |
| CA-02 | Todos los agentes conectados comparten un único estado por usuario (`~/.acm` salvo `ACM_DATA_DIR`), sea cual sea la carpeta desde la que se abran. | `test_local_mode::test_us1412_ca02_un_unico_estado_por_usuario` | PASS |
| CA-03 | Cada agente queda identificado por el nombre que declara su cliente MCP (o `ACM_AGENT`) y todo lo que hace se le atribuye. | `test_local_mode::test_us1412_ca03_identidad_valida_y_distinta_por_cliente_y_equipo`<br>`test_local_mode::test_us1412_ca03_cada_cliente_es_un_agente_con_su_nombre`<br>`test_local_mode::test_us1412_ca03_dos_sesiones_del_mismo_cliente_no_se_pisan`<br>`test_local_mode::test_us1412_ca03_acm_principal_conserva_la_identidad_admin_unica` | PASS |
| CA-04 | Mientras haya un agente conectado, la interfaz web y el supervisor funcionan sin arrancar nada más; la interfaz local no pide token. | `test_local_mode::test_us1412_ca04_solo_peticiones_locales_con_la_cabecera_de_la_interfaz`<br>`test_local_mode::test_us1412_ca04_interfaz_local_en_segundo_plano_sin_token`<br>`test_local_mode::test_us1412_ca04_la_interfaz_sobrevive_y_se_para_con_acm_stop`<br>`test_local_mode::test_us1412_ca04_el_supervisor_trabaja_en_segundo_plano`<br>`test_webui_agents::test_us1412_ca04_la_interfaz_local_entra_sola`<br>`test_webui_agents::test_us1412_ca04_con_tokens_sigue_pidiendolos` | PASS |

## US-14.13

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Las `instructions` de inicialización son breves e indican cómo obtener el proceso de trabajo. | `test_skills::test_us1413_ca01_instructions_breves_y_remiten_al_proceso` | PASS |
| CA-02 | Las skills se pueden obtener por herramientas, recursos, prompts MCP y la extensión de skills, todas con el mismo contenido. | `test_skills::test_us1413_ca02_mismo_contenido_por_herramienta_recurso_y_prompt`<br>`test_skills::test_us1413_ca02_leer_las_skills_queda_auditado`<br>`test_skills::test_us1505_ca02_skills_get_y_error` | PASS |
| CA-03 | Existe una skill que describe el proceso de trabajo con ACM de principio a fin (elegir proyecto, pedir trabajo, registrarlo, auditar). | `test_skills::test_us1413_ca03_acm_workflow_describe_el_proceso_de_principio_a_fin`<br>`test_skills::test_us1413_ca03_acm_workflow_solo_cita_herramientas_existentes`<br>`test_skills::test_us1413_ca03_pasos_de_acm_next_work_existen` | PASS |

## US-14.14

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | El agente ve los proyectos existentes, indicando en cuáles es miembro y en cuáles tiene una petición pendiente. | `test_access::test_us1414_ca01_directorio_con_rol_y_peticiones`<br>`test_access::test_us1414_ca01_fuera_del_modo_local_solo_ve_los_suyos` | PASS |
| CA-02 | Crear un proyecto nuevo no requiere aprobación y el agente queda como su owner. | `test_access::test_us1414_ca02_crear_proyecto_nuevo_sin_aprobacion` | PASS |
| CA-03 | Pedir unirse a un proyecto crea una petición pendiente; hasta su aprobación el agente no accede a nada del proyecto. | `test_access::test_us1414_ca03_pedir_unirse_deja_pendiente_y_sin_acceso`<br>`test_access::test_us1414_ca03_entradas_invalidas`<br>`test_access::test_us1414_flujo_del_agente_por_mcp` | PASS |
| CA-04 | El agente puede consultar el estado de su petición. | `test_access::test_us1414_ca04_consultar_el_estado_de_la_peticion` | PASS |

## US-14.15

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Las peticiones pendientes aparecen en la interfaz en tiempo real. | `test_access::test_us1415_ca01_las_peticiones_pendientes_llegan_en_tiempo_real`<br>`test_webui_agents::test_us1415_ca01_ca02_ca03_aprobar_y_rechazar_en_tiempo_real` | PASS |
| CA-02 | Al aprobar elijo si el agente tiene acceso de lectura o de escritura. | `test_access::test_us1415_ca02_aprobar_con_escritura_o_solo_lectura`<br>`test_access::test_us1415_ca02_rol_invalido_y_peticion_ya_decidida`<br>`test_webui_agents::test_us1415_ca01_ca02_ca03_aprobar_y_rechazar_en_tiempo_real`<br>`test_access::test_us1415_solo_una_persona_decide_y_solo_la_de_su_proyecto` | PASS |
| CA-03 | Al rechazar, el agente lo sabe al consultar su petición. | `test_access::test_us1415_ca03_rechazar_y_el_agente_lo_sabe`<br>`test_webui_agents::test_us1415_ca01_ca02_ca03_aprobar_y_rechazar_en_tiempo_real` | PASS |
| CA-04 | Puedo retirar a un agente de un proyecto en cualquier momento. | `test_access::test_us1415_ca04_retirar_a_un_agente_en_cualquier_momento`<br>`test_webui_agents::test_us1415_ca04_expulsar_a_un_agente_desde_miembros` | PASS |

## US-14.16

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | ACM responde el siguiente trabajo según el sprint y el estado del backlog (refinar, implementar, verificar, planificar), con su motivo. | `test_work::test_us1416_ca01_responde_lo_que_toca_segun_el_estado`<br>`test_work::test_us1416_ca01_avanza_con_el_estado_de_la_historia`<br>`test_work::test_us1416_ca01_sprint_planificado_sin_iniciar`<br>`test_work::test_us1416_acceso_de_solo_lectura_no_recibe_trabajo`<br>`test_work::test_us1416_flujo_del_agente_por_mcp` | PASS |
| CA-02 | El trabajo de una historia queda asignado al agente que lo recibe; otro agente no lo recibe mientras siga asignado. | `test_work::test_us1416_ca02_dos_agentes_nunca_reciben_lo_mismo`<br>`test_work::test_us1416_ca02_sin_trabajo_libre_espera`<br>`test_work::test_us1416_ca02_consultar_sin_asignar`<br>`test_local_mode::test_us1412_ca03_dos_sesiones_del_mismo_cliente_no_se_pisan` | PASS |
| CA-03 | Los cambios de estado de una historia asignada a otro agente se rechazan explicando a quién está asignada. | `test_work::test_us1416_ca03_historia_asignada_a_otro_no_se_cambia` | PASS |

## US-14.17

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Cada asignación caduca si el agente no la renueva en un plazo configurable. | `test_work::test_us1417_ca01_la_asignacion_se_renueva_al_tocar_la_historia`<br>`test_work::test_us1417_ca01_caducada_queda_libre_para_otro`<br>`test_work::test_us1417_ca01_plazo_configurable` | PASS |
| CA-02 | El agente puede liberar su trabajo al terminarlo o abandonarlo. | `test_work::test_us1417_ca02_liberar_el_trabajo`<br>`test_work::test_us1417_ca02_pedir_otra_cosa_libera_lo_que_ya_no_corresponde` | PASS |
| CA-03 | El Kanban muestra a qué agente está asignada cada historia. | `test_work::test_us1417_ca03_se_ve_quien_trabaja_en_que`<br>`test_work::test_us1417_ca03_mismo_cliente_en_dos_sesiones_no_se_pisa`<br>`test_webui_agents::test_us1417_ca03_el_kanban_muestra_el_agente_asignado` | PASS |
