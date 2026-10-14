"""Adaptador Ollama (EPIC-22): detección de modelos (US-22.01), generación local (US-22.03) y decisión (ADR-015).

Usa la API HTTP de Ollama: `GET /api/tags` (modelos instalados) y `POST /api/chat` sin streaming.

`OllamaDecisionEngine` responde preguntas tipadas (`choice`/`score`/`noul`) con un modelo generativo local cuya
salida se restringe con un esquema JSON (`format`), de modo que solo puede elegir entre las opciones dadas. Un LLM
generativo no da probabilidades reales: sus respuestas son `calibrated=False` y sin probabilidades, así que un gate
no las acepta (ADR-015) y el router prefiere antes las reglas y JEV (`decision.engine_order`).

Pendiente de verificar contra un Ollama real: SPIKE-005 (el entorno de desarrollo no puede descargar Ollama, IMP-004).
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from typing import Any

import httpx

from acm.inference.ports import (
    Answer,
    DecisionRequest,
    DecisionResult,
    EngineError,
    EngineHealth,
    EngineUnavailable,
    GenerationRequest,
    GenerationResult,
)

DEFAULT_TIMEOUT_S = 60.0


class OllamaClient:
    def __init__(
        self, base_url: str, *, timeout_s: float = DEFAULT_TIMEOUT_S, transport: httpx.BaseTransport | None = None
    ):
        self.base_url = base_url.rstrip("/")
        self._http = httpx.Client(base_url=self.base_url, timeout=timeout_s, transport=transport)

    def close(self) -> None:
        self._http.close()

    def _request(self, method: str, path: str, **kw: Any) -> dict[str, Any]:
        try:
            resp = self._http.request(method, path, **kw)
        except httpx.HTTPError as exc:  # conexión rechazada, timeout, DNS…
            raise EngineUnavailable(f"Ollama no accesible en {self.base_url}: {type(exc).__name__}: {exc}") from exc
        if resp.status_code != 200:
            try:
                reason = resp.json().get("error", resp.text)
            except ValueError:
                reason = resp.text
            raise EngineUnavailable(f"Ollama {method} {path} → HTTP {resp.status_code}: {reason}")
        try:
            body = resp.json()
        except ValueError as exc:
            raise EngineError(f"Ollama {method} {path} devolvió una respuesta que no es JSON") from exc
        if not isinstance(body, dict):
            raise EngineError(f"Ollama {method} {path} devolvió un JSON inesperado")
        return body

    def list_models(self) -> list[str]:
        """US-22.01: modelos instalados según el runtime; nunca se inventa uno que no aparezca aquí (CA-04)."""
        body = self._request("GET", "/api/tags")
        models = body.get("models")
        if not isinstance(models, list):
            raise EngineError("Ollama /api/tags no devolvió la lista 'models'")
        return sorted(m["name"] for m in models if isinstance(m, dict) and isinstance(m.get("name"), str))

    def list_details(self) -> list[dict[str, Any]]:
        """Modelos instalados con sus detalles (familia, tamaño, cuantización), para el catálogo (US-50.09)."""
        body = self._request("GET", "/api/tags")
        models = body.get("models")
        if not isinstance(models, list):
            raise EngineError("Ollama /api/tags no devolvió la lista 'models'")
        return [
            {"name": m["name"], "details": m.get("details") if isinstance(m.get("details"), dict) else {}}
            for m in sorted(
                (m for m in models if isinstance(m, dict) and isinstance(m.get("name"), str)), key=lambda m: m["name"]
            )
        ]

    def chat(
        self,
        model: str,
        messages: list[dict[str, Any]],
        *,
        max_tokens: int,
        json_schema: dict[str, Any] | None = None,
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {"num_predict": max_tokens},
        }
        if json_schema is not None:
            payload["format"] = json_schema
        if tools:
            payload["tools"] = tools  # US-22.11: herramientas de ACM que el modelo puede pedir (tool calling)
        return self._request("POST", "/api/chat", json=payload)


# El modelo es fijo (tests, configuración de arranque) o se resuelve en cada llamada desde la selección de ACM.
ModelRef = str | Callable[[], str | None] | None


def resolve(ref: ModelRef) -> str | None:
    return ref() if callable(ref) else ref


def model_health(client: OllamaClient, model: str | None, endpoint: str) -> EngineHealth:
    try:
        models = client.list_models()
    except (EngineUnavailable, EngineError) as exc:
        return EngineHealth(False, exc.message)
    if model is None:
        return EngineHealth(False, "ningún modelo seleccionado: elige uno de los detectados", tuple(models))
    if model not in models:
        return EngineHealth(False, f"el modelo {model!r} no está instalado en {endpoint}", tuple(models))
    return EngineHealth(True, f"{len(models)} modelos detectados", tuple(models))


class _OllamaEngine:
    provider = "ollama"
    prefix = "ollama"

    def __init__(self, client: OllamaClient, model: ModelRef):
        self.client = client
        self._model = model
        self.endpoint = client.base_url

    @property
    def model(self) -> str | None:
        return resolve(self._model)

    @property
    def name(self) -> str:
        return f"{self.prefix}:{self.model or '-'}"

    def require_model(self) -> str:
        model = self.model
        if model is None:
            raise EngineUnavailable(
                "no hay modelo de Ollama seleccionado: elígelo en ACM (Sistema → Modelos, acm_models_select) "
                "o con ACM_OLLAMA_MODEL"
            )
        return model

    def close(self) -> None:
        self.client.close()

    def health(self) -> EngineHealth:
        """Sano solo si el runtime responde y el modelo elegido está entre los detectados (US-22.01 CA-03/04)."""
        return model_health(self.client, self.model, self.endpoint)


def _usage(body: dict[str, Any]) -> dict[str, int]:
    return {
        k: int(body[src])
        for k, src in (("input_tokens", "prompt_eval_count"), ("output_tokens", "eval_count"))
        if isinstance(body.get(src), int)
    }


class OllamaGenerationEngine(_OllamaEngine):
    def generate(self, request: GenerationRequest) -> GenerationResult:
        start = time.perf_counter()
        model = self.require_model()
        body = self.client.chat(
            model, request.messages, max_tokens=request.max_output_tokens, json_schema=request.json_schema
        )
        message = body.get("message")
        text = message.get("content") if isinstance(message, dict) else None
        if body.get("done") is not True or not isinstance(text, str) or not text.strip():
            raise EngineError(f"ollama:{model} no devolvió una respuesta completa (done={body.get('done')!r})")  # CA-04
        return GenerationResult(text.strip(), f"ollama:{model}", _usage(body), (time.perf_counter() - start) * 1000)


# Prompt versionado (10_IA/prompt_versioning.md). En inglés: los modelos locales pequeños siguen mejor las
# instrucciones en inglés; el estado y las preguntas se pasan tal cual, en el idioma en que lleguen.
DECISION_PROMPT_VERSION = "ollama-decide@v1"
DECISION_SYSTEM_PROMPT = (
    "You are a precise decision engine. You receive a JSON object with a `state` and a set of `questions`. "
    "For each question, pick exactly one of its `options`, using the option descriptions and the question "
    "instructions, based only on the state. Reply with a JSON object mapping every question key to the chosen "
    "option key, and nothing else."
)


def _options(request: DecisionRequest) -> dict[str, dict[str, str]]:
    """Opciones de cada pregunta con su descripción (la de `criteria` o, si no hay, el propio nombre)."""
    out: dict[str, dict[str, str]] = {}
    for key, q in request.questions.items():
        if q.type == "choice":
            out[key] = dict(q.criteria or {})  # type: ignore[arg-type]
        elif q.type == "score":
            out[key] = {level: f"level {i + 1} of {len(q.options())}" for i, level in enumerate(q.options())}
        else:
            crit = q.criteria if isinstance(q.criteria, dict) else {}
            out[key] = {"true": crit.get("true", "yes"), "false": crit.get("false", "no")}
    return out


class OllamaDecisionEngine(_OllamaEngine):
    """`DecisionEngine` con un modelo generativo local de Ollama: rápido y sin coste, pero no calibrado."""

    prefix = "ollama-decide"

    def supports(self, request: DecisionRequest) -> bool:
        return True

    def decide(self, request: DecisionRequest) -> DecisionResult:
        start = time.perf_counter()
        model = self.require_model()
        name = f"{self.prefix}:{model}"
        options = _options(request)
        schema = {
            "type": "object",
            "properties": {k: {"type": "string", "enum": list(opts)} for k, opts in options.items()},
            "required": list(options),
            "additionalProperties": False,
        }
        prompt = {
            "state": request.state,
            "questions": {
                k: {"type": q.type, "instructions": q.instructions, "options": options[k]}
                for k, q in request.questions.items()
            },
        }
        messages = [
            {"role": "system", "content": DECISION_SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)},
        ]
        body = self.client.chat(model, messages, max_tokens=min(64 + 32 * len(options), 4096), json_schema=schema)
        message = body.get("message")
        text = message.get("content") if isinstance(message, dict) else None
        if body.get("done") is not True or not isinstance(text, str):
            raise EngineError(f"{name} no devolvió una respuesta completa (done={body.get('done')!r})")
        try:
            chosen = json.loads(text)
        except ValueError as exc:
            raise EngineError(f"{name} no respondió con JSON válido") from exc
        if not isinstance(chosen, dict) or set(chosen) != set(options):
            raise EngineError(f"{name} no respondió exactamente a las preguntas pedidas")
        answers = {}
        for key, q in request.questions.items():
            value = chosen[key]
            if value not in options[key]:
                raise EngineError(f"{name}: {value!r} no es una opción de {key!r}")
            if q.type == "choice":
                answers[key] = Answer("choice", value, None, None, False)
            elif q.type == "score":
                answers[key] = Answer("score", float(q.options().index(value) + 1), None, None, False)
            else:
                answers[key] = Answer("noul", 1.0 if value == "true" else 0.0, None, None, False)
        return DecisionResult(answers, name, _usage(body), (time.perf_counter() - start) * 1000)
