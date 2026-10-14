# Evidencia de SPRINT-004 — criterios de aceptación ↔ tests

Generado el 2026-09-30 por `control/tools/evidence.py` a partir de `pytest --junitxml` (198 casos) y de las secciones *Pruebas* de `01_PRODUCTO/refinements/`.
Instantánea: se regenera al cerrar el sprint.

## US-20.01

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Los roles disponibles están definidos. | `test_auth::test_us2001_ca01_roles_definidos` | PASS |
| CA-02 | Un usuario puede recibir un rol autorizado. | `test_auth::test_us2001_ca02_asignar_rol_autorizado` | PASS |
| CA-03 | Los permisos se aplican inmediatamente según política. | `test_auth::test_us2001_ca03_permisos_inmediatos` | PASS |
| CA-04 | Los cambios quedan auditados. | `test_auth::test_us2001_ca04_cambios_auditados` | PASS |
| — | regla | `test_auth::test_us2001_nunca_sin_admin_ni_owner` | PASS |

## US-20.02

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Una operación permitida se ejecuta. | `test_auth::test_us2002_ca01_ca02_ca03_permitida_se_ejecuta_denegada_sin_efectos` | PASS |
| CA-02 | Una operación no permitida es rechazada. | `test_auth::test_us2002_ca01_ca02_ca03_permitida_se_ejecuta_denegada_sin_efectos` | PASS |
| CA-03 | El rechazo no modifica el recurso protegido. | `test_auth::test_us2002_ca01_ca02_ca03_permitida_se_ejecuta_denegada_sin_efectos` | PASS |
| CA-04 | El intento queda registrado cuando la política lo requiera. | `test_auth::test_us2002_ca04_intento_registrado` | PASS |
| — | regla | `test_auth::test_us2002_owner_gestiona_miembros_member_no` | PASS |

## US-20.03

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Cada token tiene identidad y permisos. | `test_auth::test_us2003_ca01_token_con_identidad_y_permisos` | PASS |
| CA-02 | Un token revocado deja de autorizar operaciones. | `test_auth::test_us2003_ca02_revocado_deja_de_autorizar_al_instante` | PASS |
| CA-03 | Los tokens no se muestran completos después de su creación. | `test_auth::test_us2003_ca03_token_no_se_muestra_completo`<br>`test_auth::test_us2003_ca03_secreto_redactado_en_la_auditoria` | PASS |
| CA-04 | El uso queda trazado. | `test_auth::test_us2003_ca04_uso_trazado` | PASS |
| — | regla | `test_auth::test_us2003_solo_admin_crea_tokens_ajenos` | PASS |
| — | CLI de arranque | `test_auth::test_cli_crea_principal_y_token_auditados` | PASS |

## US-20.04

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Cada principal es de tipo `user` o `agent`. (definido en refinamiento) | `test_auth::test_us2004_ca01_usuarios_y_agentes` | PASS |
| CA-02 | Cada principal tiene sus propias credenciales; revocar las de uno no afecta a otro. (definido en refinamiento) | `test_auth::test_us2004_ca02_credenciales_por_principal` | PASS |
| CA-03 | La auditoría identifica a qué principal pertenece cada operación. (definido en refinamiento) | `test_auth::test_us2004_ca03_auditoria_distingue_principal` | PASS |

## US-20.05

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Una petición MCP por HTTP sin token válido recibe 401 y no ejecuta nada. (definido en refinamiento) | `test_auth::test_us2005_ca01_sin_token_401_sin_efectos` | PASS |
| CA-02 | Un token desconocido se rechaza y el intento queda registrado sin guardar el token completo. (definido en refinamiento) | `test_auth::test_us2005_ca02_token_desconocido_rechazado_y_auditado` | PASS |
| CA-03 | Cada petición se atiende con la identidad de su propio token, también con varios agentes a la vez. (definido en refinamiento) | `test_auth::test_us2005_ca03_cada_peticion_con_su_identidad` | PASS |
| — | flujo autenticado | `test_app::test_fastapi_sirve_api_y_mcp_en_un_proceso` | PASS |
| — | despliegue con otro nombre de host, TD-002 | `test_auth::test_td002_host_permitido_por_configuracion` | PASS |

## US-20.08

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Un principal no puede leer ni modificar un proyecto del que no es miembro. (definido en refinamiento) | `test_auth::test_us2008_ca01_ca02_solo_proyectos_propios` | PASS |
| CA-02 | El listado de proyectos solo incluye aquellos a los que tiene acceso. (definido en refinamiento) | `test_auth::test_us2008_ca01_ca02_solo_proyectos_propios` | PASS |
| CA-03 | Un admin accede a todos los proyectos. (definido en refinamiento) | `test_auth::test_us2008_ca03_admin_accede_a_todos` | PASS |
