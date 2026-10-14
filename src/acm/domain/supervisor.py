"""Supervisor ágil autónomo (SPRINT-008): ACM usa sus propios motores para vigilar el trabajo de cada proyecto.

Forma parte de cada ejecución del Watchdog (a demanda y periódica) y hace cuatro cosas:

1. **Revisa las historias** vivas con la interfaz de decisión (purpose `agile.story_review`): ¿cumple INVEST?, ¿sus
   criterios son verificables?, ¿es demasiado grande? Lo responde el primer motor que lo cubra según el orden del
   proyecto (JEV calibrado; Ollama sin calibrar). La revisión se guarda y no se repite mientras la historia no cambie.
2. **Vigila sprints y Kanban** con reglas deterministas: sprint vencido, sobrecargado o vacío, historias sin refinar
   en un sprint activo, historias canceladas dentro de un sprint, WIP por encima del límite, historias estancadas y
   trabajo en curso fuera del sprint activo. El riesgo de no cumplir el objetivo del sprint lo decide un motor
   (purpose `agile.sprint_review`).
3. **Actúa** según `supervisor.mode`: `off`, `propose` (solo propone) o `apply_safe` (aplica los cambios seguros).
   Un cambio es seguro si está en la lista cerrada `SAFE_ACTIONS` (todos reversibles, nunca DONE, cancelar ni
   borrar), lo decide un motor calibrado (reglas o JEV) y su confianza alcanza `supervisor.min_confidence_pct`.
   Lo demás queda como propuesta. Las acciones se ejecutan y auditan como el agente `acm-supervisor`.
4. **Informa**: lo hecho, lo pendiente, las incongruencias y las acciones. Con un motor de generación (Ollama) el
   informe se redacta en lenguaje natural (purpose `agile.report`); sin él, ACM lo compone sin modelo.
"""

from __future__ import annotations

import json
import time
from datetime import UTC, date, datetime, timedelta
from typing import Any

from acm.domain.audit import AuditService
from acm.domain.backlog import BacklogService
from acm.domain.errors import AcmError, FailedPrecondition
from acm.domain.projects import ProjectService
from acm.domain.sprints import SprintService
from acm.inference.ports import Answer, DecisionRequest, GenerationRequest, Question
from acm.inference.router import EngineRouter
from acm.inference.rules import story_checks

SUPERVISOR = "acm-supervisor"
STORY_REVIEW = "agile.story_review"
SPRINT_REVIEW = "agile.sprint_review"
REPORT = "agile.report"
REVIEWABLE = ("PLANNED", "READY", "IN_PROGRESS", "BLOCKED")
SAFE_ACTIONS = ("story.mark_ready", "story.back_to_planned", "sprint.remove_story")
REPORT_MAX_TOKENS = 700

STORY_REVIEW_QUESTIONS: dict[str, Question] = {
    "invest": Question(
        "noul",
        "¿La historia cumple INVEST: independiente, negociable, valiosa, estimable, pequeña y testeable?",
        {"true": "cumple INVEST", "false": "incumple alguno de los criterios INVEST"},
    ),
    "criteria_verifiable": Question(
        "noul",
        "¿Cada criterio de aceptación se puede comprobar de forma objetiva, con un resultado de pasa o falla?",
        {"true": "todos los criterios son verificables", "false": "algún criterio es vago o no verificable"},
    ),
    "size": Question(
        "choice",
        "¿Qué tamaño tiene la historia?",
        {
            "small": "cabe en pocos días de trabajo",
            "medium": "cabe en un sprint",
            "large": "demasiado grande para un sprint: conviene dividirla",
        },
    ),
}
SPRINT_RISK_QUESTIONS: dict[str, Question] = {
    "risk": Question(
        "score",
        "Con el avance actual y el tiempo que queda, ¿qué riesgo hay de no cumplir el objetivo del sprint?",
        ["bajo", "medio", "alto"],
    ),
}
REPORT_SYSTEM_PROMPT = (
    "Eres el supervisor ágil de ACM. Redacta en español, en Markdown y en menos de 250 palabras, un informe para el "
    "equipo con cuatro apartados: Hecho, Pendiente, Incongruencias y Acciones. Usa solo los datos que recibes, cita "
    "los identificadores (US-…, SPRINT-…) y no inventes nada."
)
REPORT_PROMPT_VERSION = "agile-report@v1"


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _finding(code: str, severity: str, target: str, message: str, source: str, **extra: Any) -> dict[str, Any]:
    return {"code": code, "severity": severity, "target": target, "message": message, "source": source, **extra}


def _judgement(answer: dict[str, Any]) -> tuple[bool, float | None]:
    """(¿respuesta afirmativa?, confianza) de una respuesta `noul` guardada; confianza solo si está calibrada."""
    p = float(answer["value"])
    return p >= 0.5, (max(p, 1 - p) if answer["calibrated"] else None)


def _choice_confidence(answer: dict[str, Any]) -> float | None:
    if not answer["calibrated"]:
        return None
    if answer.get("confidence") is not None:
        return float(answer["confidence"])
    probs = answer.get("probabilities") or {}
    return float(probs.get(answer["value"], 0.0))


class AgileSupervisor:
    def __init__(self, projects: ProjectService, backlog: BacklogService, engines: EngineRouter):
        self.projects = projects
        self.backlog = backlog
        self.sprints = SprintService(backlog)
        self.engines = engines
        self.audit = AuditService(projects)

    # ------------------------------------------------------------------ configuración
    def _config(self, project_id: str) -> dict[str, Any]:
        params = self.projects.get_config(SUPERVISOR, project_id)["parameters"]
        return {p["key"]: p["value"] for p in params}

    def _model_engines(self, order: list[str]) -> list[str]:
        """Motores con modelo (no reglas) que pueden atender revisiones con el orden del proyecto."""
        return [e.name for p in order if p != "rules" for e in self.engines.registry.decision if e.provider == p]

    # ------------------------------------------------------------------ 1. revisión de historias
    def _review(self, project_id: str, story: dict[str, Any], reqs: dict[str, dict[str, Any]]) -> dict[str, Any]:
        """Revisión de una historia, reutilizada mientras la historia no cambie."""
        db = self.projects.project_db(project_id)
        with db.read() as conn:
            row = conn.execute(
                "SELECT * FROM supervisor_reviews WHERE story_id = ? AND story_updated_at = ?",
                (story["id"], story["updated_at"]),
            ).fetchone()
        if row is not None:
            return {"engine": row["engine"], "answers": json.loads(row["answers_json"]), "cached": True}
        state = {
            "id": story["id"],
            "kind": story["kind"],
            "historia": f"Como {story['as_a']}, quiero {story['i_want']}, para {story['so_that']}.",
            "razon_tecnica": story["technical_reason"],
            "criterios": [f"{c['code']}: {c['text']}" for c in story["acceptance_criteria"]],
            "requisitos": [
                f"{r}: {reqs[r]['title']} — {reqs[r]['description']}" for r in story["requirement_ids"] if r in reqs
            ],
        }
        request = DecisionRequest(
            state=state, questions=STORY_REVIEW_QUESTIONS, purpose=STORY_REVIEW, project_id=project_id
        )
        result = self.engines.decide(SUPERVISOR, request).result
        answers = {k: a.to_json() for k, a in result.answers.items()}
        with db.write() as conn:
            conn.execute(
                "INSERT INTO supervisor_reviews(story_id, story_updated_at, engine, answers_json, reviewed_at) "
                "VALUES (?, ?, ?, ?, ?) ON CONFLICT(story_id) DO UPDATE SET "
                "story_updated_at = excluded.story_updated_at, engine = excluded.engine, "
                "answers_json = excluded.answers_json, reviewed_at = excluded.reviewed_at",
                (story["id"], story["updated_at"], result.engine, json.dumps(answers), _now()),
            )
        return {"engine": result.engine, "answers": answers, "cached": False}

    def _stories(
        self, project_id: str, stories: list[dict[str, Any]], threshold: float, can_review: bool
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]], set[str]]:
        findings: list[dict[str, Any]] = []
        actions: list[dict[str, Any]] = []
        engines: set[str] = set()
        if not can_review:
            return findings, actions, engines
        reqs = {r["id"]: r for r in self.backlog.list_requirements(SUPERVISOR, project_id)["requirements"]}
        for story in stories:
            if story["status"] not in REVIEWABLE:
                continue
            try:
                review = self._review(project_id, story, reqs)
            except AcmError as exc:
                findings.append(
                    _finding("STORY_NOT_REVIEWED", "REVIEW", story["id"], f"sin revisión: {exc}", "supervisor")
                )
                continue
            engine, a = review["engine"], review["answers"]
            engines.add(engine)
            invest_ok, invest_conf = _judgement(a["invest"])
            crit_ok, crit_conf = _judgement(a["criteria_verifiable"])
            size, size_conf = a["size"]["value"], _choice_confidence(a["size"])
            calibrated = all(x["calibrated"] for x in a.values())
            severity = "WARNING" if calibrated else "REVIEW"  # un motor no calibrado solo pide revisión (ADR-015)
            base = {"engine": engine, "calibrated": calibrated}
            if not invest_ok:
                findings.append(
                    _finding(
                        "STORY_NOT_INVEST",
                        severity,
                        story["id"],
                        "no cumple INVEST",
                        "supervisor",
                        confidence=invest_conf,
                        engine=engine,
                    )
                )
            if story["acceptance_criteria"] and not crit_ok:
                findings.append(
                    _finding(
                        "CRITERIA_NOT_VERIFIABLE",
                        severity,
                        story["id"],
                        "algún criterio es vago o no verificable",
                        "supervisor",
                        confidence=crit_conf,
                        engine=engine,
                    )
                )
            if size == "large":
                findings.append(
                    _finding(
                        "STORY_TOO_LARGE",
                        severity,
                        story["id"],
                        "demasiado grande para un sprint",
                        "supervisor",
                        confidence=size_conf,
                        engine=engine,
                    )
                )
                actions.append(
                    {
                        "type": "story.split",
                        "target": story["id"],
                        "reason": "dividirla en historias más pequeñas",
                        "confidence": size_conf,
                        **base,
                        "safe": False,
                    }
                )
            # Acción segura 1: PLANNED completa y juzgada lista → READY (reversible: READY → PLANNED).
            if story["status"] == "PLANNED" and all(story_checks(story).values()):
                if invest_ok and crit_ok and size != "large":
                    confs = [c for c in (invest_conf, crit_conf, size_conf) if c is not None]
                    conf = min(confs) if calibrated and len(confs) == 3 else None
                    actions.append(
                        {
                            "type": "story.mark_ready",
                            "target": story["id"],
                            "from": "PLANNED",
                            "to": "READY",
                            "reason": "completa, cumple INVEST y sus criterios son verificables",
                            "confidence": conf,
                            **base,
                            "safe": calibrated and conf is not None and conf >= threshold,
                        }
                    )
            # Acción segura 2: READY fuera de sprint con criterios no verificables o sin INVEST → PLANNED (reversible).
            if story["status"] == "READY" and story["sprint_id"] is None and (not invest_ok or not crit_ok):
                confs = [c for ok, c in ((invest_ok, invest_conf), (crit_ok, crit_conf)) if not ok and c is not None]
                conf = min(confs) if calibrated and confs else None
                actions.append(
                    {
                        "type": "story.back_to_planned",
                        "target": story["id"],
                        "from": "READY",
                        "to": "PLANNED",
                        "reason": "no está lista: "
                        + ("no cumple INVEST" if not invest_ok else "criterios no verificables"),
                        "confidence": conf,
                        **base,
                        "safe": calibrated and conf is not None and conf >= threshold,
                    }
                )
        return findings, actions, engines

    # ------------------------------------------------------------------ 2. sprints y Kanban
    def _flow(
        self,
        project_id: str,
        stories: list[dict[str, Any]],
        sprints: list[dict[str, Any]],
        cfg: dict[str, Any],
        can_review: bool,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]], set[str], dict[str, Any]]:
        findings: list[dict[str, Any]] = []
        actions: list[dict[str, Any]] = []
        engines: set[str] = set()
        today = datetime.now(UTC).date()
        by_id = {s["id"]: s for s in stories}
        active = next((s for s in sprints if s["status"] == "ACTIVE"), None)
        sprint_info: dict[str, Any] = {}
        for sp in (s for s in sprints if s["status"] in ("PLANNED", "ACTIVE")):
            if sp["overloaded"]:
                findings.append(
                    _finding(
                        "SPRINT_OVERLOADED",
                        "WARNING",
                        sp["id"],
                        f"{sp['load']} historias para una capacidad de {sp['capacity']}",
                        "rules",
                    )
                )
            if not sp["story_ids"]:
                findings.append(_finding("SPRINT_EMPTY", "INFO", sp["id"], "sprint sin historias", "rules"))
            for sid in sp["story_ids"]:
                st = by_id.get(sid)
                if st and st["status"] in ("CANCELLED", "DEPRECATED"):
                    findings.append(
                        _finding(
                            "SPRINT_STORY_CANCELLED",
                            "WARNING",
                            sid,
                            f"está {st['status']} dentro de {sp['id']}",
                            "rules",
                        )
                    )
                    actions.append(
                        {
                            "type": "sprint.remove_story",
                            "target": sid,
                            "sprint_id": sp["id"],
                            "reason": f"{sid} está {st['status']}: sobra en {sp['id']}",
                            "engine": "rules",
                            "calibrated": True,
                            "confidence": 1.0,
                            "safe": True,
                        }
                    )
                elif st and sp["status"] == "ACTIVE" and st["status"] == "PLANNED":
                    findings.append(
                        _finding("SPRINT_STORY_NOT_READY", "REVIEW", sid, f"sin refinar dentro de {sp['id']}", "rules")
                    )
        if active is not None:
            end = date.fromisoformat(active["end_date"])
            start = date.fromisoformat(active["start_date"])
            done = active["stories_by_status"].get("DONE", 0)
            sprint_info = {
                "id": active["id"],
                "goal": active["goal"],
                "end_date": active["end_date"],
                "done": done,
                "stories": active["load"],
                "completion_pct": round(100 * done / active["load"]) if active["load"] else 0,
            }
            if end < today:
                findings.append(
                    _finding(
                        "SPRINT_OVERDUE",
                        "WARNING",
                        active["id"],
                        f"terminó el {active['end_date']} y sigue activo",
                        "rules",
                    )
                )
                actions.append(
                    {
                        "type": "sprint.close",
                        "target": active["id"],
                        "reason": "su fecha de fin ya pasó",
                        "engine": "rules",
                        "calibrated": True,
                        "confidence": 1.0,
                        "safe": False,
                    }
                )
            if can_review and active["load"]:
                state = {
                    "objetivo": active["goal"],
                    "inicio": active["start_date"],
                    "fin": active["end_date"],
                    "hoy": today.isoformat(),
                    "dias_totales": (end - start).days + 1,
                    "dias_transcurridos": max(0, min((today - start).days + 1, (end - start).days + 1)),
                    "historias_por_estado": active["stories_by_status"],
                    "capacidad": active["capacity"],
                }
                try:
                    result = self.engines.decide(
                        SUPERVISOR,
                        DecisionRequest(
                            state=state, questions=SPRINT_RISK_QUESTIONS, purpose=SPRINT_REVIEW, project_id=project_id
                        ),
                    ).result
                    risk: Answer = result.answers["risk"]
                    engines.add(result.engine)
                    level = SPRINT_RISK_QUESTIONS["risk"].options()[min(2, max(0, round(float(risk.value)) - 1))]
                    sprint_info |= {"risk": level, "risk_engine": result.engine, "risk_calibrated": risk.calibrated}
                    if level == "alto":
                        findings.append(
                            _finding(
                                "SPRINT_AT_RISK",
                                "WARNING" if risk.calibrated else "REVIEW",
                                active["id"],
                                "riesgo alto de no cumplir el objetivo",
                                "supervisor",
                                engine=result.engine,
                                confidence=risk.confidence,
                            )
                        )
                except AcmError as exc:
                    findings.append(
                        _finding("SPRINT_NOT_REVIEWED", "REVIEW", active["id"], f"sin revisión: {exc}", "supervisor")
                    )
        wip = sum(1 for s in stories if s["status"] == "IN_PROGRESS")
        if cfg["kanban.wip_limit"] and wip > cfg["kanban.wip_limit"]:
            findings.append(
                _finding(
                    "WIP_EXCEEDED",
                    "WARNING",
                    project_id,
                    f"{wip} historias en curso; límite {cfg['kanban.wip_limit']}",
                    "rules",
                )
            )
        limit = datetime.now(UTC) - timedelta(days=cfg["supervisor.stale_days"])
        for s in stories:
            if s["status"] in ("IN_PROGRESS", "BLOCKED") and datetime.fromisoformat(s["updated_at"]) < limit:
                findings.append(
                    _finding(
                        "STORY_STALE",
                        "WARNING",
                        s["id"],
                        f"{s['status']} sin cambios desde hace más de {cfg['supervisor.stale_days']} días",
                        "rules",
                    )
                )
                actions.append(
                    {
                        "type": "story.review_stale",
                        "target": s["id"],
                        "reason": "comprobar si está bloqueada o terminada",
                        "engine": "rules",
                        "calibrated": True,
                        "confidence": 1.0,
                        "safe": False,
                    }
                )
            if active is not None and s["status"] == "IN_PROGRESS" and s["sprint_id"] != active["id"]:
                findings.append(
                    _finding(
                        "WORK_OUTSIDE_SPRINT",
                        "REVIEW",
                        s["id"],
                        f"en curso fuera del sprint activo {active['id']}",
                        "rules",
                    )
                )
        return findings, actions, engines, sprint_info

    # ------------------------------------------------------------------ 3. acciones
    def _apply(self, project_id: str, action: dict[str, Any]) -> None:
        start = time.perf_counter()
        reason = f"supervisor ({action['engine']}, confianza {action['confidence']:.2f}): {action['reason']}"
        args = {"project_id": project_id, "target": action["target"], "reason": reason}
        try:
            if action["type"] == "story.mark_ready":
                self.backlog.mark_ready(SUPERVISOR, project_id, action["target"])
            elif action["type"] == "story.back_to_planned":
                self.backlog.set_status(SUPERVISOR, project_id, action["target"], "PLANNED", reason)
            elif action["type"] == "sprint.remove_story":
                self.sprints.remove_story(SUPERVISOR, project_id, action["sprint_id"], action["target"])
            else:  # defensa: nunca se marca como aplicada una acción que ACM no sabe ejecutar
                raise FailedPrecondition(f"acción {action['type']!r} fuera de la lista de acciones seguras")
            action["applied"] = True
            self.audit.record(
                principal=SUPERVISOR,
                operation=f"supervisor:{action['type']}",
                arguments=args,
                status="ok",
                duration_ms=(time.perf_counter() - start) * 1000,
                result=action,
            )
        except AcmError as exc:
            action["applied"], action["error"] = False, str(exc)
            self.audit.record(
                principal=SUPERVISOR,
                operation=f"supervisor:{action['type']}",
                arguments=args,
                status="error",
                duration_ms=(time.perf_counter() - start) * 1000,
                error=str(exc),
            )

    # ------------------------------------------------------------------ 4. informe
    @staticmethod
    def _summary(stories: list[dict[str, Any]], sprint_info: dict[str, Any]) -> dict[str, Any]:
        def ids(*statuses: str) -> list[str]:
            return [s["id"] for s in stories if s["status"] in statuses]

        return {
            "done": ids("DONE"),
            "verified": ids("VERIFIED"),
            "in_progress": ids("IN_PROGRESS", "IMPLEMENTED", "TESTING"),
            "blocked": ids("BLOCKED", "FAILED"),
            "pending": ids("PLANNED", "READY"),
            "active_sprint": sprint_info or None,
        }

    @staticmethod
    def _plain_report(
        project_id: str, summary: dict[str, Any], findings: list[dict[str, Any]], actions: list[dict[str, Any]]
    ) -> str:
        def lst(xs: list[str]) -> str:
            return ", ".join(xs) if xs else "ninguna"

        lines = [f"## Informe del supervisor — {project_id} ({_now()[:16].replace('T', ' ')} UTC)", ""]
        lines.append(
            f"**Hecho:** {len(summary['done'])} historias terminadas ({lst(summary['done'])}); "
            f"{len(summary['verified'])} verificadas pendientes de revisión ({lst(summary['verified'])})."
        )
        lines.append(
            f"**En curso:** {lst(summary['in_progress'])}. **Bloqueadas o fallidas:** {lst(summary['blocked'])}."
        )
        lines.append(f"**Pendiente:** {len(summary['pending'])} historias por empezar ({lst(summary['pending'])}).")
        sp = summary["active_sprint"]
        if sp:
            risk = f"; riesgo {sp['risk']} según {sp['risk_engine']}" if sp.get("risk") else ""
            lines.append(
                f"**Sprint activo:** {sp['id']} «{sp['goal']}» — {sp['done']} de {sp['stories']} "
                f"terminadas ({sp['completion_pct']} %), fin {sp['end_date']}{risk}."
            )
        else:
            lines.append("**Sprint activo:** ninguno.")
        lines += [f"> {n}" for n in summary.get("notes", [])]
        issues = [f for f in findings if f["severity"] in ("CRITICAL", "WARNING", "REVIEW")]
        lines += ["", f"**Incongruencias y avisos ({len(issues)}):**"]
        lines += [f"- {f['severity']} `{f['code']}` {f['target']}: {f['message']}" for f in issues[:40]] or [
            "- ninguno"
        ]
        applied = [a for a in actions if a.get("applied")]
        proposed = [a for a in actions if not a.get("applied")]
        lines += ["", f"**Acciones aplicadas ({len(applied)}):**"]
        lines += [f"- {a['type']} {a['target']}: {a['reason']}" for a in applied] or ["- ninguna"]
        lines += ["", f"**Propuestas ({len(proposed)}):**"]
        lines += [f"- {a['type']} {a['target']}: {a['reason']}" for a in proposed[:40]] or ["- ninguna"]
        return "\n".join(lines)

    def _report(
        self, project_id: str, summary: dict[str, Any], findings: list[dict[str, Any]], actions: list[dict[str, Any]]
    ) -> tuple[str, str]:
        plain = self._plain_report(project_id, summary, findings, actions)
        if not self.engines.has_generation():
            return plain, ""
        data = {"proyecto": project_id, "resumen": summary, "hallazgos": findings[:40], "acciones": actions[:40]}
        request = GenerationRequest(
            messages=[
                {"role": "system", "content": REPORT_SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(data, ensure_ascii=False)},
            ],
            purpose=REPORT,
            project_id=project_id,
            max_output_tokens=REPORT_MAX_TOKENS,
        )
        try:
            result = self.engines.generate(SUPERVISOR, request).result
        except AcmError:
            return plain, ""  # sin informe redactado: se entrega el compuesto sin modelo
        return result.text + "\n\n---\n\n" + plain, result.engine

    # ------------------------------------------------------------------ ejecución
    def run(self, project_id: str) -> dict[str, Any]:
        self.projects.ensure_principal(SUPERVISOR, "admin", "agent")
        cfg = self._config(project_id)
        mode = cfg["supervisor.mode"]
        if mode == "off":
            return {
                "mode": mode,
                "findings": [],
                "actions": [],
                "summary": {},
                "report": "",
                "report_engine": "",
                "engines": set(),
            }
        threshold = cfg["supervisor.min_confidence_pct"] / 100
        can_review = bool(self._model_engines(cfg["decision.engine_order"]))
        stories = self.backlog.list_stories(SUPERVISOR, project_id)["stories"]
        sprints = self.sprints.list(SUPERVISOR, project_id)["sprints"]
        findings: list[dict[str, Any]] = []
        notes = []
        if not can_review:
            notes.append(
                "Sin motor de decisión con modelo (JEV u Ollama) en el orden del proyecto: la calidad de las historias "
                "y el riesgo del sprint no se revisan. Configura ACM_JEV_URL/ACM_JEV_MODEL o ACM_OLLAMA_URL/"
                "ACM_OLLAMA_MODEL."
            )
        story_findings, story_actions, engines = self._stories(project_id, stories, threshold, can_review)
        flow_findings, flow_actions, flow_engines, sprint_info = self._flow(
            project_id, stories, sprints, cfg, can_review
        )
        findings += story_findings + flow_findings
        actions = story_actions + flow_actions
        for action in actions:
            action["applied"] = False
            if mode == "apply_safe" and action["safe"] and action["type"] in SAFE_ACTIONS:
                self._apply(project_id, action)
        if any(a.get("applied") for a in actions):  # el resumen refleja lo que ya cambió
            stories = self.backlog.list_stories(SUPERVISOR, project_id)["stories"]
        summary = self._summary(stories, sprint_info) | {"notes": notes}
        report, report_engine = self._report(project_id, summary, findings, actions)
        return {
            "mode": mode,
            "findings": findings,
            "actions": actions,
            "summary": summary,
            "report": report,
            "report_engine": report_engine,
            "engines": engines | flow_engines,
        }
