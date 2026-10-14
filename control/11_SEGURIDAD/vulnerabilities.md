# Vulnerabilidades y riesgos

| ID | Fecha | Descripción | Severidad | Mitigación | Estado |
|----|-------|-------------|-----------|------------|--------|
| VULN-001 | 2026-09-30 | El HTTP de ACM (`/mcp`, `/api`) no tenía autenticación: cualquiera que alcanzara el puerto actuaba como `ACM_PRINCIPAL` (admin). | ALTA si se expone | SPRINT-004 (ADR-017): `/mcp` exige un token de ACM en cada petición | RESOLVED (2026-09-30; `tests/test_auth.py`) |
| VULN-002 | 2026-09-30 | ACM no termina TLS: si se expone sin proxy, el token viaja en claro. | ALTA si se expone sin TLS | Escucha en 127.0.0.1 por defecto; exponer solo detrás de un proxy TLS (`README.md`) | OPEN (mitigado por configuración) |
| VULN-003 | 2026-09-30 | `/api/health` es público y revela versión, número de proyectos y PRAGMAs de SQLite. | BAJA | Información no sensible; necesario para comprobaciones de salud | ACCEPTED |
| VULN-004 | 2026-09-30 | La interfaz web muestra texto escrito por agentes (historias, skills en Markdown): un script inyectado podría robar el token de la sesión. | ALTA sin mitigación | Markdown saneado con DOMPurify (`markdown.test.ts`), React escapa el resto, CSP `script-src 'self'` en `/` (`test_webui.py::test_ui_sin_errores_de_consola_y_cabeceras_de_seguridad`). El token vive en sessionStorage (se borra al cerrar la pestaña) | MITIGATED (SPRINT-007, ADR-019) |
