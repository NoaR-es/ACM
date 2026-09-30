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
| `Dashboard` | `#/` | Cifras globales, tarjetas de proyecto (semáforo, barra de estados, integridad), cambios en tiempo real | US-45.02, US-45.03, US-31.08 |
| `KanbanPage` | `#/kanban?projects=a,b` | Selección de proyectos (en la URL) + `KanbanBoard` | US-06.01, US-06.07 |
| `ProjectPage` | `#/p/:id/...` | Pestañas: Resumen (cifras, huecos), Backlog (árbol), Requisitos (traza), Historias (filtros), Kanban, Gobernanza (auditar, hallazgos, histórico), Miembros, Configuración | US-31.06, US-01.02 CA-03, US-13.10 |
| `StoryPage` | `#/p/:id/s/:story` | Enunciado, CA, trazabilidad, transiciones permitidas, historial, contexto compacto | US-06.06, US-06.02 |
| `ActivityPage` | `#/activity` (admin) | Herramientas en ejecución en vivo; auditoría filtrable; errores diferenciados | US-31.01/02/04, US-21.09 |
| `DocsPage` | `#/docs` | Skills renderizadas, flujo de estados, referencia de la API desde OpenAPI | US-31.06 CA-03 |
| `SystemPage` | `#/system` (admin) | Salud por componente, motores, ahorro de tokens, principales, tokens (sin secreto) | US-13.03, US-35.09 |
