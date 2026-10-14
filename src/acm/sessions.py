"""Identidad de los agentes locales: quién es y qué sesión es (ADR-023).

Dos cosas distintas, a propósito:

- **Principal** (permisos): se deduce del cliente MCP y del equipo, `<cliente>.<equipo>` (p. ej.
  `claude-code.portatil`), o es el nombre fijado en `ACM_AGENT`. Se aprueba una vez para un proyecto y vale para todas
  sus sesiones.
- **Sesión** (trabajo): una por conexión (`3f9a`). El reparto de trabajo y la actividad la usan para que dos sesiones
  del mismo cliente, en el mismo equipo o en equipos que comparten un servidor, no se confundan.

Un principal con `ACM_PRINCIPAL` explícito conserva el comportamiento anterior de stdio: una única identidad admin.
"""

from __future__ import annotations

import contextvars
import re
import secrets
import socket

# Nombre que declara el cliente MCP al conectarse (`clientInfo.name`) y sesión de la conexión en curso.
current_client: contextvars.ContextVar[str | None] = contextvars.ContextVar("acm_mcp_client", default=None)
current_session: contextvars.ContextVar[str] = contextvars.ContextVar("acm_session", default="")

# Un proceso stdio atiende una sola conexión: su sesión es fija durante toda su vida.
PROCESS_SESSION = secrets.token_hex(2)

_INVALID = re.compile(r"[^a-z0-9._-]+")


def _slug(text: str) -> str:
    return _INVALID.sub("-", text.lower()).strip("-._") or "agente"


def agent_principal(client: str | None, host: str | None = None) -> str:
    """`<cliente>.<equipo>` válido como identificador de principal (^[a-z0-9][a-z0-9._-]{1,63}$)."""
    host = host if host is not None else socket.gethostname().split(".")[0]
    name = f"{_slug(client or 'agente')}.{_slug(host)}"
    return name[:64].strip("-._") or "agente"


def session_id() -> str:
    """Sesión de la conexión en curso; vacía fuera de una conexión MCP (REST, interfaz, tests)."""
    return current_session.get()
