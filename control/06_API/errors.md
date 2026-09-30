# Errors

**Estado del área:** ACTIVE (SPRINT-006/007).

Formato REST único: `{"error": {"code", "message", "field"}}` (`web_api.py`). En MCP el mismo código va en el texto del `ToolError` (`CODE: [campo: ]motivo`).

| Código | HTTP | Cuándo |
|--------|------|--------|
| `INVALID_ARGUMENT` | 400 | argumento inválido (también la validación de FastAPI) |
| `UNAUTHENTICATED` | 401 | sin token o token inválido/revocado |
| `FORBIDDEN` | 403 | rol insuficiente |
| `NOT_FOUND` | 404 | no existe o no es accesible (no se revela la existencia) |
| `ALREADY_EXISTS`, `FAILED_PRECONDITION`, `DATA_INTEGRITY` | 409 | conflicto, transición no permitida, base dañada o en cuarentena |
| `ENGINE_ERROR` / `ENGINE_UNAVAILABLE` | 502 / 503 | motor de inferencia |
| otros (`STORAGE_ERROR`, `MIGRATION_ERROR`) | 500 | fallo interno |

Fuente: `HTTP_STATUS` en `src/acm/web_api.py`; tests: `tests/test_realtime.py` (formato consistente).
