<!--
FUENTE A del backlog unificado (ADR-010). Transcripción íntegra del "prompt inicial del proyecto"
aportado por el operador (NoaR-es) el 2026-09-30. No editar el contenido: los cambios de alcance
generan una nueva versión y esta pasa a 99_ARCHIVO/superseded/. Parseado por control/tools/derive_backlog.py.
-->

# PRODUCT BACKLOG COMPLETO

## Sistema Autónomo de Desarrollo de Software mediante Agentes IA

---

# 0. ESTRUCTURA DEL BACKLOG

La jerarquía utilizada es:

```text
REQUISITO
   ↓
ÉPICA
   ↓
FEATURE
   ↓
USER STORY
   ↓
CRITERIOS DE ACEPTACIÓN
   ↓
TAREAS TÉCNICAS
```

Las historias están pensadas para que:

* tengan valor funcional;
* puedan implementarse individualmente;
* puedan probarse individualmente;
* tengan criterios PASS/FAIL;
* tengan trazabilidad;
* contemplen errores y estados relevantes;
* no conviertan tareas técnicas en falsas User Stories.

---

# EPIC-01 — GESTIÓN DEL PROYECTO Y CICLO DE VIDA

## Objetivo

Permitir crear, configurar, abrir, cerrar y administrar proyectos de desarrollo autónomo.

### FEAT-01.01 — Creación de proyectos

### US-01.01 — Crear un proyecto

**Como** administrador del sistema
**quiero** crear un nuevo proyecto
**para** disponer de un espacio independiente de desarrollo autónomo.

**Precondiciones**

* El usuario está autenticado.
* Tiene permiso para crear proyectos.

**Flujo**

1. El usuario selecciona crear proyecto.
2. Introduce nombre y configuración inicial.
3. El sistema valida los datos.
4. Se crea la estructura inicial.
5. El proyecto aparece disponible.

**Errores**

* Nombre inválido.
* Proyecto duplicado.
* Error de almacenamiento.

**Criterios de aceptación**

* **CA-01:** Dado un usuario autorizado, cuando introduce datos válidos y confirma, entonces se crea exactamente un proyecto.
* **CA-02:** Si el nombre obligatorio está vacío, entonces el sistema impide la creación e identifica el campo.
* **CA-03:** Si ya existe un proyecto con el identificador correspondiente, entonces no se crea un duplicado.
* **CA-04:** Si falla el almacenamiento, entonces el proyecto no queda registrado parcialmente y se muestra un error recuperable.
* **CA-05:** Tras una creación correcta, el proyecto puede abrirse desde el listado.

**Tareas**

* Modelo de proyecto.
* Servicio de creación.
* Persistencia.
* Validaciones.
* Tests.

---

### US-01.02 — Abrir y seleccionar un proyecto

**Como** usuario autorizado
**quiero** seleccionar un proyecto existente
**para** trabajar sobre su contexto, memoria y backlog.

**Criterios de aceptación**

* **CA-01:** Solo aparecen proyectos a los que el usuario tiene acceso.
* **CA-02:** Al seleccionar un proyecto se carga su contexto.
* **CA-03:** El proyecto activo queda identificado visualmente.
* **CA-04:** Si el proyecto ya no existe, se informa del error y se limpia la selección.
* **CA-05:** Cambiar de proyecto no mezcla datos del proyecto anterior con el nuevo.

---

### US-01.03 — Configurar un proyecto

**Como** administrador del proyecto
**quiero** modificar su configuración
**para** adaptar el comportamiento del sistema.

**Criterios de aceptación**

* **CA-01:** Los parámetros modificables se muestran con su valor actual.
* **CA-02:** Los valores inválidos son rechazados antes de guardar.
* **CA-03:** Una configuración válida queda persistida.
* **CA-04:** Los cambios que requieran reinicio o recarga quedan identificados.
* **CA-05:** La configuración pertenece exclusivamente al proyecto seleccionado.

---

# EPIC-02 — MEMORIA `CONTROL/` Y FUENTE DE VERDAD

## FEAT-02.01 — Estructura documental

### US-02.01 — Inicializar `control/`

**Como** sistema autónomo
**quiero** crear la estructura `control/`
**para** disponer de una memoria persistente y organizada del proyecto.

**Criterios de aceptación**

* **CA-01:** Un proyecto nuevo genera la estructura definida.
* **CA-02:** Existe un índice raíz.
* **CA-03:** Las áreas de producto, backlog, arquitectura, calidad y planificación tienen índices.
* **CA-04:** La estructura no se genera duplicada al reinicializar.
* **CA-05:** El sistema registra la inicialización.

### US-02.02 — Consultar el índice de `control/`

**Como** agente IA
**quiero** consultar primero los índices
**para** localizar únicamente la información necesaria.

**Criterios de aceptación**

* **CA-01:** El índice identifica los documentos existentes.
* **CA-02:** Cada entrada permite localizar su contenido.
* **CA-03:** Un documento inexistente no aparece como disponible.
* **CA-04:** El agente puede localizar requisitos, arquitectura y backlog sin recorrer todo el árbol.

### US-02.03 — Actualizar memoria de proyecto

**Como** agente de desarrollo
**quiero** actualizar los documentos de control después de cambios relevantes
**para** mantener sincronizada la memoria del proyecto.

**Criterios de aceptación**

* **CA-01:** Una decisión registrada queda persistida.
* **CA-02:** Los cambios conservan trazabilidad.
* **CA-03:** No se sobrescribe información previa sin mecanismo de historial.
* **CA-04:** El índice refleja documentos nuevos o modificados.

---

# EPIC-03 — PRODUCT OWNER Y DESCUBRIMIENTO DE REQUISITOS

## FEAT-03.01 — Análisis de producto

### US-03.01 — Analizar una idea de producto

**Como** Product Owner IA
**quiero** analizar una idea completa
**para** convertirla en requisitos estructurados.

**Criterios de aceptación**

* **CA-01:** El análisis identifica actores, objetivos y funcionalidades explícitas.
* **CA-02:** Los requisitos reciben identificadores únicos.
* **CA-03:** Se diferencian requisitos explícitos, implícitos y decisiones técnicas.
* **CA-04:** Las contradicciones quedan registradas.
* **CA-05:** Ninguna funcionalidad explícita desaparece durante la transformación.

### US-03.02 — Incorporar funcionalidades confirmadas

**Como** Product Owner
**quiero** incorporar funcionalidades confirmadas posteriormente
**para** asegurar que forman parte obligatoria del producto.

**Criterios de aceptación**

* **CA-01:** Cada funcionalidad confirmada recibe trazabilidad.
* **CA-02:** Una funcionalidad confirmada no puede quedar clasificada como opcional.
* **CA-03:** El sistema detecta conflictos con requisitos existentes.
* **CA-04:** Cada funcionalidad termina vinculada a una o más historias.

### US-03.03 — Mantener trazabilidad requisito-backlog

**Como** Product Owner
**quiero** saber qué historias implementan cada requisito
**para** detectar funcionalidades sin implementar.

**Criterios de aceptación**

* **CA-01:** Cada requisito puede localizar sus épicas.
* **CA-02:** Cada épica puede localizar sus features.
* **CA-03:** Cada feature puede localizar sus historias.
* **CA-04:** Cada historia identifica sus requisitos de origen.
* **CA-05:** Los requisitos huérfanos aparecen en una auditoría.

---

# EPIC-04 — PRODUCT BACKLOG Y ÉPICAS

## FEAT-04.01 — Gestión de backlog

### US-04.01 — Crear una épica

**Como** Product Owner
**quiero** crear una épica funcional
**para** agrupar capacidades relacionadas.

**Criterios de aceptación**

* **CA-01:** La épica recibe identificador único.
* **CA-02:** Tiene objetivo y alcance.
* **CA-03:** Puede asociarse a requisitos.
* **CA-04:** Puede contener features.
* **CA-05:** No se permite crear épicas duplicadas con el mismo identificador.

### US-04.02 — Descomponer una épica en features

**Como** Product Owner
**quiero** descomponer una épica
**para** obtener capacidades funcionales manejables.

**Criterios de aceptación**

* **CA-01:** Cada feature tiene identificador.
* **CA-02:** Cada feature pertenece a una épica.
* **CA-03:** Las features cubren el objetivo de la épica.
* **CA-04:** Una feature demasiado grande puede dividirse.

### US-04.03 — Crear User Stories

**Como** Product Owner
**quiero** convertir features en historias
**para** crear unidades implementables.

**Criterios de aceptación**

* **CA-01:** Cada historia tiene actor, acción y valor.
* **CA-02:** Cada historia tiene requisito de origen.
* **CA-03:** Cada historia tiene criterios de aceptación.
* **CA-04:** Una historia incompleta no puede marcarse como READY.
* **CA-05:** Las tareas técnicas no se registran como historias de usuario salvo que exista una razón explícita.

---

# EPIC-05 — SCRUM MASTER Y PLANIFICACIÓN

## FEAT-05.01 — Planificación

### US-05.01 — Priorizar historias

**Como** Scrum Master/Product Owner
**quiero** ordenar el backlog según valor y dependencias
**para** determinar qué debe desarrollarse primero.

**Criterios de aceptación**

* **CA-01:** Cada historia tiene prioridad.
* **CA-02:** La prioridad puede modificarse.
* **CA-03:** Las dependencias se tienen en cuenta al proponer orden.
* **CA-04:** Una historia bloqueada no se presenta como inmediatamente ejecutable.

### US-05.02 — Crear un sprint

**Como** Scrum Master
**quiero** crear un sprint
**para** agrupar trabajo con un objetivo concreto.

**Criterios de aceptación**

* **CA-01:** El sprint tiene identificador y objetivo.
* **CA-02:** Las historias asignadas quedan vinculadas al sprint.
* **CA-03:** El sistema detecta dependencias incompatibles.
* **CA-04:** El sprint puede pasar por estados definidos.

### US-05.03 — Cerrar un sprint

**Como** Scrum Master
**quiero** cerrar un sprint
**para** registrar su resultado y actualizar la planificación.

**Criterios de aceptación**

* **CA-01:** El sistema identifica historias terminadas y no terminadas.
* **CA-02:** Las historias no terminadas pueden trasladarse.
* **CA-03:** Se genera un resumen del sprint.
* **CA-04:** El historial del sprint queda conservado.

---

# EPIC-06 — KANBAN REACTIVO

## FEAT-06.01 — Tablero

### US-06.01 — Visualizar el tablero Kanban

**Como** miembro del equipo
**quiero** visualizar el trabajo en columnas
**para** conocer el estado actual del desarrollo.

**Criterios de aceptación**

* **CA-01:** Cada historia aparece en exactamente una columna de estado.
* **CA-02:** Se muestran identificador, título y estado.
* **CA-03:** Solo se muestran historias del contexto seleccionado.
* **CA-04:** Una historia inexistente no aparece en el tablero.

### US-06.02 — Cambiar el estado de una historia

**Como** agente de desarrollo
**quiero** cambiar el estado de una historia
**para** reflejar su progreso real.

**Criterios de aceptación**

* **CA-01:** Un cambio permitido actualiza el estado.
* **CA-02:** El cambio queda registrado.
* **CA-03:** Las transiciones no permitidas son rechazadas.
* **CA-04:** El tablero refleja el nuevo estado.

### US-06.03 — Actualizar Kanban en tiempo real

**Como** usuario del sistema
**quiero** recibir cambios del tablero en tiempo real
**para** no tener que recargar la aplicación.

**Criterios de aceptación**

* **CA-01:** Un cambio realizado por un agente genera un evento.
* **CA-02:** Los clientes conectados reciben el cambio.
* **CA-03:** Un cliente desconectado puede recuperar el estado al reconectar.
* **CA-04:** Un evento duplicado no genera una segunda modificación.

---

# EPIC-07 — ORQUESTADOR DE AGENTES

## FEAT-07.01 — Ciclo autónomo

### US-07.01 — Iniciar el ciclo autónomo

**Como** usuario autorizado
**quiero** iniciar el ciclo autónomo
**para** que el equipo IA comience a trabajar.

**Criterios de aceptación**

* **CA-01:** El sistema comprueba que existe un proyecto válido.
* **CA-02:** Comprueba que existe trabajo ejecutable.
* **CA-03:** Inicializa el orquestador.
* **CA-04:** El estado pasa a RUNNING.
* **CA-05:** Un segundo inicio no crea dos ciclos simultáneos.

### US-07.02 — Orquestar una historia

**Como** sistema
**quiero** asignar una historia al agente adecuado
**para** ejecutar el trabajo necesario.

**Criterios de aceptación**

* **CA-01:** La historia seleccionada queda registrada.
* **CA-02:** Se determina el agente responsable.
* **CA-03:** Se respetan dependencias.
* **CA-04:** El estado de ejecución queda registrado.
* **CA-05:** Un fallo de asignación no marca la historia como terminada.

### US-07.03 — Detener el ciclo autónomo

**Como** usuario autorizado
**quiero** detener el ciclo
**para** recuperar el control del proyecto.

**Criterios de aceptación**

* **CA-01:** El sistema solicita detener nuevas ejecuciones.
* **CA-02:** No se asignan nuevas tareas después de la parada.
* **CA-03:** Las ejecuciones activas quedan registradas.
* **CA-04:** El estado global cambia a STOPPED.

---

# EPIC-08 — AGENTES, INSTANCIAS Y HILOS

## FEAT-08.01 — Gestión de agentes

### US-08.01 — Crear una instancia de agente

**Como** orquestador
**quiero** crear una instancia de un perfil
**para** ejecutar una tarea concreta con contexto aislado.

**Criterios de aceptación**

* **CA-01:** La instancia referencia su perfil.
* **CA-02:** Tiene identificador único.
* **CA-03:** Tiene proyecto y contexto asociados.
* **CA-04:** Su estado inicial es válido.
* **CA-05:** No comparte accidentalmente memoria privada de otra instancia.

### US-08.02 — Gestionar hilos de ejecución

**Como** agente
**quiero** disponer de hilos/contextos independientes
**para** ejecutar conversaciones o tareas separadas.

**Criterios de aceptación**

* **CA-01:** Cada hilo tiene identificador.
* **CA-02:** El contexto del hilo se conserva.
* **CA-03:** Los mensajes pertenecen al hilo correcto.
* **CA-04:** Dos hilos no mezclan sus mensajes.

### US-08.03 — Visualizar agentes, instancias e hilos

**Como** usuario
**quiero** conocer cuántos agentes, instancias e hilos existen
**para** supervisar el sistema.

**Criterios de aceptación**

* **CA-01:** El sistema muestra los agentes activos.
* **CA-02:** Muestra instancias.
* **CA-03:** Muestra hilos.
* **CA-04:** Los contadores se actualizan cuando cambia el estado.

---

# EPIC-09 — ROLES PROFESIONALES DEL EQUIPO IA

## FEAT-09.01 — Roles

### US-09.01 — Ejecutar Product Owner IA

**Como** sistema
**quiero** disponer de un agente Product Owner
**para** gestionar requisitos y backlog.

**Criterios de aceptación**

* **CA-01:** El agente puede analizar requisitos.
* **CA-02:** Puede crear/modificar backlog según permisos.
* **CA-03:** Sus cambios quedan trazados.
* **CA-04:** No puede ejecutar operaciones fuera de sus capacidades autorizadas.

### US-09.02 — Ejecutar Architect IA

**Como** sistema
**quiero** disponer de un agente arquitecto
**para** mantener decisiones y arquitectura.

**Criterios de aceptación**

* **CA-01:** Puede consultar requisitos.
* **CA-02:** Puede proponer decisiones arquitectónicas.
* **CA-03:** Las decisiones quedan registradas.
* **CA-04:** Las decisiones no borran requisitos funcionales.

### US-09.03 — Ejecutar Developer IA

**Como** sistema
**quiero** disponer de agentes desarrolladores
**para** implementar historias aprobadas.

**Criterios de aceptación**

* **CA-01:** Un Developer recibe una historia concreta.
* **CA-02:** Puede consultar su contexto.
* **CA-03:** Registra cambios.
* **CA-04:** Ejecuta pruebas.
* **CA-05:** No puede declarar terminada una historia sin cumplir sus criterios.

---

# EPIC-10 — DESCOMPOSICIÓN TÉCNICA Y EJECUCIÓN

## FEAT-10.01 — Tasks

### US-10.01 — Descomponer una User Story en tareas técnicas

**Como** Developer/Tech Lead IA
**quiero** convertir una historia en tareas técnicas
**para** poder implementarla de forma controlada.

**Criterios de aceptación**

* **CA-01:** Las tareas derivan de la historia.
* **CA-02:** Cada tarea tiene objetivo.
* **CA-03:** Las tareas cubren implementación y pruebas necesarias.
* **CA-04:** Ninguna tarea introduce funcionalidad no aprobada sin registrarla.

### US-10.02 — Ejecutar una tarea técnica

**Como** Developer IA
**quiero** ejecutar una tarea
**para** producir el cambio requerido.

**Criterios de aceptación**

* **CA-01:** La tarea pasa a ejecución.
* **CA-02:** Los cambios quedan registrados.
* **CA-03:** Si falla, la tarea queda en estado de error.
* **CA-04:** El agente no declara éxito sin verificación.

### US-10.03 — Verificar una historia

**Como** QA/Developer IA
**quiero** ejecutar las comprobaciones de aceptación
**para** determinar objetivamente si una historia está terminada.

**Criterios de aceptación**

* **CA-01:** Cada CA puede marcarse PASS/FAIL.
* **CA-02:** Una historia con un CA FAIL no puede pasar a DONE.
* **CA-03:** Se conserva la evidencia de la prueba.
* **CA-04:** El resultado queda vinculado a la historia.

---

# EPIC-11 — GESTIÓN DEL CÓDIGO Y REPOSITORIO

## FEAT-11.01 — Cambios

### US-11.01 — Registrar cambios realizados por un agente

**Como** sistema
**quiero** registrar cada cambio producido por un agente
**para** mantener trazabilidad.

**Criterios de aceptación**

* **CA-01:** Cada cambio identifica agente.
* **CA-02:** Identifica historia/tarea.
* **CA-03:** Registra fecha.
* **CA-04:** Registra resultado.
* **CA-05:** Puede relacionarse con la evidencia de prueba.

### US-11.02 — Detectar cambios no vinculados

**Como** sistema
**quiero** detectar cambios sin tarea o historia asociada
**para** impedir modificaciones inexplicables.

**Criterios de aceptación**

* **CA-01:** Un cambio sin referencia aparece como huérfano.
* **CA-02:** El sistema permite investigar su origen.
* **CA-03:** No se marca como cambio funcional válido automáticamente.

### US-11.03 — Mantener historial técnico

**Como** arquitecto
**quiero** conservar el historial de modificaciones relevantes
**para** comprender la evolución del sistema.

**Criterios de aceptación**

* **CA-01:** Las decisiones importantes tienen historial.
* **CA-02:** Los cambios pueden relacionarse con historias.
* **CA-03:** El historial no se elimina al cerrar un sprint.

---

# EPIC-12 — SNAPSHOTS, CHECKPOINTS Y ROLLBACK

## FEAT-12.01 — Protección del proyecto

### US-12.01 — Crear snapshot

**Como** sistema
**quiero** crear un snapshot antes de cambios de riesgo
**para** disponer de un punto de recuperación.

**Criterios de aceptación**

* **CA-01:** El snapshot tiene identificador.
* **CA-02:** Identifica estado del proyecto.
* **CA-03:** Se registra el motivo.
* **CA-04:** Puede localizarse posteriormente.

### US-12.02 — Restaurar un snapshot

**Como** usuario autorizado
**quiero** restaurar un snapshot
**para** recuperar un estado anterior.

**Criterios de aceptación**

* **CA-01:** Solo snapshots válidos pueden restaurarse.
* **CA-02:** El sistema solicita confirmación cuando corresponda.
* **CA-03:** El estado restaurado coincide con el snapshot seleccionado.
* **CA-04:** La restauración queda registrada.
* **CA-05:** No se pierde silenciosamente el historial posterior.

### US-12.03 — Recuperar tras fallo de agente

**Como** sistema
**quiero** recuperar el estado anterior a una ejecución fallida
**para** evitar daños persistentes.

**Criterios de aceptación**

* **CA-01:** El fallo se detecta.
* **CA-02:** Se identifica el checkpoint aplicable.
* **CA-03:** Se restaura cuando la política lo determine.
* **CA-04:** El fallo y recuperación quedan registrados.

---

# EPIC-13 — WATCHDOG Y AUTOSUPERVISIÓN

## FEAT-13.01 — Supervisión

### US-13.01 — Detectar agentes bloqueados

**Como** Watchdog
**quiero** detectar ejecuciones que no progresan
**para** evitar bloqueos indefinidos.

**Criterios de aceptación**

* **CA-01:** Se mide actividad/progreso.
* **CA-02:** Se aplica un umbral configurable.
* **CA-03:** Una ejecución bloqueada se marca.
* **CA-04:** No se marca como bloqueada una ejecución que continúa progresando.

### US-13.02 — Gestionar una ejecución bloqueada

**Como** Watchdog
**quiero** aplicar una estrategia de recuperación
**para** devolver el sistema a un estado operativo.

**Criterios de aceptación**

* **CA-01:** La estrategia utilizada queda registrada.
* **CA-02:** Puede cancelar, reintentar o aislar la ejecución según política.
* **CA-03:** No se generan múltiples recuperaciones simultáneas para el mismo fallo.
* **CA-04:** El estado final queda registrado.

### US-13.03 — Supervisar salud global

**Como** administrador
**quiero** conocer el estado de los servicios y agentes
**para** detectar problemas sistémicos.

**Criterios de aceptación**

* **CA-01:** Se muestran componentes relevantes.
* **CA-02:** Cada componente tiene estado.
* **CA-03:** Un componente degradado queda identificado.
* **CA-04:** La información se actualiza.

---

# EPIC-14 — MCP Y HERRAMIENTAS

## FEAT-14.01 — MCP

### US-14.01 — Registrar un servidor MCP

**Como** administrador
**quiero** registrar un servidor MCP
**para** proporcionar herramientas a los agentes.

**Criterios de aceptación**

* **CA-01:** El servidor tiene identificador.
* **CA-02:** Se valida su configuración.
* **CA-03:** Sus herramientas se descubren cuando está disponible.
* **CA-04:** Un servidor inválido no queda activo.

### US-14.02 — Asignar MCP a un proyecto

**Como** administrador
**quiero** asociar un MCP a un proyecto
**para** limitar su contexto y disponibilidad.

**Criterios de aceptación**

* **CA-01:** El MCP puede habilitarse para proyectos concretos.
* **CA-02:** Un agente de otro proyecto no puede utilizarlo si carece de autorización.
* **CA-03:** El vínculo queda registrado.

### US-14.03 — Ejecutar una herramienta MCP

**Como** agente IA
**quiero** invocar una herramienta MCP autorizada
**para** realizar una operación externa.

**Criterios de aceptación**

* **CA-01:** La herramienta debe estar disponible.
* **CA-02:** La llamada utiliza los parámetros definidos.
* **CA-03:** El resultado queda asociado a la ejecución.
* **CA-04:** Los errores se devuelven al agente sin marcar éxito.
* **CA-05:** Las herramientas no autorizadas son rechazadas.

---

# EPIC-15 — SKILLS Y CAPACIDADES REUTILIZABLES

## FEAT-15.01 — Skills

### US-15.01 — Registrar una Skill

**Como** administrador
**quiero** registrar una Skill reutilizable
**para** ampliar las capacidades de los agentes.

**Criterios de aceptación**

* **CA-01:** La Skill tiene identificador y versión.
* **CA-02:** Declara sus capacidades.
* **CA-03:** Declara dependencias.
* **CA-04:** Una Skill inválida no se activa.

### US-15.02 — Asignar una Skill a un agente

**Como** administrador
**quiero** asignar Skills
**para** configurar las capacidades de cada agente.

**Criterios de aceptación**

* **CA-01:** Solo Skills disponibles pueden asignarse.
* **CA-02:** La asignación queda registrada.
* **CA-03:** El agente puede descubrir las Skills habilitadas.
* **CA-04:** Una Skill retirada deja de estar disponible según la política definida.

### US-15.03 — Versionar Skills

**Como** administrador
**quiero** mantener versiones de Skills
**para** evitar cambios incompatibles inesperados.

**Criterios de aceptación**

* **CA-01:** Cada versión tiene identificador.
* **CA-02:** Una instancia existente conserva la versión asignada cuando corresponda.
* **CA-03:** Las actualizaciones quedan registradas.
* **CA-04:** Puede identificarse qué versión utilizó una ejecución.

---

# EPIC-16 — RAG Y MEMORIA SEMÁNTICA

## FEAT-16.01 — Conocimiento

### US-16.01 — Indexar documentación del proyecto

**Como** sistema
**quiero** indexar documentación relevante
**para** que los agentes puedan recuperarla semánticamente.

**Criterios de aceptación**

* **CA-01:** Los documentos seleccionados se procesan.
* **CA-02:** Se generan representaciones indexables.
* **CA-03:** Se conserva referencia al documento original.
* **CA-04:** Los documentos modificados pueden reindexarse.
* **CA-05:** Los documentos eliminados dejan de recuperarse.

### US-16.02 — Recuperar contexto mediante RAG

**Como** agente IA
**quiero** recuperar conocimiento relevante
**para** responder y actuar con contexto del proyecto.

**Criterios de aceptación**

* **CA-01:** La consulta produce resultados relacionados.
* **CA-02:** Cada resultado conserva su fuente.
* **CA-03:** El agente recibe contexto suficiente para utilizarlo.
* **CA-04:** Una consulta sin resultados no inventa fuentes.

### US-16.03 — Separar memoria de instancia y memoria compartida

**Como** arquitectura de agentes
**quiero** separar memoria privada y compartida
**para** evitar contaminación de contexto.

**Criterios de aceptación**

* **CA-01:** Una memoria privada no aparece en otra instancia no autorizada.
* **CA-02:** La memoria compartida puede ser consultada por agentes autorizados.
* **CA-03:** El origen de cada memoria es identificable.

---

# EPIC-17 — PRODUCT GRAPH

## FEAT-17.01 — Grafo del producto

### US-17.01 — Representar entidades del producto como grafo

**Como** sistema
**quiero** representar requisitos, features, historias, agentes y componentes como nodos
**para** relacionarlos explícitamente.

**Criterios de aceptación**

* **CA-01:** Las entidades relevantes pueden representarse.
* **CA-02:** Cada nodo tiene identificador.
* **CA-03:** Las relaciones tienen tipo.
* **CA-04:** No se crean relaciones inexistentes.

### US-17.02 — Consultar dependencias mediante Product Graph

**Como** arquitecto
**quiero** consultar relaciones entre elementos
**para** conocer el impacto de un cambio.

**Criterios de aceptación**

* **CA-01:** Una consulta devuelve relaciones existentes.
* **CA-02:** Puede seguirse una dependencia hasta su origen.
* **CA-03:** El sistema identifica elementos afectados.
* **CA-04:** Los resultados respetan el proyecto seleccionado.

### US-17.03 — Detectar elementos huérfanos

**Como** sistema de calidad
**quiero** detectar nodos sin relaciones necesarias
**para** encontrar requisitos o trabajo perdido.

**Criterios de aceptación**

* **CA-01:** Un requisito sin historia aparece como huérfano.
* **CA-02:** Una historia sin requisito queda identificada.
* **CA-03:** Una dependencia rota queda señalada.

---

# EPIC-18 — SQLITE Y PERSISTENCIA

## FEAT-18.01 — Persistencia estructurada

### US-18.01 — Persistir estado operativo

**Como** sistema
**quiero** almacenar el estado estructurado del proyecto
**para** poder recuperarlo después de reinicios.

**Criterios de aceptación**

* **CA-01:** El estado relevante queda almacenado.
* **CA-02:** Un reinicio no elimina información persistente.
* **CA-03:** El proyecto puede reconstruirse desde la persistencia.
* **CA-04:** Una escritura fallida no deja datos inconsistentes.

### US-18.02 — Mantener transacciones consistentes

**Como** sistema
**quiero** realizar operaciones relacionadas de forma transaccional
**para** evitar estados parciales.

**Criterios de aceptación**

* **CA-01:** Una operación completamente válida se confirma.
* **CA-02:** Un fallo durante la transacción revierte los cambios afectados.
* **CA-03:** No quedan registros parcialmente creados.

### US-18.03 — Gestionar migraciones

**Como** desarrollador
**quiero** versionar el esquema SQLite
**para** actualizar la estructura sin perder datos.

**Criterios de aceptación**

* **CA-01:** Cada migración tiene versión.
* **CA-02:** Las migraciones se ejecutan en orden.
* **CA-03:** Una migración fallida no deja el esquema marcado como completado.
* **CA-04:** La versión actual puede consultarse.

---

# EPIC-19 — CONCURRENCIA Y LOCKING

## FEAT-19.01 — Ejecuciones concurrentes

### US-19.01 — Controlar acceso concurrente al mismo recurso

**Como** sistema
**quiero** controlar el acceso concurrente
**para** evitar corrupción o modificaciones incompatibles.

**Criterios de aceptación**

* **CA-01:** Dos operaciones incompatibles no modifican simultáneamente el recurso protegido.
* **CA-02:** La segunda operación recibe estado de espera o rechazo según política.
* **CA-03:** Los locks se liberan después de completar o fallar.

### US-19.02 — Detectar deadlocks o locks abandonados

**Como** Watchdog
**quiero** detectar locks que no progresan
**para** evitar bloqueos permanentes.

**Criterios de aceptación**

* **CA-01:** Un lock supera el umbral definido y queda identificado.
* **CA-02:** El sistema conserva información sobre su propietario.
* **CA-03:** Se ejecuta la política de recuperación.
* **CA-04:** La recuperación queda registrada.

### US-19.03 — Evitar ejecuciones duplicadas

**Como** orquestador
**quiero** impedir que una misma tarea se ejecute dos veces simultáneamente
**para** evitar cambios duplicados.

**Criterios de aceptación**

* **CA-01:** Una tarea activa no puede iniciarse una segunda vez sin una política explícita.
* **CA-02:** Las solicitudes duplicadas reciben el estado de la ejecución existente.
* **CA-03:** No se crean dos ejecuciones funcionalmente equivalentes.

---

# EPIC-20 — RBAC, IDENTIDAD Y TOKENS

## FEAT-20.01 — Seguridad

### US-20.01 — Gestionar roles

**Como** administrador
**quiero** asignar roles
**para** controlar capacidades.

**Criterios de aceptación**

* **CA-01:** Los roles disponibles están definidos.
* **CA-02:** Un usuario puede recibir un rol autorizado.
* **CA-03:** Los permisos se aplican inmediatamente según política.
* **CA-04:** Los cambios quedan auditados.

### US-20.02 — Autorizar operaciones

**Como** sistema
**quiero** comprobar permisos antes de ejecutar operaciones
**para** impedir accesos no autorizados.

**Criterios de aceptación**

* **CA-01:** Una operación permitida se ejecuta.
* **CA-02:** Una operación no permitida es rechazada.
* **CA-03:** El rechazo no modifica el recurso protegido.
* **CA-04:** El intento queda registrado cuando la política lo requiera.

### US-20.03 — Gestionar tokens

**Como** administrador
**quiero** crear y revocar tokens
**para** permitir integraciones seguras.

**Criterios de aceptación**

* **CA-01:** Cada token tiene identidad y permisos.
* **CA-02:** Un token revocado deja de autorizar operaciones.
* **CA-03:** Los tokens no se muestran completos después de su creación.
* **CA-04:** El uso queda trazado.

---

# EPIC-21 — WEBSOCKETS Y EVENT BUS

## FEAT-21.01 — Comunicación reactiva

### US-21.01 — Emitir eventos de dominio

**Como** sistema
**quiero** publicar eventos cuando cambia el estado
**para** informar a los componentes interesados.

**Criterios de aceptación**

* **CA-01:** Un cambio relevante produce el evento definido.
* **CA-02:** El evento contiene identificador y contexto.
* **CA-03:** Un evento no se publica si la operación ha sido revertida.

### US-21.02 — Suscribirse a eventos

**Como** cliente
**quiero** suscribirme a cambios
**para** actualizar mi estado automáticamente.

**Criterios de aceptación**

* **CA-01:** Una suscripción válida recibe eventos correspondientes.
* **CA-02:** No recibe eventos de proyectos no autorizados.
* **CA-03:** Una desconexión libera la suscripción.

### US-21.03 — Recuperar estado tras reconexión

**Como** cliente
**quiero** recuperar eventos/estado después de una desconexión
**para** volver a sincronizarme.

**Criterios de aceptación**

* **CA-01:** La reconexión se detecta.
* **CA-02:** El cliente obtiene el estado necesario.
* **CA-03:** Los cambios no se duplican.
* **CA-04:** El estado final coincide con el servidor.

---

# EPIC-22 — MODELOS IA LOCALES Y OLLAMA

## FEAT-22.01 — ModelOps

### US-22.01 — Detectar modelos disponibles

**Como** sistema
**quiero** consultar los modelos disponibles
**para** seleccionar un modelo compatible con una tarea.

**Criterios de aceptación**

* **CA-01:** Se consulta el runtime configurado.
* **CA-02:** Los modelos detectados se identifican.
* **CA-03:** Un runtime inaccesible produce un estado de error.
* **CA-04:** El sistema no afirma que un modelo existe si no ha sido detectado.

### US-22.02 — Seleccionar modelo para un agente

**Como** administrador
**quiero** asignar un modelo a un agente
**para** controlar su capacidad de inferencia.

**Criterios de aceptación**

* **CA-01:** Solo modelos disponibles pueden seleccionarse como activos.
* **CA-02:** La configuración queda vinculada al agente.
* **CA-03:** La ejecución registra qué modelo utilizó.

### US-22.03 — Ejecutar inferencia local

**Como** agente IA
**quiero** utilizar un modelo local
**para** ejecutar tareas sin depender necesariamente de un proveedor cloud.

**Criterios de aceptación**

* **CA-01:** La petición llega al modelo configurado.
* **CA-02:** La respuesta queda vinculada a la ejecución.
* **CA-03:** Un fallo del modelo genera estado de error.
* **CA-04:** No se declara éxito si no existe respuesta válida.

---

# EPIC-23 — GOBERNANZA DE INFERENCIA

## FEAT-23.01 — Control de consumo

### US-23.01 — Registrar llamadas a modelos

**Como** administrador
**quiero** registrar cada llamada de inferencia
**para** conocer consumo y comportamiento.

**Criterios de aceptación**

* **CA-01:** Cada llamada identifica agente y modelo.
* **CA-02:** Se registra timestamp.
* **CA-03:** Se registra resultado.
* **CA-04:** Cuando esté disponible, se registra consumo de tokens.

### US-23.02 — Aplicar límites de uso

**Como** administrador
**quiero** establecer límites
**para** evitar consumo descontrolado.

**Criterios de aceptación**

* **CA-01:** Los límites pueden configurarse.
* **CA-02:** Una operación dentro del límite puede ejecutarse.
* **CA-03:** Una operación que excede el límite es rechazada o aplazada según política.
* **CA-04:** El motivo queda registrado.

### US-23.03 — Deshabilitar una cuenta o proveedor

**Como** administrador
**quiero** desactivar una fuente de inferencia
**para** detener su utilización.

**Criterios de aceptación**

* **CA-01:** Una fuente deshabilitada no recibe nuevas llamadas.
* **CA-02:** Las ejecuciones existentes siguen la política definida.
* **CA-03:** El estado queda visible.

---

# EPIC-24 — GESTIÓN MULTIPROYECTO

## FEAT-24.01 — Contextos aislados

### US-24.01 — Trabajar con varios proyectos

**Como** usuario
**quiero** gestionar varios proyectos
**para** utilizar el sistema como plataforma de desarrollo.

**Criterios de aceptación**

* **CA-01:** Pueden existir múltiples proyectos.
* **CA-02:** Cada proyecto tiene backlog independiente.
* **CA-03:** Cada proyecto tiene memoria independiente.
* **CA-04:** Cambiar de proyecto cambia todo el contexto operativo.

### US-24.02 — Compartir recursos autorizados entre proyectos

**Como** administrador
**quiero** definir recursos compartidos
**para** reutilizar infraestructura sin mezclar datos.

**Criterios de aceptación**

* **CA-01:** Un recurso compartido se declara explícitamente.
* **CA-02:** Solo proyectos autorizados pueden usarlo.
* **CA-03:** Los datos privados siguen aislados.

### US-24.03 — Evitar contaminación entre proyectos

**Como** sistema
**quiero** aislar contexto, memoria y eventos
**para** garantizar separación.

**Criterios de aceptación**

* **CA-01:** Un agente del proyecto A no recupera memoria privada del proyecto B.
* **CA-02:** Los eventos de B no actualizan el cliente de A.
* **CA-03:** Las consultas de backlog están limitadas al proyecto activo.

---

# EPIC-25 — DOCUMENTACIÓN VIVA

## FEAT-25.01 — Sincronización documental

### US-25.01 — Actualizar documentación después de cambios arquitectónicos

**Como** sistema
**quiero** actualizar documentación relevante
**para** mantenerla alineada con la implementación.

**Criterios de aceptación**

* **CA-01:** Una decisión arquitectónica nueva genera actualización documental.
* **CA-02:** El documento identifica la fecha/versión correspondiente.
* **CA-03:** La documentación anterior permanece trazable.

### US-25.02 — Registrar decisiones arquitectónicas

**Como** arquitecto
**quiero** registrar decisiones y motivos
**para** poder comprender por qué existe una determinada solución.

**Criterios de aceptación**

* **CA-01:** Cada decisión tiene identificador.
* **CA-02:** Se registra problema, decisión y consecuencia.
* **CA-03:** Puede localizarse desde elementos afectados.

### US-25.03 — Detectar documentación desactualizada

**Como** sistema
**quiero** detectar documentos potencialmente obsoletos
**para** evitar que los agentes trabajen con información antigua.

**Criterios de aceptación**

* **CA-01:** Los documentos pueden marcarse como desactualizados.
* **CA-02:** Un cambio relevante genera una señal de revisión.
* **CA-03:** El estado es visible para los agentes autorizados.

---

# EPIC-26 — TELEMETRÍA Y OBSERVABILIDAD

## FEAT-26.01 — Monitorización

### US-26.01 — Registrar ejecuciones de agentes

**Como** administrador
**quiero** consultar las ejecuciones
**para** conocer qué está haciendo el sistema.

**Criterios de aceptación**

* **CA-01:** Cada ejecución tiene identificador.
* **CA-02:** Se registra agente.
* **CA-03:** Se registra historia/tarea.
* **CA-04:** Se registra inicio y finalización.
* **CA-05:** Se registra resultado.

### US-26.02 — Consultar métricas

**Como** administrador
**quiero** consultar métricas operativas
**para** detectar problemas y evaluar rendimiento.

**Criterios de aceptación**

* **CA-01:** Se muestran métricas disponibles.
* **CA-02:** Las métricas pueden filtrarse por proyecto.
* **CA-03:** Las métricas distinguen ejecuciones exitosas y fallidas.
* **CA-04:** Los datos muestran su periodo temporal.

### US-26.03 — Investigar una ejecución

**Como** usuario técnico
**quiero** abrir el detalle de una ejecución
**para** conocer exactamente qué ocurrió.

**Criterios de aceptación**

* **CA-01:** El detalle muestra agente, historia y tareas.
* **CA-02:** Muestra eventos relevantes.
* **CA-03:** Muestra errores.
* **CA-04:** Permite seguir la trazabilidad hasta el cambio producido.

---

# EPIC-27 — TRAZABILIDAD END-TO-END

## FEAT-27.01 — Cadena completa

### US-27.01 — Seguir un requisito hasta el código

**Como** Product Owner/Arquitecto
**quiero** seguir un requisito hasta su implementación
**para** comprobar que realmente ha sido desarrollado.

**Criterios de aceptación**

* **CA-01:** El requisito enlaza con sus historias.
* **CA-02:** Las historias enlazan con tareas.
* **CA-03:** Las tareas enlazan con cambios.
* **CA-04:** Los cambios enlazan con pruebas.
* **CA-05:** La cadena puede consultarse de extremo a extremo.

### US-27.02 — Seguir un cambio hasta su requisito

**Como** arquitecto
**quiero** identificar por qué se realizó un cambio
**para** conocer su justificación.

**Criterios de aceptación**

* **CA-01:** Un cambio válido tiene referencia a una tarea o decisión.
* **CA-02:** La tarea tiene historia o motivo técnico.
* **CA-03:** La historia tiene requisito o decisión de origen.

### US-27.03 — Detectar cambios sin trazabilidad

**Como** QA
**quiero** detectar cambios huérfanos
**para** evitar modificaciones no justificadas.

**Criterios de aceptación**

* **CA-01:** Los cambios sin origen aparecen en auditoría.
* **CA-02:** Pueden marcarse como legítimos mediante registro explícito.
* **CA-03:** No desaparecen de la auditoría sin dejar historial.

---

# EPIC-28 — QA, TESTING Y CALIDAD

## FEAT-28.01 — Validación

### US-28.01 — Ejecutar pruebas de una historia

**Como** QA
**quiero** ejecutar las pruebas asociadas a una historia
**para** determinar si cumple los criterios de aceptación.

**Criterios de aceptación**

* **CA-01:** Cada CA puede tener resultado PASS/FAIL.
* **CA-02:** Se conserva evidencia.
* **CA-03:** Un FAIL impide marcar la historia como aceptada.
* **CA-04:** Una ejecución posterior puede actualizar el resultado.

### US-28.02 — Ejecutar regresión

**Como** sistema
**quiero** ejecutar pruebas de regresión después de cambios
**para** detectar efectos secundarios.

**Criterios de aceptación**

* **CA-01:** Se ejecuta el conjunto configurado.
* **CA-02:** Los fallos quedan asociados al cambio.
* **CA-03:** El resultado queda registrado.

### US-28.03 — Crear informe de calidad

**Como** Scrum Master
**quiero** obtener un informe de calidad
**para** conocer el estado real del producto.

**Criterios de aceptación**

* **CA-01:** El informe muestra historias aceptadas y rechazadas.
* **CA-02:** Muestra pruebas fallidas.
* **CA-03:** Muestra defectos abiertos.
* **CA-04:** Identifica bloqueos.

---

# EPIC-29 — BUGS, INCIDENTES Y RECUPERACIÓN

## FEAT-29.01 — Gestión de defectos

### US-29.01 — Registrar un bug

**Como** miembro del equipo
**quiero** registrar un defecto
**para** que pueda investigarse y corregirse.

**Criterios de aceptación**

* **CA-01:** El bug recibe identificador.
* **CA-02:** Incluye descripción y contexto.
* **CA-03:** Puede asociarse a una historia.
* **CA-04:** Tiene estado.

### US-29.02 — Asignar un bug

**Como** Scrum Master
**quiero** asignar un bug a un agente
**para** iniciar su resolución.

**Criterios de aceptación**

* **CA-01:** El agente recibe el contexto necesario.
* **CA-02:** La asignación queda registrada.
* **CA-03:** El bug cambia al estado correspondiente.

### US-29.03 — Verificar una corrección

**Como** QA
**quiero** verificar que una corrección resuelve el bug
**para** cerrarlo con evidencia.

**Criterios de aceptación**

* **CA-01:** Se reproduce el escenario original.
* **CA-02:** El escenario corregido pasa.
* **CA-03:** Las pruebas de regresión relevantes pasan.
* **CA-04:** Solo entonces puede cerrarse el bug.

---

# EPIC-30 — APIs Y SERVICIOS

## FEAT-30.01 — API interna

### US-30.01 — Exponer operaciones del proyecto mediante API

**Como** cliente de la plataforma
**quiero** acceder a operaciones mediante API
**para** integrar interfaces y automatizaciones.

**Criterios de aceptación**

* **CA-01:** Cada endpoint tiene contrato definido.
* **CA-02:** Las entradas inválidas generan respuesta de error adecuada.
* **CA-03:** La autorización se aplica.
* **CA-04:** La respuesta tiene formato consistente.

### US-30.02 — Documentar endpoints

**Como** desarrollador
**quiero** disponer de documentación de API
**para** integrar servicios correctamente.

**Criterios de aceptación**

* **CA-01:** Cada endpoint documentado indica método y ruta.
* **CA-02:** Indica entrada y salida.
* **CA-03:** Indica errores relevantes.
* **CA-04:** La documentación se actualiza cuando cambia el contrato.

### US-30.03 — Versionar API

**Como** arquitecto
**quiero** versionar cambios incompatibles
**para** evitar romper clientes existentes.

**Criterios de aceptación**

* **CA-01:** Los cambios incompatibles tienen versión.
* **CA-02:** Las versiones activas pueden identificarse.
* **CA-03:** Las rutas antiguas siguen la política de compatibilidad definida.

---

# EPIC-31 — CONSOLA Y SUPERVISIÓN OPERATIVA

## FEAT-31.01 — Consola de ejecución

### US-31.01 — Consultar consola de actividad

**Como** usuario técnico
**quiero** visualizar actividad del sistema
**para** supervisar las ejecuciones.

**Criterios de aceptación**

* **CA-01:** Se muestran eventos relevantes.
* **CA-02:** Los eventos incluyen timestamp.
* **CA-03:** Pueden filtrarse por proyecto/agente.
* **CA-04:** Un error aparece claramente diferenciado.

### US-31.02 — Filtrar actividad

**Como** usuario técnico
**quiero** filtrar la actividad
**para** localizar rápidamente un incidente.

**Criterios de aceptación**

* **CA-01:** El filtro se aplica al conjunto de eventos.
* **CA-02:** Los resultados coinciden con los filtros.
* **CA-03:** Limpiar filtros restaura la vista completa.

### US-31.03 — Inspeccionar contexto de agente

**Como** administrador
**quiero** inspeccionar el estado de un agente
**para** comprender su ejecución.

**Criterios de aceptación**

* **CA-01:** Se muestra identidad y estado.
* **CA-02:** Se muestran tareas actuales.
* **CA-03:** Se muestran dependencias relevantes.
* **CA-04:** La información sensible queda protegida según RBAC.

---

# EPIC-32 — NOTIFICACIONES Y EVENTOS DE NEGOCIO

## FEAT-32.01 — Alertas

### US-32.01 — Recibir notificación de fallo

**Como** usuario supervisor
**quiero** recibir una alerta cuando una ejecución crítica falle
**para** intervenir cuando sea necesario.

**Criterios de aceptación**

* **CA-01:** El fallo crítico genera la notificación definida.
* **CA-02:** La notificación identifica proyecto y ejecución.
* **CA-03:** Un mismo incidente no genera duplicados innecesarios.

### US-32.02 — Notificar bloqueo

**Como** supervisor
**quiero** ser informado de un bloqueo
**para** poder decidir cómo actuar.

**Criterios de aceptación**

* **CA-01:** El Watchdog genera el evento.
* **CA-02:** La notificación identifica el agente afectado.
* **CA-03:** Incluye la acción de recuperación aplicada si existe.

---

# EPIC-33 — CONFIGURACIÓN DEL SISTEMA

## FEAT-33.01 — Configuración global

### US-33.01 — Configurar parámetros globales

**Como** administrador
**quiero** modificar parámetros globales
**para** adaptar el comportamiento de la plataforma.

**Criterios de aceptación**

* **CA-01:** Solo parámetros autorizados son editables.
* **CA-02:** Los valores inválidos son rechazados.
* **CA-03:** Los cambios quedan persistidos.
* **CA-04:** Los agentes reciben la configuración aplicable.

### US-33.02 — Configurar políticas de agentes

**Como** administrador
**quiero** configurar políticas de ejecución
**para** controlar autonomía y límites.

**Criterios de aceptación**

* **CA-01:** Las políticas tienen valores explícitos.
* **CA-02:** Se aplican a nuevas ejecuciones.
* **CA-03:** Los cambios quedan auditados.

---

# EPIC-34 — GESTIÓN DE RECURSOS DEL AGENTE

## FEAT-34.01 — Herramientas de desarrollo

### US-34.01 — Permitir acceso controlado al filesystem

**Como** agente desarrollador
**quiero** acceder al filesystem autorizado
**para** modificar el proyecto.

**Criterios de aceptación**

* **CA-01:** El agente solo puede acceder a rutas autorizadas.
* **CA-02:** Un acceso fuera del alcance es rechazado.
* **CA-03:** Las operaciones quedan trazadas.

### US-34.02 — Ejecutar comandos de terminal autorizados

**Como** agente desarrollador
**quiero** ejecutar comandos permitidos
**para** construir y probar el proyecto.

**Criterios de aceptación**

* **CA-01:** El comando se ejecuta dentro del contexto autorizado.
* **CA-02:** stdout/stderr quedan registrados.
* **CA-03:** El código de salida queda registrado.
* **CA-04:** Los comandos prohibidos son rechazados.

### US-34.03 — Ejecutar pruebas/build

**Como** agente desarrollador
**quiero** ejecutar build y tests
**para** verificar cambios.

**Criterios de aceptación**

* **CA-01:** Se ejecuta el comando configurado.
* **CA-02:** El resultado queda asociado a la tarea.
* **CA-03:** Un build fallido impide declarar éxito técnico.

---

# EPIC-35 — CONTEXTO DE EJECUCIÓN Y PROMPTS

## FEAT-35.01 — Context engineering

### US-35.01 — Construir contexto para un agente

**Como** orquestador
**quiero** construir el contexto mínimo necesario
**para** que el agente trabaje sin cargar información innecesaria.

**Criterios de aceptación**

* **CA-01:** Se incluye la historia.
* **CA-02:** Se incluyen requisitos relacionados.
* **CA-03:** Se incluyen dependencias necesarias.
* **CA-04:** Se recupera documentación relevante.
* **CA-05:** No se mezcla contexto de otro proyecto.

### US-35.02 — Registrar prompt/contexto utilizado

**Como** sistema
**quiero** conservar referencia del contexto utilizado
**para** reproducir y auditar una ejecución.

**Criterios de aceptación**

* **CA-01:** La ejecución identifica la versión del contexto.
* **CA-02:** Puede determinarse qué fuentes se utilizaron.
* **CA-03:** La información sensible sigue las políticas de seguridad.

---

# EPIC-36 — AGENT MEMORY Y APRENDIZAJE

## FEAT-36.01 — Lessons learned

### US-36.01 — Registrar una lección aprendida

**Como** agente
**quiero** registrar una lección obtenida durante el desarrollo
**para** evitar repetir errores.

**Criterios de aceptación**

* **CA-01:** La lección tiene origen.
* **CA-02:** Describe problema y solución.
* **CA-03:** Puede relacionarse con tecnología o contexto.
* **CA-04:** Puede recuperarse posteriormente.

### US-36.02 — Recuperar lecciones relevantes

**Como** agente
**quiero** consultar lecciones relacionadas
**para** aplicar conocimiento previo.

**Criterios de aceptación**

* **CA-01:** La recuperación utiliza contexto.
* **CA-02:** Las fuentes pueden identificarse.
* **CA-03:** Una lección no aplicable no debe presentarse como obligatoria.

---

# EPIC-37 — GOBERNANZA DE CAMBIOS

## FEAT-37.01 — Change management

### US-37.01 — Registrar una solicitud de cambio

**Como** Product Owner
**quiero** registrar un cambio de alcance
**para** controlar la evolución del producto.

**Criterios de aceptación**

* **CA-01:** El cambio tiene identificador.
* **CA-02:** Indica motivo y alcance.
* **CA-03:** Identifica requisitos afectados.
* **CA-04:** Puede aprobarse o rechazarse.

### US-37.02 — Analizar impacto de un cambio

**Como** arquitecto
**quiero** conocer qué elementos afecta un cambio
**para** evitar modificaciones incompletas.

**Criterios de aceptación**

* **CA-01:** Se identifican historias afectadas.
* **CA-02:** Se identifican componentes afectados.
* **CA-03:** Se identifican dependencias.
* **CA-04:** El resultado queda registrado.

### US-37.03 — Propagar un cambio aprobado

**Como** sistema
**quiero** actualizar los artefactos afectados
**para** mantener coherencia.

**Criterios de aceptación**

* **CA-01:** Solo cambios aprobados se propagan.
* **CA-02:** Los elementos afectados quedan identificados.
* **CA-03:** La trazabilidad conserva el cambio original.

---

# EPIC-38 — GESTIÓN DE CONFIGURACIÓN DE MODELOS

## FEAT-38.01 — Model Registry

### US-38.01 — Registrar modelo

**Como** administrador
**quiero** registrar información de un modelo
**para** conocer sus capacidades.

**Criterios de aceptación**

* **CA-01:** El modelo tiene nombre/identificador.
* **CA-02:** Se registra proveedor/runtime.
* **CA-03:** Se registran capacidades conocidas.
* **CA-04:** Se registra versión cuando esté disponible.

### US-38.02 — Seleccionar modelo según capacidad

**Como** orquestador
**quiero** seleccionar modelos compatibles con una tarea
**para** utilizar la capacidad apropiada.

**Criterios de aceptación**

* **CA-01:** Se comparan capacidades requeridas.
* **CA-02:** Los modelos incompatibles quedan excluidos.
* **CA-03:** La selección utilizada queda registrada.

---

# EPIC-39 — RESILIENCIA Y FALLBACK

## FEAT-39.01 — Recuperación

### US-39.01 — Reintentar una operación recuperable

**Como** sistema
**quiero** reintentar operaciones que fallan de forma transitoria
**para** evitar fallos innecesarios.

**Criterios de aceptación**

* **CA-01:** Solo errores configurados como recuperables generan retry.
* **CA-02:** Se respeta el máximo de reintentos.
* **CA-03:** Cada intento queda registrado.
* **CA-04:** Superado el límite, la operación queda fallida.

### US-39.02 — Utilizar fallback de modelo

**Como** sistema
**quiero** utilizar un modelo alternativo autorizado
**para** mantener una operación cuando el modelo principal no está disponible.

**Criterios de aceptación**

* **CA-01:** El fallback está previamente configurado.
* **CA-02:** Se utiliza solo ante condiciones compatibles.
* **CA-03:** La ejecución registra modelo principal y fallback.
* **CA-04:** No se utiliza un modelo no autorizado.

### US-39.03 — Recuperar una tarea después de reinicio

**Como** sistema
**quiero** recuperar tareas persistidas
**para** continuar después de una interrupción.

**Criterios de aceptación**

* **CA-01:** Las tareas recuperables se identifican.
* **CA-02:** Una tarea ya completada no vuelve a ejecutarse.
* **CA-03:** Las tareas pendientes pueden reanudarse según política.
* **CA-04:** La recuperación queda registrada.

---

# EPIC-40 — IMPORTACIÓN Y EXPORTACIÓN DEL PROYECTO

## FEAT-40.01 — Portabilidad

### US-40.01 — Exportar proyecto

**Como** administrador
**quiero** exportar el estado del proyecto
**para** conservarlo o trasladarlo.

**Criterios de aceptación**

* **CA-01:** Se incluyen los elementos definidos por el formato.
* **CA-02:** Se conserva la estructura.
* **CA-03:** El paquete exportado puede validarse.
* **CA-04:** Los secretos no se exportan salvo política explícita.

### US-40.02 — Importar proyecto

**Como** administrador
**quiero** importar un proyecto
**para** recuperar o trasladar un entorno.

**Criterios de aceptación**

* **CA-01:** El paquete se valida antes de modificar el sistema.
* **CA-02:** Un paquete inválido no deja estado parcial.
* **CA-03:** Los identificadores se conservan o remapean explícitamente.
* **CA-04:** La importación queda registrada.

---

# EPIC-41 — MULTIAGENTE Y COLABORACIÓN

## FEAT-41.01 — Coordinación

### US-41.01 — Compartir resultado entre agentes

**Como** agente
**quiero** publicar un resultado estructurado
**para** que otro agente pueda continuar el trabajo.

**Criterios de aceptación**

* **CA-01:** El resultado identifica productor.
* **CA-02:** Identifica tarea/origen.
* **CA-03:** El consumidor recibe la versión correcta.
* **CA-04:** Un resultado inválido no se acepta como completado.

### US-41.02 — Coordinar tareas dependientes

**Como** orquestador
**quiero** activar una tarea cuando sus dependencias estén satisfechas
**para** mantener un flujo correcto.

**Criterios de aceptación**

* **CA-01:** Una tarea bloqueada no comienza.
* **CA-02:** Al completar todas sus dependencias pasa a ejecutable.
* **CA-03:** Una dependencia fallida impide la ejecución automática cuando la política así lo determine.

### US-41.03 — Resolver conflictos entre agentes

**Como** orquestador
**quiero** detectar modificaciones incompatibles
**para** impedir que dos agentes corrompan el mismo contexto.

**Criterios de aceptación**

* **CA-01:** El conflicto se detecta.
* **CA-02:** Los agentes implicados quedan identificados.
* **CA-03:** La política de resolución se aplica.
* **CA-04:** El conflicto queda registrado.

---

# EPIC-42 — GESTIÓN DEL CONTEXTO DE SPRINT

## FEAT-42.01 — Sprint Memory

### US-42.01 — Registrar contexto del sprint

**Como** Scrum Master
**quiero** mantener memoria del sprint
**para** que los agentes conozcan sus objetivos.

**Criterios de aceptación**

* **CA-01:** Se almacena objetivo.
* **CA-02:** Se almacenan historias.
* **CA-03:** Se almacenan decisiones relevantes.
* **CA-04:** El contexto se puede recuperar.

### US-42.02 — Registrar impedimentos

**Como** Scrum Master
**quiero** registrar impedimentos
**para** controlar bloqueos.

**Criterios de aceptación**

* **CA-01:** Cada impedimento tiene identificador.
* **CA-02:** Se relaciona con las historias afectadas.
* **CA-03:** Tiene estado.
* **CA-04:** Su resolución queda registrada.

---

# EPIC-43 — REPORTING DEL PRODUCTO

## FEAT-43.01 — Informes

### US-43.01 — Consultar progreso del producto

**Como** Product Owner
**quiero** consultar el progreso
**para** conocer cuánto producto está implementado.

**Criterios de aceptación**

* **CA-01:** Se muestran historias por estado.
* **CA-02:** Se muestran épicas y features.
* **CA-03:** Se distingue trabajo pendiente y completado.
* **CA-04:** Los datos corresponden al proyecto seleccionado.

### US-43.02 — Consultar progreso por requisito

**Como** Product Owner
**quiero** consultar cobertura de requisitos
**para** detectar alcance no implementado.

**Criterios de aceptación**

* **CA-01:** Cada requisito indica cobertura.
* **CA-02:** Los requisitos sin historias aparecen identificados.
* **CA-03:** La cobertura considera historias y aceptación.

---

# EPIC-44 — SEGURIDAD OPERATIVA

## FEAT-44.01 — Auditoría

### US-44.01 — Registrar acciones administrativas

**Como** sistema
**quiero** registrar acciones sensibles
**para** disponer de auditoría.

**Criterios de aceptación**

* **CA-01:** Las operaciones sensibles generan registros.
* **CA-02:** Se identifica usuario/agente.
* **CA-03:** Se registra fecha.
* **CA-04:** El registro no puede modificarse mediante una operación normal.

### US-44.02 — Proteger secretos

**Como** sistema
**quiero** proteger tokens y credenciales
**para** evitar su exposición.

**Criterios de aceptación**

* **CA-01:** Los secretos no aparecen en logs normales.
* **CA-02:** No se muestran completos en UI después de almacenarse.
* **CA-03:** Los agentes solo reciben secretos autorizados.

---

# EPIC-45 — EXPERIENCIA DE SUPERVISIÓN

## FEAT-45.01 — Dashboard

### US-45.01 — Visualizar estado global

**Como** usuario
**quiero** disponer de un dashboard
**para** conocer el estado del sistema de un vistazo.

**Criterios de aceptación**

* **CA-01:** Se muestran proyecto activo y estado del ciclo.
* **CA-02:** Se muestran agentes.
* **CA-03:** Se muestran tareas.
* **CA-04:** Se muestran bloqueos relevantes.
* **CA-05:** Los datos se actualizan.

### US-45.02 — Acceder a un elemento desde el dashboard

**Como** usuario
**quiero** abrir una ejecución, historia o agente desde el dashboard
**para** investigar su estado.

**Criterios de aceptación**

* **CA-01:** Cada elemento navegable abre su detalle.
* **CA-02:** Se conserva el contexto del proyecto.
* **CA-03:** Un elemento inexistente muestra error controlado.

---

# EPIC-46 — AUTOMATIZACIÓN DEL CICLO DE DESARROLLO

## FEAT-46.01 — Pipeline autónomo

### US-46.01 — Ejecutar ciclo completo de una historia

**Como** sistema autónomo
**quiero** ejecutar análisis → implementación → pruebas → revisión
**para** completar historias con mínima intervención humana.

**Criterios de aceptación**

* **CA-01:** El ciclo comienza con una historia READY.
* **CA-02:** Se generan/ejecutan tareas.
* **CA-03:** Se ejecutan verificaciones.
* **CA-04:** Una historia no pasa a DONE si falla aceptación.
* **CA-05:** Todos los pasos quedan trazados.

### US-46.02 — Solicitar revisión humana cuando sea necesaria

**Como** sistema autónomo
**quiero** detenerme ante decisiones que requieran intervención
**para** no tomar decisiones no autorizadas.

**Criterios de aceptación**

* **CA-01:** El sistema identifica condiciones que requieren revisión.
* **CA-02:** La historia queda bloqueada.
* **CA-03:** Se explica qué decisión falta.
* **CA-04:** El ciclo puede continuar después de resolverla.

---

# EPIC-47 — PREPARACIÓN PARA JEV / EVOLUCIÓN DEL ENTORNO DE EJECUCIÓN

## FEAT-47.01 — Entorno virtual futuro

### US-47.01 — Modelar recursos de ejecución abstractos

**Como** arquitectura
**quiero** abstraer recursos de ejecución
**para** poder evolucionar hacia un entorno JEV sin rediseñar todo el sistema.

**Criterios de aceptación**

* **CA-01:** Las tareas no dependen innecesariamente de una implementación concreta.
* **CA-02:** Los recursos de ejecución tienen interfaz abstracta.
* **CA-03:** La implementación actual continúa funcionando.
* **CA-04:** La futura implementación puede conectarse mediante el mismo contrato.

### US-47.02 — Gestionar entornos de ejecución

**Como** sistema
**quiero** identificar el entorno donde se ejecuta una tarea
**para** mantener trazabilidad de ejecución.

**Criterios de aceptación**

* **CA-01:** Cada ejecución identifica su entorno.
* **CA-02:** El entorno tiene estado.
* **CA-03:** Una ejecución no se asigna a un entorno no disponible.

---

# EPIC-48 — CONTROL Y GOBERNANZA FINAL DEL SISTEMA

## FEAT-48.01 — Estado global

### US-48.01 — Mantener estado global coherente

**Como** plataforma
**quiero** disponer de un estado global consistente
**para** que todos los subsistemas conozcan la situación real.

**Criterios de aceptación**

* **CA-01:** El estado refleja ejecuciones activas.
* **CA-02:** Refleja proyecto y sprint activos.
* **CA-03:** Refleja bloqueos.
* **CA-04:** El estado persiste cuando corresponda.
* **CA-05:** Las transiciones imposibles son rechazadas.

### US-48.02 — Ejecutar auditoría integral

**Como** administrador/Product Owner
**quiero** ejecutar una auditoría completa
**para** detectar inconsistencias antes de continuar el desarrollo.

**Criterios de aceptación**

* **CA-01:** La auditoría comprueba requisitos sin cobertura.
* **CA-02:** Comprueba historias sin criterios.
* **CA-03:** Comprueba trazabilidad rota.
* **CA-04:** Comprueba documentación desactualizada.
* **CA-05:** Comprueba cambios sin origen.
* **CA-06:** Genera un informe de hallazgos.

### US-48.03 — Obtener estado real del producto

**Como** Product Owner
**quiero** consultar el estado real del producto
**para** conocer qué está implementado, qué está probado y qué está pendiente.

**Criterios de aceptación**

* **CA-01:** El sistema diferencia planificado, en desarrollo, implementado, probado y aceptado.
* **CA-02:** Una historia no aparece como aceptada sin criterios PASS.
* **CA-03:** El estado puede rastrearse hasta requisitos.
* **CA-04:** El informe identifica bloqueos y riesgos abiertos.

---

# MATRIZ GLOBAL DE COBERTURA

La estructura resultante cubre las áreas principales del sistema:

| Área                     | Épicas  |
| ------------------------ | ------- |
| Proyecto                 | EPIC-01 |
| Memoria `control/`       | EPIC-02 |
| Product Owner            | EPIC-03 |
| Backlog                  | EPIC-04 |
| Scrum                    | EPIC-05 |
| Kanban                   | EPIC-06 |
| Orquestación             | EPIC-07 |
| Agentes/instancias/hilos | EPIC-08 |
| Roles IA                 | EPIC-09 |
| Desarrollo               | EPIC-10 |
| Código                   | EPIC-11 |
| Snapshots/Rollback       | EPIC-12 |
| Watchdog                 | EPIC-13 |
| MCP                      | EPIC-14 |
| Skills                   | EPIC-15 |
| RAG                      | EPIC-16 |
| Product Graph            | EPIC-17 |
| SQLite                   | EPIC-18 |
| Concurrencia             | EPIC-19 |
| RBAC/Tokens              | EPIC-20 |
| WebSockets/Event Bus     | EPIC-21 |
| Ollama/Modelos           | EPIC-22 |
| Gobernanza IA            | EPIC-23 |
| Multi-proyecto           | EPIC-24 |
| Documentación viva       | EPIC-25 |
| Telemetría               | EPIC-26 |
| Trazabilidad E2E         | EPIC-27 |
| QA                       | EPIC-28 |
| Bugs                     | EPIC-29 |
| APIs                     | EPIC-30 |
| Consola                  | EPIC-31 |
| Notificaciones           | EPIC-32 |
| Configuración            | EPIC-33 |
| Recursos de agentes      | EPIC-34 |
| Context Engineering      | EPIC-35 |
| Agent Memory             | EPIC-36 |
| Change Management        | EPIC-37 |
| Model Registry           | EPIC-38 |
| Resiliencia              | EPIC-39 |
| Import/Export            | EPIC-40 |
| Multiagente              | EPIC-41 |
| Sprint Memory            | EPIC-42 |
| Reporting                | EPIC-43 |
| Seguridad                | EPIC-44 |
| Dashboard                | EPIC-45 |
| Automatización E2E       | EPIC-46 |
| JEV futuro               | EPIC-47 |
| Gobernanza final         | EPIC-48 |

# REGLA DE ACEPTACIÓN DEL BACKLOG

Este backlog no debe considerarse terminado simplemente porque existan títulos de historias.

Una historia solo está **READY** cuando:

```text
REQUISITO
   ↓
ÉPICA
   ↓
FEATURE
   ↓
USER STORY
   ↓
ACTOR
   ↓
VALOR
   ↓
PRECONDICIONES
   ↓
FLUJO
   ↓
ALTERNATIVAS
   ↓
ERRORES
   ↓
REGLAS
   ↓
VALIDACIONES
   ↓
CASOS LÍMITE
   ↓
CRITERIOS DE ACEPTACIÓN
   ↓
TAREAS
   ↓
PRUEBAS
```

Y solo puede considerarse **DONE** cuando:

```text
IMPLEMENTADO
+
TESTS EJECUTADOS
+
TODOS LOS CA PASS
+
SIN BLOQUEOS
+
TRAZABILIDAD ACTUALIZADA
+
DOCUMENTACIÓN ACTUALIZADA
```

# PRINCIPIO FINAL

El objetivo de este backlog no es decirle a un desarrollador:

> "Haz un módulo de agentes."

El objetivo es que el equipo pueda saber exactamente:

> **qué debe existir, quién lo utiliza, por qué existe, cómo funciona, qué datos intervienen, qué ocurre en condiciones normales y anormales, cómo se comprueba, qué tareas técnicas requiere, de qué depende y cómo se demuestra que está terminado.**

Cada User Story es por tanto una **unidad funcional verificable**, no una simple línea de backlog.
