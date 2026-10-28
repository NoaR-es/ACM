# Evidencia de SPRINT-006 — criterios de aceptación ↔ tests

Generado el 2026-09-30 por `control/tools/evidence.py` a partir de `pytest --junitxml` (251 casos) y de las secciones *Pruebas* de `01_PRODUCTO/refinements/`.
Instantánea: se regenera al cerrar el sprint.

## US-06.01

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Cada historia aparece en exactamente una columna de estado. | `test_realtime::test_us0601_ca01_ca02_una_columna_por_historia_con_datos` | PASS |
| CA-02 | Se muestran identificador, título y estado. | `test_realtime::test_us0601_ca01_ca02_una_columna_por_historia_con_datos` | PASS |
| CA-03 | Solo se muestran historias del contexto seleccionado. | `test_realtime::test_us0601_ca03_solo_el_contexto_seleccionado_y_varios_a_la_vez`<br>`test_realtime::test_us0601_ca03_proyecto_ajeno_no_se_muestra` | PASS |
| CA-04 | Una historia inexistente no aparece en el tablero. | `test_realtime::test_us0601_ca04_historia_inexistente_no_aparece` | PASS |

## US-06.02

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Un cambio permitido actualiza el estado. | `test_realtime::test_us0602_ca01_ca02_cambio_permitido_y_registrado` | PASS |
| CA-02 | El cambio queda registrado. | `test_realtime::test_us0602_ca01_ca02_cambio_permitido_y_registrado` | PASS |
| CA-03 | Las transiciones no permitidas son rechazadas. | `test_realtime::test_us0602_ca03_transiciones_no_permitidas` | PASS |
| CA-04 | El tablero refleja el nuevo estado. | `test_realtime::test_us0602_ca04_el_tablero_refleja_el_estado` | PASS |
| — | regla | `test_realtime::test_us0602_done_solo_tras_verificar` | PASS |

## US-06.03

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Un cambio realizado por un agente genera un evento. | `test_realtime::test_us0603_ca01_ca02_agente_cambia_y_los_clientes_lo_reciben`<br>`test_realtime::test_us0603_agente_por_stdio_en_otro_proceso` | PASS |
| CA-02 | Los clientes conectados reciben el cambio. | `test_realtime::test_us0603_ca01_ca02_agente_cambia_y_los_clientes_lo_reciben`<br>`test_realtime::test_us0603_agente_por_stdio_en_otro_proceso` | PASS |
| CA-03 | Un cliente desconectado puede recuperar el estado al reconectar. | `test_realtime::test_us2103_ca01_ca02_ca03_ca04_reanuda_sin_perder_ni_duplicar` | PASS |
| CA-04 | Un evento duplicado no genera una segunda modificación. | `test_realtime::test_us0603_ca04_evento_duplicado_no_modifica_dos_veces` | PASS |

## US-21.01

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Un cambio relevante produce el evento definido. | `test_realtime::test_us2101_ca01_ca02_cambio_genera_evento_con_contexto` | PASS |
| CA-02 | El evento contiene identificador y contexto. | `test_realtime::test_us2101_ca01_ca02_cambio_genera_evento_con_contexto` | PASS |
| CA-03 | Un evento no se publica si la operación ha sido revertida. | `test_realtime::test_us2101_ca03_operacion_revertida_no_publica` | PASS |

## US-21.02

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Una suscripción válida recibe eventos correspondientes. | `test_realtime::test_us2102_ca01_ca02_solo_proyectos_autorizados` | PASS |
| CA-02 | No recibe eventos de proyectos no autorizados. | `test_realtime::test_us2102_ca01_ca02_solo_proyectos_autorizados`<br>`test_realtime::test_us2102_actividad_solo_para_admin` | PASS |
| CA-03 | Una desconexión libera la suscripción. | `test_realtime::test_us2102_ca03_desconexion_libera_la_suscripcion` | PASS |
| — | autenticación | `test_realtime::test_us2102_ws_exige_autenticacion` | PASS |

## US-21.03

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | La reconexión se detecta. | `test_realtime::test_us2103_ca01_ca02_ca03_ca04_reanuda_sin_perder_ni_duplicar` | PASS |
| CA-02 | El cliente obtiene el estado necesario. | `test_realtime::test_us2103_ca01_ca02_ca03_ca04_reanuda_sin_perder_ni_duplicar`<br>`test_realtime::test_us2103_resync_si_los_eventos_ya_no_estan`<br>`test_realtime::test_us2103_eventos_por_rest` | PASS |
| CA-03 | Los cambios no se duplican. | `test_realtime::test_us2103_ca01_ca02_ca03_ca04_reanuda_sin_perder_ni_duplicar` | PASS |
| CA-04 | El estado final coincide con el servidor. | `test_realtime::test_us2103_ca01_ca02_ca03_ca04_reanuda_sin_perder_ni_duplicar` | PASS |

## US-30.01

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Cada endpoint tiene contrato definido. | `test_realtime::test_us3001_ca01_us3002_contrato_documentado` | PASS |
| CA-02 | Las entradas inválidas generan respuesta de error adecuada. | `test_realtime::test_us3001_ca02_ca04_entradas_invalidas_formato_consistente` | PASS |
| CA-03 | La autorización se aplica. | `test_realtime::test_us3001_ca03_autorizacion_aplicada` | PASS |
| CA-04 | La respuesta tiene formato consistente. | `test_realtime::test_us3001_ca02_ca04_entradas_invalidas_formato_consistente` | PASS |
| — | lectura completa | `test_realtime::test_us3001_lectura_completa_del_proyecto` | PASS |

## US-30.02

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Cada endpoint documentado indica método y ruta. | `test_realtime::test_us3001_ca01_us3002_contrato_documentado` | PASS |
| CA-02 | Indica entrada y salida. | `test_realtime::test_us3001_ca01_us3002_contrato_documentado` | PASS |
| CA-03 | Indica errores relevantes. | `test_realtime::test_us3001_ca01_us3002_contrato_documentado` | PASS |
| CA-04 | La documentación se actualiza cuando cambia el contrato. | `test_realtime::test_us3001_ca01_us3002_contrato_documentado` | PASS |

## US-30.03

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Los cambios incompatibles tienen versión. | `test_realtime::test_us3003_ca01_ca02_ca03_version_en_la_ruta` | PASS |
| CA-02 | Las versiones activas pueden identificarse. | `test_realtime::test_us3003_ca01_ca02_ca03_version_en_la_ruta` | PASS |
| CA-03 | Las rutas antiguas siguen la política de compatibilidad definida. | `test_realtime::test_us3003_ca01_ca02_ca03_version_en_la_ruta` | PASS |
