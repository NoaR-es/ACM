"""Composición del proceso ACM (ADR-014): FastAPI con `/api` y el servidor MCP montado en `/mcp`."""

from __future__ import annotations

import contextlib
from collections.abc import AsyncIterator
from typing import Any

from fastapi import FastAPI

from acm import __version__
from acm.config import Settings
from acm.domain.errors import InvalidArgument
from acm.domain.projects import ProjectService
from acm.inference.ollama import OllamaClient, OllamaGenerationEngine
from acm.inference.router import EngineRouter
from acm.mcp_server import build_mcp_server


def build_service(settings: Settings) -> ProjectService:
    service = ProjectService(settings.data_dir, synchronous=settings.sqlite_synchronous)
    # SPRINT-001: el principal lo fija la configuración y se da de alta como admin si no existe (EPIC-20 lo sustituirá).
    service.ensure_principal(settings.principal, "admin")
    return service


def build_engines(service: ProjectService, settings: Settings) -> EngineRouter:
    """Router de inferencia: reglas siempre; Ollama si `ACM_OLLAMA_URL` y `ACM_OLLAMA_MODEL` están configurados."""
    engines = EngineRouter(service)
    if settings.ollama_url or settings.ollama_model:
        if not (settings.ollama_url and settings.ollama_model):
            raise InvalidArgument("ACM_OLLAMA_URL y ACM_OLLAMA_MODEL deben configurarse juntos", field="ollama")
        engines.registry.register(OllamaGenerationEngine(OllamaClient(settings.ollama_url), settings.ollama_model))
    return engines


def create_app(settings: Settings) -> FastAPI:
    service = build_service(settings)
    engines = build_engines(service, settings)
    mcp = build_mcp_server(service, principal=lambda: settings.principal, engines=engines)
    mcp_app = mcp.streamable_http_app(streamable_http_path="/")

    @contextlib.asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        # El sub-app MCP montado no ejecuta su propio lifespan: el gestor de sesiones se arranca aquí (SPIKE-002).
        async with mcp.session_manager.run():
            yield
        engines.registry.close()
        service.close()

    app = FastAPI(title="ACM", version=__version__, lifespan=lifespan)

    @app.get("/api/health")
    def health() -> dict[str, Any]:
        """Salud básica: versión y PRAGMAs de la base global (ADR-013: foreign_keys activo)."""
        info = service.system_info()
        ok = info["sqlite"]["foreign_keys"] and str(info["sqlite"]["journal_mode"]).lower() == "wal"
        return {"status": "ok" if ok else "degraded", "acm_version": __version__, **info}

    app.mount("/mcp", mcp_app)
    app.state.service = service
    return app
