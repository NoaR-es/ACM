"""Servidor MCP propio de ACM (ADR-008, ADR-014).

- Sin estado de sesión: toda herramienta de proyecto exige `project_id` y lo devuelve (US-01.06).
- Los errores de dominio llegan al agente como `ToolError("<CODE>: <motivo>")` (GAP-007).
- El servicio es síncrono (sqlite3): cada llamada se ejecuta en un hilo de trabajo (ADR-013).
- Cada invocación (herramientas, `skills/*` y lectura de archivos de skills) se audita (US-14.10, US-14.11).
- Extensión MCP Skills (SEP-2640) con el catálogo oficial de ACM (US-15.04..07).
- Segundo cerebro: decisiones delegadas y contexto compacto a través del router de inferencia (EPIC-35, ADR-015).
"""

from __future__ import annotations

import time
from collections.abc import Callable
from functools import partial
from typing import Any, TypeVar

import anyio
from mcp.server.extension import Extension, MethodBinding
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ResourceNotFoundError, ToolError
from mcp.server.subscriptions import InMemorySubscriptionBus
from mcp.shared.exceptions import MCPError
from mcp.shared.subscriptions import ResourcesListChanged
from mcp_types import RequestParams
from mcp_types.jsonrpc import INVALID_PARAMS

from acm import __version__
from acm.domain.audit import AuditService
from acm.domain.backlog import BacklogService
from acm.domain.context import ContextService
from acm.domain.errors import AcmError, Forbidden
from acm.domain.projects import ProjectService
from acm.inference.ports import DecisionRequest
from acm.inference.router import EngineRouter
from acm.skills_catalog import SKILL_PREFIX, SkillCatalog

T = TypeVar("T")
SKILLS_EXTENSION = "io.modelcontextprotocol/skills"

INSTRUCTIONS = (
    "Estás conectado a ACM (Agile Context Manager), la memoria de estado y gobernanza de tus proyectos.\n"
    "- ANTES DE OPERAR, descarga y lee TODAS las skills de ACM: si tu cliente soporta la extensión "
    "io.modelcontextprotocol/skills usa skills/list y resources/read (URIs skill://acm/...); si no, usa las "
    "herramientas acm_skills_list y acm_skill_get. Empieza por la skill acm-schema.\n"
    "- ACM no recuerda un 'proyecto activo': pasa SIEMPRE el parámetro project_id en cada herramienta de proyecto.\n"
    "- Obtén los project_id disponibles con acm_project_list; crea uno nuevo con acm_project_create.\n"
    "- Cada respuesta repite el project_id sobre el que actuó: compruébalo.\n"
    "- Ahorra tokens: pide el contexto de una historia con acm_context_compact y delega decisiones tipadas "
    "(sí/no, clasificar, puntuar) con acm_decide.\n"
    "- Los errores empiezan por un código (INVALID_ARGUMENT, NOT_FOUND, ALREADY_EXISTS, FORBIDDEN, "
    "FAILED_PRECONDITION, STORAGE_ERROR, ENGINE_UNAVAILABLE, ENGINE_ERROR) seguido del motivo; "
    "corrige la llamada según el motivo."
)


class SkillsListParams(RequestParams):
    pass


class SkillsGetParams(RequestParams):
    uri: str


def build_mcp_server(
    service: ProjectService,
    principal: Callable[[], str],
    catalog: SkillCatalog | None = None,
    engines: EngineRouter | None = None,
) -> MCPServer:
    """Crea el servidor MCP.

    `principal` resuelve la identidad del llamante (SPRINT-001/002: configuración; EPIC-20: token verificado).
    `engines` es el router de inferencia; por defecto, solo el motor de reglas (sin modelos).
    """
    catalog = catalog if catalog is not None else SkillCatalog()
    engines = engines if engines is not None else EngineRouter(service)
    backlog = BacklogService(service, engines)
    context = ContextService(service, backlog, engines)
    audit = AuditService(service)
    bus = InMemorySubscriptionBus()

    async def audited(operation: str, arguments: dict[str, Any], fn: Callable[..., T], *args: Any) -> T:
        who = principal()
        start = time.perf_counter()
        try:
            result = await anyio.to_thread.run_sync(partial(fn, *args))
        except Exception as exc:
            elapsed = (time.perf_counter() - start) * 1000
            record = partial(
                audit.record,
                principal=who,
                operation=operation,
                arguments=arguments,
                status="error",
                duration_ms=elapsed,
                error=str(exc) or type(exc).__name__,
            )
            await anyio.to_thread.run_sync(record)
            raise
        elapsed = (time.perf_counter() - start) * 1000
        record = partial(
            audit.record,
            principal=who,
            operation=operation,
            arguments=arguments,
            status="ok",
            duration_ms=elapsed,
            result=result,
        )
        await anyio.to_thread.run_sync(record)
        return result

    async def call(operation: str, arguments: dict[str, Any], fn: Callable[..., T], *args: Any) -> T:
        try:
            return await audited(operation, arguments, fn, *args)
        except AcmError as exc:
            raise ToolError(str(exc)) from exc

    # --------------------------------------------------------- extensión Skills
    class AcmSkillsExtension(Extension):
        identifier = SKILLS_EXTENSION

        def settings(self) -> dict[str, Any]:
            return {"directoryRead": False}

        def methods(self) -> list[MethodBinding]:
            return [
                MethodBinding("skills/list", SkillsListParams, self._list),
                MethodBinding("skills/get", SkillsGetParams, self._get),
            ]

        async def _list(self, ctx: Any, params: SkillsListParams) -> dict[str, Any]:
            skills = await audited("skills/list", {}, catalog.entries)
            return {"resultType": "complete", "skills": skills, "ttlMs": 300000, "cacheScope": "public"}

        async def _get(self, ctx: Any, params: SkillsGetParams) -> dict[str, Any]:
            def find() -> dict[str, Any]:
                skill = catalog.get_by_uri(params.uri)
                if skill is None:
                    raise MCPError(INVALID_PARAMS, f"Unknown skill: {params.uri}")
                return skill.entry()

            entry = await audited("skills/get", {"uri": params.uri}, find)
            return {"resultType": "complete", "skill": entry, "ttlMs": 300000, "cacheScope": "public"}

    server = MCPServer(
        name="acm", version=__version__, instructions=INSTRUCTIONS, extensions=[AcmSkillsExtension()], subscriptions=bus
    )

    @server.resource(f"{SKILL_PREFIX}/{{skill}}/{{filename}}", name="acm-skill-file", mime_type="text/markdown")
    async def skill_file(skill: str, filename: str) -> str:
        """Archivo de una skill de ACM, leído del catálogo vigente (una skill retirada deja de existir)."""
        uri = f"{SKILL_PREFIX}/{skill}/{filename}"

        def read() -> str:
            f = catalog.file(skill, filename)
            if f is None:
                raise ResourceNotFoundError(f"Unknown skill resource: {uri}")
            return f.text

        return await audited("resources/read", {"uri": uri}, read)

    # ------------------------------------------------ skills: respaldo y gestión
    @server.tool()
    async def acm_skills_list() -> list[dict[str, Any]]:
        """Lista las skills de ACM (uri, frontmatter con versión, digest y tamaño de cada archivo)."""
        return await call("acm_skills_list", {}, catalog.entries)

    @server.tool()
    async def acm_skill_get(name: str) -> dict[str, Any]:
        """Devuelve todos los archivos de una skill de ACM (respaldo de skills/get + resources/read)."""

        def get() -> dict[str, Any]:
            skill = catalog.skills.get(name)
            if skill is None:
                raise ToolError(f"NOT_FOUND: skill {name!r} no existe; usa acm_skills_list")
            return {**skill.entry(), "files": {f.uri: f.text for f in skill.files}}

        return await call("acm_skill_get", {"name": name}, get)

    @server.tool()
    async def acm_skills_reload() -> dict[str, Any]:
        """(admin) Relee el catálogo de skills; si cambia, notifica resources/list_changed a los suscritos."""

        def reload() -> dict[str, Any]:
            with service.global_db.read() as conn:
                if service._principal_role(conn, principal()) != "admin":
                    raise Forbidden("solo un admin puede recargar el catálogo de skills")
            changed = catalog.reload()
            return {"changed": changed, "skills": sorted(catalog.skills), "rejected": catalog.rejected}

        result = await call("acm_skills_reload", {}, reload)
        if result["changed"]:
            await bus.publish(ResourcesListChanged())
        return result

    # ---------------------------------------------------------------- proyectos
    @server.tool()
    async def acm_project_create(key: str, name: str, description: str = "") -> dict[str, Any]:
        """Crea un proyecto ACM con su propia base SQLite. `key` es el project_id: ^[a-z][a-z0-9-]{1,39}$."""
        args = {"key": key, "name": name, "description": description}
        return await call("acm_project_create", args, service.create, principal(), key, name, description)

    @server.tool()
    async def acm_project_list() -> list[dict[str, Any]]:
        """Lista los proyectos a los que tienes acceso (con su project_id)."""
        return await call("acm_project_list", {}, service.list_for, principal())

    @server.tool()
    async def acm_project_open(project_id: str) -> dict[str, Any]:
        """Abre un proyecto: devuelve metadatos, tu rol, versión de esquema y configuración efectiva."""
        return await call("acm_project_open", {"project_id": project_id}, service.open, principal(), project_id)

    @server.tool()
    async def acm_project_config_get(project_id: str) -> dict[str, Any]:
        """Devuelve cada parámetro de configuración del proyecto con su valor actual, por defecto y permitido."""
        args = {"project_id": project_id}
        return await call("acm_project_config_get", args, service.get_config, principal(), project_id)

    @server.tool()
    async def acm_project_config_set(project_id: str, changes: dict[str, Any]) -> dict[str, Any]:
        """Modifica parámetros ({parámetro: valor}). Valida todo antes de guardar; indica cuáles requieren recarga."""
        args = {"project_id": project_id, "changes": changes}
        return await call("acm_project_config_set", args, service.set_config, principal(), project_id, changes)

    @server.tool()
    async def acm_system_info() -> dict[str, Any]:
        """Estado de la plataforma: versión, esquema global, nº de proyectos, PRAGMAs y skills activas/rechazadas."""

        def info() -> dict[str, Any]:
            return {
                "acm_version": __version__,
                **service.system_info(),
                "skills": sorted(catalog.skills),
                "skills_rejected": catalog.rejected,
            }

        return await call("acm_system_info", {}, info)

    @server.tool()
    async def acm_audit_list(
        limit: int = 50, principal_id: str | None = None, operation: str | None = None, project_id: str | None = None
    ) -> dict[str, Any]:
        """(admin) Últimas invocaciones MCP auditadas: quién, operación, argumentos, resultado, estado, duración."""
        args = {"limit": limit, "principal_id": principal_id, "operation": operation, "project_id": project_id}
        fn = partial(
            audit.list,
            principal(),
            limit=limit,
            filter_principal=principal_id,
            operation=operation,
            project_id=project_id,
        )
        return await call("acm_audit_list", args, fn)

    # ------------------------------------------------------------------ backlog
    @server.tool()
    async def acm_requirement_create(
        project_id: str, title: str, description: str = "", requirement_id: str | None = None
    ) -> dict[str, Any]:
        """Registra un requisito (REQ-NNN). `requirement_id` opcional para importar IDs existentes."""
        args = {"project_id": project_id, "title": title, "description": description, "requirement_id": requirement_id}
        return await call(
            "acm_requirement_create",
            args,
            backlog.create_requirement,
            principal(),
            project_id,
            title,
            description,
            requirement_id,
        )

    @server.tool()
    async def acm_requirement_list(project_id: str) -> dict[str, Any]:
        """Lista los requisitos del proyecto."""
        args = {"project_id": project_id}
        return await call("acm_requirement_list", args, backlog.list_requirements, principal(), project_id)

    @server.tool()
    async def acm_requirement_trace(project_id: str, requirement_id: str) -> dict[str, Any]:
        """Trazabilidad de un requisito: sus épicas, las features de esas épicas y las historias que lo implementan."""
        args = {"project_id": project_id, "requirement_id": requirement_id}
        return await call(
            "acm_requirement_trace", args, backlog.trace_requirement, principal(), project_id, requirement_id
        )

    @server.tool()
    async def acm_epic_create(
        project_id: str,
        title: str,
        objective: str,
        scope: str,
        requirement_ids: list[str] | None = None,
        epic_id: str | None = None,
    ) -> dict[str, Any]:
        """Crea una épica (EPIC-NN) con objetivo y alcance obligatorios, opcionalmente asociada a requisitos."""
        args = {
            "project_id": project_id,
            "title": title,
            "objective": objective,
            "scope": scope,
            "requirement_ids": requirement_ids,
            "epic_id": epic_id,
        }
        return await call(
            "acm_epic_create",
            args,
            backlog.create_epic,
            principal(),
            project_id,
            title,
            objective,
            scope,
            requirement_ids,
            epic_id,
        )

    @server.tool()
    async def acm_epic_link_requirements(project_id: str, epic_id: str, requirement_ids: list[str]) -> dict[str, Any]:
        """Asocia requisitos existentes a una épica."""
        args = {"project_id": project_id, "epic_id": epic_id, "requirement_ids": requirement_ids}
        return await call(
            "acm_epic_link_requirements",
            args,
            backlog.link_epic_requirements,
            principal(),
            project_id,
            epic_id,
            requirement_ids,
        )

    @server.tool()
    async def acm_epic_get(project_id: str, epic_id: str) -> dict[str, Any]:
        """Devuelve una épica con sus requisitos y sus features (y las historias de cada feature)."""
        args = {"project_id": project_id, "epic_id": epic_id}
        return await call("acm_epic_get", args, backlog.get_epic, principal(), project_id, epic_id)

    @server.tool()
    async def acm_epic_list(project_id: str) -> dict[str, Any]:
        """Lista las épicas del proyecto con sus features e historias."""
        return await call("acm_epic_list", {"project_id": project_id}, backlog.list_epics, principal(), project_id)

    @server.tool()
    async def acm_epic_confirm_coverage(project_id: str, epic_id: str) -> dict[str, Any]:
        """Confirma que las features activas de la épica cubren su objetivo (requiere al menos una feature activa)."""
        args = {"project_id": project_id, "epic_id": epic_id}
        return await call(
            "acm_epic_confirm_coverage", args, backlog.confirm_epic_coverage, principal(), project_id, epic_id
        )

    @server.tool()
    async def acm_feature_create(
        project_id: str, epic_id: str, title: str, description: str = "", feature_id: str | None = None
    ) -> dict[str, Any]:
        """Crea una feature (FEAT-NN.MM) dentro de una épica."""
        args = {
            "project_id": project_id,
            "epic_id": epic_id,
            "title": title,
            "description": description,
            "feature_id": feature_id,
        }
        return await call(
            "acm_feature_create",
            args,
            backlog.create_feature,
            principal(),
            project_id,
            epic_id,
            title,
            description,
            feature_id,
        )

    @server.tool()
    async def acm_feature_split(project_id: str, feature_id: str, parts: list[dict[str, Any]]) -> dict[str, Any]:
        """Divide una feature en ≥2: parts=[{title, description?, story_ids}] repartiendo todas sus historias."""
        args = {"project_id": project_id, "feature_id": feature_id, "parts": parts}
        return await call("acm_feature_split", args, backlog.split_feature, principal(), project_id, feature_id, parts)

    @server.tool()
    async def acm_story_create(
        project_id: str,
        feature_id: str,
        as_a: str,
        i_want: str,
        so_that: str,
        requirement_ids: list[str],
        acceptance_criteria: list[str] | None = None,
        kind: str = "user_story",
        technical_reason: str = "",
        story_id: str | None = None,
    ) -> dict[str, Any]:
        """Crea una historia (US-NN.MM): actor (as_a), acción (i_want), valor (so_that), ≥1 requisito de origen y
        criterios de aceptación binarios. Una tarea técnica solo con kind='technical' y technical_reason."""
        args = {
            "project_id": project_id,
            "feature_id": feature_id,
            "as_a": as_a,
            "i_want": i_want,
            "so_that": so_that,
            "requirement_ids": requirement_ids,
            "acceptance_criteria": acceptance_criteria,
            "kind": kind,
            "technical_reason": technical_reason,
            "story_id": story_id,
        }
        return await call(
            "acm_story_create",
            args,
            backlog.create_story,
            principal(),
            project_id,
            feature_id,
            as_a,
            i_want,
            so_that,
            requirement_ids,
            acceptance_criteria,
            kind,
            technical_reason,
            story_id,
        )

    @server.tool()
    async def acm_story_add_criteria(project_id: str, story_id: str, criteria: list[str]) -> dict[str, Any]:
        """Añade criterios de aceptación (CA-NN) a una historia."""
        args = {"project_id": project_id, "story_id": story_id, "criteria": criteria}
        return await call(
            "acm_story_add_criteria", args, backlog.add_criteria, principal(), project_id, story_id, criteria
        )

    @server.tool()
    async def acm_story_get(project_id: str, story_id: str) -> dict[str, Any]:
        """Devuelve una historia con sus requisitos de origen y criterios de aceptación."""
        args = {"project_id": project_id, "story_id": story_id}
        return await call("acm_story_get", args, backlog.get_story, principal(), project_id, story_id)

    @server.tool()
    async def acm_story_mark_ready(project_id: str, story_id: str) -> dict[str, Any]:
        """Pasa una historia de PLANNED a READY si tiene actor, acción, valor, requisito y criterios."""
        args = {"project_id": project_id, "story_id": story_id}
        return await call("acm_story_mark_ready", args, backlog.mark_ready, principal(), project_id, story_id)

    @server.tool()
    async def acm_backlog_audit(project_id: str) -> dict[str, Any]:
        """Huecos de trazabilidad: requisitos huérfanos, épicas/features vacías, historias sin CA."""
        return await call("acm_backlog_audit", {"project_id": project_id}, backlog.audit, principal(), project_id)

    # ------------------------------------------------------------------ segundo cerebro (EPIC-35)
    @server.tool()
    async def acm_decide(
        project_id: str, purpose: str, questions: dict[str, Any], state: dict[str, Any] | str
    ) -> dict[str, Any]:
        """Delega una decisión tipada (noul = sí/no, choice = clasificar, score = puntuar) en el motor de decisión.

        questions: {clave: {"type": "noul"|"choice"|"score", "instructions": str, "criteria": ...}}. Respuesta con
        probabilidades, el motor que decidió (`engine`), `calibrated` y `fallback_from`. Ver skill acm-schema.
        """
        args = {"project_id": project_id, "purpose": purpose, "questions": questions, "state": state}

        def decide() -> dict[str, Any]:
            routed = engines.decide(principal(), DecisionRequest.from_json(project_id, purpose, state, questions))
            return {"project_id": project_id, "call_id": routed.call_id, **routed.result.to_json()}

        return await call("acm_decide", args, decide)

    @server.tool()
    async def acm_context_compact(project_id: str, story_id: str, budget_tokens: int | None = None) -> dict[str, Any]:
        """Contexto compacto de una historia (historia, CA, requisitos, feature, épica, historias hermanas).

        Cada sección lleva sus fuentes. Si supera `budget_tokens` (por defecto, context.max_tokens del proyecto) y hay
        un modelo local, resume las secciones de apoyo. Indica tokens entregados, equivalente completo y método.
        """
        args = {"project_id": project_id, "story_id": story_id, "budget_tokens": budget_tokens}
        fn = partial(context.compact, principal(), project_id, story_id, budget_tokens)
        return await call("acm_context_compact", args, fn)

    @server.tool()
    async def acm_engines_list() -> dict[str, Any]:
        """Motores de inferencia registrados, su último estado, modelos detectados y preguntas que cubren las reglas."""

        def listing() -> dict[str, Any]:
            rules = next(e for e in engines.registry.decision if e.provider == "rules")
            return {"engines": engines.registry.list(), "rules": rules.catalog()}  # type: ignore[attr-defined]

        return await call("acm_engines_list", {}, listing)

    @server.tool()
    async def acm_engines_refresh() -> dict[str, Any]:
        """(admin) Comprueba la salud de cada motor y detecta los modelos disponibles en su runtime."""

        def refresh() -> dict[str, Any]:
            with service.global_db.read() as conn:
                if service._principal_role(conn, principal()) != "admin":
                    raise Forbidden("solo un admin puede refrescar los motores de inferencia")
            return {"engines": engines.registry.refresh()}

        return await call("acm_engines_refresh", {}, refresh)

    @server.tool()
    async def acm_savings_report(principal_id: str | None = None, project_id: str | None = None) -> dict[str, Any]:
        """(admin) Tokens ahorrados por el contexto compacto, agregados por agente y proyecto, con el método usado."""
        args = {"principal_id": principal_id, "project_id": project_id}
        fn = partial(context.savings_report, principal(), filter_principal=principal_id, project_id=project_id)
        return await call("acm_savings_report", args, fn)

    server.acm_catalog = catalog  # type: ignore[attr-defined]
    server.acm_engines = engines  # type: ignore[attr-defined]
    return server
