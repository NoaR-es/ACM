# Agile Context Manager (ACM) — Definición de Producto v1.1

> **Fuente:** v1.0 aportada por el operador humano (NoaR-es) el 2026-09-30 + enmiendas del operador.
> **Autoridad:** documento de producto de referencia (nivel 6 — planificación, §52 CLAUDE.md).
> **Estado:** ACTIVE. Supersede a `99_ARCHIVO/superseded/product_definition_v1.md`.
> Los cambios de alcance se registran como nueva versión y la anterior pasa a `99_ARCHIVO/superseded/`.
> Las enmiendas se marcan en el texto con **[v1.1]**.
>
> **Historial de versiones**
> | Versión | Fecha | Cambio | Origen |
> |---------|-------|--------|--------|
> | 1.0 | 2026-09-30 | Definición inicial | Operador |
> | 1.1 | 2026-09-30 | ACM implementa y gestiona su propio servidor MCP y distribuye por él sus skills (FEAT-15.04, objetivo de EPIC-15 y EPIC-22, MVP §12 punto 27) | Operador; redacción del agente (ADR-008) |
> Los inventarios `epics.md`, `features.md`, `user_stories.md`, `backlog.md` y `technical_stories.md`
> se **derivan** de este documento con `control/tools/derive_backlog.py`.

---

## Sistema Autónomo de Gobernanza, Memoria, Ejecución y Trazabilidad Agile para Agentes IA

**Versión conceptual:** 1.1
**Fecha de definición:** 30 de septiembre de 2026
**Naturaleza:** Plataforma de desarrollo software asistido y autónomo por agentes IA
**Núcleo de persistencia:** SQLite
**Memoria semántica:** Base vectorial + RAG
**Inferencia local:** Ollama
**Inferencia decisional futura:** JEV
**Interfaz:** Aplicación web React
**Comunicación reactiva:** WebSockets
**Interfaz agente:** Model Context Protocol (MCP) — **[v1.1]** servidor MCP propio, implementado y gestionado por ACM, que entrega a cada agente conectado las skills necesarias para usar ACM
**Gobernanza:** Multi-agente, trazabilidad E2E, Watchdog y gates de calidad

---

# 1. DESCRIPCIÓN COMPLETA DEL PROYECTO

## 1.1. Visión

**Agile Context Manager (ACM)** es una plataforma destinada a convertirse en una infraestructura de control y memoria para el desarrollo de software realizado por humanos y, especialmente, por agentes de inteligencia artificial.

ACM no debe entenderse simplemente como:

* un gestor de proyectos;
* un tablero Kanban;
* una base de datos SQLite;
* un servidor MCP;
* una herramienta de documentación;
* un sistema RAG;
* un conjunto de agentes IA.

Es la combinación de todos esos elementos dentro de un **motor de estado, conocimiento, gobernanza, ejecución y trazabilidad**.

Su finalidad es mantener una relación verificable entre:

```text
Visión del producto
        ↓
Módulos
        ↓
Funcionalidades
        ↓
Épicas
        ↓
Historias de Usuario
        ↓
Requisitos / Criterios de Aceptación
        ↓
Sprints
        ↓
Tareas
        ↓
Planes de Implementación
        ↓
Archivos / Código
        ↓
Commits
        ↓
Walkthroughs
        ↓
Logs
        ↓
Bugs
        ↓
Causa raíz
        ↓
ADR
        ↓
Documentación
```

El sistema debe poder recorrer esta cadena tanto hacia delante como hacia atrás.

---

# 2. PROBLEMA QUE RESUELVE

Los agentes IA pueden escribir código rápidamente, pero en proyectos complejos aparecen problemas:

* pérdida de contexto;
* decisiones arquitectónicas no documentadas;
* código que deja de corresponderse con los requisitos;
* historias demasiado grandes o ambiguas;
* tareas huérfanas;
* modificaciones sin trazabilidad;
* agentes concurrentes pisándose;
* documentación desactualizada;
* bugs que reaparecen;
* deuda técnica invisible;
* decisiones contradictorias;
* falta de evidencia de que una funcionalidad realmente funciona;
* dificultad para recuperar el estado anterior;
* dificultad para saber qué está haciendo un agente;
* dificultad para saber por qué un agente tomó una decisión;
* contaminación del contexto de los modelos;
* RAG que devuelve información irrelevante;
* agentes que utilizan herramientas que no deberían utilizar;
* ausencia de una gobernanza central para múltiples agentes.

ACM pretende resolver estos problemas mediante una arquitectura de **estado persistente + conocimiento + agentes + herramientas + gobernanza + observabilidad**.

---

# 3. OBJETIVOS DEL PRODUCTO

## 3.1. Objetivos funcionales

ACM debe permitir:

1. Gestionar múltiples proyectos.
2. Mantener un contexto independiente para cada proyecto.
3. Registrar la visión y metadatos del proyecto.
4. Crear árboles funcionales.
5. Gestionar módulos y submódulos.
6. Registrar funcionalidades.
7. Registrar stack tecnológico y decisiones.
8. Crear y gestionar épicas.
9. Crear y gestionar historias de usuario.
10. Definir criterios de aceptación.
11. Gestionar sprints.
12. Crear tareas técnicas.
13. Gestionar planes de implementación.
14. Ejecutar validaciones.
15. Registrar walkthroughs.
16. Gestionar bugs.
17. Gestionar deuda técnica.
18. Registrar ADRs.
19. Mantener documentación.
20. Proporcionar un servidor MCP.
21. Permitir múltiples agentes simultáneos.
22. Proporcionar memoria RAG.
23. Integrar modelos locales.
24. Integrar modelos de decisión.
25. Aplicar permisos y gobernanza.
26. Mostrar actividad de agentes en tiempo real.
27. Mostrar el Kanban en tiempo real.
28. Auditar las acciones de los agentes.
29. Crear snapshots.
30. Restaurar estados anteriores.
31. Detectar conflictos.
32. Detectar deriva arquitectónica.
33. Detectar deuda técnica.
34. Detectar historias defectuosas.
35. Generar documentación automáticamente.
36. Ejecutar simulaciones antes de modificar el proyecto real.
37. Permitir intervención humana.
38. Proporcionar CLI.
39. Permitir extensiones y skills.
40. Mantener trazabilidad E2E.

---

# 4. ACTORES DEL SISTEMA

## ACT-01 — Operador humano

Persona responsable del proyecto.

Puede:

* crear proyectos;
* configurar ACM;
* visualizar proyectos;
* intervenir agentes;
* aprobar operaciones sensibles;
* consultar métricas;
* revisar decisiones;
* ejecutar rollback;
* gestionar usuarios y tokens.

## ACT-02 — Product Owner IA

Responsable de:

* discovery;
* funcionalidades;
* valor de negocio;
* backlog;
* refinamiento.

## ACT-03 — Arquitecto IA

Responsable de:

* arquitectura;
* módulos;
* stack;
* ADRs;
* dependencias.

## ACT-04 — Agente Constructor

Responsable de:

* ejecutar tareas;
* modificar código;
* ejecutar planes;
* aportar evidencia.

## ACT-05 — Agente Inspector / Watchdog

Responsable de:

* validar;
* auditar;
* detectar inconsistencias;
* bloquear operaciones incorrectas.

## ACT-06 — Agente QA

Responsable de:

* pruebas;
* walkthroughs;
* criterios de aceptación;
* regresión.

## ACT-07 — Agente de documentación

Responsable de:

* arquitectura;
* C4;
* ADR;
* manuales;
* documentación viva.

## ACT-08 — Agente RAG

Responsable de:

* indexación;
* recuperación;
* ranking;
* contexto.

## ACT-09 — Agente decisional JEV

Responsable de:

* evaluación de escenarios;
* reglas;
* restricciones;
* simulaciones decisionales.

## ACT-10 — Agente externo MCP

Cualquier agente conectado al servidor MCP.

---

# 5. DOMINIOS DEL PRODUCTO

El producto queda dividido conceptualmente en:

1. Gestión de proyectos.
2. Product Discovery.
3. Product Graph.
4. Agile Backlog.
5. Sprints.
6. Ejecución técnica.
7. Planificación.
8. Quality & Watchdog.
9. Bugs y deuda técnica.
10. Arquitectura y ADR.
11. Documentación viva.
12. MCP.
13. Agentes.
14. Skills.
15. Memoria RAG.
16. Modelos locales.
17. Modelos JEV.
18. Concurrencia multiagente.
19. Seguridad.
20. Telemetría.
21. Observabilidad.
22. Sandbox.
23. Snapshots.
24. Rollback.
25. Analítica.
26. Integraciones.
27. CLI.
28. Frontend operativo.

---

# 6. ARQUITECTURA DE DATOS FUNCIONAL

## 6.1. Product Graph

### `modules`

Árbol jerárquico del producto.

### `features`

Funcionalidades y reglas de negocio.

### `project_stack`

Tecnologías y decisiones técnicas.

### `project_metadata`

Configuración y visión global.

---

## 6.2. Agile Backlog

### `epics`

Objetivos macro.

### `user_stories`

Valor funcional.

### `requirements`

Criterios verificables.

---

## 6.3. Ejecución

### `sprints`

Contenedores temporales.

### `tasks`

Trabajo técnico.

### `implementation_plans`

Planes de ejecución.

### `plan_steps`

Hitos.

### `plan_validators`

Validadores de los hitos.

---

## 6.4. Calidad y conocimiento

### `bugs`

Errores y causa raíz.

### `tech_debt`

Deuda técnica.

### `adrs`

Decisiones arquitectónicas.

### `walkthrough_logs`

Evidencias de ejecución.

---

# 7. ÉPICAS DEL PRODUCTO

---

# EPIC-01 — Gestión del Proyecto y Contexto ACM

**Objetivo:** proporcionar el contexto raíz sobre el que se ejecuta todo el sistema.

**Valor:** garantizar que cada agente y cada operación sepan sobre qué proyecto están trabajando.

### FEAT-01.01 — Inicialización de proyectos

#### US-01.01

**Como operador quiero crear un proyecto ACM para disponer de un espacio independiente de gestión.**

Criterios:

* El sistema permite introducir nombre e identificador.
* Se crea el contexto físico del proyecto.
* Se crea su base SQLite.
* El proyecto queda disponible para consulta.

#### US-01.02

**Como operador quiero cambiar el proyecto activo para trabajar sobre distintos proyectos sin mezclar sus contextos.**

#### US-01.03

**Como agente quiero conocer el proyecto activo antes de ejecutar una herramienta para evitar modificar otro proyecto.**

### FEAT-01.02 — Configuración

#### US-01.04

**Como operador quiero consultar la configuración actual del proyecto para conocer sus reglas operativas.**

#### US-01.05

**Como operador quiero modificar parámetros configurables para adaptar ACM al proyecto.**

#### US-01.06

**Como operador quiero establecer umbrales de calidad, deuda, cuotas y seguridad para controlar el comportamiento autónomo.**

### FEAT-01.03 — Health Check

#### US-01.07

**Como operador quiero ejecutar una comprobación de salud para detectar problemas en la infraestructura ACM.**

#### US-01.08

**Como Watchdog quiero detectar inconsistencias de SQLite, relaciones y triggers para impedir operar sobre un estado corrupto.**

### FEAT-01.04 — Metadatos

#### US-01.09

**Como operador quiero almacenar la visión general del proyecto para que los agentes dispongan de contexto persistente.**

#### US-01.10

**Como agente quiero recuperar los metadatos relevantes antes de ejecutar una operación para trabajar con contexto actualizado.**

---

# EPIC-02 — Product Discovery y Árbol Funcional

**Objetivo:** impedir que los agentes salten directamente al desarrollo sin comprender primero el producto.

### FEAT-02.01 — Módulos

#### US-02.01

**Como Product Owner quiero crear módulos funcionales para estructurar el producto.**

#### US-02.02

**Como Product Owner quiero crear submódulos jerárquicos para representar dominios complejos.**

#### US-02.03

**Como agente quiero consultar el árbol funcional completo para localizar dónde pertenece una funcionalidad.**

#### US-02.04

**Como operador quiero visualizar el árbol funcional para comprender la estructura del producto.**

### FEAT-02.02 — Funcionalidades

#### US-02.05

**Como Product Owner quiero registrar una funcionalidad con descripción, valor, reglas y restricciones.**

#### US-02.06

**Como Product Owner quiero actualizar el estado de una funcionalidad para distinguir ideas de funcionalidades aprobadas.**

#### US-02.07

**Como agente quiero consultar las funcionalidades de un módulo antes de proponer épicas.**

### FEAT-02.03 — Discovery Socrático

#### US-02.08

**Como Product Owner quiero que el agente formule preguntas sobre la visión antes de crear el backlog.**

#### US-02.09

**Como operador quiero revisar los supuestos detectados durante Discovery.**

#### US-02.10

**Como agente quiero identificar dependencias ocultas antes de convertir funcionalidades en historias.**

#### US-02.11

**Como agente quiero identificar restricciones técnicas y de negocio antes de diseñar una solución.**

#### US-02.12

**Como operador quiero detectar conflictos entre requisitos para resolverlos antes de crear tareas.**

### FEAT-02.04 — Matriz de riesgo

#### US-02.13

**Como Product Owner quiero registrar riesgos funcionales y técnicos detectados durante Discovery.**

#### US-02.14

**Como arquitecto quiero identificar cuellos de botella potenciales antes de planificar un sprint.**

---

# EPIC-03 — Gestión del Stack y Arquitectura

### FEAT-03.01 — Stack tecnológico

#### US-03.01

**Como arquitecto quiero registrar las tecnologías utilizadas por un proyecto para que los agentes conozcan el stack oficial.**

#### US-03.02

**Como arquitecto quiero registrar el motivo de cada decisión tecnológica para conservar contexto arquitectónico.**

#### US-03.03

**Como agente quiero consultar el stack antes de generar código para evitar utilizar tecnologías no autorizadas.**

### FEAT-03.02 — ADR

#### US-03.04

**Como arquitecto quiero crear un ADR para documentar una decisión arquitectónica.**

#### US-03.05

**Como arquitecto quiero relacionar un ADR con módulos, funcionalidades y requisitos afectados.**

#### US-03.06

**Como Watchdog quiero verificar que una propuesta técnica respeta los ADR vigentes.**

#### US-03.07

**Como arquitecto quiero detectar cuándo una nueva decisión contradice una decisión anterior.**

### FEAT-03.03 — Gobierno arquitectónico

#### US-03.08

**Como operador quiero someter decisiones críticas a revisión de varios agentes especializados.**

#### US-03.09

**Como arquitecto quiero recibir una alerta cuando una propuesta genere deuda técnica no declarada.**

#### US-03.10

**Como Watchdog quiero bloquear una operación cuando incumpla restricciones arquitectónicas obligatorias.**

---

# EPIC-04 — Motor de Backlog Agile

### FEAT-04.01 — Épicas

#### US-04.01

**Como Product Owner quiero crear una épica asociada a funcionalidades concretas.**

#### US-04.02

**Como Product Owner quiero definir visión y valor de negocio de una épica.**

#### US-04.03

**Como usuario quiero consultar el progreso de una épica a partir de sus historias.**

### FEAT-04.02 — Historias

#### US-04.04

**Como Product Owner quiero crear historias INVEST para expresar valor funcional atómico.**

#### US-04.05

**Como Product Owner quiero relacionar cada historia con su origen funcional.**

#### US-04.06

**Como agente quiero dividir historias demasiado grandes antes de convertirlas en tareas.**

#### US-04.07

**Como Watchdog quiero detectar historias que no sean suficientemente pequeñas, claras o testeables.**

### FEAT-04.03 — Requisitos

#### US-04.08

**Como Product Owner quiero añadir criterios de aceptación binarios a una historia.**

#### US-04.09

**Como QA quiero comprobar cada criterio de aceptación de forma independiente.**

#### US-04.10

**Como Watchdog quiero impedir que una historia avance sin criterios de aceptación suficientes.**

---

# EPIC-05 — Refinamiento Multi-Agente y Gates de Calidad

### FEAT-05.01 — Auditor INVEST

#### US-05.01

**Como Watchdog quiero evaluar automáticamente una historia según INVEST.**

#### US-05.02

**Como Watchdog quiero identificar criterios vagos o no verificables.**

#### US-05.03

**Como Product Owner quiero recibir las deficiencias detectadas antes de aprobar una historia.**

### FEAT-05.02 — Tribunal multiagente

#### US-05.04

**Como sistema quiero solicitar validación al Product Owner IA, Arquitecto IA y QA IA antes de ejecutar una historia crítica.**

#### US-05.05

**Como operador quiero consultar las decisiones emitidas por cada agente.**

#### US-05.06

**Como sistema quiero impedir la ejecución cuando una regla de gobernanza obligatoria no haya sido aprobada.**

### FEAT-05.03 — Consensus Gate

#### US-05.07

**Como sistema quiero registrar formalmente las aprobaciones necesarias para liberar una historia.**

#### US-05.08

**Como sistema quiero mantener la trazabilidad de quién o qué agente autorizó una transición.**

---

# EPIC-06 — Sprints y Planificación Agile

### FEAT-06.01 — Sprints

#### US-06.01

**Como Scrum Master quiero crear un sprint con objetivo, fechas y capacidad.**

#### US-06.02

**Como Scrum Master quiero asignar historias a un sprint.**

#### US-06.03

**Como Scrum Master quiero cerrar un sprint conservando sus métricas históricas.**

### FEAT-06.02 — Capacidad

#### US-06.04

**Como Scrum Master quiero registrar la capacidad disponible del sprint.**

#### US-06.05

**Como Scrum Master quiero conocer la carga asignada al sprint.**

#### US-06.06

**Como sistema quiero detectar sobrecarga antes de iniciar un sprint.**

### FEAT-06.03 — Predicción

#### US-06.07

**Como Scrum Master quiero simular un sprint antes de iniciarlo para detectar dependencias ocultas.**

#### US-06.08

**Como Scrum Master quiero identificar posibles cuellos de botella antes de comprometer trabajo.**

#### US-06.09

**Como operador quiero comparar escenarios alternativos de planificación.**

---

# EPIC-07 — Ejecución Técnica y Tasks

### FEAT-07.01 — Tasks

#### US-07.01

**Como agente constructor quiero crear tareas técnicas asociadas a una historia aprobada.**

#### US-07.02

**Como agente quiero consultar las tareas disponibles para ejecutar la siguiente unidad de trabajo.**

#### US-07.03

**Como agente quiero reclamar una tarea para evitar que otro agente la ejecute simultáneamente.**

#### US-07.04

**Como agente quiero completar una tarea aportando evidencia de los cambios realizados.**

### FEAT-07.02 — Descomposición automática

#### US-07.05

**Como agente Scrum quiero descomponer una historia en tareas técnicas.**

#### US-07.06

**Como agente quiero estimar el esfuerzo de las tareas.**

#### US-07.07

**Como Watchdog quiero detectar tareas huérfanas sin historia de origen.**

### FEAT-07.03 — Vinculación con código

#### US-07.08

**Como agente quiero vincular archivos modificados con la tarea ejecutada.**

#### US-07.09

**Como operador quiero conocer qué código fue modificado para completar una historia.**

#### US-07.10

**Como Watchdog quiero detectar cambios de código sin una tarea ACM activa.**

---

# EPIC-08 — Implementation Plans y Ejecución por Hitos

### FEAT-08.01 — Planes

#### US-08.01

**Como agente quiero generar un plan de implementación antes de ejecutar cambios complejos.**

#### US-08.02

**Como sistema quiero ingerir un plan en ACM para convertirlo en hitos verificables.**

#### US-08.03

**Como operador quiero consultar el estado de cada hito del plan.**

### FEAT-08.02 — Validadores

#### US-08.04

**Como sistema quiero asociar historias y tareas a los hitos que deben validar.**

#### US-08.05

**Como sistema quiero completar automáticamente un hito cuando todos sus validadores estén satisfechos.**

#### US-08.06

**Como sistema quiero impedir completar un hito cuando falte evidencia.**

### FEAT-08.03 — Dependencias

#### US-08.07

**Como sistema quiero representar dependencias entre planes.**

#### US-08.08

**Como sistema quiero impedir que un plan dependiente comience antes de cumplir sus prerrequisitos.**

---

# EPIC-09 — Walkthroughs, Tests y Done-Done

### FEAT-09.01 — Walkthroughs

#### US-09.01

**Como desarrollador quiero marcar pasos ejecutables de un walkthrough para que ACM pueda validarlos automáticamente.**

#### US-09.02

**Como sistema quiero ejecutar los comandos marcados como automáticos.**

#### US-09.03

**Como sistema quiero registrar el resultado de cada ejecución.**

### FEAT-09.02 — Evidencia

#### US-09.04

**Como QA quiero consultar la evidencia de ejecución asociada a una historia.**

#### US-09.05

**Como Watchdog quiero impedir DONE cuando una validación obligatoria haya fallado.**

### FEAT-09.03 — Done-Done

#### US-09.06

**Como sistema quiero diferenciar entre código terminado y código verificado.**

#### US-09.07

**Como sistema quiero promover automáticamente un hito cuando todos sus validadores hayan terminado correctamente.**

---

# EPIC-10 — Watchdog y Gobernanza Autónoma

### FEAT-10.01 — Inspector

#### US-10.01

**Como Watchdog quiero auditar continuamente la integridad del proyecto.**

#### US-10.02

**Como Watchdog quiero detectar historias sin criterios.**

#### US-10.03

**Como Watchdog quiero detectar tareas huérfanas.**

#### US-10.04

**Como Watchdog quiero detectar cambios no trazables.**

### FEAT-10.02 — Semáforo

#### US-10.05

**Como operador quiero visualizar el estado de salud del proyecto mediante indicadores de gobernanza.**

#### US-10.06

**Como sistema quiero bloquear automáticamente operaciones que incumplan reglas críticas.**

### FEAT-10.03 — Auditoría

#### US-10.07

**Como operador quiero ejecutar una auditoría completa de gobernanza.**

#### US-10.08

**Como sistema quiero conservar el resultado histórico de las auditorías.**

---

# EPIC-11 — Bugs, Causa Raíz y Autocorrección

### FEAT-11.01 — Bugs

#### US-11.01

**Como sistema quiero crear automáticamente un bug cuando falle una validación.**

#### US-11.02

**Como operador quiero registrar manualmente un bug.**

#### US-11.03

**Como QA quiero asociar un bug con la historia, tarea y ejecución que lo originaron.**

### FEAT-11.02 — Root Cause

#### US-11.04

**Como agente QA quiero analizar la causa raíz de un fallo.**

#### US-11.05

**Como sistema quiero relacionar la causa raíz con el requisito o ADR que originó el problema.**

#### US-11.06

**Como sistema quiero generar una acción correctiva a partir de la causa raíz.**

### FEAT-11.03 — AutoRoot

#### US-11.07

**Como sistema quiero generar automáticamente una tarea correctiva tras detectar un fallo crítico.**

#### US-11.08

**Como sistema quiero priorizar la corrección dentro del contexto del sprint.**

#### US-11.09

**Como Watchdog quiero impedir el cierre del sprint cuando existan fallos críticos sin resolver.**

---

# EPIC-12 — Gestión de Deuda Técnica

### FEAT-12.01 — Registro

#### US-12.01

**Como arquitecto quiero registrar deuda técnica y su motivo.**

#### US-12.02

**Como agente quiero vincular deuda técnica con el código y decisión que la originaron.**

### FEAT-12.02 — Análisis

#### US-12.03

**Como Scrum Master quiero conocer el impacto de la deuda sobre el sprint.**

#### US-12.04

**Como sistema quiero detectar deuda recurrente.**

#### US-12.05

**Como sistema quiero calcular indicadores de deuda acumulada.**

### FEAT-12.03 — Debt Gate

#### US-12.06

**Como Watchdog quiero bloquear nuevas funcionalidades cuando se supere el umbral configurado de deuda.**

#### US-12.07

**Como Scrum Master quiero recibir una propuesta de sprint de refactorización cuando el umbral se supere.**

---

# EPIC-13 — Snapshots, Time Machine y Rollback

### FEAT-13.01 — Snapshots

#### US-13.01

**Como sistema quiero crear un snapshot antes de una operación crítica.**

#### US-13.02

**Como sistema quiero sincronizar el snapshot SQLite con el estado Git correspondiente.**

#### US-13.03

**Como operador quiero identificar exactamente qué estado representa un snapshot.**

### FEAT-13.02 — Restauración

#### US-13.04

**Como operador quiero listar estados restaurables.**

#### US-13.05

**Como operador quiero restaurar un proyecto a un snapshot estable.**

#### US-13.06

**Como sistema quiero restaurar de forma coherente código y contexto ACM.**

### FEAT-13.03 — Protección

#### US-13.07

**Como sistema quiero exigir autorización adicional para operaciones destructivas.**

#### US-13.08

**Como operador quiero conservar evidencia de cada rollback.**

---

# EPIC-14 — Documentación Viva y DocuTwin

### FEAT-14.01 — Documentación técnica

#### US-14.01

**Como arquitecto quiero generar documentación arquitectónica a partir del estado real del sistema.**

#### US-14.02

**Como sistema quiero mantener diagramas C4 asociados a la arquitectura.**

#### US-14.03

**Como sistema quiero actualizar la documentación cuando cambie la arquitectura.**

### FEAT-14.02 — Manual de usuario

#### US-14.04

**Como usuario final quiero disponer de un manual generado a partir de las funcionalidades verificadas.**

#### US-14.05

**Como sistema quiero actualizar el manual cuando una historia funcional quede verificada.**

### FEAT-14.03 — Sincronización

#### US-14.06

**Como sistema quiero detectar documentación desactualizada respecto al código.**

#### US-14.07

**Como sistema quiero vincular documentación con requisitos y evidencias.**

---

# EPIC-15 — Servidor MCP Multi-Proyecto

**Objetivo:** **[v1.1]** ACM implementa y gestiona su propio servidor MCP: es la puerta de entrada de los agentes IA a ACM.

**Valor:** **[v1.1]** cualquier agente que se conecte aprende a usar ACM descargando sus skills desde el propio servidor, sin configuración previa.

### FEAT-15.01 — MCP

#### US-15.01

**Como agente IA quiero conectarme a ACM mediante MCP.**

#### US-15.02

**Como agente quiero descubrir las herramientas MCP disponibles.**

#### US-15.03

**Como agente quiero ejecutar operaciones sobre el proyecto mediante herramientas MCP.**

### FEAT-15.02 — Multi-proyecto

#### US-15.04

**Como operador quiero gestionar múltiples proyectos desde una misma instancia MCP.**

#### US-15.05

**Como agente quiero seleccionar explícitamente el proyecto sobre el que opero.**

#### US-15.06

**Como sistema quiero impedir que una sesión acceda accidentalmente a otro proyecto.**

### FEAT-15.03 — Auditoría MCP

#### US-15.07

**Como operador quiero conocer qué herramienta MCP ha invocado cada agente.**

#### US-15.08

**Como sistema quiero registrar argumentos, resultado, duración y estado de cada invocación.**

### FEAT-15.04 — Distribución de skills ACM **[v1.1]**

#### US-15.09

**Como agente IA quiero que, al conectarme al servidor MCP de ACM, este me indique cómo usarlo y qué skills tiene disponibles, para operar correctamente desde el primer momento.**

Criterios:

* La respuesta de inicialización MCP incluye `instructions` que indican al agente que descargue y cargue las skills de ACM antes de operar.
* El servidor declara la capacidad `resources` y la extensión `io.modelcontextprotocol/skills`.
* `skills/list` devuelve todas las skills oficiales de ACM con `name`, `description`, `uri` y la lista de recursos con `digest` sha256 y `size`.

#### US-15.10

**Como agente IA quiero descargar todas las skills de ACM desde el propio servidor MCP para saber usarlo y sacarle el máximo partido.**

Criterios:

* Cada archivo de cada skill se puede leer con `resources/read` bajo la URI `skill://acm/<nombre>/<archivo>`.
* `skills/get` devuelve la skill solicitada y una skill inexistente devuelve el error `-32602`.
* Los clientes sin soporte de la extensión pueden listar y obtener las mismas skills mediante herramientas MCP de ACM.

#### US-15.11

**Como agente IA quiero saber si las skills que descargué están desactualizadas para volver a descargarlas.**

Criterios:

* Cada SKILL.md declara `version` en su frontmatter.
* El `digest` de un recurso cambia si y solo si cambia su contenido.
* Cuando cambia el catálogo de skills, el servidor emite la notificación de cambio de lista de recursos.

#### US-15.12

**Como operador quiero que ACM gestione el catálogo de skills que sirve para controlar qué aprenden los agentes.**

Criterios:

* Las skills oficiales se versionan junto con el código de ACM.
* Una skill retirada deja de aparecer en `skills/list` y su URI devuelve error.
* Cada descarga de skill queda registrada en la auditoría MCP (US-15.08).

---

# EPIC-16 — Identidad, Tokens, RBAC y Seguridad

### FEAT-16.01 — Identidad

#### US-16.01

**Como operador quiero disponer de credenciales independientes para usuarios y agentes.**

#### US-16.02

**Como sistema quiero autenticar cada conexión MCP.**

### FEAT-16.02 — RBAC

#### US-16.03

**Como operador quiero asignar roles a usuarios y agentes.**

#### US-16.04

**Como sistema quiero limitar las herramientas disponibles según el rol.**

#### US-16.05

**Como sistema quiero restringir el acceso por proyecto.**

### FEAT-16.03 — Tokens

#### US-16.06

**Como operador quiero crear tokens específicos para agentes.**

#### US-16.07

**Como operador quiero revocar un token inmediatamente.**

#### US-16.08

**Como sistema quiero registrar el uso de cada token.**

### FEAT-16.04 — Operaciones sensibles

#### US-16.09

**Como operador quiero exigir autorización adicional para purgar un proyecto.**

#### US-16.10

**Como operador quiero exigir autorización adicional para ejecutar rollback.**

#### US-16.11

**Como sistema quiero impedir operaciones destructivas no autorizadas.**

---

# EPIC-17 — Concurrencia Multi-Agente

### FEAT-17.01 — Locking

#### US-17.01

**Como agente quiero reservar una tarea antes de modificarla.**

#### US-17.02

**Como sistema quiero impedir que dos agentes ejecuten simultáneamente la misma tarea.**

#### US-17.03

**Como sistema quiero detectar modificaciones concurrentes del mismo recurso.**

### FEAT-17.02 — Broadcast Intent

#### US-17.04

**Como agente quiero anunciar mi intención de modificar un recurso.**

#### US-17.05

**Como agente quiero conocer qué recursos están siendo utilizados por otros agentes.**

### FEAT-17.03 — Conflictos

#### US-17.06

**Como sistema quiero detectar conflictos entre agentes.**

#### US-17.07

**Como sistema quiero intentar resolver automáticamente conflictos compatibles.**

#### US-17.08

**Como operador quiero intervenir manualmente en un conflicto no resoluble.**

### FEAT-17.04 — Contratos

#### US-17.09

**Como agente quiero negociar un contrato de modificación antes de tocar código compartido.**

#### US-17.10

**Como sistema quiero conservar el acuerdo entre agentes como evidencia.**

---

# EPIC-18 — Comunicación Reactiva y WebSockets

### FEAT-18.01 — Eventos

#### US-18.01

**Como frontend quiero recibir cambios de estado del proyecto en tiempo real.**

#### US-18.02

**Como frontend quiero recibir cambios de tareas sin refrescar la página.**

#### US-18.03

**Como frontend quiero recibir movimientos del Kanban en tiempo real.**

### FEAT-18.02 — Actividad de agentes

#### US-18.04

**Como operador quiero ver cuándo un agente comienza una tarea.**

#### US-18.05

**Como operador quiero ver cuándo termina una tarea.**

#### US-18.06

**Como operador quiero ver qué herramienta está ejecutando un agente.**

### FEAT-18.03 — Presencia

#### US-18.07

**Como operador quiero conocer qué agentes están conectados.**

#### US-18.08

**Como operador quiero conocer el estado actual de cada agente.**

---

# EPIC-19 — Dashboard, Kanban y Observabilidad

### FEAT-19.01 — Kanban

#### US-19.01

**Como operador quiero visualizar las historias y tareas de un proyecto en un tablero Kanban.**

#### US-19.02

**Como operador quiero ver los cambios provocados por agentes en tiempo real.**

#### US-19.03

**Como operador quiero abrir una tarjeta para consultar su contexto completo.**

### FEAT-19.02 — Actividad

#### US-19.04

**Como operador quiero ver un feed de actividad de los agentes.**

#### US-19.05

**Como operador quiero consultar el historial de actividad de un agente.**

### FEAT-19.03 — Telemetría

#### US-19.06

**Como operador quiero consultar duración de tareas.**

#### US-19.07

**Como operador quiero consultar consumo de tokens cuando el proveedor lo proporcione.**

#### US-19.08

**Como operador quiero consultar errores y latencias de modelos.**

### FEAT-19.04 — Multi-proyecto

#### US-19.09

**Como operador quiero visualizar actividad de varios proyectos desde un panel global.**

---

# EPIC-20 — Trazabilidad E2E

### FEAT-20.01 — Grafo

#### US-20.01

**Como operador quiero visualizar la relación entre módulo, feature, épica, historia, requisito, tarea y código.**

#### US-20.02

**Como operador quiero navegar desde un requisito hasta el código que lo implementa.**

#### US-20.03

**Como operador quiero navegar desde un commit hasta el requisito que justifica el cambio.**

### FEAT-20.02 — Cobertura

#### US-20.04

**Como Watchdog quiero detectar requisitos sin historias.**

#### US-20.05

**Como Watchdog quiero detectar historias sin requisitos.**

#### US-20.06

**Como Watchdog quiero detectar tareas sin historias.**

#### US-20.07

**Como Watchdog quiero detectar cambios de código sin trazabilidad.**

### FEAT-20.03 — Auditoría

#### US-20.08

**Como operador quiero consultar la cobertura E2E de un proyecto.**

#### US-20.09

**Como operador quiero identificar inmediatamente las brechas de trazabilidad.**

---

# EPIC-21 — Memoria Vectorial y RAG

### FEAT-21.01 — Indexación

#### US-21.01

**Como sistema quiero indexar documentación relevante del proyecto.**

#### US-21.02

**Como sistema quiero indexar código fuente de forma incremental.**

#### US-21.03

**Como sistema quiero actualizar los embeddings cuando cambien los archivos.**

### FEAT-21.02 — Recuperación

#### US-21.04

**Como agente quiero recuperar contexto semánticamente relevante antes de ejecutar una tarea.**

#### US-21.05

**Como sistema quiero combinar información estructurada de SQLite con información semántica.**

### FEAT-21.03 — Reranking

#### US-21.06

**Como sistema quiero ordenar los resultados RAG por relevancia.**

#### US-21.07

**Como agente quiero recibir contexto reducido a los fragmentos más relevantes.**

### FEAT-21.04 — Caché

#### US-21.08

**Como sistema quiero reutilizar resultados RAG equivalentes para reducir latencia.**

### FEAT-21.05 — Auditoría RAG

#### US-21.09

**Como operador quiero saber qué documentos y fragmentos influyeron en una respuesta.**

#### US-21.10

**Como Watchdog quiero detectar contaminación de contexto entre proyectos.**

---

# EPIC-22 — Skills para Agentes

**Objetivo:** **[v1.1]** disponer de las skills que enseñan a los agentes a usar ACM; ACM las gestiona y las distribuye a través de su servidor MCP (FEAT-15.04).

### FEAT-22.01 — Skills ACM

#### US-22.01

**Como agente quiero disponer de una skill que explique el esquema ACM.**

#### US-22.02

**Como agente quiero disponer de una skill de validación INVEST.**

#### US-22.03

**Como agente quiero disponer de una skill de Discovery Socrático.**

#### US-22.04

**Como agente quiero disponer de una skill de análisis de errores.**

#### US-22.05

**Como agente quiero disponer de una skill de documentación.**

### FEAT-22.02 — Selección dinámica

#### US-22.06

**Como sistema quiero seleccionar las skills relevantes según la tarea.**

#### US-22.07

**Como sistema quiero inyectar el contexto de una skill antes de ejecutar una operación.**

### FEAT-22.03 — Auditoría

#### US-22.08

**Como operador quiero consultar qué skills utiliza un agente.**

#### US-22.09

**Como operador quiero auditar las instrucciones proporcionadas por una skill.**

### FEAT-22.04 — Sandbox

#### US-22.10

**Como desarrollador quiero probar una skill sin afectar un proyecto real.**

#### US-22.11

**Como desarrollador quiero consultar el resultado de una skill de prueba.**

---

# EPIC-23 — Ollama y Modelos Locales

### FEAT-23.01 — Conexión

#### US-23.01

**Como operador quiero conectar una instancia Ollama a ACM.**

#### US-23.02

**Como sistema quiero detectar modelos disponibles en Ollama.**

### FEAT-23.02 — Selección

#### US-23.03

**Como operador quiero asignar modelos a tipos de tareas.**

#### US-23.04

**Como sistema quiero seleccionar automáticamente un modelo adecuado para una tarea.**

### FEAT-23.03 — Recursos

#### US-23.05

**Como sistema quiero supervisar recursos disponibles para modelos locales.**

#### US-23.06

**Como sistema quiero evitar lanzar más inferencias de las que el hardware puede soportar.**

### FEAT-23.04 — Failover

#### US-23.07

**Como sistema quiero cambiar a un modelo alternativo cuando el principal falle.**

#### US-23.08

**Como sistema quiero registrar los cambios de modelo utilizados durante una tarea.**

---

# EPIC-24 — Motor JEV y Decisiones

### FEAT-24.01 — Conector JEV

#### US-24.01

**Como sistema quiero conectarme a un servidor JEV para ejecutar evaluaciones decisionales.**

#### US-24.02

**Como agente quiero solicitar una evaluación JEV antes de una decisión crítica.**

### FEAT-24.02 — Orquestación híbrida

#### US-24.03

**Como sistema quiero dirigir tareas generativas hacia Ollama y tareas decisionales hacia JEV cuando corresponda.**

#### US-24.04

**Como sistema quiero registrar qué motor produjo cada decisión.**

### FEAT-24.03 — Simulación

#### US-24.05

**Como Scrum Master quiero simular diferentes escenarios de sprint.**

#### US-24.06

**Como arquitecto quiero evaluar riesgos antes de cambios estructurales.**

### FEAT-24.04 — Watchdog JEV

#### US-24.07

**Como Watchdog quiero utilizar reglas decisionales para validar propuestas de agentes.**

#### US-24.08

**Como operador quiero consultar la evaluación decisional asociada a una decisión crítica.**

---

# EPIC-25 — Sandbox y Gemelo Digital

### FEAT-25.01 — Sandbox

#### US-25.01

**Como sistema quiero crear un entorno aislado para probar cambios antes de aplicarlos.**

#### US-25.02

**Como agente quiero ejecutar un plan completo en sandbox antes de modificar el proyecto real.**

### FEAT-25.02 — Gemelo de ejecución

#### US-25.03

**Como Scrum Master quiero simular un sprint antes de iniciarlo.**

#### US-25.04

**Como QA quiero ejecutar criterios de aceptación en el gemelo.**

### FEAT-25.03 — Comparación

#### US-25.05

**Como operador quiero comparar el estado previo y posterior de una simulación.**

#### US-25.06

**Como sistema quiero impedir la promoción de un cambio cuando la simulación detecte un fallo crítico.**

### FEAT-25.04 — Chaos Testing

#### US-25.07

**Como QA quiero ejecutar escenarios de fallo controlados sobre un entorno aislado.**

#### US-25.08

**Como Watchdog quiero comprobar que el sistema recupera correctamente estados degradados.**

---

# EPIC-26 — Seguridad de Memoria y Datos

### FEAT-26.01 — Aislamiento

#### US-26.01

**Como sistema quiero aislar los datos de cada proyecto.**

#### US-26.02

**Como sistema quiero impedir que un agente consulte memoria de otro proyecto sin autorización.**

### FEAT-26.02 — Cifrado

#### US-26.03

**Como operador quiero proteger datos sensibles almacenados.**

#### US-26.04

**Como sistema quiero proteger información sensible durante las comunicaciones.**

### FEAT-26.03 — Embeddings

#### US-26.05

**Como sistema quiero proteger embeddings y metadatos asociados.**

---

# EPIC-27 — Auditoría Forense y Telemetría

### FEAT-27.01 — Audit Log

#### US-27.01

**Como operador quiero registrar cada mutación realizada por un agente.**

#### US-27.02

**Como operador quiero consultar el historial completo de una sesión.**

#### US-27.03

**Como auditor quiero reconstruir la secuencia de eventos de una incidencia.**

### FEAT-27.02 — Métricas

#### US-27.04

**Como operador quiero medir latencias de herramientas MCP.**

#### US-27.05

**Como operador quiero medir rendimiento de agentes.**

#### US-27.06

**Como operador quiero medir rendimiento de RAG.**

#### US-27.07

**Como operador quiero medir rendimiento de modelos.**

---

# EPIC-28 — Cuotas y Rate Limiting

### FEAT-28.01 — Cuotas

#### US-28.01

**Como operador quiero establecer cuotas por agente.**

#### US-28.02

**Como operador quiero establecer límites de consumo por proyecto.**

#### US-28.03

**Como sistema quiero bloquear temporalmente a un agente que supere su cuota.**

### FEAT-28.02 — Rate Limiting

#### US-28.04

**Como sistema quiero limitar la frecuencia de llamadas MCP.**

#### US-28.05

**Como sistema quiero detectar bucles excesivos de llamadas.**

### FEAT-28.03 — Revocación

#### US-28.06

**Como operador quiero revocar las credenciales de un agente en tiempo real.**

---

# EPIC-29 — Intervención Humano-IA

### FEAT-29.01 — Pausa

#### US-29.01

**Como operador quiero pausar un agente durante una operación.**

#### US-29.02

**Como operador quiero reanudar un agente pausado.**

### FEAT-29.02 — Aprobación

#### US-29.03

**Como operador quiero aprobar manualmente una operación sensible.**

#### US-29.04

**Como operador quiero rechazar una operación propuesta por un agente.**

### FEAT-29.03 — Chat

#### US-29.05

**Como operador quiero comunicarme con un agente desde el contexto de una tarea.**

#### US-29.06

**Como agente quiero recibir instrucciones humanas manteniendo el contexto de la tarea.**

---

# EPIC-30 — Notificaciones e Integraciones Externas

### FEAT-30.01 — Webhooks

#### US-30.01

**Como operador quiero configurar un webhook externo.**

#### US-30.02

**Como sistema quiero enviar eventos críticos a servicios externos.**

### FEAT-30.02 — Notificaciones

#### US-30.03

**Como operador quiero recibir una alerta cuando un agente termine una operación crítica.**

#### US-30.04

**Como operador quiero recibir una alerta cuando el Watchdog bloquee una operación.**

---

# EPIC-31 — CLI de Administración

### FEAT-31.01 — CLI

#### US-31.01

**Como desarrollador quiero consultar el estado de ACM desde terminal.**

#### US-31.02

**Como desarrollador quiero ejecutar auditorías desde CLI.**

#### US-31.03

**Como desarrollador quiero consultar trazabilidad desde CLI.**

#### US-31.04

**Como desarrollador quiero gestionar sprints desde CLI.**

### FEAT-31.02 — Operaciones administrativas

#### US-31.05

**Como operador quiero ejecutar operaciones de mantenimiento desde CLI.**

#### US-31.06

**Como operador quiero consultar la salud de la base de datos desde CLI.**

---

# EPIC-32 — Sistema de Extensiones y Plugins

### FEAT-32.01 — Plugins

#### US-32.01

**Como desarrollador quiero registrar extensiones de ACM sin modificar el núcleo.**

#### US-32.02

**Como desarrollador quiero descubrir plugins instalados.**

#### US-32.03

**Como sistema quiero controlar los permisos de cada extensión.**

### FEAT-32.02 — Herramientas personalizadas

#### US-32.04

**Como desarrollador quiero incorporar herramientas MCP personalizadas.**

#### US-32.05

**Como sistema quiero registrar y auditar las herramientas externas utilizadas.**

---

# EPIC-33 — Gestión de Dependencias y Grafos

### FEAT-33.01 — Grafo de conocimiento

#### US-33.01

**Como sistema quiero representar relaciones entre módulos, archivos, funciones, ADRs e historias.**

#### US-33.02

**Como agente quiero consultar dependencias técnicas antes de modificar un componente.**

### FEAT-33.02 — Dependencias circulares

#### US-33.03

**Como Watchdog quiero detectar dependencias circulares.**

#### US-33.04

**Como operador quiero visualizar dependencias problemáticas.**

### FEAT-33.03 — Impact Analysis

#### US-33.05

**Como arquitecto quiero conocer el impacto potencial de modificar un componente.**

#### US-33.06

**Como agente quiero identificar requisitos y funcionalidades afectadas antes de realizar un cambio.**

---

# EPIC-34 — Optimización de SQLite

### FEAT-34.01 — Rendimiento

#### US-34.01

**Como sistema quiero detectar consultas SQLite lentas.**

#### US-34.02

**Como sistema quiero registrar métricas de consultas.**

### FEAT-34.02 — Índices

#### US-34.03

**Como sistema quiero detectar oportunidades de indexación.**

#### US-34.04

**Como arquitecto quiero revisar las propuestas de optimización antes de aplicarlas automáticamente.**

### FEAT-34.03 — Concurrencia

#### US-34.05

**Como sistema quiero gestionar transacciones concurrentes sin corrupción.**

#### US-34.06

**Como sistema quiero reintentar operaciones cuando se produzcan bloqueos transitorios.**

---

# EPIC-35 — Documentación del Código y Runbooks

### FEAT-35.01 — Documentación de archivos

#### US-35.01

**Como desarrollador quiero conocer qué responsabilidad tiene cada archivo.**

#### US-35.02

**Como agente quiero consultar documentación técnica antes de modificar un archivo complejo.**

### FEAT-35.02 — Runbooks

#### US-35.03

**Como operador quiero disponer de procedimientos documentados para resolver incidencias.**

#### US-35.04

**Como sistema quiero generar un runbook a partir de una incidencia recurrente.**

---

# EPIC-36 — Gobierno de Deriva Semántica

### FEAT-36.01 — Zero Drift

#### US-36.01

**Como Watchdog quiero comprobar que cada modificación de código corresponde a una tarea activa.**

#### US-36.02

**Como Watchdog quiero comparar cambios de código con los requisitos de la tarea.**

#### US-36.03

**Como sistema quiero bloquear commits que no tengan trazabilidad válida.**

### FEAT-36.02 — ADR Guard

#### US-36.04

**Como sistema quiero comprobar las modificaciones contra los ADR vigentes.**

#### US-36.05

**Como sistema quiero exigir un nuevo ADR cuando una modificación cambie una decisión arquitectónica.**

---

# EPIC-37 — Auto-Sanación y Autopoiesis

### FEAT-37.01 — Curación causal

#### US-37.01

**Como sistema quiero recorrer la cadena causal de un error hasta su origen.**

#### US-37.02

**Como sistema quiero identificar el requisito, ADR o tarea potencialmente causante.**

### FEAT-37.02 — Regeneración

#### US-37.03

**Como agente quiero proponer una modificación de especificación cuando una implementación contradiga el requisito.**

#### US-37.04

**Como sistema quiero regenerar el plan afectado después de una corrección estructural.**

### FEAT-37.03 — Protección

#### US-37.05

**Como Watchdog quiero exigir validación antes de aplicar una autocorrección.**

#### US-37.06

**Como sistema quiero generar un snapshot antes de una autocorrección crítica.**

---

# EPIC-38 — Analítica Agile y Predictiva

### FEAT-38.01 — Velocidad

#### US-38.01

**Como Scrum Master quiero consultar la velocidad histórica de los sprints.**

#### US-38.02

**Como Scrum Master quiero comparar velocidad entre módulos.**

### FEAT-38.02 — Cuellos de botella

#### US-38.03

**Como sistema quiero detectar acumulación anormal de tareas.**

#### US-38.04

**Como operador quiero visualizar cuellos de botella en el Kanban.**

### FEAT-38.03 — Deuda

#### US-38.05

**Como operador quiero visualizar la relación entre deuda técnica y velocidad.**

### FEAT-38.04 — Predicción

#### US-38.06

**Como Scrum Master quiero consultar predicciones sobre riesgos del sprint.**

---

# EPIC-39 — Presencia y Coordinación Multi-Agente

### FEAT-39.01 — Presencia

#### US-39.01

**Como operador quiero ver todos los agentes conectados a un proyecto.**

#### US-39.02

**Como operador quiero conocer qué está haciendo cada agente.**

### FEAT-39.02 — Coordinación

#### US-39.03

**Como agente quiero comunicarme con otros agentes del mismo proyecto.**

#### US-39.04

**Como agente quiero intercambiar contexto relevante con otro agente.**

### FEAT-39.03 — Negociación

#### US-39.05

**Como agente quiero negociar prioridades cuando dos agentes necesitan el mismo recurso.**

#### US-39.06

**Como sistema quiero registrar el acuerdo alcanzado entre agentes.**

---

# EPIC-40 — Panel de Skills y Control de Agentes

### FEAT-40.01 — Skills activas

#### US-40.01

**Como operador quiero ver qué skill está utilizando un agente.**

#### US-40.02

**Como operador quiero consultar la ejecución de una skill.**

### FEAT-40.02 — Prompts

#### US-40.03

**Como desarrollador quiero inspeccionar las instrucciones asociadas a una skill.**

#### US-40.04

**Como desarrollador quiero probar una variante de una skill en sandbox.**

### FEAT-40.03 — Intervención

#### US-40.05

**Como operador quiero pausar un agente antes de una operación crítica.**

#### US-40.06

**Como operador quiero aprobar o rechazar una acción sensible desde el panel.**

---

# EPIC-41 — Sistema de Backup y Recuperación Distribuida

### FEAT-41.01 — Backup

#### US-41.01

**Como sistema quiero exportar copias de seguridad de la base ACM.**

#### US-41.02

**Como sistema quiero proteger las copias de seguridad.**

### FEAT-41.02 — Almacenamiento externo

#### US-41.03

**Como operador quiero configurar un destino externo de backup.**

#### US-41.04

**Como sistema quiero verificar que una copia exportada puede recuperarse.**

### FEAT-41.03 — Recuperación

#### US-41.05

**Como operador quiero restaurar un backup completo.**

#### US-41.06

**Como sistema quiero registrar la operación de restauración.**

---

# EPIC-42 — Auditoría y Cumplimiento de Integridad

### FEAT-42.01 — Integridad referencial

#### US-42.01

**Como Watchdog quiero comprobar que las relaciones entre entidades ACM son válidas.**

#### US-42.02

**Como sistema quiero detectar registros huérfanos.**

### FEAT-42.02 — Integridad global

#### US-42.03

**Como Watchdog quiero comprobar que una historia tiene origen, criterios y ejecución trazables.**

#### US-42.04

**Como Watchdog quiero comprobar que una tarea pertenece a una historia válida.**

### FEAT-42.03 — Gobernanza

#### US-42.05

**Como operador quiero ejecutar una auditoría global del proyecto.**

#### US-42.06

**Como operador quiero recibir un informe de incumplimientos.**

---

# EPIC-43 — Generación Automática de Contexto para Agentes

### FEAT-43.01 — Context Loader

#### US-43.01

**Como agente quiero solicitar el contexto necesario antes de comenzar una tarea.**

#### US-43.02

**Como sistema quiero seleccionar automáticamente el contexto relevante.**

### FEAT-43.02 — Contexto estructurado

#### US-43.03

**Como agente quiero recibir el estado de la historia, tarea, requisitos y ADR relacionados.**

#### US-43.04

**Como agente quiero recibir las restricciones del stack relevantes.**

### FEAT-43.03 — Contexto semántico

#### US-43.05

**Como agente quiero recibir fragmentos RAG relevantes junto al contexto estructurado.**

---

# EPIC-44 — Control de Ejecución y Ciclo Autónomo

### FEAT-44.01 — Autonomous Loop

#### US-44.01

**Como operador quiero iniciar un ciclo autónomo de desarrollo.**

#### US-44.02

**Como sistema quiero seleccionar la siguiente tarea ejecutable.**

#### US-44.03

**Como sistema quiero validar que la tarea está autorizada antes de ejecutarla.**

### FEAT-44.02 — Ciclo completo

#### US-44.04

**Como sistema quiero ejecutar la tarea, verificarla y actualizar su estado automáticamente.**

#### US-44.05

**Como sistema quiero avanzar hacia la siguiente tarea cuando la anterior haya quedado correctamente validada.**

### FEAT-44.03 — Detención

#### US-44.06

**Como sistema quiero detener el ciclo cuando aparezca un bloqueo crítico.**

#### US-44.07

**Como operador quiero reanudar el ciclo después de resolver un bloqueo.**

---

# EPIC-45 — Sistema de Notificación y Alertas del Watchdog

### FEAT-45.01 — Alertas

#### US-45.01

**Como operador quiero recibir alertas cuando un agente se desvíe de sus permisos.**

#### US-45.02

**Como operador quiero recibir alertas cuando falle una validación crítica.**

### FEAT-45.02 — Alertas predictivas

#### US-45.03

**Como operador quiero recibir alertas sobre posibles cuellos de botella.**

#### US-45.04

**Como operador quiero recibir alertas sobre degradación de arquitectura.**

---

# EPIC-46 — Visualización Avanzada de Grafos

### FEAT-46.01 — Grafo E2E

#### US-46.01

**Como operador quiero visualizar el grafo completo de trazabilidad.**

### FEAT-46.02 — Grafo RAG

#### US-46.02

**Como operador quiero visualizar las relaciones entre consultas y fragmentos recuperados.**

### FEAT-46.03 — Grafo arquitectónico

#### US-46.03

**Como arquitecto quiero visualizar dependencias entre módulos.**

#### US-46.04

**Como arquitecto quiero identificar visualmente ciclos y nodos críticos.**

### FEAT-46.04 — Grafo 3D

#### US-46.05

**Como operador quiero disponer de una representación tridimensional opcional de grafos complejos.**

---

# EPIC-47 — Generación de Manuales Mediante Agentes Sintéticos

### FEAT-47.01 — Gemelos de usuario

#### US-47.01

**Como QA quiero crear agentes que representen roles de usuario concretos.**

#### US-47.02

**Como QA quiero ejecutar un flujo como si fuera un usuario final.**

### FEAT-47.02 — Manual generado

#### US-47.03

**Como sistema quiero generar instrucciones de usuario a partir de los flujos realmente ejecutados.**

#### US-47.04

**Como sistema quiero detectar discrepancias entre manual y aplicación.**

### FEAT-47.03 — Chaos End-User

#### US-47.05

**Como QA quiero ejecutar escenarios de uso no ideales en sandbox.**

#### US-47.06

**Como sistema quiero crear bugs cuando un usuario sintético encuentre una inconsistencia.**

---

# EPIC-48 — Extensibilidad del Motor ACM

### FEAT-48.01 — Nuevos tipos de agentes

#### US-48.01

**Como desarrollador quiero registrar nuevos perfiles de agente.**

#### US-48.02

**Como desarrollador quiero definir las capacidades y permisos de un perfil.**

### FEAT-48.02 — Nuevas herramientas

#### US-48.03

**Como desarrollador quiero incorporar nuevas herramientas MCP sin modificar el núcleo.**

### FEAT-48.03 — Eventos

#### US-48.04

**Como desarrollador quiero reaccionar a eventos ACM mediante extensiones.**

---

# 8. HISTORIAS TÉCNICAS TRANSVERSALES

Estas no sustituyen a las historias de usuario. Representan trabajo técnico necesario para hacer posible el producto.

## TECH-001 — Motor de eventos interno

Implementar un sistema centralizado de eventos para propagar cambios ACM.

## TECH-002 — Bus WebSocket

Implementar distribución de eventos a clientes conectados.

## TECH-003 — Gestión WAL SQLite

Configurar y validar el modo de concurrencia apropiado.

## TECH-004 — Sistema de transacciones

Implementar transacciones seguras para operaciones ACM.

## TECH-005 — Sistema de locking

Implementar control optimista de recursos.

## TECH-006 — Índices SQLite

Diseñar índices sobre las relaciones críticas.

## TECH-007 — Migraciones de esquema

Implementar evolución versionada del esquema.

## TECH-008 — Integridad referencial

Activar y verificar claves foráneas.

## TECH-009 — Triggers ACM

Implementar los triggers necesarios para automatización de estados.

## TECH-010 — API MCP

Implementar exposición de herramientas.

## TECH-011 — Registro de herramientas

Implementar descubrimiento y metadatos de herramientas.

## TECH-012 — Sistema de autenticación

Implementar validación de credenciales.

## TECH-013 — RBAC

Implementar autorización por roles.

## TECH-014 — Auditoría

Implementar registro inmutable de operaciones.

## TECH-015 — RAG ingestion pipeline

Implementar pipeline de indexación.

## TECH-016 — Embeddings

Implementar generación y actualización incremental.

## TECH-017 — Reranking

Implementar recuperación híbrida y reranking.

## TECH-018 — Ollama adapter

Implementar conexión con Ollama.

## TECH-019 — Model router

Implementar selección y failover de modelos.

## TECH-020 — JEV adapter

Implementar integración con el motor JEV.

## TECH-021 — Snapshot engine

Implementar snapshots coordinados.

## TECH-022 — Git integration

Implementar asociación entre snapshots y commits.

## TECH-023 — Sandbox engine

Implementar entornos efímeros.

## TECH-024 — Execution engine

Implementar ejecución de walkthroughs.

## TECH-025 — Documentation generator

Implementar generación documental.

## TECH-026 — Graph engine

Implementar representación de dependencias.

## TECH-027 — Telemetry engine

Implementar métricas y eventos.

## TECH-028 — Notification engine

Implementar Webhooks y alertas.

## TECH-029 — CLI

Implementar interfaz administrativa.

## TECH-030 — Plugin system

Implementar extensión segura del servidor.

---

# 9. SPIKES / INVESTIGACIÓN

Estas cuestiones deben investigarse antes de comprometer una arquitectura definitiva.

### SPIKE-001 — Modelo de concurrencia SQLite

Determinar límites reales de concurrencia y estrategia WAL/locking.

### SPIKE-002 — Arquitectura MCP multi-proyecto

Determinar aislamiento óptimo entre proyectos y sesiones.

### SPIKE-003 — ChromaDB

Evaluar persistencia, aislamiento y rendimiento.

### SPIKE-004 — RAG híbrido

Evaluar combinación SQL + vector + reranking.

### SPIKE-005 — Ollama multiagente

Evaluar gestión de múltiples inferencias concurrentes.

### SPIKE-006 — JEV

Definir contrato real de integración.

### SPIKE-007 — Sandbox

Determinar tecnología de aislamiento.

### SPIKE-008 — Snapshots

Determinar estrategia incremental y restauración consistente.

### SPIKE-009 — Cifrado

Determinar modelo de gestión de claves.

### SPIKE-010 — Observabilidad

Determinar esquema de eventos y retención.

### SPIKE-011 — Streaming de razonamiento

Determinar qué información puede mostrarse de forma segura y qué debe representarse como trazas/eventos en lugar de exponer razonamiento interno privado.

### SPIKE-012 — WebAuthn/FIDO2

Evaluar si las operaciones críticas requieren segundo factor hardware.

---

# 10. REGLAS TRANSVERSALES DEL PRODUCTO

## Regla 1 — Nada de código sin trazabilidad

Todo cambio relevante debe poder relacionarse con una tarea.

## Regla 2 — Nada de tarea sin historia

Toda tarea funcional debe tener una historia de origen.

## Regla 3 — Nada de historia sin requisitos

Toda historia debe disponer de criterios verificables.

## Regla 4 — Nada de DONE sin evidencia

Una tarea no se considera realmente terminada sin la evidencia correspondiente.

## Regla 5 — Nada de ejecución sin contexto

El agente debe cargar contexto estructurado y semántico antes de actuar.

## Regla 6 — Nada de cambio arquitectónico silencioso

Todo cambio relevante del stack o arquitectura debe quedar documentado.

## Regla 7 — Nada de conflicto silencioso

Los conflictos entre agentes deben detectarse y registrarse.

## Regla 8 — Nada de proyecto mezclado

Cada proyecto debe disponer de aislamiento lógico y de memoria.

## Regla 9 — Nada de operación destructiva sin protección

Las operaciones críticas deben disponer de snapshot y autorización apropiada.

## Regla 10 — Nada de documentación ficticia

La documentación debe derivarse del estado real del sistema.

---

# 11. MATRIZ DE TRAZABILIDAD CONCEPTUAL

La trazabilidad oficial debe seguir:

```text
REQ
 ↓
MODULE
 ↓
FEATURE
 ↓
EPIC
 ↓
USER STORY
 ↓
REQUIREMENT / ACCEPTANCE CRITERION
 ↓
SPRINT
 ↓
TASK
 ↓
IMPLEMENTATION PLAN
 ↓
PLAN STEP
 ↓
FILE / CODE
 ↓
COMMIT
 ↓
WALKTHROUGH
 ↓
LOG
```

Y adicionalmente:

```text
BUG
 ↓
ROOT CAUSE
 ↓
TASK CORRECTIVA
 ↓
ADR / TECH DEBT
 ↓
IMPLEMENTATION PLAN
 ↓
VALIDATION
```

---

# 12. MVP PROPUESTO

El producto completo es considerablemente mayor que un MVP.

El núcleo mínimo funcional debería permitir:

1. Crear proyecto.
2. Crear módulos.
3. Crear funcionalidades.
4. Registrar stack.
5. Crear épicas.
6. Crear historias.
7. Añadir requisitos.
8. Crear sprints.
9. Crear tareas.
10. Crear planes.
11. Ejecutar walkthroughs.
12. Registrar evidencia.
13. Watchdog básico.
14. Bugs.
15. ADRs.
16. Servidor MCP.
17. Autenticación.
18. Kanban.
19. WebSockets.
20. Actividad de agentes.
21. Auditoría.
22. Snapshots.
23. Integración básica con Ollama.
24. Context loading.
25. RAG básico.
26. Trazabilidad E2E.
27. **[v1.1]** Skills ACM distribuidas por el servidor MCP propio.

---

# 13. POST-MVP

Posteriormente:

* JEV;
* sandbox avanzado;
* gemelos sintéticos;
* chaos testing;
* auto-root;
* autocorrección;
* multiagente avanzado;
* negociación;
* contratos entre agentes;
* grafos avanzados;
* RAG híbrido;
* reranking;
* documentación automática avanzada;
* CLI completa;
* plugins;
* backups externos;
* cifrado avanzado;
* WebAuthn;
* predicción;
* analítica avanzada;
* optimización de modelos;
* failover;
* simulación predictiva.

---

# 14. DEPENDENCIAS PRINCIPALES

```text
Project Context
      ↓
Product Discovery
      ↓
Modules
      ↓
Features
      ↓
Backlog
      ↓
Stories
      ↓
Requirements
      ↓
Sprints
      ↓
Tasks
      ↓
Plans
      ↓
Execution
      ↓
Validation
      ↓
DONE
```

En paralelo:

```text
Project
 ├── SQLite
 ├── Git
 ├── Vector DB
 ├── Ollama
 ├── JEV
 ├── MCP
 └── WebSocket
```

Y transversalmente:

```text
Security
Governance
Watchdog
Telemetry
Documentation
Snapshots
Audit
```

---

# 15. COBERTURA DE LAS IDEAS ORIGINALES

Las 72 ideas originales se consolidan principalmente en estos bloques:

| Grupo conceptual                  | Cobertura                   |
| --------------------------------- | --------------------------- |
| Dual-Agent Watchdog               | EPIC-05 + EPIC-10           |
| Living Docs / DocuTwin / DocuLive | EPIC-14 + EPIC-35           |
| Discovery Socrático               | EPIC-02                     |
| Time Machine / Snapshots          | EPIC-13                     |
| Gemelos sintéticos                | EPIC-47                     |
| Autopoiesis / Root Cause          | EPIC-11 + EPIC-37           |
| AutoRoot                          | EPIC-11                     |
| INVEST Gatekeeper                 | EPIC-05                     |
| Sandbox Pre-Sprint                | EPIC-25                     |
| Chaos Testing                     | EPIC-25 + EPIC-47           |
| Debt Gate                         | EPIC-12                     |
| Reverse Walkthrough               | EPIC-09                     |
| Zero Drift                        | EPIC-36                     |
| Consejo de agentes                | EPIC-05 + EPIC-39           |
| ADR Guard                         | EPIC-03 + EPIC-36           |
| Trazabilidad E2E                  | EPIC-20                     |
| Auditoría forense                 | EPIC-27                     |
| Simulación de sprints             | EPIC-06 + EPIC-24 + EPIC-25 |
| Snapshot Sync Git-SQLite          | EPIC-13                     |
| Consenso arquitectónico           | EPIC-03 + EPIC-05           |
| CI/CD Watchdog                    | EPIC-09 + EPIC-10 + EPIC-36 |
| Predicción de deuda               | EPIC-12 + EPIC-38           |
| Auto-sanación                     | EPIC-37                     |
| Contexto dinámico                 | EPIC-43                     |
| Ollama                            | EPIC-23                     |
| JEV                               | EPIC-24                     |
| Skills                            | EPIC-22 + EPIC-40           |
| WebSockets                        | EPIC-18                     |
| Kanban reactivo                   | EPIC-19                     |
| Concurrencia                      | EPIC-17                     |
| Tokens/RBAC                       | EPIC-16                     |
| RAG                               | EPIC-21                     |
| Telemetría                        | EPIC-19 + EPIC-27           |
| Grafos                            | EPIC-20 + EPIC-33 + EPIC-46 |
| Plugins                           | EPIC-32                     |
| CLI                               | EPIC-31                     |
| Backups                           | EPIC-41                     |
| Notificaciones                    | EPIC-30 + EPIC-45           |

---

# 16. REQUISITOS DE CALIDAD DEL BACKLOG

El backlog no debe considerarse completo simplemente porque existan muchas historias.

Antes de comenzar la implementación, ACM debe comprobar:

### Cobertura

Cada requisito debe tener:

```text
REQUISITO
→ FEATURE
→ ÉPICA
→ HISTORIA
→ CRITERIOS
→ TAREA
→ VALIDACIÓN
```

### Ausencias

Debe detectar:

* requisitos sin historias;
* historias sin criterios;
* historias sin origen;
* tareas sin historia;
* tareas sin evidencia;
* planes sin validadores;
* módulos sin funcionalidades;
* ADRs sin impacto;
* código sin task;
* documentación sin origen.

### Duplicados

Debe detectar:

* historias duplicadas;
* features duplicadas;
* ADRs contradictorios;
* herramientas MCP duplicadas;
* skills equivalentes;
* reglas de gobernanza solapadas.

### Coherencia

Debe verificar:

* arquitectura ↔ stack;
* stack ↔ código;
* código ↔ tareas;
* tareas ↔ historias;
* historias ↔ requisitos;
* requisitos ↔ funcionalidades;
* funcionalidades ↔ visión.

---

# 17. PRINCIPIO FUNDAMENTAL DEL PRODUCTO

ACM no debe limitarse a decir:

> "La IA ha terminado la tarea."

Debe ser capaz de demostrar:

```text
Qué se quería conseguir
        ↓
Por qué se quería conseguir
        ↓
Qué funcionalidad lo representa
        ↓
Qué historia lo expresa
        ↓
Qué requisitos determinan que está terminado
        ↓
Qué tarea lo implementó
        ↓
Qué agente la ejecutó
        ↓
Qué archivos modificó
        ↓
Qué commit produjo
        ↓
Qué pruebas ejecutó
        ↓
Qué evidencia obtuvo
        ↓
Qué Watchdog verificó
        ↓
Qué documentación actualizó
        ↓
Qué estado quedó almacenado
```

El objetivo final de ACM es convertirse en una **memoria operativa verificable del desarrollo software**, capaz de permitir que múltiples agentes IA trabajen de manera autónoma sobre múltiples proyectos sin perder contexto, sin destruir la trazabilidad y sin convertir el proyecto en una colección de decisiones aisladas tomadas dentro de conversaciones efímeras.

---

# 18. DEFINICIÓN CONCEPTUAL FINAL

**Agile Context Manager es una plataforma de infraestructura para equipos de desarrollo híbridos humano-IA.**

Su núcleo combina:

```text
                 ┌─────────────────────┐
                 │      HUMANOS        │
                 └──────────┬──────────┘
                            │
                     Web / CLI / MCP
                            │
                 ┌──────────▼──────────┐
                 │        ACM          │
                 │ Governance + State  │
                 └──────────┬──────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   SQLite / Graph       Vector RAG          Git / Code
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                ┌───────────▼───────────┐
                │    Agent Orchestrator │
                └───────────┬───────────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
          Ollama           JEV       External Agents
              │             │             │
              └─────────────┼─────────────┘
                            │
                    MCP Tool Execution
                            │
                 ┌──────────▼──────────┐
                 │       Watchdog      │
                 │ QA / Governance /   │
                 │ Traceability / Gate │
                 └──────────┬──────────┘
                            │
                 ┌──────────▼──────────┐
                 │   Verified State    │
                 └─────────────────────┘
```

La característica diferencial de ACM no es tener muchas herramientas.

Es que **todas las herramientas, agentes, decisiones, datos, ejecuciones y documentos forman parte de un mismo grafo de estado verificable**.

El sistema debe poder responder en cualquier momento:

> **Qué está ocurriendo, quién lo está haciendo, por qué lo está haciendo, qué requisito lo justifica, qué riesgos existen, qué código está afectado, qué evidencia demuestra que funciona y qué debería ocurrir después.**

Ese es el principio rector de toda la arquitectura y del backlog.
