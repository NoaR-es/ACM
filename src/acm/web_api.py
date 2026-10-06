"""API REST v1 y WebSocket de eventos de ACM (EPIC-30, EPIC-21; ADR-018).

- `/api/v1/...`: lectura de todo lo que guarda ACM y todas sus operaciones de escritura (SPRINT-008: la interfaz web
  opera ACM por completo): proyectos, configuración, backlog, criterios, sprints, miembros, principales, tokens,
  motores y auditorías. Cada escritura se audita como `rest:*` con las mismas reglas que MCP.
  Autenticación: el mismo token Bearer que `/mcp` (ADR-017).
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
from acm.domain.chat import ChatService
from acm.domain.context import ContextService
from acm.domain.errors import AcmError, Forbidden, InvalidArgument, NotFound, Unauthenticated
from acm.domain.identity import IdentityService
from acm.domain.models import ModelService
from acm.domain.projects import ProjectService
from acm.domain.sprints import SprintService
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


# Cuerpos de escritura (SPRINT-008). Los tipos son laxos a propósito: la validación la hace el dominio, con el mismo
# formato de error que MCP (campo y motivo), en lugar de dos validaciones que podrían divergir.
class ProjectIn(BaseModel):
    key: str
    name: str
    description: str = ""


class ConfigIn(BaseModel):
    changes: dict[str, Any]


class RequirementIn(BaseModel):
    title: str
    description: str = ""


class EpicIn(BaseModel):
    title: str
    objective: str
    scope: str
    requirement_ids: list[str] = []


class RequirementIds(BaseModel):
    requirement_ids: list[str]


class FeatureIn(BaseModel):
    epic_id: str
    title: str
    description: str = ""


class SplitIn(BaseModel):
    parts: list[dict[str, Any]]


class StoryIn(BaseModel):
    feature_id: str
    as_a: str
    i_want: str
    so_that: str
    requirement_ids: list[str] = []
    acceptance_criteria: list[str] = []
    kind: str = "user_story"
    technical_reason: str = ""


class CriteriaIn(BaseModel):
    criteria: list[str]


class SprintIn(BaseModel):
    name: str
    goal: str
    start_date: str
    end_date: str
    capacity: int | None = None


class StoryIds(BaseModel):
    story_ids: list[str]


class StartIn(BaseModel):
    force: bool = False


class CloseIn(BaseModel):
    carry_over_to: str | None = None


class RoleIn(BaseModel):
    role: str


class PrincipalIn(BaseModel):
    principal_id: str
    kind: str
    role: str = "user"


class TokenIn(BaseModel):
    principal_id: str
    name: str


class ModelsIn(BaseModel):
    ollama_model: str | None = None
    jev_default_model: str | None = None
    jev_models_by_purpose: dict[str, str] | None = None
    jev_model_notes: dict[str, str] | None = None


class ChatIn(BaseModel):
    message: str
    thread_id: str | None = None
    title: str | None = None


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
    sprints = SprintService(backlog)
    models = ModelService(service, engines)
    chat = ChatService(service, backlog, engines)
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

    def emit_activity(who: str, operation: str, arguments: dict[str, Any], status: str, error: str) -> None:
        """Evento `activity` (solo admin), igual que en MCP: las escrituras por REST también se ven en vivo."""
        project_id = arguments.get("project_id") if isinstance(arguments.get("project_id"), str) else None
        service.events.append(
            "activity",
            principal=who,
            project_id=project_id,
            entity_type="operation",
            entity_id=operation,
            data={"status": status, "error": error[:300]},
        )

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
            emit_activity(who, operation, arguments, "error", str(exc))
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
        emit_activity(who, operation, arguments, "ok", "")
        return result

    # ------------------------------------------------------------------ identidad y metadatos
    @r.get("/me")
    def me() -> dict[str, Any]:
        """Tu identidad: principal, tipo, rol global, proyectos y tokens activos."""
        who = request_principal()
        return identity.get_principal(who, who)

    @r.get("/meta")
    def meta() -> dict[str, Any]:
        """Versión de ACM, estados de historia, transiciones permitidas, columnas del Kanban y último evento."""
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
        """Cartera: proyectos accesibles con su semáforo de gobernanza y las historias por estado."""
        who = request_principal()
        return {"projects": [portfolio_entry(who, p) for p in service.list_for(who)]}

    @r.get("/projects/{project_id}")
    def project(project_id: str) -> dict[str, Any]:
        """Metadatos del proyecto, tu rol y su configuración."""
        return service.open(request_principal(), project_id)

    @r.get("/projects/{project_id}/backlog")
    def project_backlog(project_id: str) -> dict[str, Any]:
        """Backlog completo: requisitos, épicas con features, historias con criterios y huecos de trazabilidad."""
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
        """Historia con criterios, requisitos, historial de estados y transiciones permitidas."""
        who = request_principal()
        return {
            **backlog.get_story(who, project_id, story_id),
            "history": backlog.status_history(who, project_id, story_id)["history"],
            "allowed_transitions": list(STORY_TRANSITIONS[backlog.get_story(who, project_id, story_id)["status"]]),
        }

    @r.post("/projects/{project_id}/stories/{story_id}/status")
    def story_status(project_id: str, story_id: str, change: StatusChange) -> dict[str, Any]:
        """Mueve la historia a otro estado permitido (DONE solo desde VERIFIED)."""
        who = request_principal()
        args = {"project_id": project_id, "story_id": story_id, "status": change.status, "reason": change.reason}
        return mutate(
            "rest:story_set_status",
            args,
            lambda: backlog.set_status(who, project_id, story_id, change.status, change.reason),
        )

    @r.post("/projects/{project_id}/stories/{story_id}/ready")
    def story_ready(project_id: str, story_id: str) -> dict[str, Any]:
        """Gate de calidad: pasa la historia de PLANNED a READY si está completa."""
        who = request_principal()
        args = {"project_id": project_id, "story_id": story_id}
        return mutate("rest:story_mark_ready", args, lambda: backlog.mark_ready(who, project_id, story_id))

    @r.get("/projects/{project_id}/requirements/{requirement_id}/trace")
    def trace(project_id: str, requirement_id: str) -> dict[str, Any]:
        """Trazabilidad de un requisito: épicas, features e historias que lo implementan."""
        return backlog.trace_requirement(request_principal(), project_id, requirement_id)

    @r.get("/projects/{project_id}/context/{story_id}")
    def compact_context(project_id: str, story_id: str) -> dict[str, Any]:
        """Contexto compacto de una historia para agentes, con fuentes y tokens ahorrados."""
        return context.compact(request_principal(), project_id, story_id)

    @r.get("/projects/{project_id}/members")
    def members(project_id: str) -> dict[str, Any]:
        """Miembros del proyecto con su rol y tipo."""
        return identity.list_members(request_principal(), project_id)

    @r.get("/projects/{project_id}/config")
    def config(project_id: str) -> dict[str, Any]:
        """Parámetros de configuración del proyecto con valor, valores permitidos y quién los usa."""
        return service.get_config(request_principal(), project_id)

    @r.get("/projects/{project_id}/governance")
    def governance(project_id: str, limit: int = 20) -> dict[str, Any]:
        """Semáforo, integridad e histórico de auditorías del Watchdog."""
        who = request_principal()
        return {**watchdog.status(who, project_id), "history": watchdog.history(who, project_id, limit)["runs"]}

    @r.post("/projects/{project_id}/watchdog")
    def watchdog_run(project_id: str) -> dict[str, Any]:
        """Ejecuta ahora una auditoría de gobernanza del proyecto."""
        who = request_principal()
        return mutate("rest:watchdog_run", {"project_id": project_id}, lambda: watchdog.run(who, project_id))

    # ------------------------------------------------------------------ Kanban (US-06.01; uno o varios proyectos)
    @r.get("/kanban")
    def kanban(
        projects: str | None = Query(default=None, description="project_id separados por comas"),
        sprint: str | None = Query(default=None, description="solo las historias de este sprint (un proyecto)"),
    ) -> dict:
        """Tablero Kanban de uno o varios proyectos (o de un sprint): columnas, transiciones y tarjetas."""
        who = request_principal()
        accessible = [p["project_id"] for p in service.list_for(who)]
        wanted = accessible if not projects else [p.strip() for p in projects.split(",") if p.strip()]
        in_sprint: set[str] | None = None
        if sprint is not None:
            if len(wanted) != 1:
                raise InvalidArgument("el filtro por sprint exige un único proyecto", field="sprint")
            in_sprint = set(sprints.get(who, wanted[0], sprint)["story_ids"])
        cards = []
        for pid in wanted:
            for st in backlog.list_stories(who, pid)["stories"]:  # NOT_FOUND si alguno no es accesible
                if in_sprint is not None and st["id"] not in in_sprint:
                    continue
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
                                "sprint_id",
                            )
                        },
                        "criteria": len(st["acceptance_criteria"]),
                    }
                )
        return {
            "projects": wanted,
            "sprint": sprint,
            "columns": list(KANBAN_COLUMNS),
            "transitions": {k: list(v) for k, v in STORY_TRANSITIONS.items()},
            "cards": cards,
            "latest_event_seq": service.events.latest_seq(),
        }

    # ------------------------------------------------------------------ escritura (SPRINT-008, FEAT-31.04)
    def write(operation: str, arguments: dict[str, Any], fn: Callable[..., T], *args: Any) -> T:
        return mutate(f"rest:{operation}", arguments, lambda: fn(request_principal(), *args))

    @r.post("/projects", status_code=201)
    def project_create(body: ProjectIn) -> dict[str, Any]:
        """Crea un proyecto con su propia base SQLite (`key` = project_id)."""
        return write("project_create", body.model_dump(), service.create, body.key, body.name, body.description)

    @r.patch("/projects/{project_id}/config")
    def config_set(project_id: str, body: ConfigIn) -> dict[str, Any]:
        """Cambia parámetros de configuración; valida todos antes de guardar ninguno."""
        return write(
            "project_config_set",
            {"project_id": project_id, **body.model_dump()},
            service.set_config,
            project_id,
            body.changes,
        )

    @r.post("/projects/{project_id}/requirements", status_code=201)
    def requirement_create(project_id: str, body: RequirementIn) -> dict[str, Any]:
        """Registra un requisito REQ-NNN."""
        return write(
            "requirement_create",
            {"project_id": project_id, **body.model_dump()},
            backlog.create_requirement,
            project_id,
            body.title,
            body.description,
        )

    @r.post("/projects/{project_id}/epics", status_code=201)
    def epic_create(project_id: str, body: EpicIn) -> dict[str, Any]:
        """Crea una épica con objetivo, alcance y requisitos."""
        return write(
            "epic_create",
            {"project_id": project_id, **body.model_dump()},
            backlog.create_epic,
            project_id,
            body.title,
            body.objective,
            body.scope,
            body.requirement_ids,
        )

    @r.post("/projects/{project_id}/epics/{epic_id}/requirements")
    def epic_link(project_id: str, epic_id: str, body: RequirementIds) -> dict[str, Any]:
        """Asocia más requisitos a una épica."""
        return write(
            "epic_link_requirements",
            {"project_id": project_id, "epic_id": epic_id, **body.model_dump()},
            backlog.link_epic_requirements,
            project_id,
            epic_id,
            body.requirement_ids,
        )

    @r.post("/projects/{project_id}/epics/{epic_id}/confirm-coverage")
    def epic_confirm(project_id: str, epic_id: str) -> dict[str, Any]:
        """Confirma que las features activas cubren el objetivo de la épica."""
        return write(
            "epic_confirm_coverage",
            {"project_id": project_id, "epic_id": epic_id},
            backlog.confirm_epic_coverage,
            project_id,
            epic_id,
        )

    @r.post("/projects/{project_id}/features", status_code=201)
    def feature_create(project_id: str, body: FeatureIn) -> dict[str, Any]:
        """Crea una feature dentro de una épica."""
        return write(
            "feature_create",
            {"project_id": project_id, **body.model_dump()},
            backlog.create_feature,
            project_id,
            body.epic_id,
            body.title,
            body.description,
        )

    @r.post("/projects/{project_id}/features/{feature_id}/split")
    def feature_split(project_id: str, feature_id: str, body: SplitIn) -> dict[str, Any]:
        """Divide una feature en ≥2 features nuevas repartiendo todas sus historias."""
        return write(
            "feature_split",
            {"project_id": project_id, "feature_id": feature_id, **body.model_dump()},
            backlog.split_feature,
            project_id,
            feature_id,
            body.parts,
        )

    @r.post("/projects/{project_id}/stories", status_code=201)
    def story_create(project_id: str, body: StoryIn) -> dict[str, Any]:
        """Crea una historia (de usuario o técnica) enlazada a requisitos, con sus criterios."""
        return write(
            "story_create",
            {"project_id": project_id, **body.model_dump()},
            backlog.create_story,
            project_id,
            body.feature_id,
            body.as_a,
            body.i_want,
            body.so_that,
            body.requirement_ids,
            body.acceptance_criteria,
            body.kind,
            body.technical_reason,
        )

    @r.post("/projects/{project_id}/stories/{story_id}/criteria")
    def story_criteria(project_id: str, story_id: str, body: CriteriaIn) -> dict[str, Any]:
        """Añade criterios de aceptación a una historia."""
        return write(
            "story_add_criteria",
            {"project_id": project_id, "story_id": story_id, **body.model_dump()},
            backlog.add_criteria,
            project_id,
            story_id,
            body.criteria,
        )

    # ------------------------------------------------------------------ sprints (EPIC-05)
    @r.get("/projects/{project_id}/sprints")
    def sprint_list(project_id: str) -> dict[str, Any]:
        """Sprints con estado, historias, carga, capacidad y resumen de cierre."""
        return sprints.list(request_principal(), project_id)

    @r.get("/projects/{project_id}/sprints/{sprint_id}")
    def sprint_get(project_id: str, sprint_id: str) -> dict[str, Any]:
        """Un sprint con sus historias e historial de pertenencia."""
        return sprints.get(request_principal(), project_id, sprint_id)

    @r.post("/projects/{project_id}/sprints", status_code=201)
    def sprint_create(project_id: str, body: SprintIn) -> dict[str, Any]:
        """Crea un sprint PLANNED con objetivo, fechas y capacidad opcional (en historias)."""
        return write(
            "sprint_create",
            {"project_id": project_id, **body.model_dump()},
            sprints.create,
            project_id,
            body.name,
            body.goal,
            body.start_date,
            body.end_date,
            body.capacity,
        )

    @r.post("/projects/{project_id}/sprints/{sprint_id}/stories")
    def sprint_add(project_id: str, sprint_id: str, body: StoryIds) -> dict[str, Any]:
        """Planifica historias en un sprint abierto."""
        return write(
            "sprint_add_stories",
            {"project_id": project_id, "sprint_id": sprint_id, **body.model_dump()},
            sprints.add_stories,
            project_id,
            sprint_id,
            body.story_ids,
        )

    @r.delete("/projects/{project_id}/sprints/{sprint_id}/stories/{story_id}")
    def sprint_remove(project_id: str, sprint_id: str, story_id: str) -> dict[str, Any]:
        """Retira una historia de un sprint abierto."""
        return write(
            "sprint_remove_story",
            {"project_id": project_id, "sprint_id": sprint_id, "story_id": story_id},
            sprints.remove_story,
            project_id,
            sprint_id,
            story_id,
        )

    @r.post("/projects/{project_id}/sprints/{sprint_id}/start")
    def sprint_start(project_id: str, sprint_id: str, body: StartIn) -> dict[str, Any]:
        """Inicia un sprint PLANNED (rechaza la sobrecarga salvo force)."""
        return write(
            "sprint_start",
            {"project_id": project_id, "sprint_id": sprint_id, **body.model_dump()},
            sprints.start,
            project_id,
            sprint_id,
            body.force,
        )

    @r.post("/projects/{project_id}/sprints/{sprint_id}/close")
    def sprint_close(project_id: str, sprint_id: str, body: CloseIn) -> dict[str, Any]:
        """Cierra el sprint activo con resumen; lo no terminado se traslada o vuelve al backlog."""
        return write(
            "sprint_close",
            {"project_id": project_id, "sprint_id": sprint_id, **body.model_dump()},
            sprints.close,
            project_id,
            sprint_id,
            body.carry_over_to,
        )

    @r.post("/projects/{project_id}/sprints/{sprint_id}/cancel")
    def sprint_cancel(project_id: str, sprint_id: str) -> dict[str, Any]:
        """Cancela un sprint abierto; sus historias vuelven al backlog."""
        return write(
            "sprint_cancel", {"project_id": project_id, "sprint_id": sprint_id}, sprints.cancel, project_id, sprint_id
        )

    # ------------------------------------------------------------------ acceso (EPIC-20)
    @r.put("/projects/{project_id}/members/{principal_id}")
    def member_set(project_id: str, principal_id: str, body: RoleIn) -> dict[str, Any]:
        """(admin/owner) Añade un miembro al proyecto o cambia su rol."""
        return write(
            "member_set",
            {"project_id": project_id, "principal_id": principal_id, **body.model_dump()},
            identity.set_member,
            project_id,
            principal_id,
            body.role,
        )

    @r.delete("/projects/{project_id}/members/{principal_id}")
    def member_remove(project_id: str, principal_id: str) -> dict[str, Any]:
        """(admin/owner) Retira a un miembro del proyecto."""
        return write(
            "member_remove",
            {"project_id": project_id, "principal_id": principal_id},
            identity.remove_member,
            project_id,
            principal_id,
        )

    @r.post("/principals", status_code=201)
    def principal_create(body: PrincipalIn) -> dict[str, Any]:
        """(admin) Alta de un usuario o agente."""
        return write(
            "principal_create", body.model_dump(), identity.create_principal, body.principal_id, body.kind, body.role
        )

    @r.put("/principals/{principal_id}/role")
    def principal_role(principal_id: str, body: RoleIn) -> dict[str, Any]:
        """(admin) Cambia el rol global de un principal."""
        return write(
            "principal_set_role",
            {"principal_id": principal_id, **body.model_dump()},
            identity.set_global_role,
            principal_id,
            body.role,
        )

    @r.post("/tokens", status_code=201)
    def token_create(body: TokenIn) -> dict[str, Any]:
        """(admin) Crea un token; el secreto (`token`) solo aparece en esta respuesta y nunca se audita."""
        return write("token_create", body.model_dump(), identity.create_token, body.principal_id, body.name)

    @r.delete("/tokens/{token_id}")
    def token_revoke(token_id: str) -> dict[str, Any]:
        """Revoca un token al instante (los propios, o cualquiera si eres admin)."""
        return write("token_revoke", {"token_id": token_id}, identity.revoke_token, token_id)

    @r.post("/engines/refresh")
    def engines_refresh() -> dict[str, Any]:
        """(admin) Comprueba de nuevo la salud y los modelos de cada motor, sin reiniciar ACM."""

        def refresh(who: str) -> dict[str, Any]:
            with service.global_db.read() as conn:
                if service._principal_role(conn, who) != "admin":
                    raise Forbidden("solo un admin puede refrescar los motores de inferencia")
            return {"engines": engines.registry.refresh()}

        return write("engines_refresh", {}, refresh)

    # ------------------------------------------------------------------ modelos y conversación
    @r.get("/models")
    def models_catalog() -> dict[str, Any]:
        """Catálogo de modelos de Ollama y Ollaya: disponibles, elegidos, propósitos, notas y cómo usarlos."""
        return models.catalog(request_principal())

    @r.put("/models")
    def models_select(body: ModelsIn) -> dict[str, Any]:
        """(admin) Elige el modelo de Ollama y los de Ollaya (por defecto y por propósito); sin reiniciar."""
        args = body.model_dump()
        return mutate("rest:models_select", args, lambda: models.select(request_principal(), **args))

    @r.get("/projects/{project_id}/chat/threads")
    def chat_threads(project_id: str) -> dict[str, Any]:
        """Tus hilos de conversación con el modelo local (un admin ve todos)."""
        return chat.threads(request_principal(), project_id)

    @r.get("/projects/{project_id}/chat/threads/{thread_id}")
    def chat_thread(project_id: str, thread_id: str) -> dict[str, Any]:
        """Un hilo con sus mensajes y las herramientas que usó el modelo."""
        return chat.get(request_principal(), project_id, thread_id)

    @r.post("/projects/{project_id}/chat")
    def chat_send(project_id: str, body: ChatIn) -> dict[str, Any]:
        """Envía un mensaje al asistente local (Ollama) del proyecto; ACM conserva el hilo."""
        return write(
            "chat",
            {"project_id": project_id, **body.model_dump()},
            chat.send,
            project_id,
            body.message,
            body.thread_id,
            body.title,
        )

    # ------------------------------------------------------------------ plataforma
    @r.get("/activity")
    def activity(
        limit: int = 100, project_id: str | None = None, principal_id: str | None = None, operation: str | None = None
    ) -> dict[str, Any]:
        """Auditoría de invocaciones (solo admin), filtrable por proyecto, principal y operación."""
        return audit.list(
            request_principal(), limit=limit, filter_principal=principal_id, operation=operation, project_id=project_id
        )

    @r.get("/events")
    def events(after: int = 0, limit: int = 200) -> dict[str, Any]:
        """Eventos de dominio posteriores a un seq, filtrados por visibilidad."""
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
        """Salud de cada componente: bases SQLite, catálogo de skills y motores (solo admin)."""
        return watchdog.health(request_principal(), catalog)

    @r.get("/engines")
    def engines_list() -> dict[str, Any]:
        """Motores de inferencia registrados, estado, modelos detectados y reglas disponibles."""
        rules = next(e for e in engines.registry.decision if e.provider == "rules")
        return {"engines": engines.registry.list(), "rules": rules.catalog()}  # type: ignore[attr-defined]

    @r.get("/savings")
    def savings(principal_id: str | None = None, project_id: str | None = None) -> dict[str, Any]:
        """Tokens ahorrados a los agentes por el contexto compacto (solo admin)."""
        return context.savings_report(request_principal(), filter_principal=principal_id, project_id=project_id)

    @r.get("/skills")
    def skills() -> dict[str, Any]:
        """Catálogo de skills que ACM sirve a los agentes."""
        return {"skills": catalog.entries(), "rejected": catalog.rejected}

    @r.get("/skills/{name}")
    def skill(name: str) -> dict[str, Any]:
        """Archivos de una skill (Markdown con frontmatter)."""
        entry = catalog.skills.get(name)
        if entry is None:
            raise NotFound(f"la skill {name!r} no existe", field="name")
        return {"name": name, "frontmatter": entry.frontmatter, "files": {f.name: f.text for f in entry.files}}

    @r.get("/principals")
    def principals() -> dict[str, Any]:
        """Principales (usuarios y agentes) y roles disponibles (solo admin)."""
        return identity.list_principals(request_principal())

    @r.get("/tokens")
    def tokens(principal_id: str | None = None) -> dict[str, Any]:
        """Tokens sin su secreto: prefijo, estado y uso."""
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
