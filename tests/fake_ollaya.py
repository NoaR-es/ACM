"""Ollaya simulado para tests: servidor HTTP real con `/api/tags` y `/api/decide` (modelos de decisión JEV).

Reproduce el contrato documentado en `docs/api.md` de Ollaya (consultado el 2026-09-30; `10_IA/inference_engines.md`):
respuestas `choice`/`score`/`noul`, `usage`, errores `{"error", "code"}` con 422/404/503/500 y autenticación Bearer si
el servidor tiene clave. No reproduce la calidad de un modelo real: eso queda para SPIKE-006.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Any

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from tests.fake_ollama import free_port

ERRORS = {
    "invalid": (422, "INVALID_REQUEST"),
    "queue_full": (503, "QUEUE_FULL"),
    "load_failed": (500, "MODEL_LOAD_FAILED"),
}


@dataclass
class FakeOllayaState:
    models: list[str] = field(default_factory=lambda: ["laya:latest", "decider:latest"])
    api_key: str | None = None
    mode: str = "ok"  # ok | invalid | queue_full | load_failed | missing_answer | bad_choice
    # Respuestas fijadas por pregunta; `by_state_id` las fija solo para un estado con ese `id` (p. ej. una historia).
    answers: dict[str, dict[str, Any]] = field(default_factory=dict)
    by_state_id: dict[str, dict[str, dict[str, Any]]] = field(default_factory=dict)
    requests: list[dict[str, Any]] = field(default_factory=list)


def _answer(q: dict[str, Any], mode: str) -> dict[str, Any]:
    if q["type"] == "choice":
        opts = list(q["criteria"])
        probs = {o: (0.85 if i == 0 else round(0.15 / (len(opts) - 1), 4)) for i, o in enumerate(opts)}
        return {
            "type": "choice",
            "choice": "inventada" if mode == "bad_choice" else opts[0],
            "confidence": 0.78,
            "probabilities": probs,
        }
    if q["type"] == "score":
        levels = q["criteria"]
        probs = {str(i): (0.6 if i == 1 else round(0.4 / (len(levels) - 1), 4)) for i in range(len(levels))}
        return {
            "type": "score",
            "score": 1.1982,
            "confidence": 0.34,
            "legend": {str(i): lv for i, lv in enumerate(levels)},
            "probabilities": probs,
        }
    return {"type": "noul", "noul": 0.9127}


def _app(state: FakeOllayaState) -> FastAPI:
    app = FastAPI()

    def denied(request: Request) -> JSONResponse | None:
        if state.api_key and request.headers.get("authorization") != f"Bearer {state.api_key}":
            return JSONResponse({"error": "unauthorized", "code": "UNAUTHORIZED"}, status_code=401)
        return None

    @app.get("/api/tags")
    def tags(request: Request) -> Any:
        state.requests.append({"path": "/api/tags", "auth": request.headers.get("authorization")})
        return denied(request) or {"models": [{"name": m, "model": m, "size": 11862} for m in state.models]}

    @app.post("/api/decide")
    async def decide(request: Request) -> Any:
        body = await request.json()
        state.requests.append({"path": "/api/decide", "body": body, "auth": request.headers.get("authorization")})
        if (resp := denied(request)) is not None:
            return resp
        model = body.get("model", "")
        if model not in state.models and f"{model}:latest" not in state.models:
            return JSONResponse(
                {"error": f'model "{model}" not found, try pulling it first', "code": "MODEL_NOT_FOUND"},
                status_code=404,
            )
        if state.mode in ERRORS:
            status, code = ERRORS[state.mode]
            return JSONResponse({"error": code.lower(), "code": code}, status_code=status)
        fixed = dict(state.answers)
        if isinstance(body.get("state"), dict):
            fixed |= state.by_state_id.get(body["state"].get("id"), {})
        answers = {k: fixed.get(k) or _answer(q, state.mode) for k, q in body["questions"].items()}
        if state.mode == "missing_answer":
            answers.pop(next(iter(answers)))
        return {
            "model": f"{model}:en",
            "answers": answers,
            "usage": {"input_tokens": 118, "output_tokens": 0},
            "done_reason": "decide",
        }

    return app


class FakeOllaya:
    def __init__(self) -> None:
        self.state = FakeOllayaState()
        self.port = free_port()
        self.url = f"http://127.0.0.1:{self.port}"
        config = uvicorn.Config(_app(self.state), host="127.0.0.1", port=self.port, log_level="warning")
        self.server = uvicorn.Server(config)
        self.thread = threading.Thread(target=self.server.run, daemon=True)

    def __enter__(self) -> FakeOllaya:
        self.thread.start()
        deadline = time.monotonic() + 10
        while not self.server.started:
            if time.monotonic() > deadline:
                raise RuntimeError("el Ollaya simulado no arrancó")
            time.sleep(0.02)
        return self

    def __exit__(self, *exc: object) -> None:
        self.server.should_exit = True
        self.thread.join(timeout=10)
