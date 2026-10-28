# Secretos

| Secreto | Dónde vive | Protección |
|---------|------------|------------|
| Tokens de ACM | `api_tokens.secret_hash` (sha256) + `prefix` (12 caracteres) | El secreto se muestra solo en la respuesta de creación; nunca se guarda en claro; `AuditService` redacta las claves `token`, `secret` y `password` en argumentos y resultados |
| Clave de Ollaya (`ACM_JEV_API_KEY`) | Solo en la variable de entorno del proceso (ADR-021) | Nunca se guarda en `inference_settings` ni en otra tabla, no se devuelve en ninguna respuesta y no se muestra en la interfaz; las URL de los servidores tampoco se pueden cambiar desde la API |
| Ollama | Sin credencial (local) | — |
| Token de la interfaz local (`ui-local`) | Solo en la memoria del proceso `acm serve --local`; en la base solo su hash | Efímero: cada arranque revoca el anterior; se entrega únicamente por `/api/local-session` a este equipo (ver `vulnerabilities.md`) |

Verificado: el secreto no aparece en `acm.db` ni en la auditoría (`tests/test_auth.py::test_us2003_ca03_*`).
