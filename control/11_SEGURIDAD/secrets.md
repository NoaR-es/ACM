# Secretos

| Secreto | Dónde vive | Protección |
|---------|------------|------------|
| Tokens de ACM | `api_tokens.secret_hash` (sha256) + `prefix` (12 caracteres) | El secreto se muestra solo en la respuesta de creación; nunca se guarda en claro; `AuditService` redacta las claves `token`, `secret` y `password` en argumentos y resultados |
| Credenciales de proveedores de IA | No hay (Ollama local sin credencial) | Llegarán con EPIC-50 (TypeSafe) |

Verificado: el secreto no aparece en `acm.db` ni en la auditoría (`tests/test_auth.py::test_us2003_ca03_*`).
