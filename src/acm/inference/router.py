"""Registro de motores (US-47.01) y router con fallback (ADR-015 §3).

Los consumidores (gates, herramientas MCP, servicio de contexto) solo conocen `EngineRouter`; nunca una
implementación concreta. Conectar JEV (EPIC-50) = registrar su `DecisionEngine`: ningún consumidor cambia.

Orden de decisión: parámetro de proyecto `decision.engine_order` (proveedores `rules`, `jev`, `ollama`). Un motor que
no cubre la petición (`supports() == False`) se salta sin contar como fallo; uno que falla (`ENGINE_UNAVAILABLE`,
`ENGINE_ERROR`) cede al siguiente y la respuesta lo indica en `fallback_from`. Cada llamada se registra en
`inference_calls` (motor, propósito, proyecto, resultado, duración y tokens si el motor los da).
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from acm.domain.errors import AcmError, FailedPrecondition, Forbidden, InvalidArgument
from acm.domain.projects import ProjectService
from acm.inference.ports import (
    DecisionEngine,
    DecisionRequest,
    DecisionResult,
    EngineError,
    EngineHealth,
    EngineUnavailable,
    GenerationEngine,
    GenerationRequest,
    GenerationResult,
)
from acm.inference.rules import RulesDecisionEngine


def _now() -> str:
    return datetime.now(UTC).isoformat()


@dataclass(frozen=True)
class Routed:
    """Resultado de una llamada enrutada y el identificador de su registro en `inference_calls` (US-22.03 CA-02)."""

    result: DecisionResult | GenerationResult
    call_id: int


class EngineRegistry:
    """Motores disponibles en el proceso y su último estado de salud persistido en la base global."""

    def __init__(self, projects: ProjectService):
        self.projects = projects
        self.decision: list[DecisionEngine] = []
        self.generation: list[GenerationEngine] = []

    def register(self, engine: DecisionEngine | GenerationEngine) -> None:
        if not isinstance(getattr(engine, "name", None), str) or not getattr(engine, "provider", None):
            raise InvalidArgument("un motor necesita 'name' y 'provider'", field="engine")
        if engine.name in {e.name for e in (*self.decision, *self.generation)}:
            raise InvalidArgument(f"ya hay un motor registrado con el nombre {engine.name!r}", field="engine")
        if isinstance(engine, DecisionEngine):
            kind, target = "decision", self.decision
        elif isinstance(engine, GenerationEngine):
            kind, target = "generation", self.generation
        else:
            raise InvalidArgument("no implementa DecisionEngine ni GenerationEngine", field="engine")
        target.append(engine)
        with self.projects.global_db.write() as conn:
            conn.execute(
                "INSERT INTO inference_engines(name, kind, provider, endpoint, status) VALUES (?, ?, ?, ?, 'unknown') "
                "ON CONFLICT(name) DO UPDATE SET kind = excluded.kind, provider = excluded.provider, "
                "endpoint = excluded.endpoint",
                (engine.name, kind, engine.provider, getattr(engine, "endpoint", "")),
            )

    def close(self) -> None:
        """Libera los recursos de los motores que los tengan (p. ej. el cliente HTTP de Ollama)."""
        for engine in (*self.decision, *self.generation):
            close = getattr(engine, "close", None)
            if callable(close):
                close()

    def refresh(self) -> list[dict[str, Any]]:
        """Comprueba la salud de cada motor y guarda los modelos detectados (US-22.01)."""
        for engine in (*self.decision, *self.generation):
            try:
                health = engine.health()
            except Exception as exc:  # un motor mal implementado no debe tumbar el refresco de los demás
                health = EngineHealth(False, f"{type(exc).__name__}: {exc}")
            with self.projects.global_db.write() as conn:
                conn.execute(
                    "UPDATE inference_engines SET status = ?, detail = ?, models_json = ?, checked_at = ? "
                    "WHERE name = ?",
                    (
                        "ok" if health.ok else "error",
                        health.detail,
                        json.dumps(list(health.models)),
                        _now(),
                        engine.name,
                    ),
                )
        return self.list()

    def list(self) -> list[dict[str, Any]]:
        registered = {e.name for e in (*self.decision, *self.generation)}
        with self.projects.global_db.read() as conn:
            rows = conn.execute("SELECT * FROM inference_engines ORDER BY kind, name").fetchall()
        out = []
        for r in rows:
            row = dict(r)
            row["models"] = json.loads(row.pop("models_json"))
            row["registered"] = row["name"] in registered  # motores de ejecuciones anteriores quedan como histórico
            out.append(row)
        return out


class EngineRouter:
    def __init__(self, projects: ProjectService, registry: EngineRegistry | None = None):
        self.projects = projects
        self.registry = registry if registry is not None else EngineRegistry(projects)
        if not any(e.provider == "rules" for e in self.registry.decision):
            self.registry.register(RulesDecisionEngine())  # US-35.11 CA-02: siempre hay un motor sin modelo

    # ------------------------------------------------------------------ decisión
    def _order(self, principal: str, project_id: str) -> list[str]:
        params = self.projects.get_config(principal, project_id)["parameters"]
        return next(p["value"] for p in params if p["key"] == "decision.engine_order")

    def decide(self, principal: str, request: DecisionRequest) -> Routed:
        self.projects._project_role(principal, request.project_id)  # NOT_FOUND si el proyecto no es accesible
        order = self._order(principal, request.project_id)
        candidates = [e for provider in order for e in self.registry.decision if e.provider == provider]
        failures: list[tuple[str, AcmError]] = []
        start = time.perf_counter()
        for engine in candidates:
            if not engine.supports(request):
                continue
            try:
                result = engine.decide(request)
                if set(result.answers) != set(request.questions):
                    raise EngineError("no respondió exactamente a las preguntas pedidas")
            except (EngineUnavailable, EngineError) as exc:
                failures.append((engine.name, exc))
                continue
            if failures:
                result = DecisionResult(result.answers, result.engine, result.usage, result.duration_ms, failures[0][0])
            call_id = self._log(
                principal,
                request.project_id,
                "decision",
                request.purpose,
                result.engine,
                result.fallback_from,
                "ok",
                "",
                (time.perf_counter() - start) * 1000,
                result.usage,
            )
            return Routed(result, call_id)
        reason = (
            _describe(failures)
            if failures
            else f"ningún motor de {order} cubre el propósito {request.purpose!r} con estas preguntas"
        )
        self._log(
            principal,
            request.project_id,
            "decision",
            request.purpose,
            "",
            None,
            "error",
            reason,
            (time.perf_counter() - start) * 1000,
            {},
        )
        raise EngineUnavailable(reason)

    # ------------------------------------------------------------------ generación
    def has_generation(self) -> bool:
        return bool(self.registry.generation)

    def generate(self, principal: str, request: GenerationRequest) -> Routed:
        self.projects._project_role(principal, request.project_id)
        failures: list[tuple[str, AcmError]] = []
        start = time.perf_counter()
        for engine in self.registry.generation:
            try:
                result = engine.generate(request)
            except (EngineUnavailable, EngineError) as exc:
                failures.append((engine.name, exc))
                continue
            if failures:
                result = GenerationResult(result.text, result.engine, result.usage, result.duration_ms, failures[0][0])
            call_id = self._log(
                principal,
                request.project_id,
                "generation",
                request.purpose,
                result.engine,
                result.fallback_from,
                "ok",
                "",
                (time.perf_counter() - start) * 1000,
                result.usage,
            )
            return Routed(result, call_id)
        reason = _describe(failures) or "no hay ningún motor de generación configurado (ACM_OLLAMA_URL)"
        self._log(
            principal,
            request.project_id,
            "generation",
            request.purpose,
            "",
            None,
            "error",
            reason,
            (time.perf_counter() - start) * 1000,
            {},
        )
        # Si solo falló un motor, se conserva su código (ENGINE_ERROR ≠ no disponible: US-22.03 CA-03/04).
        if len(failures) == 1 and isinstance(failures[0][1], EngineError):
            raise EngineError(reason)
        raise EngineUnavailable(reason)

    # ------------------------------------------------------------------ registro de llamadas
    def _log(
        self,
        principal: str,
        project_id: str,
        kind: str,
        purpose: str,
        engine: str,
        fallback_from: str | None,
        status: str,
        error: str,
        duration_ms: float,
        usage: dict[str, int],
    ) -> int:
        with self.projects.global_db.write() as conn:
            cur = conn.execute(
                "INSERT INTO inference_calls(ts, principal, project_id, kind, purpose, engine, fallback_from, status, "
                "error, duration_ms, input_tokens, output_tokens) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    _now(),
                    principal,
                    project_id,
                    kind,
                    purpose,
                    engine,
                    fallback_from,
                    status,
                    error,
                    round(duration_ms, 3),
                    usage.get("input_tokens"),
                    usage.get("output_tokens"),
                ),
            )
            return int(cur.lastrowid)

    def calls(self, principal: str, *, project_id: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        """Registro de llamadas de inferencia (solo admin, como la auditoría MCP)."""
        with self.projects.global_db.read() as conn:
            if self.projects._principal_role(conn, principal) != "admin":
                raise Forbidden("solo un admin puede consultar las llamadas de inferencia")
            if project_id is None:
                rows = conn.execute("SELECT * FROM inference_calls ORDER BY id DESC LIMIT ?", (limit,))
            else:
                rows = conn.execute(
                    "SELECT * FROM inference_calls WHERE project_id = ? ORDER BY id DESC LIMIT ?", (project_id, limit)
                )
            return [dict(r) for r in rows]


def _describe(failures: list[tuple[str, AcmError]]) -> str:
    return "; ".join(f"{name} → {exc}" for name, exc in failures)


def require_calibrated(result: DecisionResult, consumer: str) -> None:
    """Un consumidor que decide automáticamente (gate) no acepta la «confianza» de un motor no calibrado (ADR-015)."""
    loose = sorted(k for k, a in result.answers.items() if not a.calibrated)
    if loose:
        raise FailedPrecondition(
            f"{consumer}: {result.engine} dio respuestas no calibradas ({loose}); requiere revisión humana"
        )
