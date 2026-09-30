"""API REST v1 y WebSocket de eventos de ACM (EPIC-30, EPIC-21; ADR-018).

- `/api/v1/...`: lectura de todo lo que guarda ACM y las mutaciones que necesita la interfaz web (cambiar el estado
  de una historia, pasarla a READY, auditar un proyecto). Autenticación: el mismo token Bearer que `/mcp` (ADR-017).
  Errores con formato único `{"error": {"code", "message", "field"}}` y código HTTP según el código de dominio.
  Contrato publicado en `/api/v1/openapi.json` (US-30.02); versión en la ruta (US-30.03).
- `/api/v1/ws`: eventos en tiempo real. El navegador no puede enviar cabeceras en un WebSocket, así que el primer
  mensaje es `{"type": "auth", "token": ..., "after": <seq> | null}`. Después el servidor envía
  `{"type": "event", "event": {seq, ts, type, project_id, principal, entity_type, entity_id, data}}` con los
  eventos visibles para ese principal, con `seq` creciente. Si el cliente se quedó demasiado atrás, recibe
  `{"type": "resync"}` y debe recargar el estado por REST (US-21.03).
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any, TypeVar

import anyio
from fastapi import APIRouter, FastAPI, Query, Request, WebSocket, WebSocketDisconnect
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from acm import __version__
from acm.auth import request_principal, request_token
from acm.domain.audit import AuditService
from acm.domain.backlog import STORY_STATUSES, STORY_TRANSITIONS, BacklogService
from acm.domain.context import ContextService
from acm.domain.errors import AcmError, Forbidden, InvalidArgument, NotFound, Unauthenticated
from acm.domain.identity import IdentityService
from acm.domain.projects import ProjectService
from acm.domain.watchdog import WatchdogService
from acm.events import ADMIN_ONLY_TYPES, REPLAY_MAX
from acm.inference.router import EngineRouter
from acm.skills_catalog import SkillCatalog

T = TypeVar("T")
HTTP_STATUS = {
    "INVALID_ARGUMENT": 400,
    "UNAUTHENTICATED": 401,
    "FORBIDDEN": 403,
    "NOT_FOUND": 404,
    "ALREADY_EXISTS": 409,
    "FAILED_PRECONDITION": 409,
    "DATA_INTEGRITY": 409,
    "ENGINE_UNAVAILABLE": 503,
    "ENGINE_ERROR": 502,
}
# Columnas del Kanban en orden de flujo (US-06.01): una por estado de historia.
KANBAN_COLUMNS = (
    "PLANNED",
    "READY",
    "IN_PROGRESS",
    "BLOCKED",
    "IMPLEMENTED",
    "TESTING",
    "FAILED",
    "VERIFIED",
    "DONE",
    "CANCELLED",
    "DEPRECATED",
)
WS_POLL_S = 0.2
WS_AUTH_TIMEOUT_S = 10.0
WS_ACCESS_REFRESH_S = 30.0


def _error_doc(description: str) -> dict[str, Any]:
    return {
        "description": description,
        "content": {
            "application/json": {"example": {"error": {"code": "CODE", "message": "motivo", "field": "campo o null"}}}
        },
    }


ERROR_RESPONSES: dict[int | str, dict[str, Any]] = {
    400: _error_doc("INVALID_ARGUMENT: entrada inválida"),
    401: _error_doc("UNAUTHENTICATED: falta el token Bearer, es desconocido o está revocado"),
    403: _error_doc("FORBIDDEN: el principal no tiene permiso"),
    404: _error_doc("NOT_FOUND: no existe o no es accesible (no se revela cuál)"),
    409: _error_doc("FAILED_PRECONDITION / ALREADY_EXISTS / DATA_INTEGRITY: estado incompatible con la operación"),
}


class StatusChange(BaseModel):
    status: str
    reason: str = ""


def error_response(exc: AcmError) -> JSONResponse:
    return JSONResponse(
        {"error": {"code": exc.code, "message": exc.message, "field": exc.field}},
        status_code=HTTP_STATUS.get(exc.code, 500),
    )


def build_api(
    service: ProjectService,
    engines: EngineRouter,
    catalog: SkillCatalog,
) -> tuple[FastAPI, APIRouter]:
    """Devuelve la sub-app REST (a envolver con `BearerAuth`) y el router del WebSocket (autenticación propia)."""
    backlog = BacklogService(service, engines)
    context = ContextService(service, backlog, engines)
    watchdog = WatchdogService(service, backlog, engines)
    identity = IdentityService(service)
    audit = AuditService(service)

    api = FastAPI(title="ACM API", version=__version__, openapi_url="/openapi.json", docs_url="/docs", redoc_url=None)

    r = APIRouter(responses=ERROR_RESPONSES)
    subscriptions = {"active": 0}

    @api.exception_handler(AcmError)
    async def acm_error(_request: Request, exc: AcmError) -> JSONResponse:
        return error_response(exc)

    @api.exception_handler(RequestValidationError)
    async def validation_error(_request: Request, exc: RequestValidationError) -> JSONResponse:
        # Mismo formato que el resto de errores (US-30.01 CA-04), no el 422 por defecto de FastAPI.
        first = exc.errors()[0] if exc.errors() else {}
        field = ".".join(str(p) for p in first.get("loc", ())[1:]) or None
        return error_response(InvalidArgument(first.get("msg", "entrada inválida"), field=field))

    def mutate(operation: str, arguments: dict[str, Any], fn: Callable[[], T]) -> T:
        """Mutaciones por REST: mismas reglas de auditoría que MCP (US-14.11) y evento de actividad (ADR-018)."""
        who, token = request_principal(), request_token()
        start = time.perf_counter()
        try:
            result = fn()
        except AcmError as exc:
            audit.record(
                principal=who,
                token_id=token,
                operation=operation,
                arguments=arguments,
                status="error",
                duration_ms=(time.perf_counter() - start) * 1000,
                error=str(exc),
            )
            raise
        audit.record(
            principal=who,
            token_id=token,
            operation=operation,
            arguments=arguments,
            status="ok",
            duration_ms=(time.perf_counter() - start) * 1000,
            result=result,
        )
        return result

    # ------------------------------------------------------------------ identidad y metadatos
    @r.get("/me")
    def me() -> dict[str, Any]:
        who = request_principal()
        return identity.get_principal(who, who)

    @r.get("/meta")
    def meta() -> dict[str, Any]:
        return {
            "acm_version": __version__,
            "story_statuses": list(STORY_STATUSES),
            "transitions": {k: list(v) for k, v in STORY_TRANSITIONS.items()},
            "kanban_columns": list(KANBAN_COLUMNS),
            "latest_event_seq": service.events.latest_seq(),
            "active_subscriptions": subscriptions["active"],
        }

    # ------------------------------------------------------------------ proyectos
    def portfolio_entry(principal: str, project: dict[str, Any]) -> dict[str, Any]:
        pid = project["project_id"]
        stories = backlog.list_stories(principal, pid)["stories"]
        by_status = {s: 0 for s in STORY_STATUSES}
        for st in stories:
            by_status[st["status"]] += 1
        return {
            **project,
            "governance": watchdog.status(principal, pid),
            "stories_by_status": by_status,
            "stories": len(stories),
        }

    @r.get("/projects")
    def projects() -> dict[str, Any]:
        who = request_principal()
        return {"projects": [portfolio_entry(who, p) for p in service.list_for(who)]}

    @r.get("/projects/{project_id}")
    def project(project_id: str) -> dict[str, Any]:
        return service.open(request_principal(), project_id)

    @r.get("/projects/{project_id}/backlog")
    def project_backlog(project_id: str) -> dict[str, Any]:
        who = request_principal()
        return {
            "project_id": project_id,
            "requirements": backlog.list_requirements(who, project_id)["requirements"],
            "epics": backlog.list_epics(who, project_id)["epics"],
            "stories": backlog.list_stories(who, project_id)["stories"],
            "gaps": backlog.audit(who, project_id),
        }

    @r.get("/projects/{project_id}/stories/{story_id}")
    def story(project_id: str, story_id: str) -> dict[str, Any]:
        who = request_principal()
        return {
            **backlog.get_story(who, project_id, story_id),
            "history": backlog.status_history(who, project_id, story_id)["history"],
            "allowed_transitions": list(STORY_TRANSITIONS[backlog.get_story(who, project_id, story_id)["status"]]),
        }

    @r.post("/projects/{project_id}/stories/{story_id}/status")
    def story_status(project_id: str, story_id: str, change: StatusChange) -> dict[str, Any]:
        who = request_principal()
        args = {"project_id": project_id, "story_id": story_id, "status": change.status, "reason": change.reason}
        return mutate(
            "rest:story_set_status",
            args,
            lambda: backlog.set_status(who, project_id, story_id, change.status, change.reason),
        )

    @r.post("/projects/{project_id}/stories/{story_id}/ready")
    def story_ready(project_id: str, story_id: str) -> dict[str, Any]:
        who = request_principal()
        args = {"project_id": project_id, "story_id": story_id}
        return mutate("rest:story_mark_ready", args, lambda: backlog.mark_ready(who, project_id, story_id))

    @r.get("/projects/{project_id}/requirements/{requirement_id}/trace")
    def trace(project_id: str, requirement_id: str) -> dict[str, Any]:
        return backlog.trace_requirement(request_principal(), project_id, requirement_id)

    @r.get("/projects/{project_id}/context/{story_id}")
    def compact_context(project_id: str, story_id: str) -> dict[str, Any]:
        return context.compact(request_principal(), project_id, story_id)

    @r.get("/projects/{project_id}/members")
    def members(project_id: str) -> dict[str, Any]:
        return identity.list_members(request_principal(), project_id)

    @r.get("/projects/{project_id}/config")
    def config(project_id: str) -> dict[str, Any]:
        return service.get_config(request_principal(), project_id)

    @r.get("/projects/{project_id}/governance")
    def governance(project_id: str, limit: int = 20) -> dict[str, Any]:
        who = request_principal()
        return {**watchdog.status(who, project_id), "history": watchdog.history(who, project_id, limit)["runs"]}

    @r.post("/projects/{project_id}/watchdog")
    def watchdog_run(project_id: str) -> dict[str, Any]:
        who = request_principal()
        return mutate("rest:watchdog_run", {"project_id": project_id}, lambda: watchdog.run(who, project_id))

    # ------------------------------------------------------------------ Kanban (US-06.01; uno o varios proyectos)
    @r.get("/kanban")
    def kanban(projects: str | None = Query(default=None, description="project_id separados por comas")) -> dict:
        who = request_principal()
        accessible = [p["project_id"] for p in service.list_for(who)]
        wanted = accessible if not projects else [p.strip() for p in projects.split(",") if p.strip()]
        cards = []
        for pid in wanted:
            for st in backlog.list_stories(who, pid)["stories"]:  # NOT_FOUND si alguno no es accesible
                cards.append(
                    {
                        "project_id": pid,
                        **{
                            k: st[k]
                            for k in (
                                "id",
                                "status",
                                "i_want",
                                "as_a",
                                "so_that",
                                "kind",
                                "feature_id",
                                "epic_id",
                                "requirement_ids",
                                "updated_at",
                            )
                        },
                        "criteria": len(st["acceptance_criteria"]),
                    }
                )
        return {
            "projects": wanted,
            "columns": list(KANBAN_COLUMNS),
            "transitions": {k: list(v) for k, v in STORY_TRANSITIONS.items()},
            "cards": cards,
            "latest_event_seq": service.events.latest_seq(),
        }

    # ------------------------------------------------------------------ plataforma
    @r.get("/activity")
    def activity(
        limit: int = 100, project_id: str | None = None, principal_id: str | None = None, operation: str | None = None
    ) -> dict[str, Any]:
        return audit.list(
            request_principal(), limit=limit, filter_principal=principal_id, operation=operation, project_id=project_id
        )

    @r.get("/events")
    def events(after: int = 0, limit: int = 200) -> dict[str, Any]:
        who = request_principal()
        if not 1 <= limit <= REPLAY_MAX:
            raise InvalidArgument(f"debe estar entre 1 y {REPLAY_MAX}", field="limit")
        access = Access(service, who)
        return {
            "events": [e for e in service.events.after(after, limit) if access.can_see(e)],
            "latest_seq": service.events.latest_seq(),
        }

    @r.get("/health")
    def health() -> dict[str, Any]:
        return watchdog.health(request_principal(), catalog)

    @r.get("/engines")
    def engines_list() -> dict[str, Any]:
        rules = next(e for e in engines.registry.decision if e.provider == "rules")
        return {"engines": engines.registry.list(), "rules": rules.catalog()}  # type: ignore[attr-defined]

    @r.get("/savings")
    def savings(principal_id: str | None = None, project_id: str | None = None) -> dict[str, Any]:
        return context.savings_report(request_principal(), filter_principal=principal_id, project_id=project_id)

    @r.get("/skills")
    def skills() -> dict[str, Any]:
        return {"skills": catalog.entries(), "rejected": catalog.rejected}

    @r.get("/skills/{name}")
    def skill(name: str) -> dict[str, Any]:
        entry = catalog.skills.get(name)
        if entry is None:
            raise NotFound(f"la skill {name!r} no existe", field="name")
        return {"name": name, "frontmatter": entry.frontmatter, "files": {f.name: f.text for f in entry.files}}

    @r.get("/principals")
    def principals() -> dict[str, Any]:
        return identity.list_principals(request_principal())

    @r.get("/tokens")
    def tokens(principal_id: str | None = None) -> dict[str, Any]:
        return identity.list_tokens(request_principal(), principal_id)

    api.include_router(r)
    ws = APIRouter()

    @ws.websocket("/api/v1/ws")
    async def events_ws(socket: WebSocket) -> None:
        await socket.accept()
        try:
            with anyio.fail_after(WS_AUTH_TIMEOUT_S):
                hello = await socket.receive_json()
            if not isinstance(hello, dict) or hello.get("type") != "auth":
                raise Unauthenticated("el primer mensaje debe ser {'type': 'auth', 'token': ...}")
            principal, _token_id = await anyio.to_thread.run_sync(identity.authenticate, hello.get("token"))
        except (TimeoutError, AcmError, ValueError) as exc:
            await socket.send_json({"type": "error", "error": str(exc) or "UNAUTHENTICATED"})
            await socket.close(code=4401)
            return
        except WebSocketDisconnect:
            return
        access = await anyio.to_thread.run_sync(Access, service, principal)
        latest = await anyio.to_thread.run_sync(service.events.latest_seq)
        after = hello.get("after")
        if after is None:
            last = latest
        elif not isinstance(after, int) or after < 0:
            last = latest
            await socket.send_json({"type": "resync", "reason": "seq inválido"})
        else:
            oldest = await anyio.to_thread.run_sync(service.events.oldest_seq)
            if oldest and after < oldest - 1:  # los eventos intermedios ya se purgaron: hay que recargar
                await socket.send_json({"type": "resync", "reason": "eventos anteriores ya no disponibles"})
                last = latest
            else:
                last = after
        await socket.send_json({"type": "ready", "principal": principal, "seq": last, "latest_seq": latest})
        subscriptions["active"] += 1
        try:
            async with anyio.create_task_group() as tg:

                async def watch_disconnect() -> None:
                    try:
                        while True:
                            await socket.receive_text()  # el cliente no necesita enviar más; detecta el cierre
                    except WebSocketDisconnect:
                        tg.cancel_scope.cancel()

                tg.start_soon(watch_disconnect)
                while True:
                    batch = await anyio.to_thread.run_sync(service.events.after, last, REPLAY_MAX)
                    if batch:
                        if any(e["type"] in ("member.changed", "project.created", "principal.changed") for e in batch):
                            access = await anyio.to_thread.run_sync(Access, service, principal)
                        for event in batch:
                            last = event["seq"]
                            if access.can_see(event):
                                await socket.send_json({"type": "event", "event": event})
                    elif access.age() > WS_ACCESS_REFRESH_S:
                        access = await anyio.to_thread.run_sync(Access, service, principal)
                    await anyio.sleep(WS_POLL_S)
        except (WebSocketDisconnect, RuntimeError):
            return
        finally:
            subscriptions["active"] -= 1  # US-21.02 CA-03: la desconexión libera la suscripción

    return api, ws


class Access:
    """Qué eventos puede ver un principal (US-21.02 CA-02). Se recalcula cuando cambian pertenencias o roles."""

    def __init__(self, service: ProjectService, principal: str):
        self.principal = principal
        self.created = time.monotonic()
        try:
            with service.global_db.read() as conn:
                self.admin = service._principal_role(conn, principal) == "admin"
        except Forbidden:
            self.admin = False
        self.projects = {p["project_id"] for p in service.list_for(principal)} if not self.admin else set()

    def age(self) -> float:
        return time.monotonic() - self.created

    def can_see(self, event: dict[str, Any]) -> bool:
        if self.admin:
            return True
        if event["type"] in ADMIN_ONLY_TYPES or event["project_id"] is None:
            return False
        return event["project_id"] in self.projects
