# Dependencias del código (versiones fijadas)

Actualizado: 2026-09-30 (SPRINT-007). Dependencias entre componentes: `04_ARQUITECTURA/dependencies.md`.

## Python (`pyproject.toml`)
| Paquete | Versión | Para qué | Decisión |
|---------|---------|----------|----------|
| mcp | 2.2.0 | Servidor MCP propio y extensión Skills | ADR-008, ADR-014 |
| fastapi | 0.142.2 | API HTTP, REST v1, WebSocket, servir la interfaz | ADR-014 |
| uvicorn | 0.54.0 | Servidor ASGI | ADR-014 |
| anyio | ≥4.15,<5 | Hilos de trabajo para sqlite3, tareas de fondo | ADR-013 |
| httpx | 0.28.1 | Cliente HTTP de Ollama | EPIC-22 |
| websockets | 17.1 | Implementación WebSocket de uvicorn | ADR-018 |
| *dev:* pytest | 9.1.1 | Tests | — |
| *dev:* ruff | 0.16.9 | Lint y formato | — |
| *dev:* playwright | 1.63.0 | e2e de la interfaz (Chromium) | ADR-019 |

## Frontend (`web/package.json`, lockfile `package-lock.json`)
| Paquete | Versión | Para qué |
|---------|---------|----------|
| react, react-dom | 19.3.0 | Interfaz |
| react-router-dom | 7.18.4 | Rutas (HashRouter) |
| @tanstack/react-query | 5.104.0 | Caché, invalidación por eventos |
| marked | 18.0.14 | Markdown de skills |
| dompurify | 3.4.16 | Saneado del Markdown (XSS) |
| *dev:* typescript | 7.0.2 | Tipos (`tsc --noEmit`) |
| *dev:* vite, @vitejs/plugin-react | 8.3.1, 6.1.1 | Build reproducible |
| *dev:* vitest, jsdom | 5.0.3, 30.1.1 | Tests unitarios |
| *dev:* @types/react, @types/react-dom | 19.3.0 | Tipos de React |

Dependencias no usadas: ninguna detectada (revisión manual en SPRINT-007; `dead_code.md`).
