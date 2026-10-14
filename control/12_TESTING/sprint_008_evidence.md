# Evidencia de SPRINT-008 — criterios de aceptación ↔ tests

Generado el 2026-10-06 por `control/tools/evidence.py` a partir de `pytest --junitxml` (381 casos) y de las secciones *Pruebas* de `01_PRODUCTO/refinements/`.
Instantánea: se regenera al cerrar el sprint.

## US-04.10

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | El supervisor señala las historias demasiado grandes o con criterios no verificables, con el motor que lo decidió. (definido en refinamiento) | `test_supervisor::test_us0410_ca01_historia_grande_o_no_testeable` | PASS |

## US-04.14

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Cada historia viva se evalúa según INVEST a través de la interfaz de decisión y las que no lo cumplen se señalan. (definido en refinamiento) | `test_supervisor::test_us0414_ca01_evalua_invest` | PASS |

## US-04.15

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | El supervisor identifica las historias con criterios vagos o no verificables. (definido en refinamiento) | `test_supervisor::test_us0415_ca01_criterios_vagos` | PASS |

## US-05.02

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | El sprint tiene identificador y objetivo. | `test_sprints::test_us0502_ca01_identificador_y_objetivo`<br>`test_sprints::test_us0502_sprints_por_mcp_con_eventos`<br>`test_webui_ops::test_us0502_us0505_us0509_us0503_sprint_completo` | PASS |
| CA-02 | Las historias asignadas quedan vinculadas al sprint. | `test_sprints::test_us0502_ca02_historias_vinculadas`<br>`test_sprints::test_us0502_sprints_por_mcp_con_eventos`<br>`test_webui_ops::test_us0502_us0505_us0509_us0503_sprint_completo` | PASS |
| CA-03 | El sistema detecta dependencias incompatibles. | — | PENDIENTE — sin modelo de dependencias entre historias (ver Reglas). |
| CA-04 | El sprint puede pasar por estados definidos. | `test_sprints::test_us0502_ca04_estados_definidos`<br>`test_webui_ops::test_us0502_us0505_us0509_us0503_sprint_completo` | PASS |
| — | regla: un sprint activo | `test_sprints::test_us0502_un_solo_sprint_activo` | PASS |

## US-05.03

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | El sistema identifica historias terminadas y no terminadas. | `test_sprints::test_us0503_ca01_terminadas_y_no_terminadas` | PASS |
| CA-02 | Las historias no terminadas pueden trasladarse. | `test_sprints::test_us0503_ca02_trasladar_no_terminadas`<br>`test_sprints::test_us0503_ca02_sin_destino_vuelven_al_backlog` | PASS |
| CA-03 | Se genera un resumen del sprint. | `test_sprints::test_us0503_ca03_resumen_del_sprint` | PASS |
| CA-04 | El historial del sprint queda conservado. | `test_sprints::test_us0503_ca04_historial_conservado` | PASS |

## US-05.04

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Un sprint guarda nombre, objetivo, fecha de inicio, fecha de fin y, opcionalmente, su capacidad en historias. (definido en refinamiento) | `test_sprints::test_us0504_ca01_objetivo_fechas_y_capacidad` | PASS |
| CA-02 | Una fecha inválida o un fin anterior al inicio se rechazan indicando el campo. (definido en refinamiento) | `test_sprints::test_us0504_ca02_fechas_invalidas` | PASS |
| CA-03 | Una capacidad que no sea un entero entre 1 y 1000 se rechaza. (definido en refinamiento) | `test_sprints::test_us0504_ca03_capacidad_fuera_de_rango` | PASS |

## US-05.05

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Las historias elegidas quedan planificadas en el sprint. (definido en refinamiento) | `test_sprints::test_us0505_ca01_ca05_asignar_y_retirar` | PASS |
| CA-02 | Una historia solo puede estar en un sprint abierto a la vez. (definido en refinamiento) | `test_sprints::test_us0505_ca02_una_historia_un_sprint_abierto` | PASS |
| CA-03 | Una historia DONE, CANCELLED o DEPRECATED no se puede planificar. (definido en refinamiento) | `test_sprints::test_us0505_ca03_terminales_rechazadas` | PASS |
| CA-04 | Planificar una historia que no está READY se permite con un aviso. (definido en refinamiento) | `test_sprints::test_us0505_ca04_aviso_si_no_esta_ready` | PASS |
| CA-05 | Una historia se puede retirar de un sprint abierto y queda en su historial. (definido en refinamiento) | `test_sprints::test_us0505_ca01_ca05_asignar_y_retirar` | PASS |
| CA-06 | El tablero Kanban puede mostrar solo las historias de un sprint. (definido en refinamiento) | `test_rest_write::test_us0505_ca06_sprints_y_kanban_del_sprint` | PASS |

## US-05.06

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | El cierre guarda las métricas del sprint (historias, terminadas, porcentaje, reparto por estado). (definido en refinamiento) | `test_sprints::test_us0506_ca01_ca02_metricas_conservadas` | PASS |
| CA-02 | Esas métricas no cambian aunque las historias cambien después. (definido en refinamiento) | `test_sprints::test_us0506_ca01_ca02_metricas_conservadas` | PASS |

## US-05.07

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | La capacidad del sprint se registra y se muestra junto a su carga. (definido en refinamiento) | `test_sprints::test_us0507_us0508_capacidad_y_carga` | PASS |

## US-05.08

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | El sprint informa de su carga (historias planificadas) y de si supera la capacidad. (definido en refinamiento) | `test_sprints::test_us0507_us0508_capacidad_y_carga` | PASS |
| CA-02 | Al superar la capacidad se avisa al planificar. (definido en refinamiento) | `test_sprints::test_us0507_us0508_capacidad_y_carga` | PASS |

## US-05.09

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Un sprint sobrecargado no se inicia y se explica por qué. (definido en refinamiento) | `test_sprints::test_us0509_ca01_ca02_sobrecarga_detectada_antes_de_iniciar`<br>`test_webui_ops::test_us0502_us0505_us0509_us0503_sprint_completo` | PASS |
| CA-02 | El Scrum Master puede iniciarlo igualmente de forma explícita. (definido en refinamiento) | `test_sprints::test_us0509_ca01_ca02_sobrecarga_detectada_antes_de_iniciar`<br>`test_webui_ops::test_us0502_us0505_us0509_us0503_sprint_completo` | PASS |

## US-13.14

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | El supervisor revisa, a demanda y periódicamente, las historias, sus criterios, los sprints y el Kanban de cada proyecto. | `test_supervisor::test_us1314_ca01_revisa_historias_sprints_y_kanban` | PASS |
| CA-02 | Las decisiones de juicio (calidad INVEST, criterios verificables, tamaño de historia, riesgo del sprint) se delegan en la interfaz de decisión común; cada hallazgo indica qué motor lo produjo y si es calibrado. | `test_supervisor::test_us1314_ca02_juicio_delegado_con_motor_y_calibracion` | PASS |
| CA-03 | Una historia que no ha cambiado no se vuelve a evaluar: se reutiliza su última revisión. | `test_supervisor::test_us1314_ca03_no_repite_revisiones_sin_cambios` | PASS |
| CA-04 | Cada revisión genera un informe con lo hecho, lo pendiente, las incongruencias y las acciones; si hay un modelo local lo redacta en lenguaje natural y, si no, ACM lo compone sin modelo. | `test_supervisor::test_us1314_ca04_informe_con_modelo_local`<br>`test_supervisor::test_us1314_ca04_informe_sin_modelo` | PASS |
| CA-05 | El informe, los hallazgos y las acciones se ven en la interfaz en tiempo real. | `test_webui_ops::test_us1314_ca05_us1315_ca03_informe_acciones_y_deshacer` | PASS |

## US-13.15

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Solo se aplican acciones de una lista cerrada de cambios reversibles; nunca se marca DONE, ni se cancela ni se borra nada. | `test_supervisor::test_us1315_ca01_solo_acciones_seguras`<br>`test_supervisor::test_us1315_devuelve_a_planned_y_saca_canceladas` | PASS |
| CA-02 | Una acción solo se aplica si la decide un motor calibrado (reglas o JEV) con una confianza igual o superior al umbral del proyecto; si no, queda como propuesta. | `test_supervisor::test_us1315_ca02_calibrado_y_umbral` | PASS |
| CA-03 | Cada acción aplicada queda auditada con su motivo, motor y confianza, figura como hecha por el agente `acm-supervisor` y se puede deshacer. | `test_supervisor::test_us1315_ca03_auditada_como_supervisor_y_reversible`<br>`test_webui_ops::test_us1314_ca05_us1315_ca03_informe_acciones_y_deshacer` | PASS |
| CA-04 | El modo del supervisor se configura por proyecto: apagado, solo proponer o aplicar cambios seguros. | `test_supervisor::test_us1315_ca04_modos_apagado_proponer_aplicar` | PASS |

## US-22.04

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Con la URL de Ollama, ACM registra su motor de generación y su motor de decisión. (definido en refinamiento) | `test_second_brain::test_us2204_ca01_registra_generacion_y_decision` | PASS |
| CA-02 | Las decisiones de Ollama solo pueden elegir entre las opciones dadas y se marcan como no calibradas. (definido en refinamiento) | `test_second_brain::test_us2204_ca02_solo_elige_entre_las_opciones` | PASS |
| CA-03 | Un gate (READY) no acepta decisiones de Ollama. (definido en refinamiento) | `test_second_brain::test_us2204_ca03_el_gate_no_acepta_a_ollama` | PASS |
| CA-04 | Una respuesta fuera de las opciones es un error. (definido en refinamiento) | `test_second_brain::test_us2204_ca04_respuesta_fuera_de_opciones_es_error` | PASS |

## US-22.06

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | El operador asigna un modelo de Ollaya a un propósito y uno por defecto, y un modelo de Ollama para lo generativo. (definido en refinamiento) | `test_models_chat::test_us2206_us2207_modelo_segun_el_proposito`<br>`test_models_chat::test_us5009_ca02_elegir_uno_de_ollama_y_varios_de_ollaya` | PASS |

## US-22.07

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Una decisión usa el modelo de Ollaya asignado a su propósito o, si no hay, el de por defecto, sin que el consumidor lo indique. (definido en refinamiento) | `test_models_chat::test_us2206_us2207_modelo_segun_el_proposito` | PASS |

## US-22.10

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | El agente envía un mensaje y recibe la respuesta del modelo Ollama seleccionado junto con el identificador del hilo. | `test_models_chat::test_us2210_ca01_ca02_hilo_con_contexto`<br>`test_models_chat::test_us2210_por_mcp`<br>`test_webui_ops::test_us2210_us2211_asistente_del_proyecto` | PASS |
| CA-02 | En los siguientes mensajes del mismo hilo ACM añade la conversación anterior; el agente solo envía el mensaje nuevo. | `test_models_chat::test_us2210_ca01_ca02_hilo_con_contexto`<br>`test_webui_ops::test_us2210_us2211_asistente_del_proyecto` | PASS |
| CA-03 | Cada hilo pertenece a un proyecto y a quien lo abrió; solo él o un administrador pueden leerlo. | `test_models_chat::test_us2210_ca03_hilo_privado` | PASS |
| CA-04 | El hilo conserva cada mensaje con su autor, fecha y modelo, y se puede consultar después. | `test_models_chat::test_us2210_ca04_mensajes_conservados`<br>`test_models_chat::test_us2210_por_mcp` | PASS |
| CA-05 | Sin modelo Ollama configurado o seleccionado, la respuesta es un error explícito, nunca una respuesta inventada. | `test_models_chat::test_us2210_ca05_sin_modelo_error_explicito` | PASS |

## US-22.11

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | El modelo local recibe herramientas de solo lectura de ACM (backlog, historias, sprints, gobernanza, contexto compacto y búsqueda) y unas instrucciones que explican el modelo de ACM y cómo usarlas. | `test_models_chat::test_us2211_ca01_ca02_consulta_el_proyecto_con_herramientas` | PASS |
| CA-02 | ACM ejecuta las herramientas que el modelo pide con los permisos de quien abrió el hilo y le devuelve el resultado; nunca le da herramientas de escritura. | `test_models_chat::test_us2211_ca01_ca02_consulta_el_proyecto_con_herramientas`<br>`test_models_chat::test_us2211_ca02_permisos_de_quien_pregunta` | PASS |
| CA-03 | La respuesta indica qué herramientas se usaron, y cada llamada queda en el hilo. | `test_models_chat::test_us2211_ca03_herramientas_en_el_hilo`<br>`test_webui_ops::test_us2210_us2211_asistente_del_proyecto` | PASS |
| CA-04 | El número de rondas de herramientas por mensaje está limitado. | `test_models_chat::test_us2211_ca04_rondas_limitadas` | PASS |

## US-31.09

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Un administrador crea un proyecto desde el panel indicando clave, nombre y descripción; una clave inválida o repetida se rechaza con el motivo. | `test_rest_write::test_us3109_ca01_crear_proyecto_y_errores`<br>`test_webui_ops::test_us3109_ca01_crear_proyecto_desde_el_panel` | PASS |
| CA-02 | Los parámetros de configuración se editan con controles adecuados a su tipo y un valor inválido se rechaza sin guardar ningún cambio. | `test_rest_write::test_us3109_ca02_configuracion_valida_todo_antes_de_guardar`<br>`test_webui_ops::test_us3109_ca02_editar_configuracion` | PASS |
| CA-03 | Solo el owner del proyecto o un administrador pueden cambiar la configuración; los demás ven los valores sin poder editarlos. | `test_rest_write::test_us3109_ca03_solo_owner_o_admin_configuran`<br>`test_webui_ops::test_us3109_ca03_miembro_no_edita_configuracion` | PASS |

## US-31.10

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Desde el backlog se crean requisitos, épicas (enlazadas a requisitos), features (dentro de una épica) e historias (dentro de una feature, enlazadas a requisitos y con sus criterios). | `test_rest_write::test_us3110_ca01_crear_todo_el_backlog`<br>`test_webui_ops::test_us3110_ca01_ca04_crear_backlog_desde_la_interfaz` | PASS |
| CA-02 | A una historia existente se le añaden criterios de aceptación desde su ficha. | `test_rest_write::test_us3110_ca02_anadir_criterios`<br>`test_webui_ops::test_us3110_ca02_anadir_criterios_desde_la_ficha` | PASS |
| CA-03 | Una épica puede enlazarse a más requisitos y su cobertura puede confirmarse; una feature puede dividirse repartiendo sus historias. | `test_rest_write::test_us3110_ca03_enlazar_confirmar_y_dividir`<br>`test_webui_ops::test_us3110_ca03_enlazar_confirmar_y_dividir` | PASS |
| CA-04 | Cada error de validación se muestra junto al formulario, con el campo afectado, sin perder lo escrito. | `test_webui_ops::test_us3110_ca01_ca04_crear_backlog_desde_la_interfaz`<br>`test_rest_write::test_us3110_ca04_error_con_campo` | PASS |

## US-31.11

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Se crean principales (usuarios o agentes) y se cambia su rol global. | `test_rest_write::test_us3111_ca01_ca02_principales_roles_y_miembros`<br>`test_webui_ops::test_us3111_ca01_ca02_principales_y_miembros` | PASS |
| CA-02 | Se añaden miembros a un proyecto, se cambia su rol y se retiran. | `test_rest_write::test_us3111_ca01_ca02_principales_roles_y_miembros`<br>`test_webui_ops::test_us3111_ca01_ca02_principales_y_miembros` | PASS |
| CA-03 | Se crean tokens para un principal: el secreto se muestra una sola vez, con opción de copiarlo, y nunca vuelve a mostrarse. | `test_rest_write::test_us3111_ca03_ca04_token_una_vez_y_revocacion_inmediata`<br>`test_webui_ops::test_us3111_ca03_ca04_token_una_vez_y_revocar` | PASS |
| CA-04 | Un token se revoca desde la interfaz y deja de funcionar de inmediato. | `test_rest_write::test_us3111_ca03_ca04_token_una_vez_y_revocacion_inmediata`<br>`test_webui_ops::test_us3111_ca03_ca04_token_una_vez_y_revocar` | PASS |

## US-31.12

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | La vista de sistema muestra cada motor con su tipo (decisión o generación), proveedor, estado y modelos detectados. | `test_webui_ops::test_us3112_ca01_ca02_ca03_motores_desde_la_interfaz` | PASS |
| CA-02 | Un administrador puede comprobar de nuevo la salud de los motores sin reiniciar ACM. | `test_webui_ops::test_us3112_ca01_ca02_ca03_motores_desde_la_interfaz`<br>`test_rest_write::test_us3112_ca02_refrescar_motores_solo_admin` | PASS |
| CA-03 | El orden de motores de decisión de un proyecto se cambia desde su configuración. | `test_webui_ops::test_us3112_ca01_ca02_ca03_motores_desde_la_interfaz` | PASS |

## US-43.08

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | El sprint activo recibe una predicción de riesgo (bajo, medio, alto) de un motor de decisión, visible en el informe; riesgo alto genera un aviso. (definido en refinamiento) | `test_supervisor::test_us4308_ca01_prediccion_de_riesgo` | PASS |

## US-50.01

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Con la URL de Ollaya y un modelo, ACM registra el motor JEV y comprueba su salud y sus modelos. (definido en refinamiento) | `test_second_brain::test_us5001_ca01_registra_jev_y_comprueba_salud` | PASS |
| CA-02 | Si el servidor exige clave, ACM la envía; con una clave errónea el motor queda en error. (definido en refinamiento) | `test_second_brain::test_us5001_ca02_envia_la_clave_del_servidor` | PASS |
| CA-03 | Un servidor inaccesible o sin el modelo queda en error sin afectar a los demás motores. (definido en refinamiento) | `test_second_brain::test_us5001_ca03_servidor_caido_o_sin_modelo_no_afecta_a_los_demas` | PASS |
| CA-04 | Una configuración incompleta se rechaza o se informa de forma explícita. (definido en refinamiento) | `test_second_brain::test_us5001_ca04_configuracion_incompleta` | PASS |

## US-50.02

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | `acm_decide` devuelve las respuestas de JEV con sus probabilidades y `calibrated: true`. (definido en refinamiento) | `test_second_brain::test_us5002_ca01_acm_decide_responde_jev_calibrado` | PASS |
| CA-02 | Las respuestas se traducen al contrato de ACM (score en 1..n con probabilidades por nivel; noul con probabilidades sí/no). (definido en refinamiento) | `test_second_brain::test_us5002_ca02_traduccion_al_contrato_de_acm` | PASS |
| CA-03 | Un rechazo o una respuesta inválida de JEV es un error, nunca una decisión. (definido en refinamiento) | `test_second_brain::test_us5002_ca03_respuesta_invalida_es_engine_error`<br>`test_second_brain::test_us5002_ca03_servidor_ocupado_es_no_disponible` | PASS |

## US-50.03

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Con ambos configurados y el orden por defecto, las decisiones sin regla las responde JEV y el resumen de contexto Ollama. (definido en refinamiento) | `test_second_brain::test_us5003_ca01_decision_a_jev_y_resumen_a_ollama` | PASS |
| CA-02 | Si JEV no está disponible, decide Ollama sin calibrar y la respuesta indica de qué motor se cayó. (definido en refinamiento) | `test_second_brain::test_us5003_ca02_sin_jev_decide_ollama_sin_calibrar` | PASS |
| CA-03 | El orden de motores se cambia por proyecto sin reiniciar. (definido en refinamiento) | `test_second_brain::test_us5003_ca03_orden_por_proyecto_sin_reiniciar` | PASS |

## US-50.04

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Cada decisión queda registrada con el motor, el propósito, el proyecto, el resultado y los tokens. (definido en refinamiento) | `test_second_brain::test_us5004_ca01_ca02_cada_decision_registra_su_motor` | PASS |
| CA-02 | La respuesta de `acm_decide` incluye el motor y el identificador de ese registro. (definido en refinamiento) | `test_second_brain::test_us5004_ca01_ca02_cada_decision_registra_su_motor` | PASS |

## US-50.09

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | ACM muestra los modelos que detecta en cada runtime, con sus detalles. | `test_models_chat::test_us5009_ca01_muestra_modelos_detectados`<br>`test_webui_ops::test_us5009_modelos_desde_la_interfaz` | PASS |
| CA-02 | El operador elige un modelo de Ollama y, en Ollaya, un modelo por defecto y uno por propósito; solo se aceptan modelos detectados. | `test_models_chat::test_us5009_ca02_elegir_uno_de_ollama_y_varios_de_ollaya`<br>`test_webui_ops::test_us5009_modelos_desde_la_interfaz` | PASS |
| CA-03 | La elección se aplica sin reiniciar ACM y tiene prioridad sobre la configuración de arranque. | `test_models_chat::test_us5009_ca03_se_aplica_sin_reiniciar_y_prevalece_sobre_el_arranque` | PASS |
| CA-04 | El operador puede anotar para qué sirve cada modelo de Ollaya. | `test_models_chat::test_us5009_ca04_notas_del_operador_y_solo_admin`<br>`test_webui_ops::test_us5009_modelos_desde_la_interfaz` | PASS |

## US-50.10

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Una herramienta MCP devuelve los modelos de Ollaya con sus detalles, los propósitos que tienen asignados y la nota del operador, y el modelo de Ollama seleccionado con los disponibles. | `test_models_chat::test_us5010_ca01_ca02_catalogo_para_agentes` | PASS |
| CA-02 | El catálogo explica cómo usar cada motor (decisiones tipadas con JEV, conversación con Ollama) y qué propósitos conoce ACM. | `test_models_chat::test_us5010_ca01_ca02_catalogo_para_agentes` | PASS |
| CA-03 | El agente puede pedir una decisión a un modelo concreto de Ollaya; si no existe, la decisión cae al siguiente motor y lo indica. | `test_models_chat::test_us5010_ca03_modelo_concreto_y_caida_indicada` | PASS |
