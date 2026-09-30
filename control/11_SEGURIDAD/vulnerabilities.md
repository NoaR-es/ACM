# Vulnerabilidades y riesgos

| ID | Fecha | Descripción | Severidad | Mitigación | Estado |
|----|-------|-------------|-----------|------------|--------|
| VULN-001 | 2026-09-30 | El HTTP de ACM (`/mcp`, `/api`) no tenía autenticación: cualquiera que alcanzara el puerto actuaba como `ACM_PRINCIPAL` (admin). | ALTA si se expone | SPRINT-004 (ADR-017): `/mcp` exige un token de ACM en cada petición | RESOLVED (2026-09-30; `tests/test_auth.py`) |
| VULN-002 | 2026-09-30 | ACM no termina TLS: si se expone sin proxy, el token viaja en claro. | ALTA si se expone sin TLS | Escucha en 127.0.0.1 por defecto; exponer solo detrás de un proxy TLS (`README.md`) | OPEN (mitigado por configuración) |
| VULN-003 | 2026-09-30 | `/api/health` es público y revela versión, número de proyectos y PRAGMAs de SQLite. | BAJA | Información no sensible; necesario para comprobaciones de salud | ACCEPTED |
