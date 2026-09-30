# Networking

**Estado del área:** ACTIVE (SPRINT-007). Escucha en `ACM_HOST:ACM_PORT` (por defecto `127.0.0.1:8765`). Rutas: `/` interfaz, `/api/health`, `/api/v1` (REST + WS `/api/v1/ws`), `/mcp`. La CSP de la interfaz limita las conexiones al mismo host (ADR-019). Host distinto → 421 salvo `ACM_ALLOWED_HOSTS`.
