"""Puertos de inferencia del núcleo (ADR-015, ajustado por ADR-016; diseño en `04_ARQUITECTURA/inference_ports.md`).

El contrato de decisión reproduce el de TypeSafe System One / Ollaya (ADR-006): preguntas `choice`, `score` y `noul`
con probabilidades. Así el adaptador JEV (EPIC-50) será una traducción 1:1 y ningún consumidor cambiará al conectarlo.

Los puertos son síncronos (ADR-016): el dominio de ACM es síncrono y la frontera MCP lo ejecuta en hilos de trabajo.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Protocol, runtime_checkable

from acm.domain.errors import AcmError, InvalidArgument

QuestionType = Literal["choice", "score", "noul"]
QUESTION_TYPES: tuple[str, ...] = ("choice", "score", "noul")
MAX_QUESTIONS = 256  # límite de Ollaya (10_IA/inference_engines.md)
MAX_CHOICE_OPTIONS = 255
SCORE_LEVELS = (2, 10)


# --------------------------------------------------------------------------------------------- errores
class EngineUnavailable(AcmError):
    """Ningún motor pudo atender la petición, o el motor elegido no está disponible."""

    code = "ENGINE_UNAVAILABLE"


class EngineError(AcmError):
    """El motor respondió, pero sin una respuesta válida (US-22.03 CA-04: no se declara éxito)."""

    code = "ENGINE_ERROR"


# --------------------------------------------------------------------------------------------- decisión
@dataclass(frozen=True)
class Question:
    type: str
    instructions: str
    criteria: dict[str, str] | list[str] | None = None

    def options(self) -> list[str]:
        """Opciones de respuesta: claves de `choice`, niveles de `score` o `true`/`false` de `noul`."""
        if self.type == "choice":
            return list(self.criteria or {})
        if self.type == "score":
            return list(self.criteria or [])
        return ["true", "false"]


@dataclass(frozen=True)
class DecisionRequest:
    state: str | dict[str, Any]
    questions: dict[str, Question]
    purpose: str
    project_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.purpose, str) or not self.purpose.strip():
            raise InvalidArgument("no puede estar vacío", field="purpose")
        if not isinstance(self.state, (str, dict)):
            raise InvalidArgument("debe ser texto o un objeto JSON", field="state")
        if not self.questions or len(self.questions) > MAX_QUESTIONS:
            raise InvalidArgument(f"debe haber entre 1 y {MAX_QUESTIONS} preguntas", field="questions")
        for key, q in self.questions.items():
            where = f"questions.{key}"
            if q.type not in QUESTION_TYPES:
                raise InvalidArgument(f"tipo {q.type!r} no admitido; usa {list(QUESTION_TYPES)}", field=where)
            if q.type == "choice":
                if not isinstance(q.criteria, dict) or not 2 <= len(q.criteria) <= MAX_CHOICE_OPTIONS:
                    raise InvalidArgument(
                        f"choice exige criteria {{opción: descripción}} con 2..{MAX_CHOICE_OPTIONS} opciones",
                        field=where,
                    )
            elif q.type == "score":
                lo, hi = SCORE_LEVELS
                if not isinstance(q.criteria, list) or not lo <= len(q.criteria) <= hi:
                    raise InvalidArgument(f"score exige criteria [nivel, ...] con {lo}..{hi} niveles", field=where)
            elif q.criteria is not None and not (isinstance(q.criteria, dict) and set(q.criteria) <= {"true", "false"}):
                raise InvalidArgument("noul solo admite criteria {'true': ..., 'false': ...}", field=where)

    @classmethod
    def from_json(cls, project_id: str, purpose: str, state: Any, questions: Any) -> DecisionRequest:
        """Construye la petición desde la forma JSON que recibe la herramienta MCP `acm_decide`."""
        if not isinstance(questions, dict):
            raise InvalidArgument("debe ser un objeto {clave: pregunta}", field="questions")
        parsed: dict[str, Question] = {}
        for key, q in questions.items():
            if not isinstance(q, dict) or not isinstance(q.get("type"), str):
                raise InvalidArgument("cada pregunta necesita 'type'", field=f"questions.{key}")
            parsed[key] = Question(q["type"], str(q.get("instructions", "")), q.get("criteria"))
        return cls(state=state, questions=parsed, purpose=purpose, project_id=project_id)


@dataclass(frozen=True)
class Answer:
    type: str
    value: str | float  # choice → opción; score → valor continuo 1..n sobre los niveles; noul → P("true")
    probabilities: dict[str, float] | None
    confidence: float | None
    calibrated: bool  # True solo si las probabilidades son reales (reglas exactas o JEV); False en un LLM generativo

    def to_json(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "value": self.value,
            "probabilities": self.probabilities,
            "confidence": self.confidence,
            "calibrated": self.calibrated,
        }


@dataclass(frozen=True)
class DecisionResult:
    answers: dict[str, Answer]
    engine: str
    usage: dict[str, int] = field(default_factory=dict)
    duration_ms: float = 0.0
    fallback_from: str | None = None

    def to_json(self) -> dict[str, Any]:
        return {
            "answers": {k: a.to_json() for k, a in self.answers.items()},
            "engine": self.engine,
            "usage": self.usage,
            "duration_ms": self.duration_ms,
            "fallback_from": self.fallback_from,
        }


@dataclass(frozen=True)
class EngineHealth:
    ok: bool
    detail: str = ""
    models: tuple[str, ...] = ()


@runtime_checkable
class DecisionEngine(Protocol):
    name: str
    provider: str

    def supports(self, request: DecisionRequest) -> bool: ...

    def decide(self, request: DecisionRequest) -> DecisionResult: ...

    def health(self) -> EngineHealth: ...


# --------------------------------------------------------------------------------------------- generación
@dataclass(frozen=True)
class GenerationRequest:
    messages: list[dict[str, str]]
    purpose: str
    project_id: str
    max_output_tokens: int
    json_schema: dict[str, Any] | None = None


@dataclass(frozen=True)
class GenerationResult:
    text: str
    engine: str
    usage: dict[str, int] = field(default_factory=dict)
    duration_ms: float = 0.0
    fallback_from: str | None = None


@runtime_checkable
class GenerationEngine(Protocol):
    name: str
    provider: str

    def generate(self, request: GenerationRequest) -> GenerationResult: ...

    def health(self) -> EngineHealth: ...
