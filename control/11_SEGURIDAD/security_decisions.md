# Decisiones de seguridad

| Decisión | Dónde | Resumen |
|----------|-------|---------|
| ADR-017 | `14_DECISIONES/decisions.md` | Tokens opacos propios validados en cada petición; stdio sigue siendo local |
| Escucha local por defecto | `config.py` (`DEFAULT_HOST`) | Exponer solo tras un proxy TLS (VULN-002) |
| No revelar proyectos ajenos | `ProjectService._project_role` | NOT_FOUND en lugar de FORBIDDEN |
| Redacción de secretos en auditoría | `AuditService.redact` | Claves `token`/`secret`/`password` |
| CSP y cabeceras de la interfaz | `webui_app.SecureStatic` (ADR-019) | Solo scripts propios; conexiones al mismo host; sin incrustar (`frame-ancestors 'none'`); `nosniff`; `no-referrer` |
| Token del navegador en sessionStorage | `web/src/api.ts` (`tokenStore`) | No persiste al cerrar la pestaña; no se usa cookie (sin CSRF) |
