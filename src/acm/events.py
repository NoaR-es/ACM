"""Eventos de dominio de ACM (EPIC-21, ADR-018).

Cada cambio confirmado añade un evento a la tabla `events` de la base global, con un `seq` creciente. Lo hace el
dominio justo después del COMMIT (un cambio revertido no genera evento, US-21.01 CA-03), en cualquier proceso de ACM:
servidor HTTP, agente por stdio o CLI. El servidor HTTP lee los eventos nuevos por `seq` y los empuja a los clientes
WebSocket; un cliente que se reconecta pide los posteriores a su último `seq` (US-21.03).

Visibilidad: un evento de proyecto lo ven sus miembros (y los admin); uno sin proyecto o de tipo `activity`, solo los
admin. Si escribir el evento falla, la operación ya confirmada no se deshace; se registra en el log (TD-003).
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from acm.db.connection import Database

logger = logging.getLogger("acm.events")
ADMIN_ONLY_TYPES = frozenset({"activity"})
REPLAY_MAX = 1000


class EventStore:
    def __init__(self, db: Database):
        self.db = db

    def append(
        self,
        type: str,
        *,
        principal: str,
        entity_type: str,
        entity_id: str,
        project_id: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> int | None:
        try:
            with self.db.write() as conn:
                cur = conn.execute(
                    "INSERT INTO events(ts, type, project_id, principal, entity_type, entity_id, data_json) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        datetime.now(UTC).isoformat(),
                        type,
                        project_id,
                        principal,
                        entity_type,
                        entity_id,
                        json.dumps(data or {}, ensure_ascii=False, default=str),
                    ),
                )
                return int(cur.lastrowid)
        except Exception:  # la operación ya está confirmada: no se revierte por no poder avisar (TD-003)
            logger.exception("no se pudo registrar el evento %s de %s %s", type, entity_type, entity_id)
            return None

    def latest_seq(self) -> int:
        with self.db.read() as conn:
            return int(conn.execute("SELECT COALESCE(MAX(seq), 0) FROM events").fetchone()[0])

    def after(self, seq: int, limit: int = REPLAY_MAX) -> list[dict[str, Any]]:
        """Eventos con `seq` mayor que el dado, en orden (sin filtrar por visibilidad)."""
        with self.db.read() as conn:
            rows = conn.execute("SELECT * FROM events WHERE seq > ? ORDER BY seq LIMIT ?", (seq, limit)).fetchall()
        return [{**{k: r[k] for k in r.keys() if k != "data_json"}, "data": json.loads(r["data_json"])} for r in rows]

    def oldest_seq(self) -> int:
        with self.db.read() as conn:
            return int(conn.execute("SELECT COALESCE(MIN(seq), 0) FROM events").fetchone()[0])

    def prune(self, keep: int) -> int:
        """Conserva los `keep` eventos más recientes. Un cliente que se quedó atrás recibe `resync` (US-21.03)."""
        with self.db.write() as conn:
            cur = conn.execute("DELETE FROM events WHERE seq <= (SELECT MAX(seq) FROM events) - ?", (keep,))
            return cur.rowcount
