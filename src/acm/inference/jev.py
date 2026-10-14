"""Adaptador JEV (EPIC-50; ADR-006, ADR-015): modelos de decisión servidos por Ollaya.

Ollaya (github.com/ollaya-dev/ollaya) es un runtime local «tipo Ollama» para modelos de decisión estilo Jev. Su API
nativa `POST /api/decide` recibe `{model, state, questions}` con preguntas `choice`/`score`/`noul` y devuelve
probabilidades; es el mismo contrato que el puerto de decisión de ACM, así que el adaptador es una traducción 1:1:

- `choice` → `{"choice", "confidence", "probabilities"}` → valor = opción elegida.
- `score` → `{"score", "confidence", "legend", "probabilities"}`, con el valor continuo en 0..n-1 sobre los niveles.
  ACM usa 1..n (igual que las reglas), así que se suma 1 y las probabilidades se indexan por el texto del nivel.
- `noul` → `{"noul": P(sí)}` → valor = P(sí), probabilidades `{"true", "false"}`.

Las probabilidades de un modelo de decisión son reales, así que sus respuestas son `calibrated=True`: un gate puede
aceptarlas, a diferencia de las de un LLM generativo.

Contrato tomado de `docs/api.md` del repositorio de Ollaya (consultado el 2026-09-30, `10_IA/inference_engines.md`).
Pendiente de verificar contra un Ollaya real (SPIKE-006; en el entorno de desarrollo no hay acceso, IMP-004).
"""

from __future__ import annotations

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
    Question,
)

DEFAULT_TIMEOUT_S = 30.0
KEEP_ALIVE = "10m"  # mantiene el modelo cargado entre decisiones seguidas


class OllayaClient:
    def __init__(
        self,
        base_url: str,
        *,
        api_key: str | None = None,
        timeout_s: float = DEFAULT_TIMEOUT_S,
        transport: httpx.BaseTransport | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}  # OLLAYA_API_KEY en el servidor
        self._http = httpx.Client(base_url=self.base_url, timeout=timeout_s, headers=headers, transport=transport)

    def close(self) -> None:
        self._http.close()

    def _request(self, method: str, path: str, **kw: Any) -> dict[str, Any]:
        try:
            resp = self._http.request(method, path, **kw)
        except httpx.HTTPError as exc:
            raise EngineUnavailable(f"Ollaya no accesible en {self.base_url}: {type(exc).__name__}: {exc}") from exc
        try:
            body = resp.json()
        except ValueError:
            body = None
        if resp.status_code != 200:
            code = body.get("code", "") if isinstance(body, dict) else ""
            reason = body.get("error", resp.text) if isinstance(body, dict) else resp.text
            detail = f"Ollaya {method} {path} → HTTP {resp.status_code} {code}: {reason}".replace("  ", " ")
            # 422 = Ollaya rechaza la petición (demasiado larga, demasiadas opciones…): el motor respondió, sin
            # decisión válida. 404 modelo ausente, 503 cola llena, 500 fallo de carga, 401 clave: no disponible.
            raise EngineError(detail) if resp.status_code == 422 else EngineUnavailable(detail)
        if not isinstance(body, dict):
            raise EngineError(f"Ollaya {method} {path} devolvió una respuesta que no es un objeto JSON")
        return body

    def list_models(self) -> list[str]:
        body = self._request("GET", "/api/tags")
        models = body.get("models")
        if not isinstance(models, list):
            raise EngineError("Ollaya /api/tags no devolvió la lista 'models'")
        return sorted(m["name"] for m in models if isinstance(m, dict) and isinstance(m.get("name"), str))

    def list_details(self) -> list[dict[str, Any]]:
        """Modelos instalados con sus detalles (familia, formato…), para el catálogo (US-50.09)."""
        body = self._request("GET", "/api/tags")
        models = body.get("models")
        if not isinstance(models, list):
            raise EngineError("Ollaya /api/tags no devolvió la lista 'models'")
        valid = sorted(
            (m for m in models if isinstance(m, dict) and isinstance(m.get("name"), str)), key=lambda m: m["name"]
        )
        return [
            {"name": m["name"], "details": m.get("details") if isinstance(m.get("details"), dict) else {}}
            for m in valid
        ]

    def decide(self, model: str, state: str | dict[str, Any], questions: dict[str, Any]) -> dict[str, Any]:
        payload = {"model": model, "state": state, "questions": questions, "keep_alive": KEEP_ALIVE}
        return self._request("POST", "/api/decide", json=payload)


def model_installed(model: str, installed: list[str]) -> bool:
    """`laya` equivale a `laya:latest`, como en Ollama/Ollaya; con etiqueta explícita, coincidencia exacta."""
    wanted = model if ":" in model else f"{model}:latest"
    return wanted in installed or model in installed


def _question_json(q: Question) -> dict[str, Any]:
    out: dict[str, Any] = {"type": q.type, "instructions": q.instructions}
    if q.criteria is not None:
        out["criteria"] = q.criteria
    return out


def _probabilities(raw: Any, where: str) -> dict[str, float]:
    if not isinstance(raw, dict) or not all(isinstance(v, (int, float)) for v in raw.values()):
        raise EngineError(f"{where}: 'probabilities' no es un objeto {{opción: probabilidad}}")
    return {str(k): float(v) for k, v in raw.items()}


def _confidence(raw: Any) -> float | None:
    return float(raw) if isinstance(raw, (int, float)) and not isinstance(raw, bool) else None


def parse_answer(key: str, q: Question, raw: Any) -> Answer:
    """Traduce una respuesta de Ollaya al `Answer` de ACM; cualquier forma inesperada es ENGINE_ERROR."""
    where = f"respuesta {key!r}"
    if not isinstance(raw, dict) or raw.get("type") != q.type:
        raise EngineError(f"{where}: se esperaba una respuesta de tipo {q.type!r}")
    if q.type == "choice":
        value = raw.get("choice")
        if value not in q.options():
            raise EngineError(f"{where}: {value!r} no es una de las opciones {q.options()}")
        probabilities = _probabilities(raw.get("probabilities"), where)
        return Answer("choice", value, probabilities, _confidence(raw.get("confidence")), True)
    if q.type == "score":
        levels = q.options()
        value = raw.get("score")
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= value <= len(levels) - 1:
            raise EngineError(f"{where}: 'score' debe estar entre 0 y {len(levels) - 1}")
        by_index = _probabilities(raw.get("probabilities"), where)
        try:
            probabilities = {levels[int(i)]: p for i, p in by_index.items()}
        except (ValueError, IndexError) as exc:
            raise EngineError(f"{where}: probabilidades de niveles inexistentes") from exc
        return Answer("score", float(value) + 1.0, probabilities, _confidence(raw.get("confidence")), True)
    p = raw.get("noul")
    if not isinstance(p, (int, float)) or isinstance(p, bool) or not 0.0 <= p <= 1.0:
        raise EngineError(f"{where}: 'noul' debe ser una probabilidad entre 0 y 1")
    return Answer("noul", float(p), {"true": float(p), "false": 1.0 - float(p)}, None, True)


# Modelo fijo, o función propósito → modelo (selección de ACM: uno por defecto y uno por propósito, US-22.07).
JevModelRef = str | Callable[[str | None], str | None] | None


class JevDecisionEngine:
    """`DecisionEngine` sobre Ollaya. Responde cualquier propósito con el modelo que le toque: el que pide el agente
    (`DecisionRequest.model`), el asignado al propósito o el modelo por defecto."""

    provider = "jev"

    def __init__(self, client: OllayaClient, model: JevModelRef):
        self.client = client
        self._model = model
        self.endpoint = client.base_url

    def model_for(self, purpose: str | None) -> str | None:
        return self._model(purpose) if callable(self._model) else self._model

    @property
    def model(self) -> str | None:
        return self.model_for(None)

    @property
    def name(self) -> str:
        return f"jev:{self.model or '-'}"

    def close(self) -> None:
        self.client.close()

    def supports(self, request: DecisionRequest) -> bool:
        return True

    def health(self) -> EngineHealth:
        try:
            models = self.client.list_models()
        except (EngineUnavailable, EngineError) as exc:
            return EngineHealth(False, exc.message)
        if self.model is None:
            return EngineHealth(
                False, "ningún modelo por defecto seleccionado: elige uno de los detectados", tuple(models)
            )
        if not model_installed(self.model, models):
            return EngineHealth(False, f"el modelo {self.model!r} no está instalado en {self.endpoint}", tuple(models))
        return EngineHealth(True, f"{len(models)} modelos detectados", tuple(models))

    def decide(self, request: DecisionRequest) -> DecisionResult:
        start = time.perf_counter()
        model = request.model or self.model_for(request.purpose)
        if model is None:
            raise EngineUnavailable(
                "no hay modelo de Ollaya para este propósito: elige uno en ACM (Sistema → Modelos, acm_models_select) "
                "o con ACM_JEV_MODEL"
            )
        name = f"jev:{model}"
        body = self.client.decide(model, request.state, {k: _question_json(q) for k, q in request.questions.items()})
        answers = body.get("answers")
        if not isinstance(answers, dict) or set(answers) != set(request.questions):
            raise EngineError(f"{name} no respondió exactamente a las preguntas pedidas")
        parsed = {k: parse_answer(k, q, answers[k]) for k, q in request.questions.items()}
        raw_usage = body.get("usage") if isinstance(body.get("usage"), dict) else {}
        usage = {k: v for k, v in raw_usage.items() if k in ("input_tokens", "output_tokens") and isinstance(v, int)}
        return DecisionResult(parsed, name, usage, (time.perf_counter() - start) * 1000)
