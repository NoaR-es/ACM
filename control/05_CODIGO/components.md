# Componentes de la interfaz web (`web/src`)

Actualizado: 2026-09-30 (SPRINT-007). Arquitectura: `frontend.md`. Hooks: `hooks.md`. Idioma de la interfaz: español.

## Comunes — `components.tsx`

| Componente | Props | Qué muestra | Accesibilidad |
|------------|-------|-------------|---------------|
| `StatusBadge` | `status` | Estado de historia con su color de la paleta | texto siempre (`STATUS_LABEL`) |
| `SemaphoreBadge` | `value`, `large?` | Semáforo de gobernanza | símbolo + texto (✔ Verde, ▲ Ámbar, ✖ Rojo, ? Sin auditar) |
| `SeverityBadge` | `severity` | CRITICAL/WARNING/REVIEW/INFO | texto |
| `ProjectChip` | `projectId`, `all`, `link?` | Etiqueta con el color estable del proyecto | nombre visible |
| `Loading`, `ErrorBox`, `Empty` | — / `error` / `children` | Estados de carga, error (con código de ACM) y vacío | `role=status` / `role=alert` |
| `Markdown` | `text` | Markdown saneado (DOMPurify) | — |
| `Section` | `title`, `actions?` | Panel con título | `aria-label` = título (región navegable) |
| `Stat` | `label`, `value` | Cifra destacada | — |
| `StatusBar` | `counts` | Distribución de historias por estado | `role=img` con texto completo en `aria-label` |
| `fmtDate(iso)` | — | Fecha en formato local es-ES | — |

## Tablero — `KanbanBoard.tsx`

| Componente | Props | Comportamiento |
|------------|-------|----------------|
| `KanbanBoard` | `board` (`/kanban`), `allProjects` | Columnas por estado (US-06.01), búsqueda, mostrar/ocultar terminales, vista mezclada o un carril por proyecto (US-06.07). Arrastrar y soltar: cualquier columna acepta el `drop`; si la transición no está permitida, se rechaza con mensaje. Resalta 4 s las tarjetas cambiadas en vivo. Mensajes en `aria-live` |
| `KanbanCard` (interno) | tarjeta, transiciones | Franja de color del proyecto, id enlazado al detalle, texto, rol, nº de CA, feature; selector «Mover a…» (alternativa de teclado) |

## Páginas — `pages/`

| Página | Ruta | Contenido | Historias |
|--------|------|-----------|-----------|
| `Login` | (sin token) | Entrada con token (sessionStorage) | US-20.05 |
| `Dashboard` | `#/` | Cifras globales, tarjetas de proyecto, cambios en tiempo real, «Nuevo proyecto» (admin) | US-45.02, US-45.03, US-31.08, US-31.09 |
| `KanbanPage` | `#/kanban?projects=a,b` | Selección de proyectos (en la URL) + `KanbanBoard` | US-06.01, US-06.07 |
| `ProjectPage` | `#/p/:id/...` | Pestañas: Resumen, Backlog (árbol + formularios), Requisitos, Historias, Sprints, Kanban, Gobernanza (auditar, supervisor, hallazgos, histórico), Asistente, Miembros (gestión para owner/admin), Configuración (editable para owner/admin) | US-31.06, US-31.09..31.11, US-01.02 CA-03, US-13.10 |
| `StoryPage` | `#/p/:id/s/:story` | Enunciado, CA, trazabilidad, transiciones permitidas, historial, contexto compacto | US-06.06, US-06.02 |
| `ActivityPage` | `#/activity` (admin) | Herramientas en ejecución en vivo; auditoría filtrable; errores diferenciados | US-31.01/02/04, US-21.09 |
| `DocsPage` | `#/docs` | Skills renderizadas, flujo de estados, referencia de la API desde OpenAPI | US-31.06 CA-03 |
| `SystemPage` | `#/system` (admin) | Salud, modelos (`Models.tsx`), motores (comprobar), ahorro de tokens, principales (crear, rol), tokens (crear mostrando el secreto una vez, revocar) | US-13.03, US-35.09, US-31.11, US-31.12, US-50.09 |
| `BacklogForms` | (dentro de Backlog, Requisitos e Historia) | Requisito, épica, feature, historia, criterios, enlazar requisitos, confirmar cobertura, dividir feature | US-31.10 |
| `SprintsView` | `#/p/:id/sprints` | Crear, planificar, iniciar (sobrecarga), cerrar con traslado, cancelar, tablero del sprint, resumen | US-05.02..05.09 |
| `SupervisorPanel` | (en Gobernanza) | Informe, acciones aplicadas con «Deshacer», propuestas | US-13.14, US-13.15 |
| `AssistantView` | `#/p/:id/assistant` | Hilos y conversación con el modelo local; herramientas usadas | US-22.10, US-22.11 |
| `ModelsSection` | (en Sistema) | Modelos detectados, guía de Ollaya, elección de Ollama y de Ollaya por propósito, notas | US-50.09, US-22.06 |
