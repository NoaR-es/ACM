"""Composición del proceso ACM (ADR-014): FastAPI con `/api` y el servidor MCP montado en `/mcp`.

`/mcp` exige un token Bearer de ACM (ADR-017). `/api/health` es público: solo informa de salud y versión.
"""

from __future__ import annotations

import contextlib
from collections.abc import AsyncIterator
from typing import Any

from fastapi import FastAPI
from mcp.server.transport_security import TransportSecuritySettings

from acm import __version__
from acm.auth import BearerAuth, request_principal, request_token
from acm.config import Settings
from acm.domain.audit import AuditService
from acm.domain.errors import InvalidArgument
from acm.domain.identity import IdentityService
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


LOCAL_HOSTS = ("127.0.0.1", "localhost", "[::1]")


def transport_security(settings: Settings) -> TransportSecuritySettings:
    """Protección contra DNS rebinding del SDK MCP: solo se aceptan los Host locales y los de `ACM_ALLOWED_HOSTS`.

    Sin esta configuración, el SDK solo admite Host locales y ACM respondía 421 al servirse con otro nombre (TD-002).
    """
    hosts = [f"{h}:*" for h in LOCAL_HOSTS] + [h for extra in settings.allowed_hosts for h in (extra, f"{extra}:*")]
    origins = [f"http://{h}:*" for h in LOCAL_HOSTS] + [
        f"{scheme}://{extra}" for extra in settings.allowed_hosts for scheme in ("https", "http")
    ]
    return TransportSecuritySettings(enable_dns_rebinding_protection=True, allowed_hosts=hosts, allowed_origins=origins)


def create_app(settings: Settings) -> FastAPI:
    service = build_service(settings)
    engines = build_engines(service, settings)
    # HTTP: la identidad sale del token Bearer de cada petición (EPIC-20, ADR-017), nunca de la configuración.
    mcp = build_mcp_server(service, principal=request_principal, engines=engines, token_id=request_token)
    mcp_app = BearerAuth(
        mcp.streamable_http_app(streamable_http_path="/", transport_security=transport_security(settings)),
        IdentityService(service),
        AuditService(service),
    )

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
