"""Segundo cerebro: contexto compacto de una historia y ahorro de tokens (US-35.08, US-35.09; ADR-012, ADR-015 §5).

`compact()` construye desde SQLite un contexto estructurado por secciones, cada una con sus fuentes. Si supera el
presupuesto y hay un motor de generación sano, resume las secciones de apoyo (nunca la historia ni sus criterios,
que se entregan literales). Sin motor, entrega el contexto sin resumir e indica por qué.

Estimación de tokens (US-35.09 CA-03): ACM no conoce el tokenizador del agente, así que usa un método explícito y
versionado, `chars/4@v1` = ⌈caracteres / 4⌉ del JSON entregado.

«Contexto completo equivalente»: lo que el agente leería sin ACM con las herramientas existentes para reunir la misma
información, es decir, `acm_story_get` de la historia, `acm_epic_get` de su épica, `acm_requirement_trace` de cada
requisito y `acm_story_get` de cada historia hermana de la feature, serializado como JSON.
"""

from __future__ import annotations

import json
import math
from datetime import UTC, datetime
from typing import Any

from acm.domain.backlog import BacklogService
from acm.domain.errors import AcmError, Forbidden, InvalidArgument
from acm.domain.projects import ProjectService
from acm.inference.ports import GenerationRequest
from acm.inference.router import EngineRouter

ESTIMATION_METHOD = "chars/4@v1"
BUDGET_RANGE = (64, 200_000)
SUMMARIZABLE = ("related_stories", "requirements", "epic", "feature")  # la historia y sus CA van siempre literales


def estimate_tokens(value: Any) -> int:
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    return math.ceil(len(text) / 4)


def _section(name: str, content: str, sources: list[str]) -> dict[str, Any]:
    return {"name": name, "content": content, "sources": sources, "summarized": False}


class ContextService:
    def __init__(self, projects: ProjectService, backlog: BacklogService, engines: EngineRouter):
        self.projects = projects
        self.backlog = backlog
        self.engines = engines

    # ------------------------------------------------------------------ construcción
    def _gather(self, principal: str, project_id: str, story_id: str) -> tuple[list[dict[str, Any]], Any]:
        story = self.backlog.get_story(principal, project_id, story_id)
        epic = self.backlog.get_epic(principal, project_id, story["epic_id"])
        feature = next(f for f in epic["features"] if f["id"] == story["feature_id"])
        traces = [self.backlog.trace_requirement(principal, project_id, r) for r in story["requirement_ids"]]
        siblings = [self.backlog.get_story(principal, project_id, s) for s in feature["story_ids"] if s != story_id]
        full = {"story": story, "epic": epic, "requirement_traces": traces, "sibling_stories": siblings}

        statement = (
            f"{story['id']} [{story['status']}] ({story['kind']}) Como {story['as_a']}, quiero {story['i_want']}, "
            f"para {story['so_that']}."
        )
        if story["technical_reason"]:
            statement += f" Razón técnica: {story['technical_reason']}"
        sections = [
            _section("story", statement, [story["id"]]),
            _section(
                "acceptance_criteria",
                "\n".join(f"{c['code']}: {c['text']}" for c in story["acceptance_criteria"]) or "(sin criterios)",
                [story["id"]],
            ),
            _section(
                "requirements",
                "\n".join(
                    f"{t['requirement']['id']} — {t['requirement']['title']}: {t['requirement']['description']}"
                    for t in traces
                ),
                [t["requirement"]["id"] for t in traces],
            ),
            _section("feature", f"{feature['id']} — {feature['title']}: {feature['description']}", [feature["id"]]),
            _section(
                "epic",
                f"{epic['id']} — {epic['title']}. Objetivo: {epic['objective']} Alcance: {epic['scope']}",
                [epic["id"]],
            ),
            _section(
                "related_stories",
                "\n".join(f"{s['id']} [{s['status']}] quiero {s['i_want']}" for s in siblings) or "(ninguna)",
                [s["id"] for s in siblings],
            ),
        ]
        return sections, full

    # ------------------------------------------------------------------ US-35.08
    def compact(self, principal: str, project_id: str, story_id: str, budget_tokens: Any = None) -> dict[str, Any]:
        if budget_tokens is None:
            params = self.projects.get_config(principal, project_id)["parameters"]
            budget_tokens = next(p["value"] for p in params if p["key"] == "context.max_tokens")
        lo, hi = BUDGET_RANGE
        if not isinstance(budget_tokens, int) or isinstance(budget_tokens, bool) or not lo <= budget_tokens <= hi:
            raise InvalidArgument(f"debe ser un entero entre {lo} y {hi}", field="budget_tokens")
        sections, full = self._gather(principal, project_id, story_id)
        full_tokens = estimate_tokens(full)

        summarized, engine, fallback_from, reason = False, "", None, ""
        if estimate_tokens(sections) <= budget_tokens:
            reason = "el contexto estructurado ya cabe en el presupuesto"
        elif not self.engines.has_generation():
            reason = "no hay modelo local de generación configurado"
        else:
            try:
                sections, engine, fallback_from = self._summarize(principal, project_id, sections, budget_tokens)
                summarized = any(s["summarized"] for s in sections)
                if not summarized:
                    reason = "los resúmenes no reducían el tamaño"
            except AcmError as exc:  # motor caído o respuesta inválida: se entrega sin resumir (CA-03)
                sections, _ = self._gather(principal, project_id, story_id)
                reason = f"no se pudo resumir: {exc}"

        delivered = estimate_tokens(sections)
        with self.projects.global_db.write() as conn:
            cur = conn.execute(
                "INSERT INTO context_deliveries(ts, principal, project_id, story_id, delivered_tokens, full_tokens, "
                "method, summarized, engine) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    datetime.now(UTC).isoformat(),
                    principal,
                    project_id,
                    story_id,
                    delivered,
                    full_tokens,
                    ESTIMATION_METHOD,
                    int(summarized),
                    engine,
                ),
            )
            delivery_id = int(cur.lastrowid)
        return {
            "project_id": project_id,
            "story_id": story_id,
            "sections": sections,
            "budget_tokens": budget_tokens,
            "delivered_tokens": delivered,
            "full_equivalent_tokens": full_tokens,
            "saved_tokens": full_tokens - delivered,
            "estimation_method": ESTIMATION_METHOD,
            "within_budget": delivered <= budget_tokens,
            "summarized": summarized,
            "summary_engine": engine,
            "fallback_from": fallback_from,
            "not_summarized_reason": "" if summarized else reason,
            "delivery_id": delivery_id,
        }

    def _summarize(
        self, principal: str, project_id: str, sections: list[dict[str, Any]], budget: int
    ) -> tuple[list[dict[str, Any]], str, str | None]:
        engine, fallback_from = "", None
        order = sorted((s for s in sections if s["name"] in SUMMARIZABLE), key=lambda s: -len(s["content"]))
        for section in order:
            excess = estimate_tokens(sections) - budget
            if excess <= 0:
                break
            original = estimate_tokens(section["content"])
            target = max(32, original - excess)
            request = GenerationRequest(
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Resume el texto para un agente de desarrollo en menos de "
                            f"{max(10, target * 3 // 4)} palabras. "
                            "Conserva literalmente los identificadores (REQ-, EPIC-, FEAT-, US-, CA-). "
                            "No añadas nada que no esté en el texto."
                        ),
                    },
                    {"role": "user", "content": section["content"]},
                ],
                purpose="context.compact",
                project_id=project_id,
                max_output_tokens=target,
            )
            result = self.engines.generate(principal, request).result
            engine, fallback_from = result.engine, fallback_from or result.fallback_from
            if estimate_tokens(result.text) < original:
                section["content"], section["summarized"] = result.text, True
        return sections, engine, fallback_from

    # ------------------------------------------------------------------ US-35.09
    def savings_report(self, principal: str, *, filter_principal: Any = None, project_id: Any = None) -> dict[str, Any]:
        with self.projects.global_db.read() as conn:
            if self.projects._principal_role(conn, principal) != "admin":
                raise Forbidden("solo un admin puede consultar el ahorro de tokens")
        clauses, args = [], []
        for column, value, field in (
            ("principal", filter_principal, "principal_id"),
            ("project_id", project_id, "project_id"),
        ):
            if value is not None:
                if not isinstance(value, str):
                    raise InvalidArgument("debe ser texto", field=field)
                clauses.append(f"{column} = ?")
                args.append(value)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with self.projects.global_db.read() as conn:
            rows = conn.execute(
                "SELECT principal, project_id, method, COUNT(*) AS deliveries, SUM(delivered_tokens) AS delivered, "
                "SUM(full_tokens) AS full_equivalent, SUM(summarized) AS summarized "
                f"FROM context_deliveries {where} GROUP BY principal, project_id, method "
                "ORDER BY principal, project_id, method",
                args,
            ).fetchall()
        groups = [{**dict(r), "saved": r["full_equivalent"] - r["delivered"]} for r in rows]
        totals = {k: sum(g[k] for g in groups) for k in ("deliveries", "delivered", "full_equivalent", "saved")}
        return {"groups": groups, "totals": totals, "methods": sorted({g["method"] for g in groups})}
