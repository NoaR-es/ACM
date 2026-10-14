"""Auditoría de invocaciones MCP (US-14.10, US-14.11; US-15.07 CA-03 para descargas de skills).

Cada invocación registra principal, operación, proyecto, argumentos, resultado (truncado), estado y duración en
la base global. Se registra también el intento de un principal desconocido (sin clave foránea a `principals`).
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

from acm.domain.errors import Forbidden, InvalidArgument
from acm.domain.projects import ProjectService

RESULT_MAX_CHARS = 4000
LIST_MAX = 500


SECRET_KEYS = frozenset({"token", "secret", "password"})
REDACTED = "[REDACTED]"


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, default=str, sort_keys=True)


def redact(value: Any) -> Any:
    """Sustituye el valor de las claves secretas (p. ej. el token recién creado) antes de auditar (ADR-017)."""
    if isinstance(value, dict):
        return {k: REDACTED if k in SECRET_KEYS else redact(v) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(v) for v in value]
    return value


class AuditService:
    def __init__(self, projects: ProjectService):
        self.projects = projects

    def record(
        self,
        *,
        principal: str,
        operation: str,
        arguments: dict[str, Any],
        status: str,
        duration_ms: float,
        result: Any = None,
        error: str = "",
        token_id: str | None = None,
    ) -> None:
        arguments = redact(arguments)
        result_json = "" if result is None else _json(redact(result))
        truncated = len(result_json) > RESULT_MAX_CHARS
        project_id = arguments.get("project_id") if isinstance(arguments.get("project_id"), str) else None
        with self.projects.global_db.write() as conn:
            conn.execute(
                "INSERT INTO mcp_audit(ts, principal, operation, project_id, arguments_json, status, error, "
                "result_json, result_truncated, duration_ms, token_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    datetime.now(UTC).isoformat(),
                    principal,
                    operation,
                    project_id,
                    _json(arguments),
                    status,
                    error,
                    result_json[:RESULT_MAX_CHARS],
                    int(truncated),
                    round(duration_ms, 3),
                    token_id,
                ),
            )

    def list(
        self,
        principal: str,
        *,
        limit: Any = 50,
        filter_principal: Any = None,
        operation: Any = None,
        project_id: Any = None,
    ) -> dict[str, Any]:
        """US-14.10: el operador consulta qué invocó cada agente. Solo principales con rol global admin."""
        with self.projects.global_db.read() as conn:
            if self.projects._principal_role(conn, principal) != "admin":
                raise Forbidden("solo un admin puede consultar la auditoría")
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= LIST_MAX:
            raise InvalidArgument(f"debe ser un entero entre 1 y {LIST_MAX}", field="limit")
        clauses, args = [], []
        for column, value, field in (
            ("principal", filter_principal, "principal"),
            ("operation", operation, "operation"),
            ("project_id", project_id, "project_id"),
        ):
            if value is not None:
                if not isinstance(value, str):
                    raise InvalidArgument("debe ser texto", field=field)
                clauses.append(f"{column} = ?")
                args.append(value)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with self.projects.global_db.read() as conn:
            rows = conn.execute(f"SELECT * FROM mcp_audit {where} ORDER BY id DESC LIMIT ?", (*args, limit)).fetchall()
        entries = []
        for r in rows:
            e = dict(r)
            e["arguments"] = json.loads(e.pop("arguments_json"))
            e["result_truncated"] = bool(e["result_truncated"])
            entries.append(e)
        return {"entries": entries}
