"""Servidor MCP propio de ACM (ADR-008, ADR-014).

- Sin estado de sesión: toda herramienta de proyecto exige `project_id` y lo devuelve (US-01.06).
- Los errores de dominio llegan al agente como `ToolError("<CODE>: <motivo>")` (GAP-007).
- El servicio es síncrono (sqlite3): cada llamada se ejecuta en un hilo de trabajo (ADR-013).
"""

from __future__ import annotations

from collections.abc import Callable
from functools import partial
from typing import Any, TypeVar

import anyio
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from acm import __version__
from acm.domain.errors import AcmError
from acm.domain.projects import ProjectService

T = TypeVar("T")

INSTRUCTIONS = (
    "Estás conectado a ACM (Agile Context Manager), la memoria de estado y gobernanza de tus proyectos.\n"
    "- ACM no recuerda un 'proyecto activo': pasa SIEMPRE el parámetro project_id en cada herramienta de proyecto.\n"
    "- Obtén los project_id disponibles con acm_project_list; crea uno nuevo con acm_project_create.\n"
    "- Cada respuesta repite el project_id sobre el que actuó: compruébalo.\n"
    "- Los errores empiezan por un código (INVALID_ARGUMENT, NOT_FOUND, ALREADY_EXISTS, FORBIDDEN, STORAGE_ERROR) "
    "seguido del motivo; corrige la llamada según el motivo."
)


def build_mcp_server(service: ProjectService, principal: Callable[[], str]) -> MCPServer:
    """Crea el servidor MCP.

    `principal` resuelve la identidad del llamante (SPRINT-001: configuración; EPIC-20: token verificado).
    """
    server = MCPServer(name="acm", version=__version__, instructions=INSTRUCTIONS)

    async def call(fn: Callable[..., T], *args: Any) -> T:
        try:
            return await anyio.to_thread.run_sync(partial(fn, *args))
        except AcmError as exc:
            raise ToolError(str(exc)) from exc

    @server.tool()
    async def acm_project_create(key: str, name: str, description: str = "") -> dict[str, Any]:
        """Crea un proyecto ACM con su propia base SQLite. `key` es el project_id: ^[a-z][a-z0-9-]{1,39}$."""
        return await call(service.create, principal(), key, name, description)

    @server.tool()
    async def acm_project_list() -> list[dict[str, Any]]:
        """Lista los proyectos a los que tienes acceso (con su project_id)."""
        return await call(service.list_for, principal())

    @server.tool()
    async def acm_project_open(project_id: str) -> dict[str, Any]:
        """Abre un proyecto: devuelve metadatos, tu rol, versión de esquema y configuración efectiva."""
        return await call(service.open, principal(), project_id)

    @server.tool()
    async def acm_project_config_get(project_id: str) -> dict[str, Any]:
        """Devuelve cada parámetro de configuración del proyecto con su valor actual, por defecto y permitido."""
        return await call(service.get_config, principal(), project_id)

    @server.tool()
    async def acm_project_config_set(project_id: str, changes: dict[str, Any]) -> dict[str, Any]:
        """Modifica parámetros ({parámetro: valor}). Valida todo antes de guardar; indica cuáles requieren recarga."""
        return await call(service.set_config, principal(), project_id, changes)

    @server.tool()
    async def acm_system_info() -> dict[str, Any]:
        """Estado de la plataforma: versión, versión del esquema global, nº de proyectos y PRAGMAs de SQLite."""
        info = await call(service.system_info)
        return {"acm_version": __version__, **info}

    return server
