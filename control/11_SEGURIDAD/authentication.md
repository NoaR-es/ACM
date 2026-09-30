# Autenticación (ADR-017, SPRINT-004)

| Canal | Mecanismo | Identidad |
|-------|-----------|-----------|
| HTTP `/mcp` | `Authorization: Bearer acm_…` validado en cada petición por `acm.auth.BearerAuth` | Principal dueño del token |
| HTTP `/api/health` | Público | — (solo salud, versión y PRAGMAs; VULN-003) |
| stdio (`acm mcp-stdio`) | Proceso local | `ACM_PRINCIPAL` |
| CLI (`acm principal`, `acm token`) | Acceso local a los datos | `ACM_PRINCIPAL` (admin local) |

- **Rechazo:** HTTP 401, `{"error": "UNAUTHENTICATED: …"}`, `WWW-Authenticate: Bearer realm="acm"`. La petición no llega al servidor MCP y se audita como `http:auth` con solo el prefijo del token.
- **Revocación:** inmediata; la siguiente petición ya recibe 401.
- **Verificado** con ACM real por HTTP (`tests/test_auth.py`) y con 8 mutaciones.
- **Pendiente:** expiración de tokens; SSO/OAuth.
