"""Conversación con el modelo local y agente interno de Ollama (US-22.10, US-22.11).

Un agente IA (o una persona desde la interfaz) delega trabajo en el modelo local de Ollama sin gastar sus propios
tokens en reenviar contexto:

- **Hilo conservado** (US-22.10): cada hilo pertenece a un proyecto y a quien lo abrió. ACM guarda cada mensaje y, en
  el siguiente, añade la conversación anterior (los últimos `HISTORY_MAX` mensajes). Quien llama solo envía el
  mensaje nuevo.
- **Agente interno con herramientas** (US-22.11): el modelo recibe unas instrucciones que le explican el modelo de ACM
  y herramientas de **solo lectura** (`TOOLS`): resumen del backlog, historia, búsqueda, trazabilidad, sprints,
  gobernanza y contexto compacto. Si el modelo pide una, ACM la ejecuta con los permisos de quien abrió el hilo y le
  devuelve el resultado (tool calling de Ollama). Como mucho `MAX_TOOL_ROUNDS` rondas por mensaje.

Prompt versionado: `CHAT_PROMPT_VERSION` (10_IA/prompt_versioning.md).
"""

from __future__ import annotations

import json
import time
from datetime import UTC, datetime
from typing import Any

from acm.domain.backlog import BacklogService
from acm.domain.context import ContextService
from acm.domain.errors import AcmError, InvalidArgument, NotFound
from acm.domain.projects import ProjectService
from acm.domain.sprints import SprintService
from acm.domain.watchdog import WatchdogService
from acm.inference.ports import EngineError, EngineUnavailable
from acm.inference.router import EngineRouter

PURPOSE = "agent.chat"
CHAT_PROMPT_VERSION = "acm-chat@v1"
MAX_TOOL_ROUNDS = 5
HISTORY_MAX = 30
MESSAGE_MAX = 20_000
TOOL_RESULT_MAX = 6_000
REPLY_MAX_TOKENS = 1_024
SYSTEM_PROMPT = (
    "Eres el asistente interno de ACM (Agile Context Manager) para el proyecto {project_id} «{name}». ACM guarda de "
    "cada proyecto: requisitos (REQ-NNN), épicas (EPIC-NN) con features (FEAT-NN.MM), historias (US-NN.MM) con su "
    "estado en el Kanban (PLANNED, READY, IN_PROGRESS, BLOCKED, IMPLEMENTED, TESTING, VERIFIED, DONE…) y sus criterios "
    "de aceptación (CA-NN), sprints (SPRINT-NN) y la gobernanza (semáforo, hallazgos, informe y acciones del "
    "supervisor ágil). Usa las herramientas para consultar esos datos antes de responder: empieza por "
    "`backlog_overview` si no sabes qué hay. No inventes datos: si algo no está en ACM, dilo. Cita los "
    "identificadores. Responde en el idioma de quien pregunta, de forma breve y concreta."
)


def _fn(
    name: str, description: str, properties: dict[str, Any] | None = None, required: list[str] | None = None
) -> dict:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {"type": "object", "properties": properties or {}, "required": required or []},
        },
    }


STORY_ID = {"story_id": {"type": "string", "description": "Identificador de la historia, p. ej. US-01.02"}}
TOOLS = [
    _fn("backlog_overview", "Resumen del backlog: requisitos, épicas con features e historias con estado y sprint."),
    _fn(
        "get_story",
        "Una historia completa: enunciado, criterios, requisitos, estado e historial.",
        STORY_ID,
        ["story_id"],
    ),
    _fn(
        "search_stories",
        "Busca historias por texto (y opcionalmente por estado).",
        {"text": {"type": "string"}, "status": {"type": "string", "description": "Estado, p. ej. IN_PROGRESS"}},
        ["text"],
    ),
    _fn(
        "trace_requirement",
        "Trazabilidad de un requisito: épicas e historias que lo implementan.",
        {"requirement_id": {"type": "string", "description": "p. ej. REQ-001"}},
        ["requirement_id"],
    ),
    _fn("list_sprints", "Sprints con objetivo, fechas, estado, historias, carga y resumen de cierre."),
    _fn("governance", "Última auditoría: semáforo, hallazgos, acciones e informe del supervisor ágil."),
    _fn(
        "story_context",
        "Contexto compacto de una historia (épica, feature, requisitos, hermanas).",
        STORY_ID,
        ["story_id"],
    ),
]
TOOL_NAMES = {t["function"]["name"] for t in TOOLS}


def _now() -> str:
    return datetime.now(UTC).isoformat()


class ChatService:
    def __init__(self, projects: ProjectService, backlog: BacklogService, engines: EngineRouter):
        self.projects = projects
        self.backlog = backlog
        self.engines = engines
        self.sprints = SprintService(backlog)
        self.context = ContextService(projects, backlog, engines)
        self.watchdog = WatchdogService(projects, backlog, engines)

    # ------------------------------------------------------------------ herramientas (solo lectura)
    def _tool(self, principal: str, project_id: str, name: str, args: dict[str, Any]) -> Any:
        if name == "backlog_overview":
            reqs = self.backlog.list_requirements(principal, project_id)["requirements"]
            epics = self.backlog.list_epics(principal, project_id)["epics"]
            stories = self.backlog.list_stories(principal, project_id)["stories"]
            return {
                "requirements": [{"id": r["id"], "title": r["title"]} for r in reqs],
                "epics": [
                    {
                        "id": e["id"],
                        "title": e["title"],
                        "features": [
                            {"id": f["id"], "title": f["title"], "stories": f["story_ids"]} for f in e["features"]
                        ],
                    }
                    for e in epics
                ],
                "stories": [
                    {
                        "id": s["id"],
                        "status": s["status"],
                        "i_want": s["i_want"],
                        "sprint": s["sprint_id"],
                        "criteria": len(s["acceptance_criteria"]),
                    }
                    for s in stories
                ],
            }
        if name == "get_story":
            story = self.backlog.get_story(principal, project_id, str(args.get("story_id", "")))
            return story | {"history": self.backlog.status_history(principal, project_id, story["id"])["history"]}
        if name == "search_stories":
            text = str(args.get("text", "")).lower()
            status = args.get("status")
            return [
                {
                    "id": s["id"],
                    "status": s["status"],
                    "as_a": s["as_a"],
                    "i_want": s["i_want"],
                    "so_that": s["so_that"],
                }
                for s in self.backlog.list_stories(principal, project_id)["stories"]
                if text in f"{s['id']} {s['as_a']} {s['i_want']} {s['so_that']}".lower()
                and (not status or s["status"] == status)
            ]
        if name == "trace_requirement":
            return self.backlog.trace_requirement(principal, project_id, str(args.get("requirement_id", "")))
        if name == "list_sprints":
            return [
                {
                    k: s[k]
                    for k in (
                        "id",
                        "name",
                        "goal",
                        "start_date",
                        "end_date",
                        "status",
                        "capacity",
                        "load",
                        "story_ids",
                        "stories_by_status",
                        "summary",
                    )
                }
                for s in self.sprints.list(principal, project_id)["sprints"]
            ]
        if name == "governance":
            runs = self.watchdog.history(principal, project_id, 1)["runs"]
            if not runs:
                return {"semaphore": "UNKNOWN", "message": "todavía no se ha auditado este proyecto"}
            run = runs[0]
            return {k: run[k] for k in ("ts", "semaphore", "critical", "warning", "review", "info")} | {
                "findings": run["findings"][:30],
                "actions": run["actions"][:30],
                "report": run["report"][:3000],
            }
        if name == "story_context":
            return self.context.compact(principal, project_id, str(args.get("story_id", "")))
        raise InvalidArgument(f"herramienta desconocida {name!r}; disponibles: {sorted(TOOL_NAMES)}", field="tool")

    def _run_tool(self, principal: str, project_id: str, call: Any) -> tuple[str, dict[str, Any], str, bool]:
        fn = call.get("function", {}) if isinstance(call, dict) else {}
        name = str(fn.get("name", ""))
        raw = fn.get("arguments", {})
        if isinstance(raw, str):  # algunos modelos devuelven los argumentos como texto JSON
            try:
                raw = json.loads(raw or "{}")
            except ValueError:
                raw = {}
        args = raw if isinstance(raw, dict) else {}
        try:
            result: Any = self._tool(principal, project_id, name, args)
            ok = True
        except AcmError as exc:
            result, ok = {"error": str(exc)}, False
        text = json.dumps(result, ensure_ascii=False, default=str)
        if len(text) > TOOL_RESULT_MAX:
            text = text[:TOOL_RESULT_MAX] + "… [truncado]"
        return name, args, text, ok

    # ------------------------------------------------------------------ hilos
    def _thread(self, conn: Any, principal: str, thread_id: str, is_admin: bool) -> dict[str, Any]:
        row = conn.execute("SELECT * FROM chat_threads WHERE id = ?", (thread_id,)).fetchone()
        if row is None or (row["created_by"] != principal and not is_admin):
            raise NotFound(f"el hilo {thread_id!r} no existe o no es tuyo", field="thread_id")
        return dict(row)

    def _is_admin(self, principal: str) -> bool:
        with self.projects.global_db.read() as conn:
            return self.projects._principal_role(conn, principal) == "admin"

    def threads(self, principal: str, project_id: str) -> dict[str, Any]:
        admin = self._is_admin(principal)
        with self.backlog._db(principal, project_id).read() as conn:
            rows = conn.execute(
                "SELECT t.*, (SELECT COUNT(*) FROM chat_messages m WHERE m.thread_id = t.id) AS messages "
                "FROM chat_threads t WHERE ? OR t.created_by = ? ORDER BY t.updated_at DESC",
                (int(admin), principal),
            ).fetchall()
        return {"project_id": project_id, "threads": [dict(r) for r in rows]}

    def get(self, principal: str, project_id: str, thread_id: str) -> dict[str, Any]:
        admin = self._is_admin(principal)
        with self.backlog._db(principal, project_id).read() as conn:
            thread = self._thread(conn, principal, thread_id, admin)
            messages = conn.execute(
                "SELECT role, content, tool_name, tool_calls_json, model, principal, created_at FROM chat_messages "
                "WHERE thread_id = ? ORDER BY id",
                (thread_id,),
            ).fetchall()
        return {
            "project_id": project_id,
            **thread,
            "messages": [
                {
                    **{k: m[k] for k in ("role", "content", "tool_name", "model", "principal", "created_at")},
                    "tool_calls": json.loads(m["tool_calls_json"]),
                }
                for m in messages
            ],
        }

    # ------------------------------------------------------------------ enviar un mensaje
    def send(
        self, principal: str, project_id: str, message: Any, thread_id: Any = None, title: Any = None
    ) -> dict[str, Any]:
        if not isinstance(message, str) or not message.strip() or len(message) > MESSAGE_MAX:
            raise InvalidArgument(f"debe ser un texto de 1 a {MESSAGE_MAX} caracteres", field="message")
        if thread_id is not None and not isinstance(thread_id, str):
            raise InvalidArgument("debe ser el identificador de un hilo", field="thread_id")
        engine = next((e for e in self.engines.registry.generation if e.provider == "ollama"), None)
        if engine is None:
            raise EngineUnavailable(
                "no hay un Ollama configurado (ACM_OLLAMA_URL): no hay modelo local con el que hablar"
            )
        model = engine.require_model()
        admin = self._is_admin(principal)
        db = self.backlog._db(principal, project_id, write=True)
        project = self.projects.open(principal, project_id)
        with db.read() as conn:
            history: list[dict[str, Any]] = []
            if thread_id is not None:
                self._thread(conn, principal, thread_id, admin)
                rows = conn.execute(
                    "SELECT role, content, tool_name, tool_calls_json FROM chat_messages WHERE thread_id = ? "
                    "ORDER BY id DESC LIMIT ?",
                    (thread_id, HISTORY_MAX),
                ).fetchall()
                for r in reversed(rows):
                    msg: dict[str, Any] = {"role": r["role"], "content": r["content"]}
                    if r["role"] == "tool":
                        msg["tool_name"] = r["tool_name"]
                    calls = json.loads(r["tool_calls_json"])
                    if calls:
                        msg["tool_calls"] = calls
                    history.append(msg)
        system = {"role": "system", "content": SYSTEM_PROMPT.format(project_id=project_id, name=project["name"])}
        messages = [system, *history, {"role": "user", "content": message.strip()}]
        new: list[dict[str, Any]] = [{"role": "user", "content": message.strip(), "tool_name": "", "tool_calls": []}]
        used: list[dict[str, Any]] = []
        usage = {"input_tokens": 0, "output_tokens": 0}
        start = time.perf_counter()
        reply = ""
        try:
            for round_ in range(MAX_TOOL_ROUNDS + 1):
                tools = TOOLS if round_ < MAX_TOOL_ROUNDS else None  # última ronda: debe responder sin herramientas
                body = engine.client.chat(model, messages, max_tokens=REPLY_MAX_TOKENS, tools=tools)
                for k, src in (("input_tokens", "prompt_eval_count"), ("output_tokens", "eval_count")):
                    usage[k] += int(body.get(src) or 0)
                out = body.get("message") if isinstance(body.get("message"), dict) else {}
                calls = out.get("tool_calls") if tools else None
                if calls:
                    content = str(out.get("content") or "")
                    messages.append({"role": "assistant", "content": content, "tool_calls": calls})
                    new.append({"role": "assistant", "content": content, "tool_name": "", "tool_calls": calls})
                    for call in calls:
                        name, args, text, ok = self._run_tool(principal, project_id, call)
                        used.append({"name": name, "arguments": args, "ok": ok})
                        messages.append({"role": "tool", "content": text, "tool_name": name})
                        new.append({"role": "tool", "content": text, "tool_name": name, "tool_calls": []})
                    continue
                reply = str(out.get("content") or "").strip()
                if body.get("done") is not True or not reply:
                    raise EngineError(f"ollama:{model} no devolvió una respuesta completa (done={body.get('done')!r})")
                break
        except (EngineUnavailable, EngineError) as exc:
            self.engines._log(
                principal,
                project_id,
                "generation",
                PURPOSE,
                "",
                None,
                "error",
                str(exc),
                (time.perf_counter() - start) * 1000,
                {},
            )
            raise
        call_id = self.engines._log(
            principal,
            project_id,
            "generation",
            PURPOSE,
            f"ollama:{model}",
            None,
            "ok",
            "",
            (time.perf_counter() - start) * 1000,
            usage,
        )
        new.append({"role": "assistant", "content": reply, "tool_name": "", "tool_calls": []})
        now = _now()
        with db.write() as conn:
            if thread_id is None:
                n = conn.execute("SELECT COUNT(*) FROM chat_threads").fetchone()[0] + 1
                thread_id = f"TH-{n:03d}"
                name = title.strip()[:120] if isinstance(title, str) and title.strip() else message.strip()[:60]
                conn.execute(
                    "INSERT INTO chat_threads(id, title, created_by, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                    (thread_id, name, principal, now, now),
                )
            else:
                conn.execute("UPDATE chat_threads SET updated_at = ? WHERE id = ?", (now, thread_id))
            conn.executemany(
                "INSERT INTO chat_messages(thread_id, role, content, tool_name, tool_calls_json, model, principal, "
                "created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                [
                    (
                        thread_id,
                        m["role"],
                        m["content"],
                        m["tool_name"],
                        json.dumps(m["tool_calls"], ensure_ascii=False),
                        "" if m["role"] == "user" else model,
                        principal,
                        now,
                    )
                    for m in new
                ],
            )
        return {
            "project_id": project_id,
            "thread_id": thread_id,
            "reply": reply,
            "model": model,
            "engine": f"ollama:{model}",
            "tool_calls": used,
            "context_messages": len(history),
            "usage": usage,
            "call_id": call_id,
        }
