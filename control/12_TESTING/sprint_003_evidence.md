# Evidencia de SPRINT-003 — criterios de aceptación ↔ tests

Generado el 2026-09-30 por `control/tools/evidence.py` a partir de `pytest --junitxml` (172 casos) y de las secciones *Pruebas* de `01_PRODUCTO/refinements/`.
Instantánea: se regenera al cerrar el sprint.

## US-22.01

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Se consulta el runtime configurado. | `test_inference::test_us2201_ca01_consulta_el_runtime_configurado` | PASS |
| CA-02 | Los modelos detectados se identifican. | `test_inference::test_us2201_ca02_modelos_detectados_identificados` | PASS |
| CA-03 | Un runtime inaccesible produce un estado de error. | `test_inference::test_us2201_ca03_runtime_inaccesible_estado_error` | PASS |
| CA-04 | El sistema no afirma que un modelo existe si no ha sido detectado. | `test_inference::test_us2201_ca04_no_afirma_modelo_no_detectado` | PASS |
| — | configuración | `test_inference::test_us2201_configuracion_incompleta_rechazada` | PASS |
| — | permiso | `test_inference::test_engines_refresh_solo_admin` | PASS |
| — | cierre de recursos | `test_inference::test_us2201_cierre_libera_el_cliente_http` | PASS |

## US-22.03

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | La petición llega al modelo configurado. | `test_inference::test_us2203_ca01_peticion_llega_al_modelo_configurado` | PASS |
| CA-02 | La respuesta queda vinculada a la ejecución. | `test_inference::test_us2203_ca02_respuesta_vinculada_a_la_ejecucion` | PASS |
| CA-03 | Un fallo del modelo genera estado de error. | `test_inference::test_us2203_ca03_fallo_del_modelo_estado_error` | PASS |
| CA-04 | No se declara éxito si no existe respuesta válida. | `test_inference::test_us2203_ca04_sin_respuesta_valida_no_hay_exito` | PASS |

## US-35.08

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | La respuesta indica el tamaño estimado en tokens del contexto entregado y del contexto completo equivalente. | `test_context::test_us3508_ca01_tamanos_entregado_y_completo` | PASS |
| CA-02 | Cada fragmento resumido identifica sus fuentes. | `test_context::test_us3508_ca02_fragmentos_identifican_fuentes` | PASS |
| CA-03 | Si no hay modelo local disponible, ACM devuelve el contexto estructurado sin resumir e indica que no se ha resumido. | `test_context::test_us3508_ca03_sin_modelo_sin_resumir`<br>`test_context::test_us3508_ca03_modelo_caido_entrega_sin_resumir` | PASS |
| — | regla | `test_context::test_us3508_historia_y_criterios_siempre_literales` | PASS |
| — | validación | `test_context::test_us3508_presupuesto_invalido` | PASS |
| — | aislamiento | `test_context::test_us3508_proyecto_ajeno_rechazado` | PASS |
| — | Ollama simulado | `test_context::test_us3508_resumen_con_ollama_simulado` | PASS |
| — | frontera MCP | `test_context::test_us3508_us3509_por_mcp` | PASS |

## US-35.09

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Cada entrega de contexto registra el tamaño entregado y la estimación del contexto completo equivalente. | `test_context::test_us3509_ca01_cada_entrega_registrada` | PASS |
| CA-02 | El ahorro puede consultarse agregado por agente y por proyecto. | `test_context::test_us3509_ca02_agregado_por_agente_y_proyecto` | PASS |
| CA-03 | La estimación indica el método de cálculo utilizado. | `test_context::test_us3509_ca03_metodo_indicado` | PASS |
| — | permiso | `test_context::test_us3509_solo_admin` | PASS |

## US-35.10

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | La respuesta es tipada e incluye la probabilidad o confianza de cada opción. | `test_inference::test_us3510_ca01_respuesta_tipada_con_probabilidades` | PASS |
| CA-02 | Queda registrado qué motor produjo la decisión. | `test_inference::test_us3510_ca02_motor_registrado` | PASS |
| CA-03 | Si el motor de decisión no está disponible, ACM devuelve un error explícito o usa el mecanismo alternativo configurado, indicándolo. | `test_inference::test_us3510_ca03_sin_motor_error_explicito`<br>`test_inference::test_us3510_ca03_fallback_indicado` | PASS |
| — | validación | `test_inference::test_us3510_peticion_invalida_rechazada` | PASS |
| — | aislamiento | `test_inference::test_us3510_proyecto_ajeno_rechazado` | PASS |

## US-35.11

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Watchdog, gates y router consumen la misma interfaz de decisión. | — | PENDIENTE (Watchdog, EPIC-13). |
| CA-02 | Existe una implementación sin modelo (reglas deterministas) que funciona sin JEV. | `test_inference::test_us3511_ca02_reglas_sin_modelo` | PASS |
| CA-03 | Conectar el adaptador JEV no requiere cambiar a los consumidores de la interfaz. | `test_inference::test_us3511_ca03_conectar_jev_no_cambia_consumidores` | PASS |
| — | consumidores actuales: gate READY y acm_decide | `test_inference::test_us3511_ca01_gate_y_herramienta_usan_el_router` | PASS |
| — | regla | `test_inference::test_us3511_gate_rechaza_motor_no_calibrado` | PASS |
| — | regla | `test_inference::test_us3511_gate_detecta_cambio_durante_la_decision` | PASS |

## US-47.01

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Las tareas no dependen innecesariamente de una implementación concreta. | `test_inference::test_us4701_ca01_consumidores_no_dependen_de_implementacion` | PASS |
| CA-02 | Los recursos de ejecución tienen interfaz abstracta. | `test_inference::test_us4701_ca02_interfaz_abstracta` | PASS |
| CA-03 | La implementación actual continúa funcionando. | `test_inference::test_us4701_ca03_implementacion_actual_sigue_funcionando` | PASS |
| CA-04 | La futura implementación puede conectarse mediante el mismo contrato. | `test_inference::test_us3511_ca03_conectar_jev_no_cambia_consumidores` | PASS |

> **Notas.** US-22.01 y US-22.03: PASS contra un Ollama simulado (`tests/fake_ollama.py`, servidor HTTP con la forma documentada de la API). No se han verificado contra un Ollama real (IMP-004), por eso quedan IMPLEMENTED. US-35.11: CA-01 queda PENDIENTE hasta que exista el Watchdog (EPIC-13); por eso queda IMPLEMENTED.
