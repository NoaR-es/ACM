# Seguridad — estado (2026-09-30, SPRINT-007)

| Área | Estado | Detalle |
|------|--------|---------|
| Autenticación | IMPLEMENTED (VERIFIED) | HTTP: token Bearer de ACM en cada petición (ADR-017, `authentication.md`). stdio: `ACM_PRINCIPAL` (local). |
| Autorización | IMPLEMENTED (VERIFIED) | Roles globales `admin`/`user` y de proyecto `owner`/`member` (`authorization.md`, `permissions.md`). Proyectos ajenos → NOT_FOUND. |
| Secretos | IMPLEMENTED | Tokens: solo hash sha256 y prefijo; redactados en la auditoría (`secrets.md`). |
| Auditoría | IMPLEMENTED | Toda invocación MCP y todo intento rechazado (incluidos los 401) en `mcp_audit`, con `token_id`. Retención: MISSING (EPIC-44). |
| Exposición de red | WARNING | Escucha en 127.0.0.1 por defecto. Para exponer: proxy TLS + `ACM_ALLOWED_HOSTS` (VULN-002). |
| Interfaz web | IMPLEMENTED (VERIFIED) | CSP estricta, `nosniff`, `no-referrer`, `DENY`; Markdown saneado; token en sessionStorage (ADR-019, VULN-004). |
| Integridad de datos | IMPLEMENTED | `foreign_keys=ON` por conexión; transacciones IMMEDIATE; creación atómica. |
