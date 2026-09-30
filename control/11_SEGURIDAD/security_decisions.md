# Decisiones de seguridad

| Decisión | Dónde | Resumen |
|----------|-------|---------|
| ADR-017 | `14_DECISIONES/decisions.md` | Tokens opacos propios validados en cada petición; stdio sigue siendo local |
| Escucha local por defecto | `config.py` (`DEFAULT_HOST`) | Exponer solo tras un proxy TLS (VULN-002) |
| No revelar proyectos ajenos | `ProjectService._project_role` | NOT_FOUND en lugar de FORBIDDEN |
| Redacción de secretos en auditoría | `AuditService.redact` | Claves `token`/`secret`/`password` |
