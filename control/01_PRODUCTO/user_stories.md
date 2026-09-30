<!-- GENERADO por control/tools/derive_backlog.py desde 01_PRODUCTO/backlog_completo_v1.md (A) y 01_PRODUCTO/product_definition_v2.md (B). No editar a mano: editar las fuentes o el mapeo del script y regenerar. -->

# User Stories (backlog unificado)

Total: **488** · Con criterios de aceptación: **137** · Sin criterios: **351** · Posibles solapamientos señalados: **37**

> READY exige la cadena completa de la *Regla de aceptación del backlog* (fuente A): precondiciones, flujo,
> alternativas, errores, reglas, validaciones, casos límite, CA, tareas y pruebas. Ninguna historia la cumple
> todavía; todas permanecen en PLANNED (GAP-001).

## EPIC-01 — GESTIÓN DEL PROYECTO Y CICLO DE VIDA

### FEAT-01.01 — Creación de proyectos · origen A:FEAT-01.01

#### US-01.01 — Crear un proyecto

- **Como** administrador del sistema **quiero** crear un nuevo proyecto **para** disponer de un espacio independiente de desarrollo autónomo.
- Origen: A:US-01.01 · Épica: EPIC-01 · Feature: FEAT-01.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Precondiciones:
  - El usuario está autenticado.
  - Tiene permiso para crear proyectos.
- Flujo:
  - El usuario selecciona crear proyecto.
  - Introduce nombre y configuración inicial.
  - El sistema valida los datos.
  - Se crea la estructura inicial.
  - El proyecto aparece disponible.
- Errores:
  - Nombre inválido.
  - Proyecto duplicado.
  - Error de almacenamiento.
- Tareas:
  - Modelo de proyecto.
  - Servicio de creación.
  - Persistencia.
  - Validaciones.
  - Tests.
- Criterios de aceptación:
  - [ ] CA-01: Dado un usuario autorizado, cuando introduce datos válidos y confirma, entonces se crea exactamente un proyecto.
  - [ ] CA-02: Si el nombre obligatorio está vacío, entonces el sistema impide la creación e identifica el campo.
  - [ ] CA-03: Si ya existe un proyecto con el identificador correspondiente, entonces no se crea un duplicado.
  - [ ] CA-04: Si falla el almacenamiento, entonces el proyecto no queda registrado parcialmente y se muestra un error recuperable.
  - [ ] CA-05: Tras una creación correcta, el proyecto puede abrirse desde el listado.

#### US-01.02 — Abrir y seleccionar un proyecto

- **Como** usuario autorizado **quiero** seleccionar un proyecto existente **para** trabajar sobre su contexto, memoria y backlog.
- Origen: A:US-01.02 · Épica: EPIC-01 · Feature: FEAT-01.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Solo aparecen proyectos a los que el usuario tiene acceso.
  - [ ] CA-02: Al seleccionar un proyecto se carga su contexto.
  - [ ] CA-03: El proyecto activo queda identificado visualmente.
  - [ ] CA-04: Si el proyecto ya no existe, se informa del error y se limpia la selección.
  - [ ] CA-05: Cambiar de proyecto no mezcla datos del proyecto anterior con el nuevo.

#### US-01.03 — Configurar un proyecto

- **Como** administrador del proyecto **quiero** modificar su configuración **para** adaptar el comportamiento del sistema.
- Origen: A:US-01.03 · Épica: EPIC-01 · Feature: FEAT-01.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Los parámetros modificables se muestran con su valor actual.
  - [ ] CA-02: Los valores inválidos son rechazados antes de guardar.
  - [ ] CA-03: Una configuración válida queda persistida.
  - [ ] CA-04: Los cambios que requieran reinicio o recarga quedan identificados.
  - [ ] CA-05: La configuración pertenece exclusivamente al proyecto seleccionado.

### FEAT-01.02 — Inicialización de proyectos · origen B:FEAT-01.01

#### US-01.04

- Enunciado: Como operador quiero crear un proyecto ACM para disponer de un espacio independiente de gestión.
- Origen: B:US-01.01 · Épica: EPIC-01 · Feature: FEAT-01.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- ⚠ Posible solapamiento con US-01.01: revisar si es duplicado, detalle o historia distinta (GAP-006)
- Criterios de aceptación:
  - [ ] CA-01: El sistema permite introducir nombre e identificador.
  - [ ] CA-02: Se crea el contexto físico del proyecto.
  - [ ] CA-03: Se crea su base SQLite.
  - [ ] CA-04: El proyecto queda disponible para consulta.

#### US-01.05

- Enunciado: Como operador quiero cambiar el proyecto activo para trabajar sobre distintos proyectos sin mezclar sus contextos.
- Origen: B:US-01.02 · Épica: EPIC-01 · Feature: FEAT-01.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-01.06

- Enunciado: Como agente quiero conocer el proyecto activo antes de ejecutar una herramienta para evitar modificar otro proyecto.
- Origen: B:US-01.03 · Épica: EPIC-01 · Feature: FEAT-01.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-01.03 — Configuración · origen B:FEAT-01.02

#### US-01.07

- Enunciado: Como operador quiero consultar la configuración actual del proyecto para conocer sus reglas operativas.
- Origen: B:US-01.04 · Épica: EPIC-01 · Feature: FEAT-01.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-01.08

- Enunciado: Como operador quiero modificar parámetros configurables para adaptar ACM al proyecto.
- Origen: B:US-01.05 · Épica: EPIC-01 · Feature: FEAT-01.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- ⚠ Posible solapamiento con US-01.03: revisar si es duplicado, detalle o historia distinta (GAP-006)
- Criterios de aceptación: MISSING

#### US-01.09

- Enunciado: Como operador quiero establecer umbrales de calidad, deuda, cuotas y seguridad para controlar el comportamiento autónomo.
- Origen: B:US-01.06 · Épica: EPIC-01 · Feature: FEAT-01.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-01.04 — Metadatos · origen B:FEAT-01.04

#### US-01.10

- Enunciado: Como operador quiero almacenar la visión general del proyecto para que los agentes dispongan de contexto persistente.
- Origen: B:US-01.09 · Épica: EPIC-01 · Feature: FEAT-01.04 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-01.11

- Enunciado: Como agente quiero recuperar los metadatos relevantes antes de ejecutar una operación para trabajar con contexto actualizado.
- Origen: B:US-01.10 · Épica: EPIC-01 · Feature: FEAT-01.04 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

## EPIC-02 — MEMORIA `CONTROL/` Y FUENTE DE VERDAD

### FEAT-02.01 — Estructura documental · origen A:FEAT-02.01

#### US-02.01 — Inicializar `control/`

- **Como** sistema autónomo **quiero** crear la estructura `control/` **para** disponer de una memoria persistente y organizada del proyecto.
- Origen: A:US-02.01 · Épica: EPIC-02 · Feature: FEAT-02.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Un proyecto nuevo genera la estructura definida.
  - [ ] CA-02: Existe un índice raíz.
  - [ ] CA-03: Las áreas de producto, backlog, arquitectura, calidad y planificación tienen índices.
  - [ ] CA-04: La estructura no se genera duplicada al reinicializar.
  - [ ] CA-05: El sistema registra la inicialización.

#### US-02.02 — Consultar el índice de `control/`

- **Como** agente IA **quiero** consultar primero los índices **para** localizar únicamente la información necesaria.
- Origen: A:US-02.02 · Épica: EPIC-02 · Feature: FEAT-02.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: El índice identifica los documentos existentes.
  - [ ] CA-02: Cada entrada permite localizar su contenido.
  - [ ] CA-03: Un documento inexistente no aparece como disponible.
  - [ ] CA-04: El agente puede localizar requisitos, arquitectura y backlog sin recorrer todo el árbol.

#### US-02.03 — Actualizar memoria de proyecto

- **Como** agente de desarrollo **quiero** actualizar los documentos de control después de cambios relevantes **para** mantener sincronizada la memoria del proyecto.
- Origen: A:US-02.03 · Épica: EPIC-02 · Feature: FEAT-02.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Una decisión registrada queda persistida.
  - [ ] CA-02: Los cambios conservan trazabilidad.
  - [ ] CA-03: No se sobrescribe información previa sin mecanismo de historial.
  - [ ] CA-04: El índice refleja documentos nuevos o modificados.

## EPIC-03 — PRODUCT OWNER Y DESCUBRIMIENTO DE REQUISITOS

### FEAT-03.01 — Análisis de producto · origen A:FEAT-03.01

#### US-03.01 — Analizar una idea de producto

- **Como** Product Owner IA **quiero** analizar una idea completa **para** convertirla en requisitos estructurados.
- Origen: A:US-03.01 · Épica: EPIC-03 · Feature: FEAT-03.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: El análisis identifica actores, objetivos y funcionalidades explícitas.
  - [ ] CA-02: Los requisitos reciben identificadores únicos.
  - [ ] CA-03: Se diferencian requisitos explícitos, implícitos y decisiones técnicas.
  - [ ] CA-04: Las contradicciones quedan registradas.
  - [ ] CA-05: Ninguna funcionalidad explícita desaparece durante la transformación.

#### US-03.02 — Incorporar funcionalidades confirmadas

- **Como** Product Owner **quiero** incorporar funcionalidades confirmadas posteriormente **para** asegurar que forman parte obligatoria del producto.
- Origen: A:US-03.02 · Épica: EPIC-03 · Feature: FEAT-03.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Cada funcionalidad confirmada recibe trazabilidad.
  - [ ] CA-02: Una funcionalidad confirmada no puede quedar clasificada como opcional.
  - [ ] CA-03: El sistema detecta conflictos con requisitos existentes.
  - [ ] CA-04: Cada funcionalidad termina vinculada a una o más historias.

#### US-03.03 — Mantener trazabilidad requisito-backlog

- **Como** Product Owner **quiero** saber qué historias implementan cada requisito **para** detectar funcionalidades sin implementar.
- Origen: A:US-03.03 · Épica: EPIC-03 · Feature: FEAT-03.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Cada requisito puede localizar sus épicas.
  - [ ] CA-02: Cada épica puede localizar sus features.
  - [ ] CA-03: Cada feature puede localizar sus historias.
  - [ ] CA-04: Cada historia identifica sus requisitos de origen.
  - [ ] CA-05: Los requisitos huérfanos aparecen en una auditoría.

### FEAT-03.02 — Discovery Socrático · origen B:FEAT-02.03

#### US-03.04

- Enunciado: Como Product Owner quiero que el agente formule preguntas sobre la visión antes de crear el backlog.
- Origen: B:US-02.08 · Épica: EPIC-03 · Feature: FEAT-03.02 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-03.05

- Enunciado: Como operador quiero revisar los supuestos detectados durante Discovery.
- Origen: B:US-02.09 · Épica: EPIC-03 · Feature: FEAT-03.02 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-03.06

- Enunciado: Como agente quiero identificar dependencias ocultas antes de convertir funcionalidades en historias.
- Origen: B:US-02.10 · Épica: EPIC-03 · Feature: FEAT-03.02 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-03.07

- Enunciado: Como agente quiero identificar restricciones técnicas y de negocio antes de diseñar una solución.
- Origen: B:US-02.11 · Épica: EPIC-03 · Feature: FEAT-03.02 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-03.08

- Enunciado: Como operador quiero detectar conflictos entre requisitos para resolverlos antes de crear tareas.
- Origen: B:US-02.12 · Épica: EPIC-03 · Feature: FEAT-03.02 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-03.03 — Matriz de riesgo · origen B:FEAT-02.04

#### US-03.09

- Enunciado: Como Product Owner quiero registrar riesgos funcionales y técnicos detectados durante Discovery.
- Origen: B:US-02.13 · Épica: EPIC-03 · Feature: FEAT-03.03 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-03.10

- Enunciado: Como arquitecto quiero identificar cuellos de botella potenciales antes de planificar un sprint.
- Origen: B:US-02.14 · Épica: EPIC-03 · Feature: FEAT-03.03 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

## EPIC-04 — PRODUCT BACKLOG Y ÉPICAS

### FEAT-04.01 — Gestión de backlog · origen A:FEAT-04.01

#### US-04.01 — Crear una épica

- **Como** Product Owner **quiero** crear una épica funcional **para** agrupar capacidades relacionadas.
- Origen: A:US-04.01 · Épica: EPIC-04 · Feature: FEAT-04.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: La épica recibe identificador único.
  - [ ] CA-02: Tiene objetivo y alcance.
  - [ ] CA-03: Puede asociarse a requisitos.
  - [ ] CA-04: Puede contener features.
  - [ ] CA-05: No se permite crear épicas duplicadas con el mismo identificador.

#### US-04.02 — Descomponer una épica en features

- **Como** Product Owner **quiero** descomponer una épica **para** obtener capacidades funcionales manejables.
- Origen: A:US-04.02 · Épica: EPIC-04 · Feature: FEAT-04.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Cada feature tiene identificador.
  - [ ] CA-02: Cada feature pertenece a una épica.
  - [ ] CA-03: Las features cubren el objetivo de la épica.
  - [ ] CA-04: Una feature demasiado grande puede dividirse.

#### US-04.03 — Crear User Stories

- **Como** Product Owner **quiero** convertir features en historias **para** crear unidades implementables.
- Origen: A:US-04.03 · Épica: EPIC-04 · Feature: FEAT-04.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Cada historia tiene actor, acción y valor.
  - [ ] CA-02: Cada historia tiene requisito de origen.
  - [ ] CA-03: Cada historia tiene criterios de aceptación.
  - [ ] CA-04: Una historia incompleta no puede marcarse como READY.
  - [ ] CA-05: Las tareas técnicas no se registran como historias de usuario salvo que exista una razón explícita.

### FEAT-04.02 — Épicas · origen B:FEAT-04.01

#### US-04.04

- Enunciado: Como Product Owner quiero crear una épica asociada a funcionalidades concretas.
- Origen: B:US-04.01 · Épica: EPIC-04 · Feature: FEAT-04.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-04.05

- Enunciado: Como Product Owner quiero definir visión y valor de negocio de una épica.
- Origen: B:US-04.02 · Épica: EPIC-04 · Feature: FEAT-04.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-04.06

- Enunciado: Como usuario quiero consultar el progreso de una épica a partir de sus historias.
- Origen: B:US-04.03 · Épica: EPIC-04 · Feature: FEAT-04.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-04.03 — Historias · origen B:FEAT-04.02

#### US-04.07

- Enunciado: Como Product Owner quiero crear historias INVEST para expresar valor funcional atómico.
- Origen: B:US-04.04 · Épica: EPIC-04 · Feature: FEAT-04.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-04.08

- Enunciado: Como Product Owner quiero relacionar cada historia con su origen funcional.
- Origen: B:US-04.05 · Épica: EPIC-04 · Feature: FEAT-04.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-04.09

- Enunciado: Como agente quiero dividir historias demasiado grandes antes de convertirlas en tareas.
- Origen: B:US-04.06 · Épica: EPIC-04 · Feature: FEAT-04.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-04.10

- Enunciado: Como Watchdog quiero detectar historias que no sean suficientemente pequeñas, claras o testeables.
- Origen: B:US-04.07 · Épica: EPIC-04 · Feature: FEAT-04.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-04.04 — Requisitos · origen B:FEAT-04.03

#### US-04.11

- Enunciado: Como Product Owner quiero añadir criterios de aceptación binarios a una historia.
- Origen: B:US-04.08 · Épica: EPIC-04 · Feature: FEAT-04.04 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-04.12

- Enunciado: Como QA quiero comprobar cada criterio de aceptación de forma independiente.
- Origen: B:US-04.09 · Épica: EPIC-04 · Feature: FEAT-04.04 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-04.13

- Enunciado: Como Watchdog quiero impedir que una historia avance sin criterios de aceptación suficientes.
- Origen: B:US-04.10 · Épica: EPIC-04 · Feature: FEAT-04.04 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-04.05 — Auditor INVEST · origen B:FEAT-05.01

#### US-04.14

- Enunciado: Como Watchdog quiero evaluar automáticamente una historia según INVEST.
- Origen: B:US-05.01 · Épica: EPIC-04 · Feature: FEAT-04.05 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-04.15

- Enunciado: Como Watchdog quiero identificar criterios vagos o no verificables.
- Origen: B:US-05.02 · Épica: EPIC-04 · Feature: FEAT-04.05 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-04.16

- Enunciado: Como Product Owner quiero recibir las deficiencias detectadas antes de aprobar una historia.
- Origen: B:US-05.03 · Épica: EPIC-04 · Feature: FEAT-04.05 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

## EPIC-05 — SCRUM MASTER Y PLANIFICACIÓN

### FEAT-05.01 — Planificación · origen A:FEAT-05.01

#### US-05.01 — Priorizar historias

- **Como** Scrum Master/Product Owner **quiero** ordenar el backlog según valor y dependencias **para** determinar qué debe desarrollarse primero.
- Origen: A:US-05.01 · Épica: EPIC-05 · Feature: FEAT-05.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Cada historia tiene prioridad.
  - [ ] CA-02: La prioridad puede modificarse.
  - [ ] CA-03: Las dependencias se tienen en cuenta al proponer orden.
  - [ ] CA-04: Una historia bloqueada no se presenta como inmediatamente ejecutable.

#### US-05.02 — Crear un sprint

- **Como** Scrum Master **quiero** crear un sprint **para** agrupar trabajo con un objetivo concreto.
- Origen: A:US-05.02 · Épica: EPIC-05 · Feature: FEAT-05.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: El sprint tiene identificador y objetivo.
  - [ ] CA-02: Las historias asignadas quedan vinculadas al sprint.
  - [ ] CA-03: El sistema detecta dependencias incompatibles.
  - [ ] CA-04: El sprint puede pasar por estados definidos.

#### US-05.03 — Cerrar un sprint

- **Como** Scrum Master **quiero** cerrar un sprint **para** registrar su resultado y actualizar la planificación.
- Origen: A:US-05.03 · Épica: EPIC-05 · Feature: FEAT-05.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: El sistema identifica historias terminadas y no terminadas.
  - [ ] CA-02: Las historias no terminadas pueden trasladarse.
  - [ ] CA-03: Se genera un resumen del sprint.
  - [ ] CA-04: El historial del sprint queda conservado.

### FEAT-05.02 — Sprints · origen B:FEAT-06.01

#### US-05.04

- Enunciado: Como Scrum Master quiero crear un sprint con objetivo, fechas y capacidad.
- Origen: B:US-06.01 · Épica: EPIC-05 · Feature: FEAT-05.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- ⚠ Posible solapamiento con US-05.02: revisar si es duplicado, detalle o historia distinta (GAP-006)
- Criterios de aceptación: MISSING

#### US-05.05

- Enunciado: Como Scrum Master quiero asignar historias a un sprint.
- Origen: B:US-06.02 · Épica: EPIC-05 · Feature: FEAT-05.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-05.06

- Enunciado: Como Scrum Master quiero cerrar un sprint conservando sus métricas históricas.
- Origen: B:US-06.03 · Épica: EPIC-05 · Feature: FEAT-05.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-05.03 — Capacidad · origen B:FEAT-06.02

#### US-05.07

- Enunciado: Como Scrum Master quiero registrar la capacidad disponible del sprint.
- Origen: B:US-06.04 · Épica: EPIC-05 · Feature: FEAT-05.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- ⚠ Posible solapamiento con US-05.03: revisar si es duplicado, detalle o historia distinta (GAP-006)
- Criterios de aceptación: MISSING

#### US-05.08

- Enunciado: Como Scrum Master quiero conocer la carga asignada al sprint.
- Origen: B:US-06.05 · Épica: EPIC-05 · Feature: FEAT-05.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-05.09

- Enunciado: Como sistema quiero detectar sobrecarga antes de iniciar un sprint.
- Origen: B:US-06.06 · Épica: EPIC-05 · Feature: FEAT-05.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-05.04 — Predicción · origen B:FEAT-06.03

#### US-05.10

- Enunciado: Como Scrum Master quiero simular un sprint antes de iniciarlo para detectar dependencias ocultas.
- Origen: B:US-06.07 · Épica: EPIC-05 · Feature: FEAT-05.04 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-05.11

- Enunciado: Como Scrum Master quiero identificar posibles cuellos de botella antes de comprometer trabajo.
- Origen: B:US-06.08 · Épica: EPIC-05 · Feature: FEAT-05.04 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-05.12

- Enunciado: Como operador quiero comparar escenarios alternativos de planificación.
- Origen: B:US-06.09 · Épica: EPIC-05 · Feature: FEAT-05.04 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

## EPIC-06 — KANBAN REACTIVO

### FEAT-06.01 — Tablero · origen A:FEAT-06.01

#### US-06.01 — Visualizar el tablero Kanban

- **Como** miembro del equipo **quiero** visualizar el trabajo en columnas **para** conocer el estado actual del desarrollo.
- Origen: A:US-06.01 · Épica: EPIC-06 · Feature: FEAT-06.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Cada historia aparece en exactamente una columna de estado.
  - [ ] CA-02: Se muestran identificador, título y estado.
  - [ ] CA-03: Solo se muestran historias del contexto seleccionado.
  - [ ] CA-04: Una historia inexistente no aparece en el tablero.

#### US-06.02 — Cambiar el estado de una historia

- **Como** agente de desarrollo **quiero** cambiar el estado de una historia **para** reflejar su progreso real.
- Origen: A:US-06.02 · Épica: EPIC-06 · Feature: FEAT-06.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Un cambio permitido actualiza el estado.
  - [ ] CA-02: El cambio queda registrado.
  - [ ] CA-03: Las transiciones no permitidas son rechazadas.
  - [ ] CA-04: El tablero refleja el nuevo estado.

#### US-06.03 — Actualizar Kanban en tiempo real

- **Como** usuario del sistema **quiero** recibir cambios del tablero en tiempo real **para** no tener que recargar la aplicación.
- Origen: A:US-06.03 · Épica: EPIC-06 · Feature: FEAT-06.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Un cambio realizado por un agente genera un evento.
  - [ ] CA-02: Los clientes conectados reciben el cambio.
  - [ ] CA-03: Un cliente desconectado puede recuperar el estado al reconectar.
  - [ ] CA-04: Un evento duplicado no genera una segunda modificación.

### FEAT-06.02 — Kanban · origen B:FEAT-19.01

#### US-06.04

- Enunciado: Como operador quiero visualizar las historias y tareas de un proyecto en un tablero Kanban.
- Origen: B:US-19.01 · Épica: EPIC-06 · Feature: FEAT-06.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- ⚠ Posible solapamiento con US-06.01: revisar si es duplicado, detalle o historia distinta (GAP-006)
- Criterios de aceptación: MISSING

#### US-06.05

- Enunciado: Como operador quiero ver los cambios provocados por agentes en tiempo real.
- Origen: B:US-19.02 · Épica: EPIC-06 · Feature: FEAT-06.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- ⚠ Posible solapamiento con US-06.03: revisar si es duplicado, detalle o historia distinta (GAP-006)
- Criterios de aceptación: MISSING

#### US-06.06

- Enunciado: Como operador quiero abrir una tarjeta para consultar su contexto completo.
- Origen: B:US-19.03 · Épica: EPIC-06 · Feature: FEAT-06.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

## EPIC-07 — ORQUESTADOR DE AGENTES

### FEAT-07.01 — Ciclo autónomo · origen A:FEAT-07.01

#### US-07.01 — Iniciar el ciclo autónomo

- **Como** usuario autorizado **quiero** iniciar el ciclo autónomo **para** que el equipo IA comience a trabajar.
- Origen: A:US-07.01 · Épica: EPIC-07 · Feature: FEAT-07.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: El sistema comprueba que existe un proyecto válido.
  - [ ] CA-02: Comprueba que existe trabajo ejecutable.
  - [ ] CA-03: Inicializa el orquestador.
  - [ ] CA-04: El estado pasa a RUNNING.
  - [ ] CA-05: Un segundo inicio no crea dos ciclos simultáneos.

#### US-07.02 — Orquestar una historia

- **Como** sistema **quiero** asignar una historia al agente adecuado **para** ejecutar el trabajo necesario.
- Origen: A:US-07.02 · Épica: EPIC-07 · Feature: FEAT-07.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: La historia seleccionada queda registrada.
  - [ ] CA-02: Se determina el agente responsable.
  - [ ] CA-03: Se respetan dependencias.
  - [ ] CA-04: El estado de ejecución queda registrado.
  - [ ] CA-05: Un fallo de asignación no marca la historia como terminada.

#### US-07.03 — Detener el ciclo autónomo

- **Como** usuario autorizado **quiero** detener el ciclo **para** recuperar el control del proyecto.
- Origen: A:US-07.03 · Épica: EPIC-07 · Feature: FEAT-07.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: El sistema solicita detener nuevas ejecuciones.
  - [ ] CA-02: No se asignan nuevas tareas después de la parada.
  - [ ] CA-03: Las ejecuciones activas quedan registradas.
  - [ ] CA-04: El estado global cambia a STOPPED.

### FEAT-07.02 — Autonomous Loop · origen B:FEAT-44.01

#### US-07.04

- Enunciado: Como operador quiero iniciar un ciclo autónomo de desarrollo.
- Origen: B:US-44.01 · Épica: EPIC-07 · Feature: FEAT-07.02 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- ⚠ Posible solapamiento con US-07.01: revisar si es duplicado, detalle o historia distinta (GAP-006)
- Criterios de aceptación: MISSING

#### US-07.05

- Enunciado: Como sistema quiero seleccionar la siguiente tarea ejecutable.
- Origen: B:US-44.02 · Épica: EPIC-07 · Feature: FEAT-07.02 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-07.06

- Enunciado: Como sistema quiero validar que la tarea está autorizada antes de ejecutarla.
- Origen: B:US-44.03 · Épica: EPIC-07 · Feature: FEAT-07.02 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-07.03 — Ciclo completo · origen B:FEAT-44.02

#### US-07.07

- Enunciado: Como sistema quiero ejecutar la tarea, verificarla y actualizar su estado automáticamente.
- Origen: B:US-44.04 · Épica: EPIC-07 · Feature: FEAT-07.03 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-07.08

- Enunciado: Como sistema quiero avanzar hacia la siguiente tarea cuando la anterior haya quedado correctamente validada.
- Origen: B:US-44.05 · Épica: EPIC-07 · Feature: FEAT-07.03 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-07.04 — Detención · origen B:FEAT-44.03

#### US-07.09

- Enunciado: Como sistema quiero detener el ciclo cuando aparezca un bloqueo crítico.
- Origen: B:US-44.06 · Épica: EPIC-07 · Feature: FEAT-07.04 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- ⚠ Posible solapamiento con US-07.03: revisar si es duplicado, detalle o historia distinta (GAP-006)
- Criterios de aceptación: MISSING

#### US-07.10

- Enunciado: Como operador quiero reanudar el ciclo después de resolver un bloqueo.
- Origen: B:US-44.07 · Épica: EPIC-07 · Feature: FEAT-07.04 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

## EPIC-08 — AGENTES, INSTANCIAS Y HILOS

### FEAT-08.01 — Gestión de agentes · origen A:FEAT-08.01

#### US-08.01 — Crear una instancia de agente

- **Como** orquestador **quiero** crear una instancia de un perfil **para** ejecutar una tarea concreta con contexto aislado.
- Origen: A:US-08.01 · Épica: EPIC-08 · Feature: FEAT-08.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: La instancia referencia su perfil.
  - [ ] CA-02: Tiene identificador único.
  - [ ] CA-03: Tiene proyecto y contexto asociados.
  - [ ] CA-04: Su estado inicial es válido.
  - [ ] CA-05: No comparte accidentalmente memoria privada de otra instancia.

#### US-08.02 — Gestionar hilos de ejecución

- **Como** agente **quiero** disponer de hilos/contextos independientes **para** ejecutar conversaciones o tareas separadas.
- Origen: A:US-08.02 · Épica: EPIC-08 · Feature: FEAT-08.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Cada hilo tiene identificador.
  - [ ] CA-02: El contexto del hilo se conserva.
  - [ ] CA-03: Los mensajes pertenecen al hilo correcto.
  - [ ] CA-04: Dos hilos no mezclan sus mensajes.

#### US-08.03 — Visualizar agentes, instancias e hilos

- **Como** usuario **quiero** conocer cuántos agentes, instancias e hilos existen **para** supervisar el sistema.
- Origen: A:US-08.03 · Épica: EPIC-08 · Feature: FEAT-08.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: El sistema muestra los agentes activos.
  - [ ] CA-02: Muestra instancias.
  - [ ] CA-03: Muestra hilos.
  - [ ] CA-04: Los contadores se actualizan cuando cambia el estado.

## EPIC-09 — ROLES PROFESIONALES DEL EQUIPO IA

### FEAT-09.01 — Roles · origen A:FEAT-09.01

#### US-09.01 — Ejecutar Product Owner IA

- **Como** sistema **quiero** disponer de un agente Product Owner **para** gestionar requisitos y backlog.
- Origen: A:US-09.01 · Épica: EPIC-09 · Feature: FEAT-09.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: El agente puede analizar requisitos.
  - [ ] CA-02: Puede crear/modificar backlog según permisos.
  - [ ] CA-03: Sus cambios quedan trazados.
  - [ ] CA-04: No puede ejecutar operaciones fuera de sus capacidades autorizadas.

#### US-09.02 — Ejecutar Architect IA

- **Como** sistema **quiero** disponer de un agente arquitecto **para** mantener decisiones y arquitectura.
- Origen: A:US-09.02 · Épica: EPIC-09 · Feature: FEAT-09.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Puede consultar requisitos.
  - [ ] CA-02: Puede proponer decisiones arquitectónicas.
  - [ ] CA-03: Las decisiones quedan registradas.
  - [ ] CA-04: Las decisiones no borran requisitos funcionales.

#### US-09.03 — Ejecutar Developer IA

- **Como** sistema **quiero** disponer de agentes desarrolladores **para** implementar historias aprobadas.
- Origen: A:US-09.03 · Épica: EPIC-09 · Feature: FEAT-09.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Un Developer recibe una historia concreta.
  - [ ] CA-02: Puede consultar su contexto.
  - [ ] CA-03: Registra cambios.
  - [ ] CA-04: Ejecuta pruebas.
  - [ ] CA-05: No puede declarar terminada una historia sin cumplir sus criterios.

## EPIC-10 — DESCOMPOSICIÓN TÉCNICA Y EJECUCIÓN

### FEAT-10.01 — Tasks · origen A:FEAT-10.01

#### US-10.01 — Descomponer una User Story en tareas técnicas

- **Como** Developer/Tech Lead IA **quiero** convertir una historia en tareas técnicas **para** poder implementarla de forma controlada.
- Origen: A:US-10.01 · Épica: EPIC-10 · Feature: FEAT-10.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Las tareas derivan de la historia.
  - [ ] CA-02: Cada tarea tiene objetivo.
  - [ ] CA-03: Las tareas cubren implementación y pruebas necesarias.
  - [ ] CA-04: Ninguna tarea introduce funcionalidad no aprobada sin registrarla.

#### US-10.02 — Ejecutar una tarea técnica

- **Como** Developer IA **quiero** ejecutar una tarea **para** producir el cambio requerido.
- Origen: A:US-10.02 · Épica: EPIC-10 · Feature: FEAT-10.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: La tarea pasa a ejecución.
  - [ ] CA-02: Los cambios quedan registrados.
  - [ ] CA-03: Si falla, la tarea queda en estado de error.
  - [ ] CA-04: El agente no declara éxito sin verificación.

#### US-10.03 — Verificar una historia

- **Como** QA/Developer IA **quiero** ejecutar las comprobaciones de aceptación **para** determinar objetivamente si una historia está terminada.
- Origen: A:US-10.03 · Épica: EPIC-10 · Feature: FEAT-10.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Cada CA puede marcarse PASS/FAIL.
  - [ ] CA-02: Una historia con un CA FAIL no puede pasar a DONE.
  - [ ] CA-03: Se conserva la evidencia de la prueba.
  - [ ] CA-04: El resultado queda vinculado a la historia.

### FEAT-10.02 — Tasks · origen B:FEAT-07.01

#### US-10.04

- Enunciado: Como agente constructor quiero crear tareas técnicas asociadas a una historia aprobada.
- Origen: B:US-07.01 · Épica: EPIC-10 · Feature: FEAT-10.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- ⚠ Posible solapamiento con US-10.01: revisar si es duplicado, detalle o historia distinta (GAP-006)
- Criterios de aceptación: MISSING

#### US-10.05

- Enunciado: Como agente quiero consultar las tareas disponibles para ejecutar la siguiente unidad de trabajo.
- Origen: B:US-07.02 · Épica: EPIC-10 · Feature: FEAT-10.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-10.06

- Enunciado: Como agente quiero reclamar una tarea para evitar que otro agente la ejecute simultáneamente.
- Origen: B:US-07.03 · Épica: EPIC-10 · Feature: FEAT-10.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-10.07

- Enunciado: Como agente quiero completar una tarea aportando evidencia de los cambios realizados.
- Origen: B:US-07.04 · Épica: EPIC-10 · Feature: FEAT-10.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-10.03 — Descomposición automática · origen B:FEAT-07.02

#### US-10.08

- Enunciado: Como agente Scrum quiero descomponer una historia en tareas técnicas.
- Origen: B:US-07.05 · Épica: EPIC-10 · Feature: FEAT-10.03 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- ⚠ Posible solapamiento con US-10.01: revisar si es duplicado, detalle o historia distinta (GAP-006)
- Criterios de aceptación: MISSING

#### US-10.09

- Enunciado: Como agente quiero estimar el esfuerzo de las tareas.
- Origen: B:US-07.06 · Épica: EPIC-10 · Feature: FEAT-10.03 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-10.10

- Enunciado: Como Watchdog quiero detectar tareas huérfanas sin historia de origen.
- Origen: B:US-07.07 · Épica: EPIC-10 · Feature: FEAT-10.03 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-10.04 — Planes · origen B:FEAT-08.01

#### US-10.11

- Enunciado: Como agente quiero generar un plan de implementación antes de ejecutar cambios complejos.
- Origen: B:US-08.01 · Épica: EPIC-10 · Feature: FEAT-10.04 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-10.12

- Enunciado: Como sistema quiero ingerir un plan en ACM para convertirlo en hitos verificables.
- Origen: B:US-08.02 · Épica: EPIC-10 · Feature: FEAT-10.04 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-10.13

- Enunciado: Como operador quiero consultar el estado de cada hito del plan.
- Origen: B:US-08.03 · Épica: EPIC-10 · Feature: FEAT-10.04 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-10.05 — Validadores · origen B:FEAT-08.02

#### US-10.14

- Enunciado: Como sistema quiero asociar historias y tareas a los hitos que deben validar.
- Origen: B:US-08.04 · Épica: EPIC-10 · Feature: FEAT-10.05 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-10.15

- Enunciado: Como sistema quiero completar automáticamente un hito cuando todos sus validadores estén satisfechos.
- Origen: B:US-08.05 · Épica: EPIC-10 · Feature: FEAT-10.05 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-10.16

- Enunciado: Como sistema quiero impedir completar un hito cuando falte evidencia.
- Origen: B:US-08.06 · Épica: EPIC-10 · Feature: FEAT-10.05 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-10.06 — Dependencias · origen B:FEAT-08.03

#### US-10.17

- Enunciado: Como sistema quiero representar dependencias entre planes.
- Origen: B:US-08.07 · Épica: EPIC-10 · Feature: FEAT-10.06 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-10.18

- Enunciado: Como sistema quiero impedir que un plan dependiente comience antes de cumplir sus prerrequisitos.
- Origen: B:US-08.08 · Épica: EPIC-10 · Feature: FEAT-10.06 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

## EPIC-11 — GESTIÓN DEL CÓDIGO Y REPOSITORIO

### FEAT-11.01 — Cambios · origen A:FEAT-11.01

#### US-11.01 — Registrar cambios realizados por un agente

- **Como** sistema **quiero** registrar cada cambio producido por un agente **para** mantener trazabilidad.
- Origen: A:US-11.01 · Épica: EPIC-11 · Feature: FEAT-11.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Cada cambio identifica agente.
  - [ ] CA-02: Identifica historia/tarea.
  - [ ] CA-03: Registra fecha.
  - [ ] CA-04: Registra resultado.
  - [ ] CA-05: Puede relacionarse con la evidencia de prueba.

#### US-11.02 — Detectar cambios no vinculados

- **Como** sistema **quiero** detectar cambios sin tarea o historia asociada **para** impedir modificaciones inexplicables.
- Origen: A:US-11.02 · Épica: EPIC-11 · Feature: FEAT-11.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Un cambio sin referencia aparece como huérfano.
  - [ ] CA-02: El sistema permite investigar su origen.
  - [ ] CA-03: No se marca como cambio funcional válido automáticamente.

#### US-11.03 — Mantener historial técnico

- **Como** arquitecto **quiero** conservar el historial de modificaciones relevantes **para** comprender la evolución del sistema.
- Origen: A:US-11.03 · Épica: EPIC-11 · Feature: FEAT-11.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Las decisiones importantes tienen historial.
  - [ ] CA-02: Los cambios pueden relacionarse con historias.
  - [ ] CA-03: El historial no se elimina al cerrar un sprint.

### FEAT-11.02 — Vinculación con código · origen B:FEAT-07.03

#### US-11.04

- Enunciado: Como agente quiero vincular archivos modificados con la tarea ejecutada.
- Origen: B:US-07.08 · Épica: EPIC-11 · Feature: FEAT-11.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-11.05

- Enunciado: Como operador quiero conocer qué código fue modificado para completar una historia.
- Origen: B:US-07.09 · Épica: EPIC-11 · Feature: FEAT-11.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-11.06

- Enunciado: Como Watchdog quiero detectar cambios de código sin una tarea ACM activa.
- Origen: B:US-07.10 · Épica: EPIC-11 · Feature: FEAT-11.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- ⚠ Posible solapamiento con US-11.02: revisar si es duplicado, detalle o historia distinta (GAP-006)
- Criterios de aceptación: MISSING

## EPIC-12 — SNAPSHOTS, CHECKPOINTS Y ROLLBACK

### FEAT-12.01 — Protección del proyecto · origen A:FEAT-12.01

#### US-12.01 — Crear snapshot

- **Como** sistema **quiero** crear un snapshot antes de cambios de riesgo **para** disponer de un punto de recuperación.
- Origen: A:US-12.01 · Épica: EPIC-12 · Feature: FEAT-12.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: El snapshot tiene identificador.
  - [ ] CA-02: Identifica estado del proyecto.
  - [ ] CA-03: Se registra el motivo.
  - [ ] CA-04: Puede localizarse posteriormente.

#### US-12.02 — Restaurar un snapshot

- **Como** usuario autorizado **quiero** restaurar un snapshot **para** recuperar un estado anterior.
- Origen: A:US-12.02 · Épica: EPIC-12 · Feature: FEAT-12.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Solo snapshots válidos pueden restaurarse.
  - [ ] CA-02: El sistema solicita confirmación cuando corresponda.
  - [ ] CA-03: El estado restaurado coincide con el snapshot seleccionado.
  - [ ] CA-04: La restauración queda registrada.
  - [ ] CA-05: No se pierde silenciosamente el historial posterior.

#### US-12.03 — Recuperar tras fallo de agente

- **Como** sistema **quiero** recuperar el estado anterior a una ejecución fallida **para** evitar daños persistentes.
- Origen: A:US-12.03 · Épica: EPIC-12 · Feature: FEAT-12.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: El fallo se detecta.
  - [ ] CA-02: Se identifica el checkpoint aplicable.
  - [ ] CA-03: Se restaura cuando la política lo determine.
  - [ ] CA-04: El fallo y recuperación quedan registrados.

### FEAT-12.02 — Snapshots · origen B:FEAT-13.01

#### US-12.04

- Enunciado: Como sistema quiero crear un snapshot antes de una operación crítica.
- Origen: B:US-13.01 · Épica: EPIC-12 · Feature: FEAT-12.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- ⚠ Posible solapamiento con US-12.01: revisar si es duplicado, detalle o historia distinta (GAP-006)
- Criterios de aceptación: MISSING

#### US-12.05

- Enunciado: Como sistema quiero sincronizar el snapshot SQLite con el estado Git correspondiente.
- Origen: B:US-13.02 · Épica: EPIC-12 · Feature: FEAT-12.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-12.06

- Enunciado: Como operador quiero identificar exactamente qué estado representa un snapshot.
- Origen: B:US-13.03 · Épica: EPIC-12 · Feature: FEAT-12.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-12.03 — Restauración · origen B:FEAT-13.02

#### US-12.07

- Enunciado: Como operador quiero listar estados restaurables.
- Origen: B:US-13.04 · Épica: EPIC-12 · Feature: FEAT-12.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-12.08

- Enunciado: Como operador quiero restaurar un proyecto a un snapshot estable.
- Origen: B:US-13.05 · Épica: EPIC-12 · Feature: FEAT-12.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- ⚠ Posible solapamiento con US-12.02: revisar si es duplicado, detalle o historia distinta (GAP-006)
- Criterios de aceptación: MISSING

#### US-12.09

- Enunciado: Como sistema quiero restaurar de forma coherente código y contexto ACM.
- Origen: B:US-13.06 · Épica: EPIC-12 · Feature: FEAT-12.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-12.04 — Protección · origen B:FEAT-13.03

#### US-12.10

- Enunciado: Como sistema quiero exigir autorización adicional para operaciones destructivas.
- Origen: B:US-13.07 · Épica: EPIC-12 · Feature: FEAT-12.04 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-12.11

- Enunciado: Como operador quiero conservar evidencia de cada rollback.
- Origen: B:US-13.08 · Épica: EPIC-12 · Feature: FEAT-12.04 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

## EPIC-13 — WATCHDOG Y AUTOSUPERVISIÓN

### FEAT-13.01 — Supervisión · origen A:FEAT-13.01

#### US-13.01 — Detectar agentes bloqueados

- **Como** Watchdog **quiero** detectar ejecuciones que no progresan **para** evitar bloqueos indefinidos.
- Origen: A:US-13.01 · Épica: EPIC-13 · Feature: FEAT-13.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Se mide actividad/progreso.
  - [ ] CA-02: Se aplica un umbral configurable.
  - [ ] CA-03: Una ejecución bloqueada se marca.
  - [ ] CA-04: No se marca como bloqueada una ejecución que continúa progresando.

#### US-13.02 — Gestionar una ejecución bloqueada

- **Como** Watchdog **quiero** aplicar una estrategia de recuperación **para** devolver el sistema a un estado operativo.
- Origen: A:US-13.02 · Épica: EPIC-13 · Feature: FEAT-13.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: La estrategia utilizada queda registrada.
  - [ ] CA-02: Puede cancelar, reintentar o aislar la ejecución según política.
  - [ ] CA-03: No se generan múltiples recuperaciones simultáneas para el mismo fallo.
  - [ ] CA-04: El estado final queda registrado.

#### US-13.03 — Supervisar salud global

- **Como** administrador **quiero** conocer el estado de los servicios y agentes **para** detectar problemas sistémicos.
- Origen: A:US-13.03 · Épica: EPIC-13 · Feature: FEAT-13.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Se muestran componentes relevantes.
  - [ ] CA-02: Cada componente tiene estado.
  - [ ] CA-03: Un componente degradado queda identificado.
  - [ ] CA-04: La información se actualiza.

### FEAT-13.02 — Health Check · origen B:FEAT-01.03

#### US-13.04

- Enunciado: Como operador quiero ejecutar una comprobación de salud para detectar problemas en la infraestructura ACM.
- Origen: B:US-01.07 · Épica: EPIC-13 · Feature: FEAT-13.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- ⚠ Posible solapamiento con US-13.03: revisar si es duplicado, detalle o historia distinta (GAP-006)
- Criterios de aceptación: MISSING

#### US-13.05

- Enunciado: Como Watchdog quiero detectar inconsistencias de SQLite, relaciones y triggers para impedir operar sobre un estado corrupto.
- Origen: B:US-01.08 · Épica: EPIC-13 · Feature: FEAT-13.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-13.03 — Inspector · origen B:FEAT-10.01

#### US-13.06

- Enunciado: Como Watchdog quiero auditar continuamente la integridad del proyecto.
- Origen: B:US-10.01 · Épica: EPIC-13 · Feature: FEAT-13.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-13.07

- Enunciado: Como Watchdog quiero detectar historias sin criterios.
- Origen: B:US-10.02 · Épica: EPIC-13 · Feature: FEAT-13.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-13.08

- Enunciado: Como Watchdog quiero detectar tareas huérfanas.
- Origen: B:US-10.03 · Épica: EPIC-13 · Feature: FEAT-13.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-13.09

- Enunciado: Como Watchdog quiero detectar cambios no trazables.
- Origen: B:US-10.04 · Épica: EPIC-13 · Feature: FEAT-13.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-13.04 — Semáforo · origen B:FEAT-10.02

#### US-13.10

- Enunciado: Como operador quiero visualizar el estado de salud del proyecto mediante indicadores de gobernanza.
- Origen: B:US-10.05 · Épica: EPIC-13 · Feature: FEAT-13.04 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-13.11

- Enunciado: Como sistema quiero bloquear automáticamente operaciones que incumplan reglas críticas.
- Origen: B:US-10.06 · Épica: EPIC-13 · Feature: FEAT-13.04 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-13.05 — Auditoría · origen B:FEAT-10.03

#### US-13.12

- Enunciado: Como operador quiero ejecutar una auditoría completa de gobernanza.
- Origen: B:US-10.07 · Épica: EPIC-13 · Feature: FEAT-13.05 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-13.13

- Enunciado: Como sistema quiero conservar el resultado histórico de las auditorías.
- Origen: B:US-10.08 · Épica: EPIC-13 · Feature: FEAT-13.05 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

## EPIC-14 — MCP Y HERRAMIENTAS

### FEAT-14.01 — MCP · origen A:FEAT-14.01

#### US-14.01 — Registrar un servidor MCP

- **Como** administrador **quiero** registrar un servidor MCP **para** proporcionar herramientas a los agentes.
- Origen: A:US-14.01 · Épica: EPIC-14 · Feature: FEAT-14.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: El servidor tiene identificador.
  - [ ] CA-02: Se valida su configuración.
  - [ ] CA-03: Sus herramientas se descubren cuando está disponible.
  - [ ] CA-04: Un servidor inválido no queda activo.

#### US-14.02 — Asignar MCP a un proyecto

- **Como** administrador **quiero** asociar un MCP a un proyecto **para** limitar su contexto y disponibilidad.
- Origen: A:US-14.02 · Épica: EPIC-14 · Feature: FEAT-14.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: El MCP puede habilitarse para proyectos concretos.
  - [ ] CA-02: Un agente de otro proyecto no puede utilizarlo si carece de autorización.
  - [ ] CA-03: El vínculo queda registrado.

#### US-14.03 — Ejecutar una herramienta MCP

- **Como** agente IA **quiero** invocar una herramienta MCP autorizada **para** realizar una operación externa.
- Origen: A:US-14.03 · Épica: EPIC-14 · Feature: FEAT-14.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: La herramienta debe estar disponible.
  - [ ] CA-02: La llamada utiliza los parámetros definidos.
  - [ ] CA-03: El resultado queda asociado a la ejecución.
  - [ ] CA-04: Los errores se devuelven al agente sin marcar éxito.
  - [ ] CA-05: Las herramientas no autorizadas son rechazadas.

### FEAT-14.02 — MCP · origen B:FEAT-15.01

#### US-14.04

- Enunciado: Como agente IA quiero conectarme a ACM mediante MCP.
- Origen: B:US-15.01 · Épica: EPIC-14 · Feature: FEAT-14.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-14.05

- Enunciado: Como agente quiero descubrir las herramientas MCP disponibles.
- Origen: B:US-15.02 · Épica: EPIC-14 · Feature: FEAT-14.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-14.06

- Enunciado: Como agente quiero ejecutar operaciones sobre el proyecto mediante herramientas MCP.
- Origen: B:US-15.03 · Épica: EPIC-14 · Feature: FEAT-14.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-14.03 — Multi-proyecto · origen B:FEAT-15.02

#### US-14.07

- Enunciado: Como operador quiero gestionar múltiples proyectos desde una misma instancia MCP.
- Origen: B:US-15.04 · Épica: EPIC-14 · Feature: FEAT-14.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-14.08

- Enunciado: Como agente quiero seleccionar explícitamente el proyecto sobre el que opero.
- Origen: B:US-15.05 · Épica: EPIC-14 · Feature: FEAT-14.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-14.09

- Enunciado: Como sistema quiero impedir que una sesión acceda accidentalmente a otro proyecto.
- Origen: B:US-15.06 · Épica: EPIC-14 · Feature: FEAT-14.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-14.04 — Auditoría MCP · origen B:FEAT-15.03

#### US-14.10

- Enunciado: Como operador quiero conocer qué herramienta MCP ha invocado cada agente.
- Origen: B:US-15.07 · Épica: EPIC-14 · Feature: FEAT-14.04 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-14.11

- Enunciado: Como sistema quiero registrar argumentos, resultado, duración y estado de cada invocación.
- Origen: B:US-15.08 · Épica: EPIC-14 · Feature: FEAT-14.04 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

## EPIC-15 — SKILLS Y CAPACIDADES REUTILIZABLES

### FEAT-15.01 — Skills · origen A:FEAT-15.01

#### US-15.01 — Registrar una Skill

- **Como** administrador **quiero** registrar una Skill reutilizable **para** ampliar las capacidades de los agentes.
- Origen: A:US-15.01 · Épica: EPIC-15 · Feature: FEAT-15.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: La Skill tiene identificador y versión.
  - [ ] CA-02: Declara sus capacidades.
  - [ ] CA-03: Declara dependencias.
  - [ ] CA-04: Una Skill inválida no se activa.

#### US-15.02 — Asignar una Skill a un agente

- **Como** administrador **quiero** asignar Skills **para** configurar las capacidades de cada agente.
- Origen: A:US-15.02 · Épica: EPIC-15 · Feature: FEAT-15.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Solo Skills disponibles pueden asignarse.
  - [ ] CA-02: La asignación queda registrada.
  - [ ] CA-03: El agente puede descubrir las Skills habilitadas.
  - [ ] CA-04: Una Skill retirada deja de estar disponible según la política definida.

#### US-15.03 — Versionar Skills

- **Como** administrador **quiero** mantener versiones de Skills **para** evitar cambios incompatibles inesperados.
- Origen: A:US-15.03 · Épica: EPIC-15 · Feature: FEAT-15.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Cada versión tiene identificador.
  - [ ] CA-02: Una instancia existente conserva la versión asignada cuando corresponda.
  - [ ] CA-03: Las actualizaciones quedan registradas.
  - [ ] CA-04: Puede identificarse qué versión utilizó una ejecución.

### FEAT-15.02 — Distribución de skills ACM **[v1.1]** · origen B:FEAT-15.04

#### US-15.04

- Enunciado: Como agente IA quiero que, al conectarme al servidor MCP de ACM, este me indique cómo usarlo y qué skills tiene disponibles, para operar correctamente desde el primer momento.
- Origen: B:US-15.09 · Épica: EPIC-15 · Feature: FEAT-15.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: La respuesta de inicialización MCP incluye `instructions` que indican al agente que descargue y cargue las skills de ACM antes de operar.
  - [ ] CA-02: El servidor declara la capacidad `resources` y la extensión `io.modelcontextprotocol/skills`.
  - [ ] CA-03: `skills/list` devuelve todas las skills oficiales de ACM con `name`, `description`, `uri` y la lista de recursos con `digest` sha256 y `size`.

#### US-15.05

- Enunciado: Como agente IA quiero descargar todas las skills de ACM desde el propio servidor MCP para saber usarlo y sacarle el máximo partido.
- Origen: B:US-15.10 · Épica: EPIC-15 · Feature: FEAT-15.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Cada archivo de cada skill se puede leer con `resources/read` bajo la URI `skill://acm/<nombre>/<archivo>`.
  - [ ] CA-02: `skills/get` devuelve la skill solicitada y una skill inexistente devuelve el error `-32602`.
  - [ ] CA-03: Los clientes sin soporte de la extensión pueden listar y obtener las mismas skills mediante herramientas MCP de ACM.

#### US-15.06

- Enunciado: Como agente IA quiero saber si las skills que descargué están desactualizadas para volver a descargarlas.
- Origen: B:US-15.11 · Épica: EPIC-15 · Feature: FEAT-15.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Cada SKILL.md declara `version` en su frontmatter.
  - [ ] CA-02: El `digest` de un recurso cambia si y solo si cambia su contenido.
  - [ ] CA-03: Cuando cambia el catálogo de skills, el servidor emite la notificación de cambio de lista de recursos.

#### US-15.07

- Enunciado: Como operador quiero que ACM gestione el catálogo de skills que sirve para controlar qué aprenden los agentes.
- Origen: B:US-15.12 · Épica: EPIC-15 · Feature: FEAT-15.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Las skills oficiales se versionan junto con el código de ACM.
  - [ ] CA-02: Una skill retirada deja de aparecer en `skills/list` y su URI devuelve error.
  - [ ] CA-03: Cada descarga de skill queda registrada en la auditoría MCP (US-15.08).

### FEAT-15.03 — Skills ACM · origen B:FEAT-22.01

#### US-15.08

- Enunciado: Como agente quiero disponer de una skill que explique el esquema ACM.
- Origen: B:US-22.01 · Épica: EPIC-15 · Feature: FEAT-15.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-15.09

- Enunciado: Como agente quiero disponer de una skill de validación INVEST.
- Origen: B:US-22.02 · Épica: EPIC-15 · Feature: FEAT-15.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-15.10

- Enunciado: Como agente quiero disponer de una skill de Discovery Socrático.
- Origen: B:US-22.03 · Épica: EPIC-15 · Feature: FEAT-15.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-15.11

- Enunciado: Como agente quiero disponer de una skill de análisis de errores.
- Origen: B:US-22.04 · Épica: EPIC-15 · Feature: FEAT-15.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-15.12

- Enunciado: Como agente quiero disponer de una skill de documentación.
- Origen: B:US-22.05 · Épica: EPIC-15 · Feature: FEAT-15.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-15.04 — Selección dinámica · origen B:FEAT-22.02

#### US-15.13

- Enunciado: Como sistema quiero seleccionar las skills relevantes según la tarea.
- Origen: B:US-22.06 · Épica: EPIC-15 · Feature: FEAT-15.04 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-15.14

- Enunciado: Como sistema quiero inyectar el contexto de una skill antes de ejecutar una operación.
- Origen: B:US-22.07 · Épica: EPIC-15 · Feature: FEAT-15.04 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-15.05 — Auditoría · origen B:FEAT-22.03

#### US-15.15

- Enunciado: Como operador quiero consultar qué skills utiliza un agente.
- Origen: B:US-22.08 · Épica: EPIC-15 · Feature: FEAT-15.05 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-15.16

- Enunciado: Como operador quiero auditar las instrucciones proporcionadas por una skill.
- Origen: B:US-22.09 · Épica: EPIC-15 · Feature: FEAT-15.05 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-15.06 — Sandbox · origen B:FEAT-22.04

#### US-15.17

- Enunciado: Como desarrollador quiero probar una skill sin afectar un proyecto real.
- Origen: B:US-22.10 · Épica: EPIC-15 · Feature: FEAT-15.06 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-15.18

- Enunciado: Como desarrollador quiero consultar el resultado de una skill de prueba.
- Origen: B:US-22.11 · Épica: EPIC-15 · Feature: FEAT-15.06 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-15.07 — Skills activas · origen B:FEAT-40.01

#### US-15.19

- Enunciado: Como operador quiero ver qué skill está utilizando un agente.
- Origen: B:US-40.01 · Épica: EPIC-15 · Feature: FEAT-15.07 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-15.20

- Enunciado: Como operador quiero consultar la ejecución de una skill.
- Origen: B:US-40.02 · Épica: EPIC-15 · Feature: FEAT-15.07 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-15.08 — Prompts · origen B:FEAT-40.02

#### US-15.21

- Enunciado: Como desarrollador quiero inspeccionar las instrucciones asociadas a una skill.
- Origen: B:US-40.03 · Épica: EPIC-15 · Feature: FEAT-15.08 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-15.22

- Enunciado: Como desarrollador quiero probar una variante de una skill en sandbox.
- Origen: B:US-40.04 · Épica: EPIC-15 · Feature: FEAT-15.08 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

## EPIC-16 — RAG Y MEMORIA SEMÁNTICA

### FEAT-16.01 — Conocimiento · origen A:FEAT-16.01

#### US-16.01 — Indexar documentación del proyecto

- **Como** sistema **quiero** indexar documentación relevante **para** que los agentes puedan recuperarla semánticamente.
- Origen: A:US-16.01 · Épica: EPIC-16 · Feature: FEAT-16.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Los documentos seleccionados se procesan.
  - [ ] CA-02: Se generan representaciones indexables.
  - [ ] CA-03: Se conserva referencia al documento original.
  - [ ] CA-04: Los documentos modificados pueden reindexarse.
  - [ ] CA-05: Los documentos eliminados dejan de recuperarse.

#### US-16.02 — Recuperar contexto mediante RAG

- **Como** agente IA **quiero** recuperar conocimiento relevante **para** responder y actuar con contexto del proyecto.
- Origen: A:US-16.02 · Épica: EPIC-16 · Feature: FEAT-16.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: La consulta produce resultados relacionados.
  - [ ] CA-02: Cada resultado conserva su fuente.
  - [ ] CA-03: El agente recibe contexto suficiente para utilizarlo.
  - [ ] CA-04: Una consulta sin resultados no inventa fuentes.

#### US-16.03 — Separar memoria de instancia y memoria compartida

- **Como** arquitectura de agentes **quiero** separar memoria privada y compartida **para** evitar contaminación de contexto.
- Origen: A:US-16.03 · Épica: EPIC-16 · Feature: FEAT-16.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Una memoria privada no aparece en otra instancia no autorizada.
  - [ ] CA-02: La memoria compartida puede ser consultada por agentes autorizados.
  - [ ] CA-03: El origen de cada memoria es identificable.

### FEAT-16.02 — Indexación · origen B:FEAT-21.01

#### US-16.04

- Enunciado: Como sistema quiero indexar documentación relevante del proyecto.
- Origen: B:US-21.01 · Épica: EPIC-16 · Feature: FEAT-16.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- ⚠ Posible solapamiento con US-16.01: revisar si es duplicado, detalle o historia distinta (GAP-006)
- Criterios de aceptación: MISSING

#### US-16.05

- Enunciado: Como sistema quiero indexar código fuente de forma incremental.
- Origen: B:US-21.02 · Épica: EPIC-16 · Feature: FEAT-16.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-16.06

- Enunciado: Como sistema quiero actualizar los embeddings cuando cambien los archivos.
- Origen: B:US-21.03 · Épica: EPIC-16 · Feature: FEAT-16.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-16.03 — Recuperación · origen B:FEAT-21.02

#### US-16.07

- Enunciado: Como agente quiero recuperar contexto semánticamente relevante antes de ejecutar una tarea.
- Origen: B:US-21.04 · Épica: EPIC-16 · Feature: FEAT-16.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- ⚠ Posible solapamiento con US-16.02: revisar si es duplicado, detalle o historia distinta (GAP-006)
- Criterios de aceptación: MISSING

#### US-16.08

- Enunciado: Como sistema quiero combinar información estructurada de SQLite con información semántica.
- Origen: B:US-21.05 · Épica: EPIC-16 · Feature: FEAT-16.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-16.04 — Reranking · origen B:FEAT-21.03

#### US-16.09

- Enunciado: Como sistema quiero ordenar los resultados RAG por relevancia.
- Origen: B:US-21.06 · Épica: EPIC-16 · Feature: FEAT-16.04 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-16.10

- Enunciado: Como agente quiero recibir contexto reducido a los fragmentos más relevantes.
- Origen: B:US-21.07 · Épica: EPIC-16 · Feature: FEAT-16.04 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-16.05 — Caché · origen B:FEAT-21.04

#### US-16.11

- Enunciado: Como sistema quiero reutilizar resultados RAG equivalentes para reducir latencia.
- Origen: B:US-21.08 · Épica: EPIC-16 · Feature: FEAT-16.05 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-16.06 — Auditoría RAG · origen B:FEAT-21.05

#### US-16.12

- Enunciado: Como operador quiero saber qué documentos y fragmentos influyeron en una respuesta.
- Origen: B:US-21.09 · Épica: EPIC-16 · Feature: FEAT-16.06 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-16.13

- Enunciado: Como Watchdog quiero detectar contaminación de contexto entre proyectos.
- Origen: B:US-21.10 · Épica: EPIC-16 · Feature: FEAT-16.06 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

## EPIC-17 — PRODUCT GRAPH

### FEAT-17.01 — Grafo del producto · origen A:FEAT-17.01

#### US-17.01 — Representar entidades del producto como grafo

- **Como** sistema **quiero** representar requisitos, features, historias, agentes y componentes como nodos **para** relacionarlos explícitamente.
- Origen: A:US-17.01 · Épica: EPIC-17 · Feature: FEAT-17.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Las entidades relevantes pueden representarse.
  - [ ] CA-02: Cada nodo tiene identificador.
  - [ ] CA-03: Las relaciones tienen tipo.
  - [ ] CA-04: No se crean relaciones inexistentes.

#### US-17.02 — Consultar dependencias mediante Product Graph

- **Como** arquitecto **quiero** consultar relaciones entre elementos **para** conocer el impacto de un cambio.
- Origen: A:US-17.02 · Épica: EPIC-17 · Feature: FEAT-17.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Una consulta devuelve relaciones existentes.
  - [ ] CA-02: Puede seguirse una dependencia hasta su origen.
  - [ ] CA-03: El sistema identifica elementos afectados.
  - [ ] CA-04: Los resultados respetan el proyecto seleccionado.

#### US-17.03 — Detectar elementos huérfanos

- **Como** sistema de calidad **quiero** detectar nodos sin relaciones necesarias **para** encontrar requisitos o trabajo perdido.
- Origen: A:US-17.03 · Épica: EPIC-17 · Feature: FEAT-17.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Un requisito sin historia aparece como huérfano.
  - [ ] CA-02: Una historia sin requisito queda identificada.
  - [ ] CA-03: Una dependencia rota queda señalada.

### FEAT-17.02 — Módulos · origen B:FEAT-02.01

#### US-17.04

- Enunciado: Como Product Owner quiero crear módulos funcionales para estructurar el producto.
- Origen: B:US-02.01 · Épica: EPIC-17 · Feature: FEAT-17.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-17.05

- Enunciado: Como Product Owner quiero crear submódulos jerárquicos para representar dominios complejos.
- Origen: B:US-02.02 · Épica: EPIC-17 · Feature: FEAT-17.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-17.06

- Enunciado: Como agente quiero consultar el árbol funcional completo para localizar dónde pertenece una funcionalidad.
- Origen: B:US-02.03 · Épica: EPIC-17 · Feature: FEAT-17.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-17.07

- Enunciado: Como operador quiero visualizar el árbol funcional para comprender la estructura del producto.
- Origen: B:US-02.04 · Épica: EPIC-17 · Feature: FEAT-17.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-17.03 — Funcionalidades · origen B:FEAT-02.02

#### US-17.08

- Enunciado: Como Product Owner quiero registrar una funcionalidad con descripción, valor, reglas y restricciones.
- Origen: B:US-02.05 · Épica: EPIC-17 · Feature: FEAT-17.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-17.09

- Enunciado: Como Product Owner quiero actualizar el estado de una funcionalidad para distinguir ideas de funcionalidades aprobadas.
- Origen: B:US-02.06 · Épica: EPIC-17 · Feature: FEAT-17.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-17.10

- Enunciado: Como agente quiero consultar las funcionalidades de un módulo antes de proponer épicas.
- Origen: B:US-02.07 · Épica: EPIC-17 · Feature: FEAT-17.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-17.04 — Grafo de conocimiento · origen B:FEAT-33.01

#### US-17.11

- Enunciado: Como sistema quiero representar relaciones entre módulos, archivos, funciones, ADRs e historias.
- Origen: B:US-33.01 · Épica: EPIC-17 · Feature: FEAT-17.04 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-17.12

- Enunciado: Como agente quiero consultar dependencias técnicas antes de modificar un componente.
- Origen: B:US-33.02 · Épica: EPIC-17 · Feature: FEAT-17.04 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-17.05 — Dependencias circulares · origen B:FEAT-33.02

#### US-17.13

- Enunciado: Como Watchdog quiero detectar dependencias circulares.
- Origen: B:US-33.03 · Épica: EPIC-17 · Feature: FEAT-17.05 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-17.14

- Enunciado: Como operador quiero visualizar dependencias problemáticas.
- Origen: B:US-33.04 · Épica: EPIC-17 · Feature: FEAT-17.05 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-17.06 — Impact Analysis · origen B:FEAT-33.03

#### US-17.15

- Enunciado: Como arquitecto quiero conocer el impacto potencial de modificar un componente.
- Origen: B:US-33.05 · Épica: EPIC-17 · Feature: FEAT-17.06 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-17.16

- Enunciado: Como agente quiero identificar requisitos y funcionalidades afectadas antes de realizar un cambio.
- Origen: B:US-33.06 · Épica: EPIC-17 · Feature: FEAT-17.06 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-17.07 — Grafo E2E · origen B:FEAT-46.01

#### US-17.17

- Enunciado: Como operador quiero visualizar el grafo completo de trazabilidad.
- Origen: B:US-46.01 · Épica: EPIC-17 · Feature: FEAT-17.07 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-17.08 — Grafo RAG · origen B:FEAT-46.02

#### US-17.18

- Enunciado: Como operador quiero visualizar las relaciones entre consultas y fragmentos recuperados.
- Origen: B:US-46.02 · Épica: EPIC-17 · Feature: FEAT-17.08 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-17.09 — Grafo arquitectónico · origen B:FEAT-46.03

#### US-17.19

- Enunciado: Como arquitecto quiero visualizar dependencias entre módulos.
- Origen: B:US-46.03 · Épica: EPIC-17 · Feature: FEAT-17.09 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-17.20

- Enunciado: Como arquitecto quiero identificar visualmente ciclos y nodos críticos.
- Origen: B:US-46.04 · Épica: EPIC-17 · Feature: FEAT-17.09 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-17.10 — Grafo 3D · origen B:FEAT-46.04

#### US-17.21

- Enunciado: Como operador quiero disponer de una representación tridimensional opcional de grafos complejos.
- Origen: B:US-46.05 · Épica: EPIC-17 · Feature: FEAT-17.10 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

## EPIC-18 — SQLITE Y PERSISTENCIA

### FEAT-18.01 — Persistencia estructurada · origen A:FEAT-18.01

#### US-18.01 — Persistir estado operativo

- **Como** sistema **quiero** almacenar el estado estructurado del proyecto **para** poder recuperarlo después de reinicios.
- Origen: A:US-18.01 · Épica: EPIC-18 · Feature: FEAT-18.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: El estado relevante queda almacenado.
  - [ ] CA-02: Un reinicio no elimina información persistente.
  - [ ] CA-03: El proyecto puede reconstruirse desde la persistencia.
  - [ ] CA-04: Una escritura fallida no deja datos inconsistentes.

#### US-18.02 — Mantener transacciones consistentes

- **Como** sistema **quiero** realizar operaciones relacionadas de forma transaccional **para** evitar estados parciales.
- Origen: A:US-18.02 · Épica: EPIC-18 · Feature: FEAT-18.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Una operación completamente válida se confirma.
  - [ ] CA-02: Un fallo durante la transacción revierte los cambios afectados.
  - [ ] CA-03: No quedan registros parcialmente creados.

#### US-18.03 — Gestionar migraciones

- **Como** desarrollador **quiero** versionar el esquema SQLite **para** actualizar la estructura sin perder datos.
- Origen: A:US-18.03 · Épica: EPIC-18 · Feature: FEAT-18.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Cada migración tiene versión.
  - [ ] CA-02: Las migraciones se ejecutan en orden.
  - [ ] CA-03: Una migración fallida no deja el esquema marcado como completado.
  - [ ] CA-04: La versión actual puede consultarse.

### FEAT-18.02 — Rendimiento · origen B:FEAT-34.01

#### US-18.04

- Enunciado: Como sistema quiero detectar consultas SQLite lentas.
- Origen: B:US-34.01 · Épica: EPIC-18 · Feature: FEAT-18.02 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-18.05

- Enunciado: Como sistema quiero registrar métricas de consultas.
- Origen: B:US-34.02 · Épica: EPIC-18 · Feature: FEAT-18.02 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-18.03 — Índices · origen B:FEAT-34.02

#### US-18.06

- Enunciado: Como sistema quiero detectar oportunidades de indexación.
- Origen: B:US-34.03 · Épica: EPIC-18 · Feature: FEAT-18.03 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-18.07

- Enunciado: Como arquitecto quiero revisar las propuestas de optimización antes de aplicarlas automáticamente.
- Origen: B:US-34.04 · Épica: EPIC-18 · Feature: FEAT-18.03 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-18.04 — Concurrencia · origen B:FEAT-34.03

#### US-18.08

- Enunciado: Como sistema quiero gestionar transacciones concurrentes sin corrupción.
- Origen: B:US-34.05 · Épica: EPIC-18 · Feature: FEAT-18.04 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-18.09

- Enunciado: Como sistema quiero reintentar operaciones cuando se produzcan bloqueos transitorios.
- Origen: B:US-34.06 · Épica: EPIC-18 · Feature: FEAT-18.04 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

## EPIC-19 — CONCURRENCIA Y LOCKING

### FEAT-19.01 — Ejecuciones concurrentes · origen A:FEAT-19.01

#### US-19.01 — Controlar acceso concurrente al mismo recurso

- **Como** sistema **quiero** controlar el acceso concurrente **para** evitar corrupción o modificaciones incompatibles.
- Origen: A:US-19.01 · Épica: EPIC-19 · Feature: FEAT-19.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Dos operaciones incompatibles no modifican simultáneamente el recurso protegido.
  - [ ] CA-02: La segunda operación recibe estado de espera o rechazo según política.
  - [ ] CA-03: Los locks se liberan después de completar o fallar.

#### US-19.02 — Detectar deadlocks o locks abandonados

- **Como** Watchdog **quiero** detectar locks que no progresan **para** evitar bloqueos permanentes.
- Origen: A:US-19.02 · Épica: EPIC-19 · Feature: FEAT-19.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Un lock supera el umbral definido y queda identificado.
  - [ ] CA-02: El sistema conserva información sobre su propietario.
  - [ ] CA-03: Se ejecuta la política de recuperación.
  - [ ] CA-04: La recuperación queda registrada.

#### US-19.03 — Evitar ejecuciones duplicadas

- **Como** orquestador **quiero** impedir que una misma tarea se ejecute dos veces simultáneamente **para** evitar cambios duplicados.
- Origen: A:US-19.03 · Épica: EPIC-19 · Feature: FEAT-19.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Una tarea activa no puede iniciarse una segunda vez sin una política explícita.
  - [ ] CA-02: Las solicitudes duplicadas reciben el estado de la ejecución existente.
  - [ ] CA-03: No se crean dos ejecuciones funcionalmente equivalentes.

### FEAT-19.02 — Locking · origen B:FEAT-17.01

#### US-19.04

- Enunciado: Como agente quiero reservar una tarea antes de modificarla.
- Origen: B:US-17.01 · Épica: EPIC-19 · Feature: FEAT-19.02 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-19.05

- Enunciado: Como sistema quiero impedir que dos agentes ejecuten simultáneamente la misma tarea.
- Origen: B:US-17.02 · Épica: EPIC-19 · Feature: FEAT-19.02 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- ⚠ Posible solapamiento con US-19.03: revisar si es duplicado, detalle o historia distinta (GAP-006)
- Criterios de aceptación: MISSING

#### US-19.06

- Enunciado: Como sistema quiero detectar modificaciones concurrentes del mismo recurso.
- Origen: B:US-17.03 · Épica: EPIC-19 · Feature: FEAT-19.02 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- ⚠ Posible solapamiento con US-19.01: revisar si es duplicado, detalle o historia distinta (GAP-006)
- Criterios de aceptación: MISSING

### FEAT-19.03 — Broadcast Intent · origen B:FEAT-17.02

#### US-19.07

- Enunciado: Como agente quiero anunciar mi intención de modificar un recurso.
- Origen: B:US-17.04 · Épica: EPIC-19 · Feature: FEAT-19.03 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-19.08

- Enunciado: Como agente quiero conocer qué recursos están siendo utilizados por otros agentes.
- Origen: B:US-17.05 · Épica: EPIC-19 · Feature: FEAT-19.03 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

## EPIC-20 — RBAC, IDENTIDAD Y TOKENS

### FEAT-20.01 — Seguridad · origen A:FEAT-20.01

#### US-20.01 — Gestionar roles

- **Como** administrador **quiero** asignar roles **para** controlar capacidades.
- Origen: A:US-20.01 · Épica: EPIC-20 · Feature: FEAT-20.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Los roles disponibles están definidos.
  - [ ] CA-02: Un usuario puede recibir un rol autorizado.
  - [ ] CA-03: Los permisos se aplican inmediatamente según política.
  - [ ] CA-04: Los cambios quedan auditados.

#### US-20.02 — Autorizar operaciones

- **Como** sistema **quiero** comprobar permisos antes de ejecutar operaciones **para** impedir accesos no autorizados.
- Origen: A:US-20.02 · Épica: EPIC-20 · Feature: FEAT-20.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Una operación permitida se ejecuta.
  - [ ] CA-02: Una operación no permitida es rechazada.
  - [ ] CA-03: El rechazo no modifica el recurso protegido.
  - [ ] CA-04: El intento queda registrado cuando la política lo requiera.

#### US-20.03 — Gestionar tokens

- **Como** administrador **quiero** crear y revocar tokens **para** permitir integraciones seguras.
- Origen: A:US-20.03 · Épica: EPIC-20 · Feature: FEAT-20.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Cada token tiene identidad y permisos.
  - [ ] CA-02: Un token revocado deja de autorizar operaciones.
  - [ ] CA-03: Los tokens no se muestran completos después de su creación.
  - [ ] CA-04: El uso queda trazado.

### FEAT-20.02 — Identidad · origen B:FEAT-16.01

#### US-20.04

- Enunciado: Como operador quiero disponer de credenciales independientes para usuarios y agentes.
- Origen: B:US-16.01 · Épica: EPIC-20 · Feature: FEAT-20.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-20.05

- Enunciado: Como sistema quiero autenticar cada conexión MCP.
- Origen: B:US-16.02 · Épica: EPIC-20 · Feature: FEAT-20.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-20.03 — RBAC · origen B:FEAT-16.02

#### US-20.06

- Enunciado: Como operador quiero asignar roles a usuarios y agentes.
- Origen: B:US-16.03 · Épica: EPIC-20 · Feature: FEAT-20.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- ⚠ Posible solapamiento con US-20.01: revisar si es duplicado, detalle o historia distinta (GAP-006)
- Criterios de aceptación: MISSING

#### US-20.07

- Enunciado: Como sistema quiero limitar las herramientas disponibles según el rol.
- Origen: B:US-16.04 · Épica: EPIC-20 · Feature: FEAT-20.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-20.08

- Enunciado: Como sistema quiero restringir el acceso por proyecto.
- Origen: B:US-16.05 · Épica: EPIC-20 · Feature: FEAT-20.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-20.04 — Tokens · origen B:FEAT-16.03

#### US-20.09

- Enunciado: Como operador quiero crear tokens específicos para agentes.
- Origen: B:US-16.06 · Épica: EPIC-20 · Feature: FEAT-20.04 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- ⚠ Posible solapamiento con US-20.03: revisar si es duplicado, detalle o historia distinta (GAP-006)
- Criterios de aceptación: MISSING

#### US-20.10

- Enunciado: Como operador quiero revocar un token inmediatamente.
- Origen: B:US-16.07 · Épica: EPIC-20 · Feature: FEAT-20.04 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-20.11

- Enunciado: Como sistema quiero registrar el uso de cada token.
- Origen: B:US-16.08 · Épica: EPIC-20 · Feature: FEAT-20.04 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-20.05 — Operaciones sensibles · origen B:FEAT-16.04

#### US-20.12

- Enunciado: Como operador quiero exigir autorización adicional para purgar un proyecto.
- Origen: B:US-16.09 · Épica: EPIC-20 · Feature: FEAT-20.05 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-20.13

- Enunciado: Como operador quiero exigir autorización adicional para ejecutar rollback.
- Origen: B:US-16.10 · Épica: EPIC-20 · Feature: FEAT-20.05 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-20.14

- Enunciado: Como sistema quiero impedir operaciones destructivas no autorizadas.
- Origen: B:US-16.11 · Épica: EPIC-20 · Feature: FEAT-20.05 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- ⚠ Posible solapamiento con US-20.02: revisar si es duplicado, detalle o historia distinta (GAP-006)
- Criterios de aceptación: MISSING

### FEAT-20.06 — Revocación · origen B:FEAT-28.03

#### US-20.15

- Enunciado: Como operador quiero revocar las credenciales de un agente en tiempo real.
- Origen: B:US-28.06 · Épica: EPIC-20 · Feature: FEAT-20.06 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

## EPIC-21 — WEBSOCKETS Y EVENT BUS

### FEAT-21.01 — Comunicación reactiva · origen A:FEAT-21.01

#### US-21.01 — Emitir eventos de dominio

- **Como** sistema **quiero** publicar eventos cuando cambia el estado **para** informar a los componentes interesados.
- Origen: A:US-21.01 · Épica: EPIC-21 · Feature: FEAT-21.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Un cambio relevante produce el evento definido.
  - [ ] CA-02: El evento contiene identificador y contexto.
  - [ ] CA-03: Un evento no se publica si la operación ha sido revertida.

#### US-21.02 — Suscribirse a eventos

- **Como** cliente **quiero** suscribirme a cambios **para** actualizar mi estado automáticamente.
- Origen: A:US-21.02 · Épica: EPIC-21 · Feature: FEAT-21.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Una suscripción válida recibe eventos correspondientes.
  - [ ] CA-02: No recibe eventos de proyectos no autorizados.
  - [ ] CA-03: Una desconexión libera la suscripción.

#### US-21.03 — Recuperar estado tras reconexión

- **Como** cliente **quiero** recuperar eventos/estado después de una desconexión **para** volver a sincronizarme.
- Origen: A:US-21.03 · Épica: EPIC-21 · Feature: FEAT-21.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: La reconexión se detecta.
  - [ ] CA-02: El cliente obtiene el estado necesario.
  - [ ] CA-03: Los cambios no se duplican.
  - [ ] CA-04: El estado final coincide con el servidor.

### FEAT-21.02 — Eventos · origen B:FEAT-18.01

#### US-21.04

- Enunciado: Como frontend quiero recibir cambios de estado del proyecto en tiempo real.
- Origen: B:US-18.01 · Épica: EPIC-21 · Feature: FEAT-21.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-21.05

- Enunciado: Como frontend quiero recibir cambios de tareas sin refrescar la página.
- Origen: B:US-18.02 · Épica: EPIC-21 · Feature: FEAT-21.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-21.06

- Enunciado: Como frontend quiero recibir movimientos del Kanban en tiempo real.
- Origen: B:US-18.03 · Épica: EPIC-21 · Feature: FEAT-21.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-21.03 — Actividad de agentes · origen B:FEAT-18.02

#### US-21.07

- Enunciado: Como operador quiero ver cuándo un agente comienza una tarea.
- Origen: B:US-18.04 · Épica: EPIC-21 · Feature: FEAT-21.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-21.08

- Enunciado: Como operador quiero ver cuándo termina una tarea.
- Origen: B:US-18.05 · Épica: EPIC-21 · Feature: FEAT-21.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-21.09

- Enunciado: Como operador quiero ver qué herramienta está ejecutando un agente.
- Origen: B:US-18.06 · Épica: EPIC-21 · Feature: FEAT-21.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-21.04 — Presencia · origen B:FEAT-18.03

#### US-21.10

- Enunciado: Como operador quiero conocer qué agentes están conectados.
- Origen: B:US-18.07 · Épica: EPIC-21 · Feature: FEAT-21.04 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-21.11

- Enunciado: Como operador quiero conocer el estado actual de cada agente.
- Origen: B:US-18.08 · Épica: EPIC-21 · Feature: FEAT-21.04 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

## EPIC-22 — MODELOS IA LOCALES Y OLLAMA

### FEAT-22.01 — ModelOps · origen A:FEAT-22.01

#### US-22.01 — Detectar modelos disponibles

- **Como** sistema **quiero** consultar los modelos disponibles **para** seleccionar un modelo compatible con una tarea.
- Origen: A:US-22.01 · Épica: EPIC-22 · Feature: FEAT-22.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Se consulta el runtime configurado.
  - [ ] CA-02: Los modelos detectados se identifican.
  - [ ] CA-03: Un runtime inaccesible produce un estado de error.
  - [ ] CA-04: El sistema no afirma que un modelo existe si no ha sido detectado.

#### US-22.02 — Seleccionar modelo para un agente

- **Como** administrador **quiero** asignar un modelo a un agente **para** controlar su capacidad de inferencia.
- Origen: A:US-22.02 · Épica: EPIC-22 · Feature: FEAT-22.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Solo modelos disponibles pueden seleccionarse como activos.
  - [ ] CA-02: La configuración queda vinculada al agente.
  - [ ] CA-03: La ejecución registra qué modelo utilizó.

#### US-22.03 — Ejecutar inferencia local

- **Como** agente IA **quiero** utilizar un modelo local **para** ejecutar tareas sin depender necesariamente de un proveedor cloud.
- Origen: A:US-22.03 · Épica: EPIC-22 · Feature: FEAT-22.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: La petición llega al modelo configurado.
  - [ ] CA-02: La respuesta queda vinculada a la ejecución.
  - [ ] CA-03: Un fallo del modelo genera estado de error.
  - [ ] CA-04: No se declara éxito si no existe respuesta válida.

### FEAT-22.02 — Conexión · origen B:FEAT-23.01

#### US-22.04

- Enunciado: Como operador quiero conectar una instancia Ollama a ACM.
- Origen: B:US-23.01 · Épica: EPIC-22 · Feature: FEAT-22.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-22.05

- Enunciado: Como sistema quiero detectar modelos disponibles en Ollama.
- Origen: B:US-23.02 · Épica: EPIC-22 · Feature: FEAT-22.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- ⚠ Posible solapamiento con US-22.01: revisar si es duplicado, detalle o historia distinta (GAP-006)
- Criterios de aceptación: MISSING

### FEAT-22.03 — Selección · origen B:FEAT-23.02

#### US-22.06

- Enunciado: Como operador quiero asignar modelos a tipos de tareas.
- Origen: B:US-23.03 · Épica: EPIC-22 · Feature: FEAT-22.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-22.07

- Enunciado: Como sistema quiero seleccionar automáticamente un modelo adecuado para una tarea.
- Origen: B:US-23.04 · Épica: EPIC-22 · Feature: FEAT-22.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- ⚠ Posible solapamiento con US-22.01: revisar si es duplicado, detalle o historia distinta (GAP-006)
- Criterios de aceptación: MISSING

### FEAT-22.04 — Recursos · origen B:FEAT-23.03

#### US-22.08

- Enunciado: Como sistema quiero supervisar recursos disponibles para modelos locales.
- Origen: B:US-23.05 · Épica: EPIC-22 · Feature: FEAT-22.04 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-22.09

- Enunciado: Como sistema quiero evitar lanzar más inferencias de las que el hardware puede soportar.
- Origen: B:US-23.06 · Épica: EPIC-22 · Feature: FEAT-22.04 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

## EPIC-23 — GOBERNANZA DE INFERENCIA

### FEAT-23.01 — Control de consumo · origen A:FEAT-23.01

#### US-23.01 — Registrar llamadas a modelos

- **Como** administrador **quiero** registrar cada llamada de inferencia **para** conocer consumo y comportamiento.
- Origen: A:US-23.01 · Épica: EPIC-23 · Feature: FEAT-23.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Cada llamada identifica agente y modelo.
  - [ ] CA-02: Se registra timestamp.
  - [ ] CA-03: Se registra resultado.
  - [ ] CA-04: Cuando esté disponible, se registra consumo de tokens.

#### US-23.02 — Aplicar límites de uso

- **Como** administrador **quiero** establecer límites **para** evitar consumo descontrolado.
- Origen: A:US-23.02 · Épica: EPIC-23 · Feature: FEAT-23.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Los límites pueden configurarse.
  - [ ] CA-02: Una operación dentro del límite puede ejecutarse.
  - [ ] CA-03: Una operación que excede el límite es rechazada o aplazada según política.
  - [ ] CA-04: El motivo queda registrado.

#### US-23.03 — Deshabilitar una cuenta o proveedor

- **Como** administrador **quiero** desactivar una fuente de inferencia **para** detener su utilización.
- Origen: A:US-23.03 · Épica: EPIC-23 · Feature: FEAT-23.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Una fuente deshabilitada no recibe nuevas llamadas.
  - [ ] CA-02: Las ejecuciones existentes siguen la política definida.
  - [ ] CA-03: El estado queda visible.

### FEAT-23.02 — Cuotas · origen B:FEAT-28.01

#### US-23.04

- Enunciado: Como operador quiero establecer cuotas por agente.
- Origen: B:US-28.01 · Épica: EPIC-23 · Feature: FEAT-23.02 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-23.05

- Enunciado: Como operador quiero establecer límites de consumo por proyecto.
- Origen: B:US-28.02 · Épica: EPIC-23 · Feature: FEAT-23.02 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- ⚠ Posible solapamiento con US-23.02: revisar si es duplicado, detalle o historia distinta (GAP-006)
- Criterios de aceptación: MISSING

#### US-23.06

- Enunciado: Como sistema quiero bloquear temporalmente a un agente que supere su cuota.
- Origen: B:US-28.03 · Épica: EPIC-23 · Feature: FEAT-23.02 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-23.03 — Rate Limiting · origen B:FEAT-28.02

#### US-23.07

- Enunciado: Como sistema quiero limitar la frecuencia de llamadas MCP.
- Origen: B:US-28.04 · Épica: EPIC-23 · Feature: FEAT-23.03 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-23.08

- Enunciado: Como sistema quiero detectar bucles excesivos de llamadas.
- Origen: B:US-28.05 · Épica: EPIC-23 · Feature: FEAT-23.03 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

## EPIC-24 — GESTIÓN MULTIPROYECTO

### FEAT-24.01 — Contextos aislados · origen A:FEAT-24.01

#### US-24.01 — Trabajar con varios proyectos

- **Como** usuario **quiero** gestionar varios proyectos **para** utilizar el sistema como plataforma de desarrollo.
- Origen: A:US-24.01 · Épica: EPIC-24 · Feature: FEAT-24.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Pueden existir múltiples proyectos.
  - [ ] CA-02: Cada proyecto tiene backlog independiente.
  - [ ] CA-03: Cada proyecto tiene memoria independiente.
  - [ ] CA-04: Cambiar de proyecto cambia todo el contexto operativo.

#### US-24.02 — Compartir recursos autorizados entre proyectos

- **Como** administrador **quiero** definir recursos compartidos **para** reutilizar infraestructura sin mezclar datos.
- Origen: A:US-24.02 · Épica: EPIC-24 · Feature: FEAT-24.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Un recurso compartido se declara explícitamente.
  - [ ] CA-02: Solo proyectos autorizados pueden usarlo.
  - [ ] CA-03: Los datos privados siguen aislados.

#### US-24.03 — Evitar contaminación entre proyectos

- **Como** sistema **quiero** aislar contexto, memoria y eventos **para** garantizar separación.
- Origen: A:US-24.03 · Épica: EPIC-24 · Feature: FEAT-24.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Un agente del proyecto A no recupera memoria privada del proyecto B.
  - [ ] CA-02: Los eventos de B no actualizan el cliente de A.
  - [ ] CA-03: Las consultas de backlog están limitadas al proyecto activo.

### FEAT-24.02 — Aislamiento · origen B:FEAT-26.01

#### US-24.04

- Enunciado: Como sistema quiero aislar los datos de cada proyecto.
- Origen: B:US-26.01 · Épica: EPIC-24 · Feature: FEAT-24.02 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-24.05

- Enunciado: Como sistema quiero impedir que un agente consulte memoria de otro proyecto sin autorización.
- Origen: B:US-26.02 · Épica: EPIC-24 · Feature: FEAT-24.02 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

## EPIC-25 — DOCUMENTACIÓN VIVA

### FEAT-25.01 — Sincronización documental · origen A:FEAT-25.01

#### US-25.01 — Actualizar documentación después de cambios arquitectónicos

- **Como** sistema **quiero** actualizar documentación relevante **para** mantenerla alineada con la implementación.
- Origen: A:US-25.01 · Épica: EPIC-25 · Feature: FEAT-25.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Una decisión arquitectónica nueva genera actualización documental.
  - [ ] CA-02: El documento identifica la fecha/versión correspondiente.
  - [ ] CA-03: La documentación anterior permanece trazable.

#### US-25.02 — Registrar decisiones arquitectónicas

- **Como** arquitecto **quiero** registrar decisiones y motivos **para** poder comprender por qué existe una determinada solución.
- Origen: A:US-25.02 · Épica: EPIC-25 · Feature: FEAT-25.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Cada decisión tiene identificador.
  - [ ] CA-02: Se registra problema, decisión y consecuencia.
  - [ ] CA-03: Puede localizarse desde elementos afectados.

#### US-25.03 — Detectar documentación desactualizada

- **Como** sistema **quiero** detectar documentos potencialmente obsoletos **para** evitar que los agentes trabajen con información antigua.
- Origen: A:US-25.03 · Épica: EPIC-25 · Feature: FEAT-25.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Los documentos pueden marcarse como desactualizados.
  - [ ] CA-02: Un cambio relevante genera una señal de revisión.
  - [ ] CA-03: El estado es visible para los agentes autorizados.

### FEAT-25.02 — Stack tecnológico · origen B:FEAT-03.01

#### US-25.04

- Enunciado: Como arquitecto quiero registrar las tecnologías utilizadas por un proyecto para que los agentes conozcan el stack oficial.
- Origen: B:US-03.01 · Épica: EPIC-25 · Feature: FEAT-25.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-25.05

- Enunciado: Como arquitecto quiero registrar el motivo de cada decisión tecnológica para conservar contexto arquitectónico.
- Origen: B:US-03.02 · Épica: EPIC-25 · Feature: FEAT-25.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-25.06

- Enunciado: Como agente quiero consultar el stack antes de generar código para evitar utilizar tecnologías no autorizadas.
- Origen: B:US-03.03 · Épica: EPIC-25 · Feature: FEAT-25.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-25.03 — ADR · origen B:FEAT-03.02

#### US-25.07

- Enunciado: Como arquitecto quiero crear un ADR para documentar una decisión arquitectónica.
- Origen: B:US-03.04 · Épica: EPIC-25 · Feature: FEAT-25.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-25.08

- Enunciado: Como arquitecto quiero relacionar un ADR con módulos, funcionalidades y requisitos afectados.
- Origen: B:US-03.05 · Épica: EPIC-25 · Feature: FEAT-25.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-25.09

- Enunciado: Como Watchdog quiero verificar que una propuesta técnica respeta los ADR vigentes.
- Origen: B:US-03.06 · Épica: EPIC-25 · Feature: FEAT-25.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-25.10

- Enunciado: Como arquitecto quiero detectar cuándo una nueva decisión contradice una decisión anterior.
- Origen: B:US-03.07 · Épica: EPIC-25 · Feature: FEAT-25.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-25.04 — Gobierno arquitectónico · origen B:FEAT-03.03

#### US-25.11

- Enunciado: Como operador quiero someter decisiones críticas a revisión de varios agentes especializados.
- Origen: B:US-03.08 · Épica: EPIC-25 · Feature: FEAT-25.04 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-25.12

- Enunciado: Como arquitecto quiero recibir una alerta cuando una propuesta genere deuda técnica no declarada.
- Origen: B:US-03.09 · Épica: EPIC-25 · Feature: FEAT-25.04 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-25.13

- Enunciado: Como Watchdog quiero bloquear una operación cuando incumpla restricciones arquitectónicas obligatorias.
- Origen: B:US-03.10 · Épica: EPIC-25 · Feature: FEAT-25.04 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-25.05 — Documentación técnica · origen B:FEAT-14.01

#### US-25.14

- Enunciado: Como arquitecto quiero generar documentación arquitectónica a partir del estado real del sistema.
- Origen: B:US-14.01 · Épica: EPIC-25 · Feature: FEAT-25.05 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-25.15

- Enunciado: Como sistema quiero mantener diagramas C4 asociados a la arquitectura.
- Origen: B:US-14.02 · Épica: EPIC-25 · Feature: FEAT-25.05 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-25.16

- Enunciado: Como sistema quiero actualizar la documentación cuando cambie la arquitectura.
- Origen: B:US-14.03 · Épica: EPIC-25 · Feature: FEAT-25.05 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- ⚠ Posible solapamiento con US-25.01: revisar si es duplicado, detalle o historia distinta (GAP-006)
- Criterios de aceptación: MISSING

### FEAT-25.06 — Manual de usuario · origen B:FEAT-14.02

#### US-25.17

- Enunciado: Como usuario final quiero disponer de un manual generado a partir de las funcionalidades verificadas.
- Origen: B:US-14.04 · Épica: EPIC-25 · Feature: FEAT-25.06 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-25.18

- Enunciado: Como sistema quiero actualizar el manual cuando una historia funcional quede verificada.
- Origen: B:US-14.05 · Épica: EPIC-25 · Feature: FEAT-25.06 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-25.07 — Sincronización · origen B:FEAT-14.03

#### US-25.19

- Enunciado: Como sistema quiero detectar documentación desactualizada respecto al código.
- Origen: B:US-14.06 · Épica: EPIC-25 · Feature: FEAT-25.07 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- ⚠ Posible solapamiento con US-25.03: revisar si es duplicado, detalle o historia distinta (GAP-006)
- Criterios de aceptación: MISSING

#### US-25.20

- Enunciado: Como sistema quiero vincular documentación con requisitos y evidencias.
- Origen: B:US-14.07 · Épica: EPIC-25 · Feature: FEAT-25.07 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-25.08 — Documentación de archivos · origen B:FEAT-35.01

#### US-25.21

- Enunciado: Como desarrollador quiero conocer qué responsabilidad tiene cada archivo.
- Origen: B:US-35.01 · Épica: EPIC-25 · Feature: FEAT-25.08 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-25.22

- Enunciado: Como agente quiero consultar documentación técnica antes de modificar un archivo complejo.
- Origen: B:US-35.02 · Épica: EPIC-25 · Feature: FEAT-25.08 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-25.09 — Runbooks · origen B:FEAT-35.02

#### US-25.23

- Enunciado: Como operador quiero disponer de procedimientos documentados para resolver incidencias.
- Origen: B:US-35.03 · Épica: EPIC-25 · Feature: FEAT-25.09 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-25.24

- Enunciado: Como sistema quiero generar un runbook a partir de una incidencia recurrente.
- Origen: B:US-35.04 · Épica: EPIC-25 · Feature: FEAT-25.09 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

## EPIC-26 — TELEMETRÍA Y OBSERVABILIDAD

### FEAT-26.01 — Monitorización · origen A:FEAT-26.01

#### US-26.01 — Registrar ejecuciones de agentes

- **Como** administrador **quiero** consultar las ejecuciones **para** conocer qué está haciendo el sistema.
- Origen: A:US-26.01 · Épica: EPIC-26 · Feature: FEAT-26.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Cada ejecución tiene identificador.
  - [ ] CA-02: Se registra agente.
  - [ ] CA-03: Se registra historia/tarea.
  - [ ] CA-04: Se registra inicio y finalización.
  - [ ] CA-05: Se registra resultado.

#### US-26.02 — Consultar métricas

- **Como** administrador **quiero** consultar métricas operativas **para** detectar problemas y evaluar rendimiento.
- Origen: A:US-26.02 · Épica: EPIC-26 · Feature: FEAT-26.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Se muestran métricas disponibles.
  - [ ] CA-02: Las métricas pueden filtrarse por proyecto.
  - [ ] CA-03: Las métricas distinguen ejecuciones exitosas y fallidas.
  - [ ] CA-04: Los datos muestran su periodo temporal.

#### US-26.03 — Investigar una ejecución

- **Como** usuario técnico **quiero** abrir el detalle de una ejecución **para** conocer exactamente qué ocurrió.
- Origen: A:US-26.03 · Épica: EPIC-26 · Feature: FEAT-26.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: El detalle muestra agente, historia y tareas.
  - [ ] CA-02: Muestra eventos relevantes.
  - [ ] CA-03: Muestra errores.
  - [ ] CA-04: Permite seguir la trazabilidad hasta el cambio producido.

### FEAT-26.02 — Telemetría · origen B:FEAT-19.03

#### US-26.04

- Enunciado: Como operador quiero consultar duración de tareas.
- Origen: B:US-19.06 · Épica: EPIC-26 · Feature: FEAT-26.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-26.05

- Enunciado: Como operador quiero consultar consumo de tokens cuando el proveedor lo proporcione.
- Origen: B:US-19.07 · Épica: EPIC-26 · Feature: FEAT-26.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-26.06

- Enunciado: Como operador quiero consultar errores y latencias de modelos.
- Origen: B:US-19.08 · Épica: EPIC-26 · Feature: FEAT-26.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-26.03 — Métricas · origen B:FEAT-27.02

#### US-26.07

- Enunciado: Como operador quiero medir latencias de herramientas MCP.
- Origen: B:US-27.04 · Épica: EPIC-26 · Feature: FEAT-26.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-26.08

- Enunciado: Como operador quiero medir rendimiento de agentes.
- Origen: B:US-27.05 · Épica: EPIC-26 · Feature: FEAT-26.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-26.09

- Enunciado: Como operador quiero medir rendimiento de RAG.
- Origen: B:US-27.06 · Épica: EPIC-26 · Feature: FEAT-26.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-26.10

- Enunciado: Como operador quiero medir rendimiento de modelos.
- Origen: B:US-27.07 · Épica: EPIC-26 · Feature: FEAT-26.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

## EPIC-27 — TRAZABILIDAD END-TO-END

### FEAT-27.01 — Cadena completa · origen A:FEAT-27.01

#### US-27.01 — Seguir un requisito hasta el código

- **Como** Product Owner/Arquitecto **quiero** seguir un requisito hasta su implementación **para** comprobar que realmente ha sido desarrollado.
- Origen: A:US-27.01 · Épica: EPIC-27 · Feature: FEAT-27.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: El requisito enlaza con sus historias.
  - [ ] CA-02: Las historias enlazan con tareas.
  - [ ] CA-03: Las tareas enlazan con cambios.
  - [ ] CA-04: Los cambios enlazan con pruebas.
  - [ ] CA-05: La cadena puede consultarse de extremo a extremo.

#### US-27.02 — Seguir un cambio hasta su requisito

- **Como** arquitecto **quiero** identificar por qué se realizó un cambio **para** conocer su justificación.
- Origen: A:US-27.02 · Épica: EPIC-27 · Feature: FEAT-27.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Un cambio válido tiene referencia a una tarea o decisión.
  - [ ] CA-02: La tarea tiene historia o motivo técnico.
  - [ ] CA-03: La historia tiene requisito o decisión de origen.

#### US-27.03 — Detectar cambios sin trazabilidad

- **Como** QA **quiero** detectar cambios huérfanos **para** evitar modificaciones no justificadas.
- Origen: A:US-27.03 · Épica: EPIC-27 · Feature: FEAT-27.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Los cambios sin origen aparecen en auditoría.
  - [ ] CA-02: Pueden marcarse como legítimos mediante registro explícito.
  - [ ] CA-03: No desaparecen de la auditoría sin dejar historial.

### FEAT-27.02 — Grafo · origen B:FEAT-20.01

#### US-27.04

- Enunciado: Como operador quiero visualizar la relación entre módulo, feature, épica, historia, requisito, tarea y código.
- Origen: B:US-20.01 · Épica: EPIC-27 · Feature: FEAT-27.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-27.05

- Enunciado: Como operador quiero navegar desde un requisito hasta el código que lo implementa.
- Origen: B:US-20.02 · Épica: EPIC-27 · Feature: FEAT-27.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- ⚠ Posible solapamiento con US-27.01: revisar si es duplicado, detalle o historia distinta (GAP-006)
- Criterios de aceptación: MISSING

#### US-27.06

- Enunciado: Como operador quiero navegar desde un commit hasta el requisito que justifica el cambio.
- Origen: B:US-20.03 · Épica: EPIC-27 · Feature: FEAT-27.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- ⚠ Posible solapamiento con US-27.02: revisar si es duplicado, detalle o historia distinta (GAP-006)
- Criterios de aceptación: MISSING

### FEAT-27.03 — Cobertura · origen B:FEAT-20.02

#### US-27.07

- Enunciado: Como Watchdog quiero detectar requisitos sin historias.
- Origen: B:US-20.04 · Épica: EPIC-27 · Feature: FEAT-27.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-27.08

- Enunciado: Como Watchdog quiero detectar historias sin requisitos.
- Origen: B:US-20.05 · Épica: EPIC-27 · Feature: FEAT-27.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-27.09

- Enunciado: Como Watchdog quiero detectar tareas sin historias.
- Origen: B:US-20.06 · Épica: EPIC-27 · Feature: FEAT-27.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-27.10

- Enunciado: Como Watchdog quiero detectar cambios de código sin trazabilidad.
- Origen: B:US-20.07 · Épica: EPIC-27 · Feature: FEAT-27.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- ⚠ Posible solapamiento con US-27.03: revisar si es duplicado, detalle o historia distinta (GAP-006)
- Criterios de aceptación: MISSING

### FEAT-27.04 — Auditoría · origen B:FEAT-20.03

#### US-27.11

- Enunciado: Como operador quiero consultar la cobertura E2E de un proyecto.
- Origen: B:US-20.08 · Épica: EPIC-27 · Feature: FEAT-27.04 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-27.12

- Enunciado: Como operador quiero identificar inmediatamente las brechas de trazabilidad.
- Origen: B:US-20.09 · Épica: EPIC-27 · Feature: FEAT-27.04 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-27.05 — Zero Drift · origen B:FEAT-36.01

#### US-27.13

- Enunciado: Como Watchdog quiero comprobar que cada modificación de código corresponde a una tarea activa.
- Origen: B:US-36.01 · Épica: EPIC-27 · Feature: FEAT-27.05 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-27.14

- Enunciado: Como Watchdog quiero comparar cambios de código con los requisitos de la tarea.
- Origen: B:US-36.02 · Épica: EPIC-27 · Feature: FEAT-27.05 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-27.15

- Enunciado: Como sistema quiero bloquear commits que no tengan trazabilidad válida.
- Origen: B:US-36.03 · Épica: EPIC-27 · Feature: FEAT-27.05 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-27.06 — ADR Guard · origen B:FEAT-36.02

#### US-27.16

- Enunciado: Como sistema quiero comprobar las modificaciones contra los ADR vigentes.
- Origen: B:US-36.04 · Épica: EPIC-27 · Feature: FEAT-27.06 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-27.17

- Enunciado: Como sistema quiero exigir un nuevo ADR cuando una modificación cambie una decisión arquitectónica.
- Origen: B:US-36.05 · Épica: EPIC-27 · Feature: FEAT-27.06 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

## EPIC-28 — QA, TESTING Y CALIDAD

### FEAT-28.01 — Validación · origen A:FEAT-28.01

#### US-28.01 — Ejecutar pruebas de una historia

- **Como** QA **quiero** ejecutar las pruebas asociadas a una historia **para** determinar si cumple los criterios de aceptación.
- Origen: A:US-28.01 · Épica: EPIC-28 · Feature: FEAT-28.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Cada CA puede tener resultado PASS/FAIL.
  - [ ] CA-02: Se conserva evidencia.
  - [ ] CA-03: Un FAIL impide marcar la historia como aceptada.
  - [ ] CA-04: Una ejecución posterior puede actualizar el resultado.

#### US-28.02 — Ejecutar regresión

- **Como** sistema **quiero** ejecutar pruebas de regresión después de cambios **para** detectar efectos secundarios.
- Origen: A:US-28.02 · Épica: EPIC-28 · Feature: FEAT-28.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Se ejecuta el conjunto configurado.
  - [ ] CA-02: Los fallos quedan asociados al cambio.
  - [ ] CA-03: El resultado queda registrado.

#### US-28.03 — Crear informe de calidad

- **Como** Scrum Master **quiero** obtener un informe de calidad **para** conocer el estado real del producto.
- Origen: A:US-28.03 · Épica: EPIC-28 · Feature: FEAT-28.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: El informe muestra historias aceptadas y rechazadas.
  - [ ] CA-02: Muestra pruebas fallidas.
  - [ ] CA-03: Muestra defectos abiertos.
  - [ ] CA-04: Identifica bloqueos.

### FEAT-28.02 — Walkthroughs · origen B:FEAT-09.01

#### US-28.04

- Enunciado: Como desarrollador quiero marcar pasos ejecutables de un walkthrough para que ACM pueda validarlos automáticamente.
- Origen: B:US-09.01 · Épica: EPIC-28 · Feature: FEAT-28.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-28.05

- Enunciado: Como sistema quiero ejecutar los comandos marcados como automáticos.
- Origen: B:US-09.02 · Épica: EPIC-28 · Feature: FEAT-28.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-28.06

- Enunciado: Como sistema quiero registrar el resultado de cada ejecución.
- Origen: B:US-09.03 · Épica: EPIC-28 · Feature: FEAT-28.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-28.03 — Evidencia · origen B:FEAT-09.02

#### US-28.07

- Enunciado: Como QA quiero consultar la evidencia de ejecución asociada a una historia.
- Origen: B:US-09.04 · Épica: EPIC-28 · Feature: FEAT-28.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-28.08

- Enunciado: Como Watchdog quiero impedir DONE cuando una validación obligatoria haya fallado.
- Origen: B:US-09.05 · Épica: EPIC-28 · Feature: FEAT-28.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-28.04 — Done-Done · origen B:FEAT-09.03

#### US-28.09

- Enunciado: Como sistema quiero diferenciar entre código terminado y código verificado.
- Origen: B:US-09.06 · Épica: EPIC-28 · Feature: FEAT-28.04 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-28.10

- Enunciado: Como sistema quiero promover automáticamente un hito cuando todos sus validadores hayan terminado correctamente.
- Origen: B:US-09.07 · Épica: EPIC-28 · Feature: FEAT-28.04 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

## EPIC-29 — BUGS, INCIDENTES Y RECUPERACIÓN

### FEAT-29.01 — Gestión de defectos · origen A:FEAT-29.01

#### US-29.01 — Registrar un bug

- **Como** miembro del equipo **quiero** registrar un defecto **para** que pueda investigarse y corregirse.
- Origen: A:US-29.01 · Épica: EPIC-29 · Feature: FEAT-29.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: El bug recibe identificador.
  - [ ] CA-02: Incluye descripción y contexto.
  - [ ] CA-03: Puede asociarse a una historia.
  - [ ] CA-04: Tiene estado.

#### US-29.02 — Asignar un bug

- **Como** Scrum Master **quiero** asignar un bug a un agente **para** iniciar su resolución.
- Origen: A:US-29.02 · Épica: EPIC-29 · Feature: FEAT-29.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: El agente recibe el contexto necesario.
  - [ ] CA-02: La asignación queda registrada.
  - [ ] CA-03: El bug cambia al estado correspondiente.

#### US-29.03 — Verificar una corrección

- **Como** QA **quiero** verificar que una corrección resuelve el bug **para** cerrarlo con evidencia.
- Origen: A:US-29.03 · Épica: EPIC-29 · Feature: FEAT-29.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Se reproduce el escenario original.
  - [ ] CA-02: El escenario corregido pasa.
  - [ ] CA-03: Las pruebas de regresión relevantes pasan.
  - [ ] CA-04: Solo entonces puede cerrarse el bug.

### FEAT-29.02 — Bugs · origen B:FEAT-11.01

#### US-29.04

- Enunciado: Como sistema quiero crear automáticamente un bug cuando falle una validación.
- Origen: B:US-11.01 · Épica: EPIC-29 · Feature: FEAT-29.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-29.05

- Enunciado: Como operador quiero registrar manualmente un bug.
- Origen: B:US-11.02 · Épica: EPIC-29 · Feature: FEAT-29.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- ⚠ Posible solapamiento con US-29.01: revisar si es duplicado, detalle o historia distinta (GAP-006)
- Criterios de aceptación: MISSING

#### US-29.06

- Enunciado: Como QA quiero asociar un bug con la historia, tarea y ejecución que lo originaron.
- Origen: B:US-11.03 · Épica: EPIC-29 · Feature: FEAT-29.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-29.03 — Root Cause · origen B:FEAT-11.02

#### US-29.07

- Enunciado: Como agente QA quiero analizar la causa raíz de un fallo.
- Origen: B:US-11.04 · Épica: EPIC-29 · Feature: FEAT-29.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-29.08

- Enunciado: Como sistema quiero relacionar la causa raíz con el requisito o ADR que originó el problema.
- Origen: B:US-11.05 · Épica: EPIC-29 · Feature: FEAT-29.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-29.09

- Enunciado: Como sistema quiero generar una acción correctiva a partir de la causa raíz.
- Origen: B:US-11.06 · Épica: EPIC-29 · Feature: FEAT-29.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-29.04 — AutoRoot · origen B:FEAT-11.03

#### US-29.10

- Enunciado: Como sistema quiero generar automáticamente una tarea correctiva tras detectar un fallo crítico.
- Origen: B:US-11.07 · Épica: EPIC-29 · Feature: FEAT-29.04 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-29.11

- Enunciado: Como sistema quiero priorizar la corrección dentro del contexto del sprint.
- Origen: B:US-11.08 · Épica: EPIC-29 · Feature: FEAT-29.04 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-29.12

- Enunciado: Como Watchdog quiero impedir el cierre del sprint cuando existan fallos críticos sin resolver.
- Origen: B:US-11.09 · Épica: EPIC-29 · Feature: FEAT-29.04 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-29.05 — Curación causal · origen B:FEAT-37.01

#### US-29.13

- Enunciado: Como sistema quiero recorrer la cadena causal de un error hasta su origen.
- Origen: B:US-37.01 · Épica: EPIC-29 · Feature: FEAT-29.05 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-29.14

- Enunciado: Como sistema quiero identificar el requisito, ADR o tarea potencialmente causante.
- Origen: B:US-37.02 · Épica: EPIC-29 · Feature: FEAT-29.05 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-29.06 — Regeneración · origen B:FEAT-37.02

#### US-29.15

- Enunciado: Como agente quiero proponer una modificación de especificación cuando una implementación contradiga el requisito.
- Origen: B:US-37.03 · Épica: EPIC-29 · Feature: FEAT-29.06 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-29.16

- Enunciado: Como sistema quiero regenerar el plan afectado después de una corrección estructural.
- Origen: B:US-37.04 · Épica: EPIC-29 · Feature: FEAT-29.06 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-29.07 — Protección · origen B:FEAT-37.03

#### US-29.17

- Enunciado: Como Watchdog quiero exigir validación antes de aplicar una autocorrección.
- Origen: B:US-37.05 · Épica: EPIC-29 · Feature: FEAT-29.07 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-29.18

- Enunciado: Como sistema quiero generar un snapshot antes de una autocorrección crítica.
- Origen: B:US-37.06 · Épica: EPIC-29 · Feature: FEAT-29.07 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

## EPIC-30 — APIs Y SERVICIOS

### FEAT-30.01 — API interna · origen A:FEAT-30.01

#### US-30.01 — Exponer operaciones del proyecto mediante API

- **Como** cliente de la plataforma **quiero** acceder a operaciones mediante API **para** integrar interfaces y automatizaciones.
- Origen: A:US-30.01 · Épica: EPIC-30 · Feature: FEAT-30.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Cada endpoint tiene contrato definido.
  - [ ] CA-02: Las entradas inválidas generan respuesta de error adecuada.
  - [ ] CA-03: La autorización se aplica.
  - [ ] CA-04: La respuesta tiene formato consistente.

#### US-30.02 — Documentar endpoints

- **Como** desarrollador **quiero** disponer de documentación de API **para** integrar servicios correctamente.
- Origen: A:US-30.02 · Épica: EPIC-30 · Feature: FEAT-30.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Cada endpoint documentado indica método y ruta.
  - [ ] CA-02: Indica entrada y salida.
  - [ ] CA-03: Indica errores relevantes.
  - [ ] CA-04: La documentación se actualiza cuando cambia el contrato.

#### US-30.03 — Versionar API

- **Como** arquitecto **quiero** versionar cambios incompatibles **para** evitar romper clientes existentes.
- Origen: A:US-30.03 · Épica: EPIC-30 · Feature: FEAT-30.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Los cambios incompatibles tienen versión.
  - [ ] CA-02: Las versiones activas pueden identificarse.
  - [ ] CA-03: Las rutas antiguas siguen la política de compatibilidad definida.

## EPIC-31 — CONSOLA Y SUPERVISIÓN OPERATIVA

### FEAT-31.01 — Consola de ejecución · origen A:FEAT-31.01

#### US-31.01 — Consultar consola de actividad

- **Como** usuario técnico **quiero** visualizar actividad del sistema **para** supervisar las ejecuciones.
- Origen: A:US-31.01 · Épica: EPIC-31 · Feature: FEAT-31.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Se muestran eventos relevantes.
  - [ ] CA-02: Los eventos incluyen timestamp.
  - [ ] CA-03: Pueden filtrarse por proyecto/agente.
  - [ ] CA-04: Un error aparece claramente diferenciado.

#### US-31.02 — Filtrar actividad

- **Como** usuario técnico **quiero** filtrar la actividad **para** localizar rápidamente un incidente.
- Origen: A:US-31.02 · Épica: EPIC-31 · Feature: FEAT-31.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: El filtro se aplica al conjunto de eventos.
  - [ ] CA-02: Los resultados coinciden con los filtros.
  - [ ] CA-03: Limpiar filtros restaura la vista completa.

#### US-31.03 — Inspeccionar contexto de agente

- **Como** administrador **quiero** inspeccionar el estado de un agente **para** comprender su ejecución.
- Origen: A:US-31.03 · Épica: EPIC-31 · Feature: FEAT-31.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Se muestra identidad y estado.
  - [ ] CA-02: Se muestran tareas actuales.
  - [ ] CA-03: Se muestran dependencias relevantes.
  - [ ] CA-04: La información sensible queda protegida según RBAC.

### FEAT-31.02 — Actividad · origen B:FEAT-19.02

#### US-31.04

- Enunciado: Como operador quiero ver un feed de actividad de los agentes.
- Origen: B:US-19.04 · Épica: EPIC-31 · Feature: FEAT-31.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-31.05

- Enunciado: Como operador quiero consultar el historial de actividad de un agente.
- Origen: B:US-19.05 · Épica: EPIC-31 · Feature: FEAT-31.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- ⚠ Posible solapamiento con US-31.01: revisar si es duplicado, detalle o historia distinta (GAP-006)
- Criterios de aceptación: MISSING

## EPIC-32 — NOTIFICACIONES Y EVENTOS DE NEGOCIO

### FEAT-32.01 — Alertas · origen A:FEAT-32.01

#### US-32.01 — Recibir notificación de fallo

- **Como** usuario supervisor **quiero** recibir una alerta cuando una ejecución crítica falle **para** intervenir cuando sea necesario.
- Origen: A:US-32.01 · Épica: EPIC-32 · Feature: FEAT-32.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: El fallo crítico genera la notificación definida.
  - [ ] CA-02: La notificación identifica proyecto y ejecución.
  - [ ] CA-03: Un mismo incidente no genera duplicados innecesarios.

#### US-32.02 — Notificar bloqueo

- **Como** supervisor **quiero** ser informado de un bloqueo **para** poder decidir cómo actuar.
- Origen: A:US-32.02 · Épica: EPIC-32 · Feature: FEAT-32.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: El Watchdog genera el evento.
  - [ ] CA-02: La notificación identifica el agente afectado.
  - [ ] CA-03: Incluye la acción de recuperación aplicada si existe.

### FEAT-32.02 — Webhooks · origen B:FEAT-30.01

#### US-32.03

- Enunciado: Como operador quiero configurar un webhook externo.
- Origen: B:US-30.01 · Épica: EPIC-32 · Feature: FEAT-32.02 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-32.04

- Enunciado: Como sistema quiero enviar eventos críticos a servicios externos.
- Origen: B:US-30.02 · Épica: EPIC-32 · Feature: FEAT-32.02 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-32.03 — Notificaciones · origen B:FEAT-30.02

#### US-32.05

- Enunciado: Como operador quiero recibir una alerta cuando un agente termine una operación crítica.
- Origen: B:US-30.03 · Épica: EPIC-32 · Feature: FEAT-32.03 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- ⚠ Posible solapamiento con US-32.01: revisar si es duplicado, detalle o historia distinta (GAP-006)
- Criterios de aceptación: MISSING

#### US-32.06

- Enunciado: Como operador quiero recibir una alerta cuando el Watchdog bloquee una operación.
- Origen: B:US-30.04 · Épica: EPIC-32 · Feature: FEAT-32.03 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-32.04 — Alertas · origen B:FEAT-45.01

#### US-32.07

- Enunciado: Como operador quiero recibir alertas cuando un agente se desvíe de sus permisos.
- Origen: B:US-45.01 · Épica: EPIC-32 · Feature: FEAT-32.04 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-32.08

- Enunciado: Como operador quiero recibir alertas cuando falle una validación crítica.
- Origen: B:US-45.02 · Épica: EPIC-32 · Feature: FEAT-32.04 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- ⚠ Posible solapamiento con US-32.01: revisar si es duplicado, detalle o historia distinta (GAP-006)
- Criterios de aceptación: MISSING

### FEAT-32.05 — Alertas predictivas · origen B:FEAT-45.02

#### US-32.09

- Enunciado: Como operador quiero recibir alertas sobre posibles cuellos de botella.
- Origen: B:US-45.03 · Épica: EPIC-32 · Feature: FEAT-32.05 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-32.10

- Enunciado: Como operador quiero recibir alertas sobre degradación de arquitectura.
- Origen: B:US-45.04 · Épica: EPIC-32 · Feature: FEAT-32.05 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

## EPIC-33 — CONFIGURACIÓN DEL SISTEMA

### FEAT-33.01 — Configuración global · origen A:FEAT-33.01

#### US-33.01 — Configurar parámetros globales

- **Como** administrador **quiero** modificar parámetros globales **para** adaptar el comportamiento de la plataforma.
- Origen: A:US-33.01 · Épica: EPIC-33 · Feature: FEAT-33.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Solo parámetros autorizados son editables.
  - [ ] CA-02: Los valores inválidos son rechazados.
  - [ ] CA-03: Los cambios quedan persistidos.
  - [ ] CA-04: Los agentes reciben la configuración aplicable.

#### US-33.02 — Configurar políticas de agentes

- **Como** administrador **quiero** configurar políticas de ejecución **para** controlar autonomía y límites.
- Origen: A:US-33.02 · Épica: EPIC-33 · Feature: FEAT-33.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Las políticas tienen valores explícitos.
  - [ ] CA-02: Se aplican a nuevas ejecuciones.
  - [ ] CA-03: Los cambios quedan auditados.

## EPIC-34 — GESTIÓN DE RECURSOS DEL AGENTE

### FEAT-34.01 — Herramientas de desarrollo · origen A:FEAT-34.01

#### US-34.01 — Permitir acceso controlado al filesystem

- **Como** agente desarrollador **quiero** acceder al filesystem autorizado **para** modificar el proyecto.
- Origen: A:US-34.01 · Épica: EPIC-34 · Feature: FEAT-34.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: El agente solo puede acceder a rutas autorizadas.
  - [ ] CA-02: Un acceso fuera del alcance es rechazado.
  - [ ] CA-03: Las operaciones quedan trazadas.

#### US-34.02 — Ejecutar comandos de terminal autorizados

- **Como** agente desarrollador **quiero** ejecutar comandos permitidos **para** construir y probar el proyecto.
- Origen: A:US-34.02 · Épica: EPIC-34 · Feature: FEAT-34.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: El comando se ejecuta dentro del contexto autorizado.
  - [ ] CA-02: stdout/stderr quedan registrados.
  - [ ] CA-03: El código de salida queda registrado.
  - [ ] CA-04: Los comandos prohibidos son rechazados.

#### US-34.03 — Ejecutar pruebas/build

- **Como** agente desarrollador **quiero** ejecutar build y tests **para** verificar cambios.
- Origen: A:US-34.03 · Épica: EPIC-34 · Feature: FEAT-34.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Se ejecuta el comando configurado.
  - [ ] CA-02: El resultado queda asociado a la tarea.
  - [ ] CA-03: Un build fallido impide declarar éxito técnico.

## EPIC-35 — CONTEXTO DE EJECUCIÓN Y PROMPTS

### FEAT-35.01 — Context engineering · origen A:FEAT-35.01

#### US-35.01 — Construir contexto para un agente

- **Como** orquestador **quiero** construir el contexto mínimo necesario **para** que el agente trabaje sin cargar información innecesaria.
- Origen: A:US-35.01 · Épica: EPIC-35 · Feature: FEAT-35.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Se incluye la historia.
  - [ ] CA-02: Se incluyen requisitos relacionados.
  - [ ] CA-03: Se incluyen dependencias necesarias.
  - [ ] CA-04: Se recupera documentación relevante.
  - [ ] CA-05: No se mezcla contexto de otro proyecto.

#### US-35.02 — Registrar prompt/contexto utilizado

- **Como** sistema **quiero** conservar referencia del contexto utilizado **para** reproducir y auditar una ejecución.
- Origen: A:US-35.02 · Épica: EPIC-35 · Feature: FEAT-35.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: La ejecución identifica la versión del contexto.
  - [ ] CA-02: Puede determinarse qué fuentes se utilizaron.
  - [ ] CA-03: La información sensible sigue las políticas de seguridad.

### FEAT-35.02 — Context Loader · origen B:FEAT-43.01

#### US-35.03

- Enunciado: Como agente quiero solicitar el contexto necesario antes de comenzar una tarea.
- Origen: B:US-43.01 · Épica: EPIC-35 · Feature: FEAT-35.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-35.04

- Enunciado: Como sistema quiero seleccionar automáticamente el contexto relevante.
- Origen: B:US-43.02 · Épica: EPIC-35 · Feature: FEAT-35.02 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-35.03 — Contexto estructurado · origen B:FEAT-43.02

#### US-35.05

- Enunciado: Como agente quiero recibir el estado de la historia, tarea, requisitos y ADR relacionados.
- Origen: B:US-43.03 · Épica: EPIC-35 · Feature: FEAT-35.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-35.06

- Enunciado: Como agente quiero recibir las restricciones del stack relevantes.
- Origen: B:US-43.04 · Épica: EPIC-35 · Feature: FEAT-35.03 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-35.04 — Contexto semántico · origen B:FEAT-43.03

#### US-35.07

- Enunciado: Como agente quiero recibir fragmentos RAG relevantes junto al contexto estructurado.
- Origen: B:US-43.05 · Épica: EPIC-35 · Feature: FEAT-35.04 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

## EPIC-36 — AGENT MEMORY Y APRENDIZAJE

### FEAT-36.01 — Lessons learned · origen A:FEAT-36.01

#### US-36.01 — Registrar una lección aprendida

- **Como** agente **quiero** registrar una lección obtenida durante el desarrollo **para** evitar repetir errores.
- Origen: A:US-36.01 · Épica: EPIC-36 · Feature: FEAT-36.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: La lección tiene origen.
  - [ ] CA-02: Describe problema y solución.
  - [ ] CA-03: Puede relacionarse con tecnología o contexto.
  - [ ] CA-04: Puede recuperarse posteriormente.

#### US-36.02 — Recuperar lecciones relevantes

- **Como** agente **quiero** consultar lecciones relacionadas **para** aplicar conocimiento previo.
- Origen: A:US-36.02 · Épica: EPIC-36 · Feature: FEAT-36.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: La recuperación utiliza contexto.
  - [ ] CA-02: Las fuentes pueden identificarse.
  - [ ] CA-03: Una lección no aplicable no debe presentarse como obligatoria.

## EPIC-37 — GOBERNANZA DE CAMBIOS

### FEAT-37.01 — Change management · origen A:FEAT-37.01

#### US-37.01 — Registrar una solicitud de cambio

- **Como** Product Owner **quiero** registrar un cambio de alcance **para** controlar la evolución del producto.
- Origen: A:US-37.01 · Épica: EPIC-37 · Feature: FEAT-37.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: El cambio tiene identificador.
  - [ ] CA-02: Indica motivo y alcance.
  - [ ] CA-03: Identifica requisitos afectados.
  - [ ] CA-04: Puede aprobarse o rechazarse.

#### US-37.02 — Analizar impacto de un cambio

- **Como** arquitecto **quiero** conocer qué elementos afecta un cambio **para** evitar modificaciones incompletas.
- Origen: A:US-37.02 · Épica: EPIC-37 · Feature: FEAT-37.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Se identifican historias afectadas.
  - [ ] CA-02: Se identifican componentes afectados.
  - [ ] CA-03: Se identifican dependencias.
  - [ ] CA-04: El resultado queda registrado.

#### US-37.03 — Propagar un cambio aprobado

- **Como** sistema **quiero** actualizar los artefactos afectados **para** mantener coherencia.
- Origen: A:US-37.03 · Épica: EPIC-37 · Feature: FEAT-37.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Solo cambios aprobados se propagan.
  - [ ] CA-02: Los elementos afectados quedan identificados.
  - [ ] CA-03: La trazabilidad conserva el cambio original.

## EPIC-38 — GESTIÓN DE CONFIGURACIÓN DE MODELOS

### FEAT-38.01 — Model Registry · origen A:FEAT-38.01

#### US-38.01 — Registrar modelo

- **Como** administrador **quiero** registrar información de un modelo **para** conocer sus capacidades.
- Origen: A:US-38.01 · Épica: EPIC-38 · Feature: FEAT-38.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: El modelo tiene nombre/identificador.
  - [ ] CA-02: Se registra proveedor/runtime.
  - [ ] CA-03: Se registran capacidades conocidas.
  - [ ] CA-04: Se registra versión cuando esté disponible.

#### US-38.02 — Seleccionar modelo según capacidad

- **Como** orquestador **quiero** seleccionar modelos compatibles con una tarea **para** utilizar la capacidad apropiada.
- Origen: A:US-38.02 · Épica: EPIC-38 · Feature: FEAT-38.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Se comparan capacidades requeridas.
  - [ ] CA-02: Los modelos incompatibles quedan excluidos.
  - [ ] CA-03: La selección utilizada queda registrada.

## EPIC-39 — RESILIENCIA Y FALLBACK

### FEAT-39.01 — Recuperación · origen A:FEAT-39.01

#### US-39.01 — Reintentar una operación recuperable

- **Como** sistema **quiero** reintentar operaciones que fallan de forma transitoria **para** evitar fallos innecesarios.
- Origen: A:US-39.01 · Épica: EPIC-39 · Feature: FEAT-39.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Solo errores configurados como recuperables generan retry.
  - [ ] CA-02: Se respeta el máximo de reintentos.
  - [ ] CA-03: Cada intento queda registrado.
  - [ ] CA-04: Superado el límite, la operación queda fallida.

#### US-39.02 — Utilizar fallback de modelo

- **Como** sistema **quiero** utilizar un modelo alternativo autorizado **para** mantener una operación cuando el modelo principal no está disponible.
- Origen: A:US-39.02 · Épica: EPIC-39 · Feature: FEAT-39.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: El fallback está previamente configurado.
  - [ ] CA-02: Se utiliza solo ante condiciones compatibles.
  - [ ] CA-03: La ejecución registra modelo principal y fallback.
  - [ ] CA-04: No se utiliza un modelo no autorizado.

#### US-39.03 — Recuperar una tarea después de reinicio

- **Como** sistema **quiero** recuperar tareas persistidas **para** continuar después de una interrupción.
- Origen: A:US-39.03 · Épica: EPIC-39 · Feature: FEAT-39.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Las tareas recuperables se identifican.
  - [ ] CA-02: Una tarea ya completada no vuelve a ejecutarse.
  - [ ] CA-03: Las tareas pendientes pueden reanudarse según política.
  - [ ] CA-04: La recuperación queda registrada.

### FEAT-39.02 — Failover · origen B:FEAT-23.04

#### US-39.04

- Enunciado: Como sistema quiero cambiar a un modelo alternativo cuando el principal falle.
- Origen: B:US-23.07 · Épica: EPIC-39 · Feature: FEAT-39.02 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- ⚠ Posible solapamiento con US-39.02: revisar si es duplicado, detalle o historia distinta (GAP-006)
- Criterios de aceptación: MISSING

#### US-39.05

- Enunciado: Como sistema quiero registrar los cambios de modelo utilizados durante una tarea.
- Origen: B:US-23.08 · Épica: EPIC-39 · Feature: FEAT-39.02 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

## EPIC-40 — IMPORTACIÓN Y EXPORTACIÓN DEL PROYECTO

### FEAT-40.01 — Portabilidad · origen A:FEAT-40.01

#### US-40.01 — Exportar proyecto

- **Como** administrador **quiero** exportar el estado del proyecto **para** conservarlo o trasladarlo.
- Origen: A:US-40.01 · Épica: EPIC-40 · Feature: FEAT-40.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Se incluyen los elementos definidos por el formato.
  - [ ] CA-02: Se conserva la estructura.
  - [ ] CA-03: El paquete exportado puede validarse.
  - [ ] CA-04: Los secretos no se exportan salvo política explícita.

#### US-40.02 — Importar proyecto

- **Como** administrador **quiero** importar un proyecto **para** recuperar o trasladar un entorno.
- Origen: A:US-40.02 · Épica: EPIC-40 · Feature: FEAT-40.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: El paquete se valida antes de modificar el sistema.
  - [ ] CA-02: Un paquete inválido no deja estado parcial.
  - [ ] CA-03: Los identificadores se conservan o remapean explícitamente.
  - [ ] CA-04: La importación queda registrada.

### FEAT-40.02 — Backup · origen B:FEAT-41.01

#### US-40.03

- Enunciado: Como sistema quiero exportar copias de seguridad de la base ACM.
- Origen: B:US-41.01 · Épica: EPIC-40 · Feature: FEAT-40.02 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-40.04

- Enunciado: Como sistema quiero proteger las copias de seguridad.
- Origen: B:US-41.02 · Épica: EPIC-40 · Feature: FEAT-40.02 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-40.03 — Almacenamiento externo · origen B:FEAT-41.02

#### US-40.05

- Enunciado: Como operador quiero configurar un destino externo de backup.
- Origen: B:US-41.03 · Épica: EPIC-40 · Feature: FEAT-40.03 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-40.06

- Enunciado: Como sistema quiero verificar que una copia exportada puede recuperarse.
- Origen: B:US-41.04 · Épica: EPIC-40 · Feature: FEAT-40.03 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-40.04 — Recuperación · origen B:FEAT-41.03

#### US-40.07

- Enunciado: Como operador quiero restaurar un backup completo.
- Origen: B:US-41.05 · Épica: EPIC-40 · Feature: FEAT-40.04 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-40.08

- Enunciado: Como sistema quiero registrar la operación de restauración.
- Origen: B:US-41.06 · Épica: EPIC-40 · Feature: FEAT-40.04 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

## EPIC-41 — MULTIAGENTE Y COLABORACIÓN

### FEAT-41.01 — Coordinación · origen A:FEAT-41.01

#### US-41.01 — Compartir resultado entre agentes

- **Como** agente **quiero** publicar un resultado estructurado **para** que otro agente pueda continuar el trabajo.
- Origen: A:US-41.01 · Épica: EPIC-41 · Feature: FEAT-41.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: El resultado identifica productor.
  - [ ] CA-02: Identifica tarea/origen.
  - [ ] CA-03: El consumidor recibe la versión correcta.
  - [ ] CA-04: Un resultado inválido no se acepta como completado.

#### US-41.02 — Coordinar tareas dependientes

- **Como** orquestador **quiero** activar una tarea cuando sus dependencias estén satisfechas **para** mantener un flujo correcto.
- Origen: A:US-41.02 · Épica: EPIC-41 · Feature: FEAT-41.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Una tarea bloqueada no comienza.
  - [ ] CA-02: Al completar todas sus dependencias pasa a ejecutable.
  - [ ] CA-03: Una dependencia fallida impide la ejecución automática cuando la política así lo determine.

#### US-41.03 — Resolver conflictos entre agentes

- **Como** orquestador **quiero** detectar modificaciones incompatibles **para** impedir que dos agentes corrompan el mismo contexto.
- Origen: A:US-41.03 · Épica: EPIC-41 · Feature: FEAT-41.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: El conflicto se detecta.
  - [ ] CA-02: Los agentes implicados quedan identificados.
  - [ ] CA-03: La política de resolución se aplica.
  - [ ] CA-04: El conflicto queda registrado.

### FEAT-41.02 — Tribunal multiagente · origen B:FEAT-05.02

#### US-41.04

- Enunciado: Como sistema quiero solicitar validación al Product Owner IA, Arquitecto IA y QA IA antes de ejecutar una historia crítica.
- Origen: B:US-05.04 · Épica: EPIC-41 · Feature: FEAT-41.02 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-41.05

- Enunciado: Como operador quiero consultar las decisiones emitidas por cada agente.
- Origen: B:US-05.05 · Épica: EPIC-41 · Feature: FEAT-41.02 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-41.06

- Enunciado: Como sistema quiero impedir la ejecución cuando una regla de gobernanza obligatoria no haya sido aprobada.
- Origen: B:US-05.06 · Épica: EPIC-41 · Feature: FEAT-41.02 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-41.03 — Consensus Gate · origen B:FEAT-05.03

#### US-41.07

- Enunciado: Como sistema quiero registrar formalmente las aprobaciones necesarias para liberar una historia.
- Origen: B:US-05.07 · Épica: EPIC-41 · Feature: FEAT-41.03 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-41.08

- Enunciado: Como sistema quiero mantener la trazabilidad de quién o qué agente autorizó una transición.
- Origen: B:US-05.08 · Épica: EPIC-41 · Feature: FEAT-41.03 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-41.04 — Conflictos · origen B:FEAT-17.03

#### US-41.09

- Enunciado: Como sistema quiero detectar conflictos entre agentes.
- Origen: B:US-17.06 · Épica: EPIC-41 · Feature: FEAT-41.04 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- ⚠ Posible solapamiento con US-41.03: revisar si es duplicado, detalle o historia distinta (GAP-006)
- Criterios de aceptación: MISSING

#### US-41.10

- Enunciado: Como sistema quiero intentar resolver automáticamente conflictos compatibles.
- Origen: B:US-17.07 · Épica: EPIC-41 · Feature: FEAT-41.04 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-41.11

- Enunciado: Como operador quiero intervenir manualmente en un conflicto no resoluble.
- Origen: B:US-17.08 · Épica: EPIC-41 · Feature: FEAT-41.04 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-41.05 — Contratos · origen B:FEAT-17.04

#### US-41.12

- Enunciado: Como agente quiero negociar un contrato de modificación antes de tocar código compartido.
- Origen: B:US-17.09 · Épica: EPIC-41 · Feature: FEAT-41.05 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-41.13

- Enunciado: Como sistema quiero conservar el acuerdo entre agentes como evidencia.
- Origen: B:US-17.10 · Épica: EPIC-41 · Feature: FEAT-41.05 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-41.06 — Presencia · origen B:FEAT-39.01

#### US-41.14

- Enunciado: Como operador quiero ver todos los agentes conectados a un proyecto.
- Origen: B:US-39.01 · Épica: EPIC-41 · Feature: FEAT-41.06 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-41.15

- Enunciado: Como operador quiero conocer qué está haciendo cada agente.
- Origen: B:US-39.02 · Épica: EPIC-41 · Feature: FEAT-41.06 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-41.07 — Coordinación · origen B:FEAT-39.02

#### US-41.16

- Enunciado: Como agente quiero comunicarme con otros agentes del mismo proyecto.
- Origen: B:US-39.03 · Épica: EPIC-41 · Feature: FEAT-41.07 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-41.17

- Enunciado: Como agente quiero intercambiar contexto relevante con otro agente.
- Origen: B:US-39.04 · Épica: EPIC-41 · Feature: FEAT-41.07 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-41.08 — Negociación · origen B:FEAT-39.03

#### US-41.18

- Enunciado: Como agente quiero negociar prioridades cuando dos agentes necesitan el mismo recurso.
- Origen: B:US-39.05 · Épica: EPIC-41 · Feature: FEAT-41.08 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-41.19

- Enunciado: Como sistema quiero registrar el acuerdo alcanzado entre agentes.
- Origen: B:US-39.06 · Épica: EPIC-41 · Feature: FEAT-41.08 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

## EPIC-42 — GESTIÓN DEL CONTEXTO DE SPRINT

### FEAT-42.01 — Sprint Memory · origen A:FEAT-42.01

#### US-42.01 — Registrar contexto del sprint

- **Como** Scrum Master **quiero** mantener memoria del sprint **para** que los agentes conozcan sus objetivos.
- Origen: A:US-42.01 · Épica: EPIC-42 · Feature: FEAT-42.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Se almacena objetivo.
  - [ ] CA-02: Se almacenan historias.
  - [ ] CA-03: Se almacenan decisiones relevantes.
  - [ ] CA-04: El contexto se puede recuperar.

#### US-42.02 — Registrar impedimentos

- **Como** Scrum Master **quiero** registrar impedimentos **para** controlar bloqueos.
- Origen: A:US-42.02 · Épica: EPIC-42 · Feature: FEAT-42.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Cada impedimento tiene identificador.
  - [ ] CA-02: Se relaciona con las historias afectadas.
  - [ ] CA-03: Tiene estado.
  - [ ] CA-04: Su resolución queda registrada.

## EPIC-43 — REPORTING DEL PRODUCTO

### FEAT-43.01 — Informes · origen A:FEAT-43.01

#### US-43.01 — Consultar progreso del producto

- **Como** Product Owner **quiero** consultar el progreso **para** conocer cuánto producto está implementado.
- Origen: A:US-43.01 · Épica: EPIC-43 · Feature: FEAT-43.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Se muestran historias por estado.
  - [ ] CA-02: Se muestran épicas y features.
  - [ ] CA-03: Se distingue trabajo pendiente y completado.
  - [ ] CA-04: Los datos corresponden al proyecto seleccionado.

#### US-43.02 — Consultar progreso por requisito

- **Como** Product Owner **quiero** consultar cobertura de requisitos **para** detectar alcance no implementado.
- Origen: A:US-43.02 · Épica: EPIC-43 · Feature: FEAT-43.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Cada requisito indica cobertura.
  - [ ] CA-02: Los requisitos sin historias aparecen identificados.
  - [ ] CA-03: La cobertura considera historias y aceptación.

### FEAT-43.02 — Velocidad · origen B:FEAT-38.01

#### US-43.03

- Enunciado: Como Scrum Master quiero consultar la velocidad histórica de los sprints.
- Origen: B:US-38.01 · Épica: EPIC-43 · Feature: FEAT-43.02 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-43.04

- Enunciado: Como Scrum Master quiero comparar velocidad entre módulos.
- Origen: B:US-38.02 · Épica: EPIC-43 · Feature: FEAT-43.02 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-43.03 — Cuellos de botella · origen B:FEAT-38.02

#### US-43.05

- Enunciado: Como sistema quiero detectar acumulación anormal de tareas.
- Origen: B:US-38.03 · Épica: EPIC-43 · Feature: FEAT-43.03 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-43.06

- Enunciado: Como operador quiero visualizar cuellos de botella en el Kanban.
- Origen: B:US-38.04 · Épica: EPIC-43 · Feature: FEAT-43.03 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-43.04 — Deuda · origen B:FEAT-38.03

#### US-43.07

- Enunciado: Como operador quiero visualizar la relación entre deuda técnica y velocidad.
- Origen: B:US-38.05 · Épica: EPIC-43 · Feature: FEAT-43.04 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-43.05 — Predicción · origen B:FEAT-38.04

#### US-43.08

- Enunciado: Como Scrum Master quiero consultar predicciones sobre riesgos del sprint.
- Origen: B:US-38.06 · Épica: EPIC-43 · Feature: FEAT-43.05 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

## EPIC-44 — SEGURIDAD OPERATIVA

### FEAT-44.01 — Auditoría · origen A:FEAT-44.01

#### US-44.01 — Registrar acciones administrativas

- **Como** sistema **quiero** registrar acciones sensibles **para** disponer de auditoría.
- Origen: A:US-44.01 · Épica: EPIC-44 · Feature: FEAT-44.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Las operaciones sensibles generan registros.
  - [ ] CA-02: Se identifica usuario/agente.
  - [ ] CA-03: Se registra fecha.
  - [ ] CA-04: El registro no puede modificarse mediante una operación normal.

#### US-44.02 — Proteger secretos

- **Como** sistema **quiero** proteger tokens y credenciales **para** evitar su exposición.
- Origen: A:US-44.02 · Épica: EPIC-44 · Feature: FEAT-44.01 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Los secretos no aparecen en logs normales.
  - [ ] CA-02: No se muestran completos en UI después de almacenarse.
  - [ ] CA-03: Los agentes solo reciben secretos autorizados.

### FEAT-44.02 — Cifrado · origen B:FEAT-26.02

#### US-44.03

- Enunciado: Como operador quiero proteger datos sensibles almacenados.
- Origen: B:US-26.03 · Épica: EPIC-44 · Feature: FEAT-44.02 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-44.04

- Enunciado: Como sistema quiero proteger información sensible durante las comunicaciones.
- Origen: B:US-26.04 · Épica: EPIC-44 · Feature: FEAT-44.02 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-44.03 — Embeddings · origen B:FEAT-26.03

#### US-44.05

- Enunciado: Como sistema quiero proteger embeddings y metadatos asociados.
- Origen: B:US-26.05 · Épica: EPIC-44 · Feature: FEAT-44.03 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-44.04 — Audit Log · origen B:FEAT-27.01

#### US-44.06

- Enunciado: Como operador quiero registrar cada mutación realizada por un agente.
- Origen: B:US-27.01 · Épica: EPIC-44 · Feature: FEAT-44.04 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-44.07

- Enunciado: Como operador quiero consultar el historial completo de una sesión.
- Origen: B:US-27.02 · Épica: EPIC-44 · Feature: FEAT-44.04 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-44.08

- Enunciado: Como auditor quiero reconstruir la secuencia de eventos de una incidencia.
- Origen: B:US-27.03 · Épica: EPIC-44 · Feature: FEAT-44.04 · Alcance: MVP · Prioridad: P1 · Estado: PLANNED
- Criterios de aceptación: MISSING

## EPIC-45 — EXPERIENCIA DE SUPERVISIÓN

### FEAT-45.01 — Dashboard · origen A:FEAT-45.01

#### US-45.01 — Visualizar estado global

- **Como** usuario **quiero** disponer de un dashboard **para** conocer el estado del sistema de un vistazo.
- Origen: A:US-45.01 · Épica: EPIC-45 · Feature: FEAT-45.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Se muestran proyecto activo y estado del ciclo.
  - [ ] CA-02: Se muestran agentes.
  - [ ] CA-03: Se muestran tareas.
  - [ ] CA-04: Se muestran bloqueos relevantes.
  - [ ] CA-05: Los datos se actualizan.

#### US-45.02 — Acceder a un elemento desde el dashboard

- **Como** usuario **quiero** abrir una ejecución, historia o agente desde el dashboard **para** investigar su estado.
- Origen: A:US-45.02 · Épica: EPIC-45 · Feature: FEAT-45.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Cada elemento navegable abre su detalle.
  - [ ] CA-02: Se conserva el contexto del proyecto.
  - [ ] CA-03: Un elemento inexistente muestra error controlado.

### FEAT-45.02 — Multi-proyecto · origen B:FEAT-19.04

#### US-45.03

- Enunciado: Como operador quiero visualizar actividad de varios proyectos desde un panel global.
- Origen: B:US-19.09 · Épica: EPIC-45 · Feature: FEAT-45.02 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- ⚠ Posible solapamiento con US-45.01: revisar si es duplicado, detalle o historia distinta (GAP-006)
- Criterios de aceptación: MISSING

## EPIC-46 — AUTOMATIZACIÓN DEL CICLO DE DESARROLLO

### FEAT-46.01 — Pipeline autónomo · origen A:FEAT-46.01

#### US-46.01 — Ejecutar ciclo completo de una historia

- **Como** sistema autónomo **quiero** ejecutar análisis → implementación → pruebas → revisión **para** completar historias con mínima intervención humana.
- Origen: A:US-46.01 · Épica: EPIC-46 · Feature: FEAT-46.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: El ciclo comienza con una historia READY.
  - [ ] CA-02: Se generan/ejecutan tareas.
  - [ ] CA-03: Se ejecutan verificaciones.
  - [ ] CA-04: Una historia no pasa a DONE si falla aceptación.
  - [ ] CA-05: Todos los pasos quedan trazados.

#### US-46.02 — Solicitar revisión humana cuando sea necesaria

- **Como** sistema autónomo **quiero** detenerme ante decisiones que requieran intervención **para** no tomar decisiones no autorizadas.
- Origen: A:US-46.02 · Épica: EPIC-46 · Feature: FEAT-46.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: El sistema identifica condiciones que requieren revisión.
  - [ ] CA-02: La historia queda bloqueada.
  - [ ] CA-03: Se explica qué decisión falta.
  - [ ] CA-04: El ciclo puede continuar después de resolverla.

### FEAT-46.02 — Pausa · origen B:FEAT-29.01

#### US-46.03

- Enunciado: Como operador quiero pausar un agente durante una operación.
- Origen: B:US-29.01 · Épica: EPIC-46 · Feature: FEAT-46.02 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-46.04

- Enunciado: Como operador quiero reanudar un agente pausado.
- Origen: B:US-29.02 · Épica: EPIC-46 · Feature: FEAT-46.02 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-46.03 — Aprobación · origen B:FEAT-29.02

#### US-46.05

- Enunciado: Como operador quiero aprobar manualmente una operación sensible.
- Origen: B:US-29.03 · Épica: EPIC-46 · Feature: FEAT-46.03 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-46.06

- Enunciado: Como operador quiero rechazar una operación propuesta por un agente.
- Origen: B:US-29.04 · Épica: EPIC-46 · Feature: FEAT-46.03 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-46.04 — Chat · origen B:FEAT-29.03

#### US-46.07

- Enunciado: Como operador quiero comunicarme con un agente desde el contexto de una tarea.
- Origen: B:US-29.05 · Épica: EPIC-46 · Feature: FEAT-46.04 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-46.08

- Enunciado: Como agente quiero recibir instrucciones humanas manteniendo el contexto de la tarea.
- Origen: B:US-29.06 · Épica: EPIC-46 · Feature: FEAT-46.04 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-46.05 — Intervención · origen B:FEAT-40.03

#### US-46.09

- Enunciado: Como operador quiero pausar un agente antes de una operación crítica.
- Origen: B:US-40.05 · Épica: EPIC-46 · Feature: FEAT-46.05 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-46.10

- Enunciado: Como operador quiero aprobar o rechazar una acción sensible desde el panel.
- Origen: B:US-40.06 · Épica: EPIC-46 · Feature: FEAT-46.05 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

## EPIC-47 — PREPARACIÓN PARA JEV / EVOLUCIÓN DEL ENTORNO DE EJECUCIÓN

### FEAT-47.01 — Entorno virtual futuro · origen A:FEAT-47.01

#### US-47.01 — Modelar recursos de ejecución abstractos

- **Como** arquitectura **quiero** abstraer recursos de ejecución **para** poder evolucionar hacia un entorno JEV sin rediseñar todo el sistema.
- Origen: A:US-47.01 · Épica: EPIC-47 · Feature: FEAT-47.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Las tareas no dependen innecesariamente de una implementación concreta.
  - [ ] CA-02: Los recursos de ejecución tienen interfaz abstracta.
  - [ ] CA-03: La implementación actual continúa funcionando.
  - [ ] CA-04: La futura implementación puede conectarse mediante el mismo contrato.

#### US-47.02 — Gestionar entornos de ejecución

- **Como** sistema **quiero** identificar el entorno donde se ejecuta una tarea **para** mantener trazabilidad de ejecución.
- Origen: A:US-47.02 · Épica: EPIC-47 · Feature: FEAT-47.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: Cada ejecución identifica su entorno.
  - [ ] CA-02: El entorno tiene estado.
  - [ ] CA-03: Una ejecución no se asigna a un entorno no disponible.

## EPIC-48 — CONTROL Y GOBERNANZA FINAL DEL SISTEMA

### FEAT-48.01 — Estado global · origen A:FEAT-48.01

#### US-48.01 — Mantener estado global coherente

- **Como** plataforma **quiero** disponer de un estado global consistente **para** que todos los subsistemas conozcan la situación real.
- Origen: A:US-48.01 · Épica: EPIC-48 · Feature: FEAT-48.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: El estado refleja ejecuciones activas.
  - [ ] CA-02: Refleja proyecto y sprint activos.
  - [ ] CA-03: Refleja bloqueos.
  - [ ] CA-04: El estado persiste cuando corresponda.
  - [ ] CA-05: Las transiciones imposibles son rechazadas.

#### US-48.02 — Ejecutar auditoría integral

- **Como** administrador/Product Owner **quiero** ejecutar una auditoría completa **para** detectar inconsistencias antes de continuar el desarrollo.
- Origen: A:US-48.02 · Épica: EPIC-48 · Feature: FEAT-48.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: La auditoría comprueba requisitos sin cobertura.
  - [ ] CA-02: Comprueba historias sin criterios.
  - [ ] CA-03: Comprueba trazabilidad rota.
  - [ ] CA-04: Comprueba documentación desactualizada.
  - [ ] CA-05: Comprueba cambios sin origen.
  - [ ] CA-06: Genera un informe de hallazgos.

#### US-48.03 — Obtener estado real del producto

- **Como** Product Owner **quiero** consultar el estado real del producto **para** conocer qué está implementado, qué está probado y qué está pendiente.
- Origen: A:US-48.03 · Épica: EPIC-48 · Feature: FEAT-48.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación:
  - [ ] CA-01: El sistema diferencia planificado, en desarrollo, implementado, probado y aceptado.
  - [ ] CA-02: Una historia no aparece como aceptada sin criterios PASS.
  - [ ] CA-03: El estado puede rastrearse hasta requisitos.
  - [ ] CA-04: El informe identifica bloqueos y riesgos abiertos.

### FEAT-48.02 — Integridad referencial · origen B:FEAT-42.01

#### US-48.04

- Enunciado: Como Watchdog quiero comprobar que las relaciones entre entidades ACM son válidas.
- Origen: B:US-42.01 · Épica: EPIC-48 · Feature: FEAT-48.02 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-48.05

- Enunciado: Como sistema quiero detectar registros huérfanos.
- Origen: B:US-42.02 · Épica: EPIC-48 · Feature: FEAT-48.02 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-48.03 — Integridad global · origen B:FEAT-42.02

#### US-48.06

- Enunciado: Como Watchdog quiero comprobar que una historia tiene origen, criterios y ejecución trazables.
- Origen: B:US-42.03 · Épica: EPIC-48 · Feature: FEAT-48.03 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-48.07

- Enunciado: Como Watchdog quiero comprobar que una tarea pertenece a una historia válida.
- Origen: B:US-42.04 · Épica: EPIC-48 · Feature: FEAT-48.03 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-48.04 — Gobernanza · origen B:FEAT-42.03

#### US-48.08

- Enunciado: Como operador quiero ejecutar una auditoría global del proyecto.
- Origen: B:US-42.05 · Épica: EPIC-48 · Feature: FEAT-48.04 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- ⚠ Posible solapamiento con US-48.02: revisar si es duplicado, detalle o historia distinta (GAP-006)
- Criterios de aceptación: MISSING

#### US-48.09

- Enunciado: Como operador quiero recibir un informe de incumplimientos.
- Origen: B:US-42.06 · Épica: EPIC-48 · Feature: FEAT-48.04 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

## EPIC-49 — GESTIÓN DE DEUDA TÉCNICA

### FEAT-49.01 — Registro · origen B:FEAT-12.01

#### US-49.01

- Enunciado: Como arquitecto quiero registrar deuda técnica y su motivo.
- Origen: B:US-12.01 · Épica: EPIC-49 · Feature: FEAT-49.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-49.02

- Enunciado: Como agente quiero vincular deuda técnica con el código y decisión que la originaron.
- Origen: B:US-12.02 · Épica: EPIC-49 · Feature: FEAT-49.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-49.02 — Análisis · origen B:FEAT-12.02

#### US-49.03

- Enunciado: Como Scrum Master quiero conocer el impacto de la deuda sobre el sprint.
- Origen: B:US-12.03 · Épica: EPIC-49 · Feature: FEAT-49.02 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-49.04

- Enunciado: Como sistema quiero detectar deuda recurrente.
- Origen: B:US-12.04 · Épica: EPIC-49 · Feature: FEAT-49.02 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-49.05

- Enunciado: Como sistema quiero calcular indicadores de deuda acumulada.
- Origen: B:US-12.05 · Épica: EPIC-49 · Feature: FEAT-49.02 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-49.03 — Debt Gate · origen B:FEAT-12.03

#### US-49.06

- Enunciado: Como Watchdog quiero bloquear nuevas funcionalidades cuando se supere el umbral configurado de deuda.
- Origen: B:US-12.06 · Épica: EPIC-49 · Feature: FEAT-49.03 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-49.07

- Enunciado: Como Scrum Master quiero recibir una propuesta de sprint de refactorización cuando el umbral se supere.
- Origen: B:US-12.07 · Épica: EPIC-49 · Feature: FEAT-49.03 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

## EPIC-50 — MODELOS DE DECISIÓN JEV (OLLAYA)

### FEAT-50.01 — Conector JEV · origen B:FEAT-24.01

#### US-50.01

- Enunciado: Como sistema quiero conectarme a un servidor JEV para ejecutar evaluaciones decisionales.
- Origen: B:US-24.01 · Épica: EPIC-50 · Feature: FEAT-50.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-50.02

- Enunciado: Como agente quiero solicitar una evaluación JEV antes de una decisión crítica.
- Origen: B:US-24.02 · Épica: EPIC-50 · Feature: FEAT-50.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-50.02 — Orquestación híbrida · origen B:FEAT-24.02

#### US-50.03

- Enunciado: Como sistema quiero dirigir tareas generativas hacia Ollama y tareas decisionales hacia JEV cuando corresponda.
- Origen: B:US-24.03 · Épica: EPIC-50 · Feature: FEAT-50.02 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-50.04

- Enunciado: Como sistema quiero registrar qué motor produjo cada decisión.
- Origen: B:US-24.04 · Épica: EPIC-50 · Feature: FEAT-50.02 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-50.03 — Simulación · origen B:FEAT-24.03

#### US-50.05

- Enunciado: Como Scrum Master quiero simular diferentes escenarios de sprint.
- Origen: B:US-24.05 · Épica: EPIC-50 · Feature: FEAT-50.03 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-50.06

- Enunciado: Como arquitecto quiero evaluar riesgos antes de cambios estructurales.
- Origen: B:US-24.06 · Épica: EPIC-50 · Feature: FEAT-50.03 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-50.04 — Watchdog JEV · origen B:FEAT-24.04

#### US-50.07

- Enunciado: Como Watchdog quiero utilizar reglas decisionales para validar propuestas de agentes.
- Origen: B:US-24.07 · Épica: EPIC-50 · Feature: FEAT-50.04 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-50.08

- Enunciado: Como operador quiero consultar la evaluación decisional asociada a una decisión crítica.
- Origen: B:US-24.08 · Épica: EPIC-50 · Feature: FEAT-50.04 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

## EPIC-51 — SANDBOX, GEMELO DIGITAL Y USUARIOS SINTÉTICOS

### FEAT-51.01 — Sandbox · origen B:FEAT-25.01

#### US-51.01

- Enunciado: Como sistema quiero crear un entorno aislado para probar cambios antes de aplicarlos.
- Origen: B:US-25.01 · Épica: EPIC-51 · Feature: FEAT-51.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-51.02

- Enunciado: Como agente quiero ejecutar un plan completo en sandbox antes de modificar el proyecto real.
- Origen: B:US-25.02 · Épica: EPIC-51 · Feature: FEAT-51.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-51.02 — Gemelo de ejecución · origen B:FEAT-25.02

#### US-51.03

- Enunciado: Como Scrum Master quiero simular un sprint antes de iniciarlo.
- Origen: B:US-25.03 · Épica: EPIC-51 · Feature: FEAT-51.02 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-51.04

- Enunciado: Como QA quiero ejecutar criterios de aceptación en el gemelo.
- Origen: B:US-25.04 · Épica: EPIC-51 · Feature: FEAT-51.02 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-51.03 — Comparación · origen B:FEAT-25.03

#### US-51.05

- Enunciado: Como operador quiero comparar el estado previo y posterior de una simulación.
- Origen: B:US-25.05 · Épica: EPIC-51 · Feature: FEAT-51.03 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-51.06

- Enunciado: Como sistema quiero impedir la promoción de un cambio cuando la simulación detecte un fallo crítico.
- Origen: B:US-25.06 · Épica: EPIC-51 · Feature: FEAT-51.03 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-51.04 — Chaos Testing · origen B:FEAT-25.04

#### US-51.07

- Enunciado: Como QA quiero ejecutar escenarios de fallo controlados sobre un entorno aislado.
- Origen: B:US-25.07 · Épica: EPIC-51 · Feature: FEAT-51.04 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-51.08

- Enunciado: Como Watchdog quiero comprobar que el sistema recupera correctamente estados degradados.
- Origen: B:US-25.08 · Épica: EPIC-51 · Feature: FEAT-51.04 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-51.05 — Gemelos de usuario · origen B:FEAT-47.01

#### US-51.09

- Enunciado: Como QA quiero crear agentes que representen roles de usuario concretos.
- Origen: B:US-47.01 · Épica: EPIC-51 · Feature: FEAT-51.05 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-51.10

- Enunciado: Como QA quiero ejecutar un flujo como si fuera un usuario final.
- Origen: B:US-47.02 · Épica: EPIC-51 · Feature: FEAT-51.05 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-51.06 — Manual generado · origen B:FEAT-47.02

#### US-51.11

- Enunciado: Como sistema quiero generar instrucciones de usuario a partir de los flujos realmente ejecutados.
- Origen: B:US-47.03 · Épica: EPIC-51 · Feature: FEAT-51.06 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-51.12

- Enunciado: Como sistema quiero detectar discrepancias entre manual y aplicación.
- Origen: B:US-47.04 · Épica: EPIC-51 · Feature: FEAT-51.06 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-51.07 — Chaos End-User · origen B:FEAT-47.03

#### US-51.13

- Enunciado: Como QA quiero ejecutar escenarios de uso no ideales en sandbox.
- Origen: B:US-47.05 · Épica: EPIC-51 · Feature: FEAT-51.07 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-51.14

- Enunciado: Como sistema quiero crear bugs cuando un usuario sintético encuentre una inconsistencia.
- Origen: B:US-47.06 · Épica: EPIC-51 · Feature: FEAT-51.07 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

## EPIC-52 — CLI DE ADMINISTRACIÓN

### FEAT-52.01 — CLI · origen B:FEAT-31.01

#### US-52.01

- Enunciado: Como desarrollador quiero consultar el estado de ACM desde terminal.
- Origen: B:US-31.01 · Épica: EPIC-52 · Feature: FEAT-52.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-52.02

- Enunciado: Como desarrollador quiero ejecutar auditorías desde CLI.
- Origen: B:US-31.02 · Épica: EPIC-52 · Feature: FEAT-52.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-52.03

- Enunciado: Como desarrollador quiero consultar trazabilidad desde CLI.
- Origen: B:US-31.03 · Épica: EPIC-52 · Feature: FEAT-52.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-52.04

- Enunciado: Como desarrollador quiero gestionar sprints desde CLI.
- Origen: B:US-31.04 · Épica: EPIC-52 · Feature: FEAT-52.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-52.02 — Operaciones administrativas · origen B:FEAT-31.02

#### US-52.05

- Enunciado: Como operador quiero ejecutar operaciones de mantenimiento desde CLI.
- Origen: B:US-31.05 · Épica: EPIC-52 · Feature: FEAT-52.02 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-52.06

- Enunciado: Como operador quiero consultar la salud de la base de datos desde CLI.
- Origen: B:US-31.06 · Épica: EPIC-52 · Feature: FEAT-52.02 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

## EPIC-53 — EXTENSIONES, PLUGINS Y EXTENSIBILIDAD DEL MOTOR

### FEAT-53.01 — Plugins · origen B:FEAT-32.01

#### US-53.01

- Enunciado: Como desarrollador quiero registrar extensiones de ACM sin modificar el núcleo.
- Origen: B:US-32.01 · Épica: EPIC-53 · Feature: FEAT-53.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-53.02

- Enunciado: Como desarrollador quiero descubrir plugins instalados.
- Origen: B:US-32.02 · Épica: EPIC-53 · Feature: FEAT-53.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-53.03

- Enunciado: Como sistema quiero controlar los permisos de cada extensión.
- Origen: B:US-32.03 · Épica: EPIC-53 · Feature: FEAT-53.01 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-53.02 — Herramientas personalizadas · origen B:FEAT-32.02

#### US-53.04

- Enunciado: Como desarrollador quiero incorporar herramientas MCP personalizadas.
- Origen: B:US-32.04 · Épica: EPIC-53 · Feature: FEAT-53.02 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-53.05

- Enunciado: Como sistema quiero registrar y auditar las herramientas externas utilizadas.
- Origen: B:US-32.05 · Épica: EPIC-53 · Feature: FEAT-53.02 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-53.03 — Nuevos tipos de agentes · origen B:FEAT-48.01

#### US-53.06

- Enunciado: Como desarrollador quiero registrar nuevos perfiles de agente.
- Origen: B:US-48.01 · Épica: EPIC-53 · Feature: FEAT-53.03 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

#### US-53.07

- Enunciado: Como desarrollador quiero definir las capacidades y permisos de un perfil.
- Origen: B:US-48.02 · Épica: EPIC-53 · Feature: FEAT-53.03 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-53.04 — Nuevas herramientas · origen B:FEAT-48.02

#### US-53.08

- Enunciado: Como desarrollador quiero incorporar nuevas herramientas MCP sin modificar el núcleo.
- Origen: B:US-48.03 · Épica: EPIC-53 · Feature: FEAT-53.04 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

### FEAT-53.05 — Eventos · origen B:FEAT-48.03

#### US-53.09

- Enunciado: Como desarrollador quiero reaccionar a eventos ACM mediante extensiones.
- Origen: B:US-48.04 · Épica: EPIC-53 · Feature: FEAT-53.05 · Alcance: POST-MVP · Prioridad: P3 · Estado: PLANNED
- Criterios de aceptación: MISSING

