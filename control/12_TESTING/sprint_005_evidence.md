# Evidencia de SPRINT-005 — criterios de aceptación ↔ tests

Generado el 2026-09-30 por `control/tools/evidence.py` a partir de `pytest --junitxml` (220 casos) y de las secciones *Pruebas* de `01_PRODUCTO/refinements/`.
Instantánea: se regenera al cerrar el sprint.

## US-13.03

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Se muestran componentes relevantes. | `test_watchdog::test_us1303_ca01_ca02_componentes_con_estado` | PASS |
| CA-02 | Cada componente tiene estado. | `test_watchdog::test_us1303_ca01_ca02_componentes_con_estado` | PASS |
| CA-03 | Un componente degradado queda identificado. | `test_watchdog::test_us1303_ca03_componente_degradado_identificado` | PASS |
| CA-04 | La información se actualiza. | `test_watchdog::test_us1303_ca04_informacion_actualizada` | PASS |
| — | permiso | `test_watchdog::test_us1303_solo_admin` | PASS |

## US-13.05

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Se detectan la corrupción física de la base y las relaciones rotas (claves foráneas). (definido en refinamiento) | `test_watchdog::test_us1305_ca01_detecta_relaciones_rotas`<br>`test_watchdog::test_us1305_ca01_detecta_base_danada` | PASS |
| CA-02 | Mientras exista la inconsistencia, ACM no opera sobre ese estado: rechaza las escrituras del proyecto. (definido en refinamiento) | `test_watchdog::test_us1305_ca02_us1311_ca01_ca03_escrituras_bloqueadas_sin_efectos` | PASS |
| CA-03 | Una vez reparada, una nueva auditoría lo detecta y vuelve a permitir las escrituras. (definido en refinamiento) | `test_watchdog::test_us1305_ca03_reparada_se_levanta_la_cuarentena` | PASS |

## US-13.06

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | ACM audita todos los proyectos periódicamente, sin intervención. (definido en refinamiento) | `test_watchdog::test_us1306_ca01_se_ejecuta_periodicamente` | PASS |
| CA-02 | Un proyecto con problemas no impide auditar los demás. (definido en refinamiento) | `test_watchdog::test_us1306_ca02_fallo_en_un_proyecto_no_detiene_a_los_demas` | PASS |
| CA-03 | El intervalo es configurable y puede desactivarse. (definido en refinamiento) | `test_watchdog::test_us1306_ca03_intervalo_configurable_y_solo_admin` | PASS |

## US-13.07

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Cada historia activa sin criterios de aceptación aparece como hallazgo con su identificador. (definido en refinamiento) | `test_watchdog::test_us1307_ca01_historia_sin_criterios_detectada` | PASS |
| CA-02 | La evaluación se hace a través de la interfaz de decisión común y queda registrado qué motor la hizo. (definido en refinamiento) | `test_watchdog::test_us1307_ca02_evaluada_por_el_motor_de_decision` | PASS |
| CA-03 | Una historia completa no genera hallazgos. (definido en refinamiento) | `test_watchdog::test_us1307_ca03_historia_completa_sin_hallazgos` | PASS |
| — | regla | `test_watchdog::test_us1307_motor_no_calibrado_pide_revision` | PASS |

## US-13.10

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | El semáforo es GREEN, AMBER o RED según reglas explícitas sobre la severidad de los hallazgos. (definido en refinamiento) | `test_watchdog::test_us1310_ca01_reglas_del_semaforo` | PASS |
| CA-02 | Se puede consultar el semáforo del proyecto con los recuentos por severidad de la última auditoría. (definido en refinamiento) | `test_watchdog::test_us1310_ca02_ca03_indicadores_del_proyecto` | PASS |
| CA-03 | Un proyecto sin auditar lo indica (`UNKNOWN`) en lugar de aparentar estar bien. (definido en refinamiento) | `test_watchdog::test_us1310_ca02_ca03_indicadores_del_proyecto` | PASS |

## US-13.11

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Una escritura en un proyecto que incumple una regla crítica (integridad) se bloquea automáticamente. (definido en refinamiento) | `test_watchdog::test_us1305_ca02_us1311_ca01_ca03_escrituras_bloqueadas_sin_efectos` | PASS |
| CA-02 | El rechazo explica la causa y cómo levantar el bloqueo. (definido en refinamiento) | `test_watchdog::test_us1311_ca02_bloqueo_explicado` | PASS |
| CA-03 | La operación bloqueada no deja efectos. (definido en refinamiento) | `test_watchdog::test_us1305_ca02_us1311_ca01_ca03_escrituras_bloqueadas_sin_efectos` | PASS |

## US-13.12

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | El operador puede lanzar una auditoría completa del proyecto por MCP. (definido en refinamiento) | `test_watchdog::test_us1312_ca01_ca02_ca03_auditoria_completa_por_mcp` | PASS |
| CA-02 | La auditoría cubre integridad, calidad de las historias y estructura del backlog. (definido en refinamiento) | `test_watchdog::test_us1312_ca01_ca02_ca03_auditoria_completa_por_mcp` | PASS |
| CA-03 | El resultado lista cada hallazgo con código, severidad, objetivo y mensaje. (definido en refinamiento) | `test_watchdog::test_us1312_ca01_ca02_ca03_auditoria_completa_por_mcp` | PASS |

## US-13.13

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Cada auditoría queda conservada. (definido en refinamiento) | `test_watchdog::test_us1313_ca01_ca02_ca03_historico` | PASS |
| CA-02 | El histórico se consulta por proyecto, de la más reciente a la más antigua. (definido en refinamiento) | `test_watchdog::test_us1313_ca01_ca02_ca03_historico` | PASS |
| CA-03 | Cada entrada incluye su semáforo y sus hallazgos. (definido en refinamiento) | `test_watchdog::test_us1313_ca01_ca02_ca03_historico` | PASS |
| CA-04 | Solo quien tiene acceso al proyecto consulta su histórico. (definido en refinamiento) | `test_watchdog::test_us1313_ca04_historico_aislado_por_proyecto` | PASS |

---

# Anexo — historia de un sprint anterior cerrada en SPRINT-005

## US-35.11 (SPRINT-003)

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Watchdog, gates y router consumen la misma interfaz de decisión. | `test_inference::test_us3511_ca01_gate_y_herramienta_usan_el_router`<br>`test_watchdog::test_us3511_ca01_watchdog_consume_la_interfaz` | PASS |
| CA-02 | Existe una implementación sin modelo (reglas deterministas) que funciona sin JEV. | `test_inference::test_us3511_ca02_reglas_sin_modelo` | PASS |
| CA-03 | Conectar el adaptador JEV no requiere cambiar a los consumidores de la interfaz. | `test_inference::test_us3511_ca03_conectar_jev_no_cambia_consumidores` | PASS |
| — | regla | `test_inference::test_us3511_gate_rechaza_motor_no_calibrado` | PASS |
| — | regla | `test_inference::test_us3511_gate_detecta_cambio_durante_la_decision` | PASS |
