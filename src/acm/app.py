"""Composición del proceso ACM (ADR-014): FastAPI con `/api` y el servidor MCP montado en `/mcp`.

`/mcp` exige un token Bearer de ACM (ADR-017). `/api/health` es público: solo informa de salud y versión.
"""

from __future__ import annotations

import contextlib
import logging
from collections.abc import AsyncIterator
from typing import Any

import anyio
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from mcp.server.transport_security import TransportSecuritySettings

from acm import __version__
from acm.auth import BearerAuth, request_principal, request_token
from acm.config import Settings
from acm.domain.audit import AuditService
from acm.domain.backlog import BacklogService
from acm.domain.errors import InvalidArgument
from acm.domain.identity import IdentityService
from acm.domain.projects import ProjectService
from acm.domain.watchdog import WatchdogService
from acm.inference.jev import JevDecisionEngine, OllayaClient
from acm.inference.ollama import OllamaClient, OllamaDecisionEngine, OllamaGenerationEngine
from acm.inference.router import EngineRouter
from acm.inference.selection import ModelSelection
from acm.local import LOCAL_SESSION_NAME, is_local_request, write_pid
from acm.mcp_server import build_mcp_server
from acm.skills_catalog import SkillCatalog
from acm.web_api import build_api
from acm.webui_app import SecureStatic, webui_available


def build_service(settings: Settings) -> ProjectService:
    service = ProjectService(settings.data_dir, synchronous=settings.sqlite_synchronous, local_mode=settings.local_mode)
    # SPRINT-001: el principal lo fija la configuración y se da de alta como admin si no existe (EPIC-20 lo sustituirá).
    service.ensure_principal(settings.principal, "admin")
    return service


def build_engines(service: ProjectService, settings: Settings) -> EngineRouter:
    """Router de inferencia (ADR-015). Reglas siempre. JEV (Ollaya) si hay `ACM_JEV_URL`: decisiones calibradas.
    Ollama si hay `ACM_OLLAMA_URL`: resume el contexto, conversa (agente interno) y decide sin calibrar.

    Los modelos se eligen en ACM (US-50.09: Sistema → Modelos o `acm_models_select`) entre los que detecta cada runtime;
    `ACM_OLLAMA_MODEL` y `ACM_JEV_MODEL` solo dan el valor inicial. Qué motor decide primero lo fija cada proyecto
    (`decision.engine_order`, por defecto reglas → JEV → Ollama).
    """
    if settings.jev_model and not settings.jev_url:
        raise InvalidArgument("ACM_JEV_MODEL necesita ACM_JEV_URL", field="jev")
    if settings.ollama_model and not settings.ollama_url:
        raise InvalidArgument("ACM_OLLAMA_MODEL necesita ACM_OLLAMA_URL", field="ollama")
    engines = EngineRouter(service)
    selection = ModelSelection(service, ollama_model=settings.ollama_model, jev_model=settings.jev_model)
    engines.selection = selection
    if settings.jev_url:
        client = OllayaClient(settings.jev_url, api_key=settings.jev_api_key)
        engines.registry.register(JevDecisionEngine(client, selection.jev_model))
    if settings.ollama_url:
        engines.registry.register(OllamaGenerationEngine(OllamaClient(settings.ollama_url), selection.ollama_model))
        engines.registry.register(OllamaDecisionEngine(OllamaClient(settings.ollama_url), selection.ollama_model))
    return engines


LOCAL_HOSTS = ("127.0.0.1", "localhost", "[::1]")
logger = logging.getLogger("acm")


def transport_security(settings: Settings) -> TransportSecuritySettings:
    """Protección contra DNS rebinding del SDK MCP: solo se aceptan los Host locales y los de `ACM_ALLOWED_HOSTS`.

    Sin esta configuración, el SDK solo admite Host locales y ACM respondía 421 al servirse con otro nombre (TD-002).
    """
    hosts = [f"{h}:*" for h in LOCAL_HOSTS] + [h for extra in settings.allowed_hosts for h in (extra, f"{extra}:*")]
    origins = [f"http://{h}:*" for h in LOCAL_HOSTS] + [
        f"{scheme}://{extra}" for extra in settings.allowed_hosts for scheme in ("https", "http")
    ]
    return TransportSecuritySettings(enable_dns_rebinding_protection=True, allowed_hosts=hosts, allowed_origins=origins)


async def scheduled_watchdog(watchdog: WatchdogService, settings: Settings) -> None:
    """US-13.06: audita todos los proyectos cada `ACM_WATCHDOG_INTERVAL_S` segundos como el admin local."""
    while True:
        await anyio.sleep(settings.watchdog_interval_s)
        try:
            await anyio.to_thread.run_sync(watchdog.run_all, settings.principal)
        except Exception:  # una ronda fallida no detiene el Watchdog; queda en el log del proceso
            logger.exception("ronda periódica del Watchdog fallida")


def _local_session_token(service: ProjectService, settings: Settings) -> str:
    """Token efímero del admin local para la interfaz del propio equipo. Cada arranque revoca los anteriores."""
    identity = IdentityService(service)
    for t in identity.list_tokens(settings.principal, settings.principal)["tokens"]:
        if t["name"] == LOCAL_SESSION_NAME and t["active"]:
            identity.revoke_token(settings.principal, t["token_id"])
    write_pid(settings)
    return str(identity.create_token(settings.principal, settings.principal, LOCAL_SESSION_NAME)["token"])


async def prune_events(service: ProjectService, settings: Settings) -> None:
    """ADR-018: conserva los últimos `ACM_EVENTS_KEEP` eventos; un cliente más atrasado recibe `resync`."""
    while True:
        try:
            await anyio.to_thread.run_sync(service.events.prune, settings.events_keep)
        except Exception:
            logger.exception("no se pudieron purgar los eventos antiguos")
        await anyio.sleep(60)


def create_app(settings: Settings) -> FastAPI:
    service = build_service(settings)
    engines = build_engines(service, settings)
    # HTTP: la identidad sale del token Bearer de cada petición (EPIC-20, ADR-017), nunca de la configuración.
    catalog = SkillCatalog()
    mcp = build_mcp_server(
        service, principal=request_principal, catalog=catalog, engines=engines, token_id=request_token
    )
    mcp_app = BearerAuth(
        mcp.streamable_http_app(streamable_http_path="/", transport_security=transport_security(settings)),
        IdentityService(service),
        AuditService(service),
    )

    watchdog = WatchdogService(service, BacklogService(service, engines), engines)
    local_token = _local_session_token(service, settings) if settings.local_mode else None

    @contextlib.asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        # El sub-app MCP montado no ejecuta su propio lifespan: el gestor de sesiones se arranca aquí (SPIKE-002).
        async with mcp.session_manager.run(), anyio.create_task_group() as tg:
            if settings.watchdog_interval_s > 0:
                tg.start_soon(scheduled_watchdog, watchdog, settings)
            tg.start_soon(prune_events, service, settings)
            yield
            tg.cancel_scope.cancel()
        engines.registry.close()
        service.close()

    app = FastAPI(title="ACM", version=__version__, lifespan=lifespan)

    @app.get("/api/health")
    def health() -> dict[str, Any]:
        """Salud básica: versión y PRAGMAs de la base global (ADR-013: foreign_keys activo)."""
        info = service.system_info()
        ok = info["sqlite"]["foreign_keys"] and str(info["sqlite"]["journal_mode"]).lower() == "wal"
        return {"status": "ok" if ok else "degraded", "acm_version": __version__, **info}

    @app.get("/api/local-session", include_in_schema=False)
    def local_session(request: Request) -> JSONResponse:
        """US-14.12 CA-04: la interfaz de este equipo obtiene su token sin que la persona lo pegue (solo modo local)."""
        client = request.client.host if request.client else None
        local = local_token is not None and is_local_request(
            client, request.headers.get("host", ""), request.headers.get("x-acm-local")
        )
        # Siempre 200: un 404 aparecería como error rojo en la consola de cualquier navegador que abra ACM.
        return JSONResponse({"token": local_token if local else None}, headers={"cache-control": "no-store"})

    api, ws = build_api(service, engines, catalog)
    app.include_router(ws)  # WebSocket con autenticación propia (primer mensaje), antes del montaje de /api/v1
    app.mount("/api/v1", BearerAuth(api, IdentityService(service), AuditService(service)))
    app.mount("/mcp", mcp_app)
    if webui_available():  # ADR-019: la interfaz compilada va dentro del paquete; se monta la última
        app.mount("/", SecureStatic(), name="webui")
    else:
        logger.warning("interfaz web no compilada (src/acm/webui): ejecuta `npm run build` en web/")
    app.state.service = service
    return app
