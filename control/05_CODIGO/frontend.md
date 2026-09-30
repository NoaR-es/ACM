# Interfaz web — arquitectura del código (`web/`)

Actualizado: 2026-09-30 (SPRINT-007). Decisión: ADR-019. Componentes: `components.md`. Hooks: `hooks.md`.

## Pila
React 19 + TypeScript 7 (estricto) + Vite 8; `@tanstack/react-query` (caché e invalidación), `react-router-dom` (HashRouter), `marked` + `dompurify` (Markdown seguro); vitest + jsdom para tests unitarios. Versiones fijadas: `dependencies.md`.

## Arranque y proveedores (`main.tsx`)
```text
QueryClientProvider (staleTime 30 s, refresco de seguridad 120 s)
└── PrefsProvider (tema)
    └── AuthProvider (token + /me)
        └── LiveProvider (WebSocket)
            └── HashRouter → App (cabecera + rutas)
```
HashRouter: las rutas de la interfaz van tras `#`, así no chocan con `/api` ni `/mcp` y FastAPI no necesita reglas de reescritura.

## Flujo de datos
1. **Lectura:** cada página pide sus datos por REST (`api.ts`) mediante `useQuery` con claves estables.
2. **Mutación:** botones y el Kanban llaman a `POST /api/v1/...` (`useMutation`) e invalidan sus claves.
3. **Tiempo real:** `LiveProvider` recibe eventos por `/api/v1/ws`. Por cada evento nuevo (por `seq`), invalida las claves afectadas y react-query recarga solo esos datos. Guarda los últimos 300 eventos para los feeds, marca las entidades cambiadas (resaltado en el Kanban) y anuncia el cambio por `aria-live`.
4. **Reconexión:** backoff exponencial (0,5 s … 10 s). Al reconectar envía `after` = último `seq` y aplica lo perdido; si recibe `resync`, invalida todo.
5. **Sesión:** un 401 de la API o un cierre 4401 del WebSocket cierran la sesión.

## Tema y accesibilidad
- `theme.ts` es la **única** fuente de colores. `PrefsProvider` los aplica como variables CSS y `styles.css` solo usa variables.
- `theme.test.ts` verifica el contraste AA de toda la paleta (texto ≥ 4.5:1; franjas y semáforo ≥ 3:1). `test_webui.py::test_us3107_ca01_*` lo mide sobre la página renderizada en ambos temas.
- El estado nunca va solo en color: texto en los badges y símbolos en el semáforo.
- Hay alternativa de teclado al arrastrar («Mover a…»), foco visible, enlace «Saltar al contenido» y `prefers-reduced-motion`.

## Build y servicio
- `npm run build` = `tsc --noEmit` + `vite build` → `src/acm/webui/` (versionado en Git: `pip install` basta, sin Node).
- La CI comprueba que el bundle versionado coincide con el código (`git diff --exit-code`); el build es reproducible byte a byte (verificado desde otra ruta con `npm ci`).
- FastAPI lo sirve en `/` con `SecureStatic` (`webui_app.py`) y cabeceras de seguridad. En desarrollo, `npm run dev` hace de proxy de `/api` (incluido el WebSocket) hacia `127.0.0.1:8765`.

## Seguridad en el cliente
El token está en `sessionStorage` (se borra al cerrar la pestaña). El Markdown se sanea con DOMPurify. La CSP (`script-src 'self'`) impide ejecutar scripts inyectados. La interfaz solo muestra lo que la API autoriza; ocultar enlaces de admin es comodidad, no seguridad.

## Cómo añadir una vista
1. Página en `pages/` y ruta en `App.tsx`.
2. Tipos en `types.ts`.
3. Si depende de eventos, su clave en `liveCore.affectedKeys` (con test).
4. Test e2e en `tests/test_webui.py`.
5. Fila en `file_inventory.md` (lo exige `code_inventory --check`) y entrada en `components.md`.
