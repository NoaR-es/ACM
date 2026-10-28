# Requisitos

## Requisitos funcionales (definición §3.1)

La asignación requisito → épica es una **propuesta del agente** (2026-09-30), derivada por afinidad de títulos. Desde ADR-010 (2026-09-30) está expresada en la **numeración unificada**, traducida automáticamente desde la numeración B con `FEATURE_MAP`.

La fuente A no enumera requisitos formales: sus historias se trazan a estos REQ-F mediante sus épicas.

> Aviso: la traducción es por épica completa, así que puede añadir épicas de más (p. ej. EPIC-13 en REQ-F-01..03, por el Health Check de B:EPIC-01) y omitir épicas propias de A (p. ej. EPIC-24 multiproyecto en REQ-F-01/02). La revisión se hará en TASK-000-10.

| ID | Requisito | Épicas que lo cubren | Estado |
|----|-----------|----------------------|--------|
| REQ-F-01 | Gestionar múltiples proyectos. | EPIC-01, EPIC-13, EPIC-14, EPIC-15 | PLANNED |
| REQ-F-02 | Mantener un contexto independiente para cada proyecto. | EPIC-01, EPIC-13, EPIC-24, EPIC-44 | PLANNED |
| REQ-F-03 | Registrar la visión y metadatos del proyecto. | EPIC-01, EPIC-13 | PLANNED |
| REQ-F-04 | Crear árboles funcionales. | EPIC-03, EPIC-17 | PLANNED |
| REQ-F-05 | Gestionar módulos y submódulos. | EPIC-03, EPIC-17 | PLANNED |
| REQ-F-06 | Registrar funcionalidades. | EPIC-03, EPIC-17 | PLANNED |
| REQ-F-07 | Registrar stack tecnológico y decisiones. | EPIC-25 | PLANNED |
| REQ-F-08 | Crear y gestionar épicas. | EPIC-04 | PLANNED |
| REQ-F-09 | Crear y gestionar historias de usuario. | EPIC-04 | PLANNED |
| REQ-F-10 | Definir criterios de aceptación. | EPIC-04, EPIC-41 | PLANNED |
| REQ-F-11 | Gestionar sprints. | EPIC-05 | PLANNED |
| REQ-F-12 | Crear tareas técnicas. | EPIC-10, EPIC-11 | PLANNED |
| REQ-F-13 | Gestionar planes de implementación. | EPIC-10 | PLANNED |
| REQ-F-14 | Ejecutar validaciones. | EPIC-10, EPIC-28 | PLANNED |
| REQ-F-15 | Registrar walkthroughs. | EPIC-28 | PLANNED |
| REQ-F-16 | Gestionar bugs. | EPIC-29 | PLANNED |
| REQ-F-17 | Gestionar deuda técnica. | EPIC-49 | PLANNED |
| REQ-F-18 | Registrar ADRs. | EPIC-25 | PLANNED |
| REQ-F-19 | Mantener documentación. | EPIC-25 | PLANNED |
| REQ-F-20 | Proporcionar un servidor MCP. | EPIC-14, EPIC-15 | PLANNED |
| REQ-F-21 | Permitir múltiples agentes simultáneos. | EPIC-19, EPIC-41 | PLANNED |
| REQ-F-22 | Proporcionar memoria RAG. | EPIC-16 | PLANNED |
| REQ-F-23 | Integrar modelos locales. | EPIC-22, EPIC-39 | PLANNED |
| REQ-F-24 | Integrar modelos de decisión. | EPIC-50 | PLANNED |
| REQ-F-25 | Aplicar permisos y gobernanza. | EPIC-20, EPIC-23 | PLANNED |
| REQ-F-26 | Mostrar actividad de agentes en tiempo real. | EPIC-06, EPIC-21, EPIC-26, EPIC-31, EPIC-45 | PLANNED |
| REQ-F-27 | Mostrar el Kanban en tiempo real. | EPIC-06, EPIC-21, EPIC-26, EPIC-31, EPIC-45 | PLANNED |
| REQ-F-28 | Auditar las acciones de los agentes. | EPIC-26, EPIC-44 | PLANNED |
| REQ-F-29 | Crear snapshots. | EPIC-12 | PLANNED |
| REQ-F-30 | Restaurar estados anteriores. | EPIC-12, EPIC-40 | PLANNED |
| REQ-F-31 | Detectar conflictos. | EPIC-19, EPIC-41 | PLANNED |
| REQ-F-32 | Detectar deriva arquitectónica. | EPIC-27 | PLANNED |
| REQ-F-33 | Detectar deuda técnica. | EPIC-49 | PLANNED |
| REQ-F-34 | Detectar historias defectuosas. | EPIC-04, EPIC-41 | PLANNED |
| REQ-F-35 | Generar documentación automáticamente. | EPIC-25, EPIC-51 | PLANNED |
| REQ-F-36 | Ejecutar simulaciones antes de modificar el proyecto real. | EPIC-51 | PLANNED |
| REQ-F-37 | Permitir intervención humana. | EPIC-46 | PLANNED |
| REQ-F-38 | Proporcionar CLI. | EPIC-52 | PLANNED |
| REQ-F-39 | Permitir extensiones y skills. | EPIC-15, EPIC-53 | PLANNED |
| REQ-F-40 | Mantener trazabilidad E2E. | EPIC-27 | PLANNED |

## Requisitos no funcionales
MISSING — la definición no fija latencias, volúmenes, concurrencia objetivo ni plataformas soportadas. Se abordan en SPIKE-001, SPIKE-005, SPIKE-010.

## Requisitos añadidos

| ID | Requisito | Épicas que lo cubren | Estado |
|----|-----------|----------------------|--------|
| REQ-F-41 | Actuar como segundo cerebro del agente IA: contexto compacto y decisiones tipadas con modelos locales (Ollama, JEV) para reducir los tokens que consume el agente (definición v1.2 §1.2, 2026-09-30). | EPIC-35, EPIC-47, EPIC-50, EPIC-22 | PLANNED |
| REQ-F-42 | Preparar la arquitectura para integrar JEV sin rediseño: interfaz de decisión común desde el MVP (ADR-012). | EPIC-35, EPIC-47, EPIC-50 | PLANNED |
