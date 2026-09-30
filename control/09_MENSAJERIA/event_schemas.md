# Esquemas de eventos y protocolo WebSocket (SPRINT-006)

Evento:
```json
{"seq": 42, "ts": "2026-09-30T12:00:00+00:00", "type": "story.status_changed", "project_id": "alpha",
 "principal": "bot-1", "entity_type": "story", "entity_id": "US-01.02",
 "data": {"status": "IN_PROGRESS", "from": "READY", "feature_id": "FEAT-01.01", "epic_id": "EPIC-01",
          "i_want": "…", "kind": "user_story"}}
```

WebSocket `/api/v1/ws`:
1. Cliente → `{"type": "auth", "token": "acm_…", "after": 41 | null}` (en 10 s como máximo).
2. Servidor → `{"type": "ready", "principal": "…", "seq": <punto de partida>, "latest_seq": <último>}`.
   - Si `after` es inválido o sus eventos ya se purgaron, antes envía `{"type": "resync", "reason": "…"}`.
3. Servidor → `{"type": "event", "event": {…}}` por cada evento visible, en orden de `seq`.
4. Autenticación fallida → `{"type": "error", "error": "UNAUTHENTICATED: …"}` y cierre con código 4401.
