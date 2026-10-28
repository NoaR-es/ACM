# Evidencia de SPRINT-002 — criterios de aceptación ↔ tests

Generado el 2026-09-30 por `control/tools/evidence.py` a partir de `pytest --junitxml` (122 casos) y de las secciones *Pruebas* de `01_PRODUCTO/refinements/`.
Instantánea: se regenera al cerrar el sprint.

## US-03.03

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Cada requisito puede localizar sus épicas. | `test_backlog::test_us0303_ca01_requisito_localiza_sus_epicas` | PASS |
| CA-02 | Cada épica puede localizar sus features. | `test_backlog::test_us0303_ca02_epica_localiza_sus_features` | PASS |
| CA-03 | Cada feature puede localizar sus historias. | `test_backlog::test_us0303_ca03_feature_localiza_sus_historias` | PASS |
| CA-04 | Cada historia identifica sus requisitos de origen. | `test_backlog::test_us0303_ca04_historia_identifica_requisitos` | PASS |
| CA-05 | Los requisitos huérfanos aparecen en una auditoría. | `test_backlog::test_us0303_ca05_requisitos_huerfanos_en_auditoria` | PASS |

## US-04.01

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | La épica recibe identificador único. | `test_backlog::test_us0401_ca01_id_unico_generado` | PASS |
| CA-02 | Tiene objetivo y alcance. | `test_backlog::test_us0401_ca02_objetivo_y_alcance_obligatorios` | PASS |
| CA-03 | Puede asociarse a requisitos. | `test_backlog::test_us0401_ca03_asociar_requisitos` | PASS |
| CA-04 | Puede contener features. | `test_backlog::test_us0401_ca04_contiene_features` | PASS |
| CA-05 | No se permite crear épicas duplicadas con el mismo identificador. | `test_backlog::test_us0401_ca05_id_explicito_duplicado_rechazado` | PASS |

## US-04.02

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Cada feature tiene identificador. | `test_backlog::test_us0402_ca01_feature_con_identificador` | PASS |
| CA-02 | Cada feature pertenece a una épica. | `test_backlog::test_us0402_ca02_feature_pertenece_a_una_epica` | PASS |
| CA-03 | Las features cubren el objetivo de la épica. | `test_backlog::test_us0402_ca03_confirmar_cobertura_del_objetivo` | PASS |
| CA-04 | Una feature demasiado grande puede dividirse. | `test_backlog::test_us0402_ca04_dividir_feature` | PASS |

## US-04.03

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Cada historia tiene actor, acción y valor. | `test_backlog::test_us0403_ca01_actor_accion_valor_obligatorios` | PASS |
| CA-02 | Cada historia tiene requisito de origen. | `test_backlog::test_us0403_ca02_requisito_de_origen_obligatorio` | PASS |
| CA-03 | Cada historia tiene criterios de aceptación. | `test_backlog::test_us0403_ca03_criterios_de_aceptacion` | PASS |
| CA-04 | Una historia incompleta no puede marcarse como READY. | `test_backlog::test_us0403_ca04_incompleta_no_pasa_a_ready` | PASS |
| CA-05 | Las tareas técnicas no se registran como historias de usuario salvo que exista una razón explícita. | `test_backlog::test_us0403_ca05_tarea_tecnica_requiere_razon` | PASS |

## US-14.04

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Un agente se conecta al servidor MCP de ACM por Streamable HTTP en `/mcp/` y puede invocar herramientas. (definido en refinamiento) | `test_app::test_fastapi_sirve_api_y_mcp_en_un_proceso` | PASS |
| CA-02 | Un agente se conecta por stdio lanzando `acm mcp-stdio` y puede invocar herramientas. (definido en refinamiento) | `test_app::test_modo_stdio_del_cli` | PASS |
| CA-03 | Al conectar, el agente recibe `instructions` que explican cómo usar ACM (skills y `project_id`). (definido en refinamiento) | `test_app::test_fastapi_sirve_api_y_mcp_en_un_proceso` | PASS |

## US-14.05

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | `tools/list` devuelve todas las herramientas de ACM, cada una con esquema de entrada. (definido en refinamiento) | `test_mcp::test_us1405_ca01_ca02_descubrir_herramientas` | PASS |
| CA-02 | Ninguna herramienta tiene descripción vacía. (definido en refinamiento) | `test_mcp::test_us1405_ca01_ca02_descubrir_herramientas` | PASS |
| CA-03 | Las herramientas que actúan sobre un proyecto declaran `project_id` como obligatorio en su esquema. (definido en refinamiento) | `test_mcp::test_us1405_ca03_herramientas_de_proyecto_declaran_project_id` | PASS |

## US-14.06

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Una operación ejecutada con una herramienta MCP queda persistida y es visible en una lectura posterior, incluso tras reiniciar ACM. (definido en refinamiento) | `test_mcp::test_us1406_ca01_operacion_persiste` | PASS |
| CA-02 | Una operación rechazada no produce ningún cambio en el proyecto. (definido en refinamiento) | `test_mcp::test_us1406_ca02_operacion_rechazada_sin_efectos` | PASS |

## US-14.07

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Una misma instancia del servidor y una misma conexión MCP operan sobre varios proyectos. (definido en refinamiento) | `test_mcp::test_us1407_varios_proyectos_misma_instancia` | PASS |
| CA-02 | Cada llamada actúa solo sobre el `project_id` indicado. (definido en refinamiento) | `test_mcp::test_us1407_varios_proyectos_misma_instancia` | PASS |

## US-14.09

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Una llamada nunca opera sobre un proyecto usado en llamadas anteriores si no se indica su `project_id`: sin `project_id` la llamada se rechaza. (definido en refinamiento) | `test_mcp::test_us1409_ca01_sin_project_id_no_reutiliza_el_anterior` | PASS |
| CA-02 | Una llamada sobre un proyecto al que el principal no tiene acceso devuelve `NOT_FOUND` y no produce efectos. (definido en refinamiento) | `test_mcp::test_us1409_ca02_proyecto_ajeno_rechazado_sin_efectos` | PASS |

## US-14.10

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Un admin obtiene con `acm_audit_list` las invocaciones recientes con principal, operación, proyecto y fecha, de la más reciente a la más antigua. (definido en refinamiento) | `test_audit::test_us1410_ca01_admin_lista_invocaciones` | PASS |
| CA-02 | La consulta se puede filtrar por principal, por operación y por proyecto. (definido en refinamiento) | `test_audit::test_us1410_ca02_filtros` | PASS |
| CA-03 | Un principal sin rol admin no puede consultar la auditoría (`FORBIDDEN`). (definido en refinamiento) | `test_audit::test_us1410_ca03_no_admin_rechazado` | PASS |

## US-14.11

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Cada invocación de herramienta registra sus argumentos. (definido en refinamiento) | `test_audit::test_us1411_ca01_ca03_argumentos_y_duracion` | PASS |
| CA-02 | Se registra el resultado. Si supera 4000 caracteres, se trunca y se marca `result_truncated`. (definido en refinamiento) | `test_audit::test_us1411_ca02_resultado_truncado` | PASS |
| CA-03 | Se registra la duración en milisegundos. (definido en refinamiento) | `test_audit::test_us1411_ca01_ca03_argumentos_y_duracion` | PASS |
| CA-04 | Se registra el estado (`ok`/`error`) y, si hay error, su motivo con código. (definido en refinamiento) | `test_audit::test_us1411_ca04_estado_y_error` | PASS |
| CA-05 | También se registran los intentos de principales desconocidos o sin permiso. (definido en refinamiento) | `test_audit::test_us1411_ca05_intentos_no_autorizados` | PASS |

## US-15.01

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | La Skill tiene identificador y versión. | `test_skills::test_us1501_ca01_id_y_version` | PASS |
| CA-02 | Declara sus capacidades. | `test_skills::test_us1501_ca02_ca03_capacidades_y_dependencias` | PASS |
| CA-03 | Declara dependencias. | `test_skills::test_us1501_ca02_ca03_capacidades_y_dependencias` | PASS |
| CA-04 | Una Skill inválida no se activa. | `test_skills::test_us1501_ca04_skill_invalida_no_se_activa` | PASS |

## US-15.04

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | La respuesta de inicialización MCP incluye `instructions` que indican al agente que descargue y cargue las skills de ACM antes de operar. | `test_skills::test_us1504_ca01_instructions_piden_cargar_skills` | PASS |
| CA-02 | El servidor declara la capacidad `resources` y la extensión `io.modelcontextprotocol/skills`. | `test_skills::test_us1504_ca02_capacidades_declaradas` | PASS |
| CA-03 | `skills/list` devuelve todas las skills oficiales de ACM con `name`, `description`, `uri` y la lista de recursos con `digest` sha256 y `size`. | `test_skills::test_us1504_ca03_skills_list` | PASS |

## US-15.05

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Cada archivo de cada skill se puede leer con `resources/read` bajo la URI `skill://acm/<nombre>/<archivo>`. | `test_skills::test_us1505_ca01_leer_cada_archivo_y_verificar_digest` | PASS |
| CA-02 | `skills/get` devuelve la skill solicitada y una skill inexistente devuelve el error `-32602`. | `test_skills::test_us1505_ca02_skills_get_y_error` | PASS |
| CA-03 | Los clientes sin soporte de la extensión pueden listar y obtener las mismas skills mediante herramientas MCP de ACM. | `test_skills::test_us1505_ca03_herramientas_de_respaldo` | PASS |

## US-15.06

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Cada SKILL.md declara `version` en su frontmatter. | `test_skills::test_us1506_ca01_version_en_frontmatter` | PASS |
| CA-02 | El `digest` de un recurso cambia si y solo si cambia su contenido. | `test_skills::test_us1506_ca02_digest_cambia_solo_si_cambia_el_contenido` | PASS |
| CA-03 | Cuando cambia el catálogo de skills, el servidor emite la notificación de cambio de lista de recursos. | `test_skills::test_us1506_ca03_notificacion_al_cambiar_catalogo` | PASS |

## US-15.07

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Las skills oficiales se versionan junto con el código de ACM. | `test_skills::test_us1507_ca01_skills_oficiales_versionadas_con_el_codigo` | PASS |
| CA-02 | Una skill retirada deja de aparecer en `skills/list` y su URI devuelve error. | `test_skills::test_us1507_ca02_skill_retirada_desaparece` | PASS |
| CA-03 | Cada descarga de skill queda registrada en la auditoría MCP (US-15.08). | `test_skills::test_us1507_ca03_descargas_auditadas` | PASS |

## US-15.08

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | La skill `acm-schema` está en el catálogo oficial con frontmatter válido. (definido en refinamiento) | `test_skills::test_us1508_ca01_acm_schema_valida` | PASS |
| CA-02 | Documenta todas las herramientas MCP que expone el servidor. (definido en refinamiento) | `test_skills::test_us1508_ca02_ca03_documenta_exactamente_las_herramientas` | PASS |
| CA-03 | Solo menciona herramientas que existen. (definido en refinamiento) | `test_skills::test_us1508_ca02_ca03_documenta_exactamente_las_herramientas` | PASS |
| CA-04 | Describe el modelo (proyecto, requisito, épica, feature, historia, criterio) y el flujo recomendado. (definido en refinamiento) | `test_skills::test_us1508_ca04_modelo_y_flujo` | PASS |

## US-15.09

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | La skill `acm-invest` está en el catálogo con frontmatter válido y depende de `acm-schema`. (definido en refinamiento) | `test_skills::test_us1509_ca01_acm_invest_valida` | PASS |
| CA-02 | Cubre las seis letras de INVEST, cada una con la pregunta y qué hacer si falla. (definido en refinamiento) | `test_skills::test_us1509_ca02_ca03_invest_y_criterios_binarios` | PASS |
| CA-03 | Define qué es un criterio de aceptación binario (PASS/FAIL sin interpretación). (definido en refinamiento) | `test_skills::test_us1509_ca02_ca03_invest_y_criterios_binarios` | PASS |
| CA-04 | Solo menciona herramientas de ACM que existen. (definido en refinamiento) | `test_skills::test_us1509_us1510_ca04_solo_herramientas_existentes` | PASS |

## US-15.10

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | La skill `acm-discovery` está en el catálogo con frontmatter válido y depende de `acm-schema`. (definido en refinamiento) | `test_skills::test_us1510_ca01_acm_discovery_valida` | PASS |
| CA-02 | Incluye preguntas sobre visión, actores, alcance, restricciones, dependencias ocultas, riesgos y conflictos. (definido en refinamiento) | `test_skills::test_us1510_ca02_ca03_preguntas_y_registro` | PASS |
| CA-03 | Explica cómo registrar el resultado con `acm_requirement_create` y `acm_epic_create`, y cómo comprobar la trazabilidad. (definido en refinamiento) | `test_skills::test_us1510_ca02_ca03_preguntas_y_registro` | PASS |
| CA-04 | Solo menciona herramientas de ACM que existen. (definido en refinamiento) | `test_skills::test_us1509_us1510_ca04_solo_herramientas_existentes` | PASS |

## US-24.01

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Pueden existir múltiples proyectos. | `test_isolation::test_us2401_ca01_multiples_proyectos` | PASS |
| CA-02 | Cada proyecto tiene backlog independiente. | `test_isolation::test_us2401_ca02_backlog_independiente` | PASS |
| CA-03 | Cada proyecto tiene memoria independiente. | `test_isolation::test_us2401_ca03_memoria_independiente` | PASS |
| CA-04 | Cambiar de proyecto cambia todo el contexto operativo. | `test_isolation::test_us2401_ca04_cambiar_de_proyecto_cambia_contexto` | PASS |

## US-24.03

| CA | Criterio | Tests | Resultado |
|----|----------|-------|-----------|
| CA-01 | Un agente del proyecto A no recupera memoria privada del proyecto B. | `test_isolation::test_us2403_ca01_agente_de_a_no_recupera_memoria_de_b` | PASS |
| CA-02 | Los eventos de B no actualizan el cliente de A. | — | PENDIENTE (EPIC-21). |
| CA-03 | Las consultas de backlog están limitadas al proyecto activo. | `test_isolation::test_us2403_ca03_consultas_limitadas_al_proyecto` | PASS |
