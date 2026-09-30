# Seguridad — estado (2026-09-30)

| Área | Estado | Detalle |
|------|--------|---------|
| Autenticación | MISSING | EPIC-20. En SPRINT-001 la identidad es `ACM_PRINCIPAL` (configuración del proceso). |
| Autorización | IMPLEMENTED (mínima) | Rol global `admin`/`user`; pertenencia `owner`/`member` por proyecto. Crear: admin. Modificar configuración: owner o admin. Proyectos ajenos → NOT_FOUND (no se revela su existencia). |
| Exposición de red | Mitigado | `acm serve` escucha en 127.0.0.1 por defecto (VULN-001). |
| Integridad de datos | IMPLEMENTED | `foreign_keys=ON` verificado por conexión; transacciones IMMEDIATE; creación atómica. |
| Secretos | N/A | No hay secretos todavía. |
