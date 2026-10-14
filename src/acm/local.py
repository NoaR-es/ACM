"""Modo local de ACM (ADR-023): un agente conectado por stdio sin instalar ni configurar nada más.

- `local_principal`: identidad de cada agente. Se deduce de su cliente MCP y de este equipo (`sessions.agent_principal`)
  o de `ACM_AGENT`; se da de alta como agente no admin la primera vez. Quien aprueba su acceso a un proyecto es una
  persona, desde la interfaz.
- `start_local_ui`: levanta `acm serve --local` en un proceso aparte (interfaz, REST, Watchdog y supervisor) si no hay
  ya uno en el puerto. El proceso sobrevive al agente que lo arrancó y sigue hasta que se pare (`acm stop`). Los
  agentes siguen funcionando sin él.
- `local_session`: la interfaz de este equipo entra sin pegar token (US-14.12 CA-04). El navegador pide un token efímero
  a `/api/local-session`, que solo responde a una petición de este equipo con la cabecera `X-ACM-Local` (un sitio web
  ajeno no puede enviarla sin permiso previo del navegador) y un nombre de servidor local (contra DNS rebinding).
"""

from __future__ import annotations

import logging
import os
import signal
import socket
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

from acm.config import Settings
from acm.domain.projects import ProjectService
from acm.sessions import _slug, agent_principal, current_client

logger = logging.getLogger("acm")
LOCAL_SESSION_NAME = "ui-local"
LOCAL_HOST_HEADERS = ("127.0.0.1", "localhost", "[::1]")


def local_principal(service: ProjectService, settings: Settings) -> Callable[[], str]:
    """Principal del agente que habla por esta conexión; se crea al usarlo por primera vez."""
    known: set[str] = set()
    fixed = _slug(settings.agent) if settings.agent else None

    def resolve() -> str:
        name = fixed or agent_principal(current_client.get())
        if name not in known:
            service.ensure_principal(name, "user", "agent")
            known.add(name)
        return name

    return resolve


def port_in_use(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.3)
        return s.connect_ex((host, port)) == 0


def start_local_ui(settings: Settings) -> bool:
    """Arranca la interfaz local en segundo plano. Devuelve True si lanzó un proceso nuevo.

    Si el puerto ya está ocupado se da por hecho que es ACM (otro agente la arrancó antes). Dos agentes que arrancan
    a la vez pueden lanzar dos procesos: el segundo no consigue el puerto y termina solo.
    """
    if port_in_use("127.0.0.1", settings.port):
        return False
    command = [sys.executable, "-m", "acm", "serve", "--local", "--data-dir", str(settings.data_dir)]
    command += ["--host", "127.0.0.1", "--port", str(settings.port)]
    try:
        subprocess.Popen(  # noqa: S603 - comando propio, sin entrada externa
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,  # sobrevive al agente que lo arrancó
            close_fds=True,
        )
    except OSError:
        logger.exception("no se pudo arrancar la interfaz local; los agentes siguen funcionando sin ella")
        return False
    return True


def _host_name(host_header: str) -> str:
    if host_header.startswith("["):  # IPv6 literal: [::1]:8765
        return host_header[: host_header.find("]") + 1]
    return host_header.rsplit(":", 1)[0] if ":" in host_header else host_header


def is_local_request(client_host: str | None, host_header: str, marker: str | None) -> bool:
    """¿La petición viene de este equipo, a un nombre local y con la cabecera propia de la interfaz?"""
    return client_host in ("127.0.0.1", "::1") and _host_name(host_header) in LOCAL_HOST_HEADERS and marker == "1"


def pid_file(settings: Settings) -> Path:
    return settings.data_dir / "ui.pid"


def write_pid(settings: Settings) -> None:
    pid_file(settings).write_text(str(os.getpid()), encoding="utf-8")


def stop_local_ui(settings: Settings) -> str:
    """`acm stop`: para la interfaz local que arrancó un agente. Devuelve lo que hizo, para mostrarlo."""
    path = pid_file(settings)
    try:
        pid = int(path.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return "No hay ninguna interfaz local de ACM en marcha."
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        path.unlink(missing_ok=True)
        return "La interfaz local ya no estaba en marcha."
    path.unlink(missing_ok=True)
    return f"Interfaz local de ACM parada (proceso {pid})."
