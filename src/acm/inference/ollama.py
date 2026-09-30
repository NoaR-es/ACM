"""Adaptador Ollama (EPIC-22): detección de modelos (US-22.01) y generación local (US-22.03).

Usa la API HTTP de Ollama: `GET /api/tags` (modelos instalados) y `POST /api/chat` sin streaming.
Pendiente de verificar contra un Ollama real: SPIKE-005 (el entorno de SPRINT-003 no pudo descargar Ollama ni modelos).
"""

from __future__ import annotations

import time
from typing import Any

import httpx

from acm.inference.ports import EngineError, EngineHealth, EngineUnavailable, GenerationRequest, GenerationResult

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

    def chat(
        self, model: str, messages: list[dict[str, str]], *, max_tokens: int, json_schema: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {"num_predict": max_tokens},
        }
        if json_schema is not None:
            payload["format"] = json_schema
        return self._request("POST", "/api/chat", json=payload)


class OllamaGenerationEngine:
    provider = "ollama"

    def __init__(self, client: OllamaClient, model: str):
        self.client = client
        self.model = model
        self.name = f"ollama:{model}"
        self.endpoint = client.base_url

    def close(self) -> None:
        self.client.close()

    def health(self) -> EngineHealth:
        """Sano solo si el runtime responde y el modelo configurado está entre los detectados (US-22.01 CA-03/04)."""
        try:
            models = self.client.list_models()
        except (EngineUnavailable, EngineError) as exc:
            return EngineHealth(False, exc.message)
        if self.model not in models:
            return EngineHealth(False, f"el modelo {self.model!r} no está instalado en {self.endpoint}", tuple(models))
        return EngineHealth(True, f"{len(models)} modelos detectados", tuple(models))

    def generate(self, request: GenerationRequest) -> GenerationResult:
        start = time.perf_counter()
        body = self.client.chat(
            self.model, request.messages, max_tokens=request.max_output_tokens, json_schema=request.json_schema
        )
        message = body.get("message")
        text = message.get("content") if isinstance(message, dict) else None
        if body.get("done") is not True or not isinstance(text, str) or not text.strip():
            raise EngineError(f"{self.name} no devolvió una respuesta completa (done={body.get('done')!r})")  # CA-04
        usage = {
            k: int(body[src])
            for k, src in (("input_tokens", "prompt_eval_count"), ("output_tokens", "eval_count"))
            if isinstance(body.get(src), int)
        }
        return GenerationResult(text.strip(), self.name, usage, (time.perf_counter() - start) * 1000)
