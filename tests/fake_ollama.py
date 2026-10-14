"""Ollama simulado para tests: servidor HTTP real (uvicorn en un hilo) con `/api/tags` y `/api/chat`.

Reproduce la forma documentada de la API de Ollama, no su comportamiento real: la compatibilidad con un Ollama de
verdad queda pendiente de SPIKE-005.
"""

from __future__ import annotations

import json
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
    # Decisiones (petición con `format`): opción elegida por pregunta; si falta, la primera del `enum` del esquema.
    decisions: dict[str, str] = field(default_factory=dict)
    # Conversación con herramientas (petición con `tools`): mensajes que devuelve en orden; cada uno es
    # {"tool_calls": [...]} (formato de Ollama) o {"content": "..."}. Vacío: responde `reply`.
    script: list[dict[str, Any]] = field(default_factory=list)
    script_always: bool = False  # el modelo sigue pidiendo herramientas aunque no se le ofrezcan
    requests: list[dict[str, Any]] = field(default_factory=list)


def _app(state: FakeOllamaState) -> FastAPI:
    app = FastAPI()

    @app.get("/api/tags")
    def tags() -> dict[str, Any]:
        state.requests.append({"path": "/api/tags"})
        details = {"format": "gguf", "family": "qwen2", "parameter_size": "494M", "quantization_level": "Q4_K_M"}
        return {"models": [{"name": m, "model": m, "size": 1, "details": details} for m in state.models]}

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
        if (body.get("tools") or state.script_always) and state.script and state.mode == "ok":
            step = state.script.pop(0)
            message = {"role": "assistant", "content": step.get("content", "")}
            if "tool_calls" in step:
                message["tool_calls"] = step["tool_calls"]
            return {"model": body["model"], "message": message, "done": True, "prompt_eval_count": 50, "eval_count": 5}
        schema = body.get("format")
        if isinstance(schema, dict) and state.mode == "ok":
            props = schema.get("properties", {})
            content = json.dumps({k: state.decisions.get(k, p["enum"][0]) for k, p in props.items()})
        else:
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
