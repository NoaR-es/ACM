"""Ollama simulado para tests: servidor HTTP real (uvicorn en un hilo) con `/api/tags` y `/api/chat`.

Reproduce la forma documentada de la API de Ollama, no su comportamiento real: la compatibilidad con un Ollama de
verdad queda pendiente de SPIKE-005.
"""

from __future__ import annotations

import socket
import threading
import time
from dataclasses import dataclass, field
from typing import Any

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


@dataclass
class FakeOllamaState:
    models: list[str] = field(default_factory=lambda: ["qwen2.5:0.5b", "llama3.2:1b"])
    mode: str = "ok"  # ok | empty | not_done | error500 | not_json
    reply: str = "Resumen conservando REQ-001."
    requests: list[dict[str, Any]] = field(default_factory=list)


def _app(state: FakeOllamaState) -> FastAPI:
    app = FastAPI()

    @app.get("/api/tags")
    def tags() -> dict[str, Any]:
        state.requests.append({"path": "/api/tags"})
        return {"models": [{"name": m, "model": m, "size": 1} for m in state.models]}

    @app.post("/api/chat")
    async def chat(request: Request) -> Any:
        body = await request.json()
        state.requests.append({"path": "/api/chat", "body": body})
        if body.get("model") not in state.models:
            return JSONResponse({"error": f"model '{body.get('model')}' not found"}, status_code=404)
        if state.mode == "error500":
            return JSONResponse({"error": "llama runner process has terminated"}, status_code=500)
        if state.mode == "not_json":
            return JSONResponse(content="no es un objeto", status_code=200)
        content = "" if state.mode == "empty" else state.reply
        return {
            "model": body["model"],
            "message": {"role": "assistant", "content": content},
            "done": state.mode != "not_done",
            "prompt_eval_count": 42,
            "eval_count": 7,
        }

    return app


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class FakeOllama:
    def __init__(self) -> None:
        self.state = FakeOllamaState()
        self.port = free_port()
        self.url = f"http://127.0.0.1:{self.port}"
        config = uvicorn.Config(_app(self.state), host="127.0.0.1", port=self.port, log_level="warning")
        self.server = uvicorn.Server(config)
        self.thread = threading.Thread(target=self.server.run, daemon=True)

    def __enter__(self) -> FakeOllama:
        self.thread.start()
        deadline = time.monotonic() + 10
        while not self.server.started:
            if time.monotonic() > deadline:
                raise RuntimeError("el Ollama simulado no arrancó")
            time.sleep(0.02)
        return self

    def __exit__(self, *exc: object) -> None:
        self.server.should_exit = True
        self.thread.join(timeout=10)
