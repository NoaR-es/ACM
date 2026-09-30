"""`RulesDecisionEngine`: implementación sin modelo del puerto de decisión (US-35.11 CA-02).

Responde solo preguntas con una regla determinista registrada para su `purpose`; para el resto `supports()` es False
y el router pasa al siguiente motor. Las respuestas son exactas: probabilidad 1/0 y `calibrated=True`.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from acm.domain.errors import InvalidArgument
from acm.inference.ports import Answer, DecisionRequest, DecisionResult, EngineHealth, Question

RuleFn = Callable[[dict[str, Any], Question], Answer]


@dataclass(frozen=True)
class Rule:
    type: str  # tipo de pregunta que responde
    description: str
    fn: RuleFn


def noul(value: bool) -> Answer:
    p = 1.0 if value else 0.0
    return Answer("noul", p, {"true": p, "false": 1.0 - p}, 1.0, True)


def choice(option: str, options: list[str]) -> Answer:
    return Answer("choice", option, {o: 1.0 if o == option else 0.0 for o in options}, 1.0, True)


def score(level: int, levels: list[str]) -> Answer:
    """`level` es 1..n sobre `levels` (el valor continuo de un score exacto coincide con un nivel)."""
    return Answer("score", float(level), {lv: 1.0 if i + 1 == level else 0.0 for i, lv in enumerate(levels)}, 1.0, True)


# ------------------------------------------------------------------ purpose "story.quality"
STORY_FIELDS = ("as_a", "i_want", "so_that", "requirement_ids", "acceptance_criteria", "kind", "technical_reason")


def _story(state: dict[str, Any]) -> dict[str, Any]:
    missing = [f for f in STORY_FIELDS if f not in state]
    if missing:
        raise InvalidArgument(
            f"el estado de story.quality debe ser una historia (acm_story_get); faltan {missing}", field="state"
        )
    return state


def story_checks(state: dict[str, Any]) -> dict[str, bool]:
    """Comprobaciones estructurales de una historia (misma regla READY de US-04.03 CA-04)."""
    s = _story(state)
    return {
        "has_statement": all(str(s[f]).strip() for f in ("as_a", "i_want", "so_that")),
        "has_requirements": bool(s["requirement_ids"]),
        "has_acceptance_criteria": bool(s["acceptance_criteria"]),
        "technical_reason_ok": s["kind"] != "technical" or bool(str(s["technical_reason"]).strip()),
    }


def _check(name: str) -> RuleFn:
    return lambda state, q: noul(story_checks(state)[name])


def _readiness(state: dict[str, Any], q: Question) -> Answer:
    options = q.options()
    if set(options) != {"ready", "not_ready"}:
        raise InvalidArgument("readiness exige las opciones 'ready' y 'not_ready'", field="questions.readiness")
    return choice("ready" if all(story_checks(state).values()) else "not_ready", options)


def _completeness(state: dict[str, Any], q: Question) -> Answer:
    levels = q.options()
    if len(levels) != 5:
        raise InvalidArgument(
            "completeness exige 5 niveles (0..4 comprobaciones superadas)", field="questions.completeness"
        )
    return score(sum(story_checks(state).values()) + 1, levels)


STORY_QUALITY_RULES: dict[str, Rule] = {
    "has_statement": Rule("noul", "Tiene rol, objetivo y beneficio (as_a, i_want, so_that)", _check("has_statement")),
    "has_requirements": Rule("noul", "Enlaza al menos un requisito de origen", _check("has_requirements")),
    "has_acceptance_criteria": Rule(
        "noul", "Tiene al menos un criterio de aceptación", _check("has_acceptance_criteria")
    ),
    "technical_reason_ok": Rule("noul", "Si es técnica, declara su razón", _check("technical_reason_ok")),
    "readiness": Rule("choice", "ready | not_ready según las cuatro comprobaciones", _readiness),
    "completeness": Rule("score", "Nivel 1..5 = comprobaciones superadas + 1", _completeness),
}

DEFAULT_RULES: dict[str, dict[str, Rule]] = {"story.quality": STORY_QUALITY_RULES}


class RulesDecisionEngine:
    name = "rules"
    provider = "rules"

    def __init__(self, rules: dict[str, dict[str, Rule]] | None = None):
        self.rules = rules if rules is not None else DEFAULT_RULES

    def catalog(self) -> dict[str, dict[str, dict[str, str]]]:
        """Preguntas que sabe responder, por purpose (para la skill y `acm_engines_list`)."""
        return {
            p: {k: {"type": r.type, "description": r.description} for k, r in rs.items()}
            for p, rs in self.rules.items()
        }

    def supports(self, request: DecisionRequest) -> bool:
        rules = self.rules.get(request.purpose)
        if rules is None or not isinstance(request.state, dict):
            return False
        return all(k in rules and rules[k].type == q.type for k, q in request.questions.items())

    def decide(self, request: DecisionRequest) -> DecisionResult:
        start = time.perf_counter()
        if not self.supports(request):
            raise InvalidArgument(
                f"el motor de reglas no cubre estas preguntas para {request.purpose!r}", field="questions"
            )
        rules = self.rules[request.purpose]
        answers = {k: rules[k].fn(request.state, q) for k, q in request.questions.items()}
        return DecisionResult(answers, self.name, {}, (time.perf_counter() - start) * 1000)

    def health(self) -> EngineHealth:
        return EngineHealth(True, "reglas deterministas en proceso")
