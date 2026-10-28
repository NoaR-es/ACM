"""Catálogo y selección de modelos (US-50.09, US-50.10, US-22.06, US-22.07).

- `catalog()` lo pueden leer operadores y agentes: qué runtimes hay (Ollama, Ollaya), qué modelos detecta cada uno
  (con sus detalles), qué modelo está elegido y para qué propósitos, la nota del operador de cada modelo de Ollaya y
  cómo usar cada motor. Así un agente sabe en qué modelo delegar sin gastar tokens en averiguarlo.
- `select()` (solo admin) elige un modelo de Ollama y, en Ollaya, uno por defecto y uno por propósito. Solo se aceptan
  modelos que el runtime detecta en ese momento (US-22.02 CA-01: nunca un modelo inventado).
"""

from __future__ import annotations

from typing import Any

from acm.domain.errors import AcmError, FailedPrecondition, Forbidden, InvalidArgument
from acm.domain.projects import ProjectService
from acm.inference.jev import model_installed
from acm.inference.ollaya_models import guide_for, overview
from acm.inference.router import EngineRouter

# Propósitos que usa ACM por sí mismo. Los agentes pueden usar otros en `acm_decide`; aparecen en `seen_purposes`.
KNOWN_PURPOSES: dict[str, str] = {
    "story.quality": "Gate READY: ¿la historia está completa? Lo responden las reglas, sin modelo.",
    "agile.story_review": "Supervisor: ¿cumple INVEST?, ¿criterios verificables?, ¿tamaño? (JEV u Ollama).",
    "agile.sprint_review": "Supervisor: riesgo de no cumplir el objetivo del sprint (JEV u Ollama).",
    "agile.report": "Supervisor: redacción del informe de lo hecho, pendiente e incongruencias (Ollama).",
    "context.compact": "Resumen de las secciones de apoyo del contexto compacto (Ollama).",
    "agent.chat": "Conversación de un agente o persona con el modelo local, con herramientas de ACM (Ollama).",
}
USAGE = {
    "jev": (
        "Decisiones tipadas con probabilidades reales (calibradas): `acm_decide(project_id, purpose, questions, state, "
        "model?)` con preguntas noul (sí/no), choice (clasificar) o score (puntuar). Sin `model`, ACM usa el modelo "
        "asignado al propósito o el de por defecto. Úsalo para clasificar, filtrar o validar sin razonar tú."
    ),
    "ollama": (
        "Modelo generativo local: `acm_chat(project_id, message, thread_id?)` conversa en un hilo que ACM conserva "
        "(solo envías el mensaje nuevo) y el modelo consulta él mismo el proyecto con herramientas de ACM "
        "de solo lectura. "
        "También resume el contexto compacto y, sin JEV, decide sin calibrar."
    ),
}


class ModelService:
    def __init__(self, projects: ProjectService, engines: EngineRouter):
        self.projects = projects
        self.engines = engines

    def _require_known(self, principal: str) -> str:
        with self.projects.global_db.read() as conn:
            return self.projects._principal_role(conn, principal)

    def _engine(self, provider: str, kind: str = "decision") -> Any:
        pool = self.engines.registry.decision if kind == "decision" else self.engines.registry.generation
        return next((e for e in pool if e.provider == provider), None)

    @staticmethod
    def _detect(engine: Any) -> tuple[list[dict[str, Any]], str]:
        try:
            return engine.client.list_details(), ""
        except AcmError as exc:
            return [], exc.message

    def _seen_purposes(self) -> list[str]:
        with self.projects.global_db.read() as conn:
            rows = conn.execute("SELECT DISTINCT purpose FROM inference_calls ORDER BY purpose").fetchall()
        return [r[0] for r in rows if r[0] not in KNOWN_PURPOSES]

    # ------------------------------------------------------------------ lectura (US-50.10)
    def catalog(self, principal: str) -> dict[str, Any]:
        self._require_known(principal)
        sel = self.engines.selection
        out: dict[str, Any] = {"purposes": KNOWN_PURPOSES, "seen_purposes": self._seen_purposes(), "usage": USAGE}
        ollama = self._engine("ollama", "generation")
        if ollama is None:
            out["ollama"] = {"configured": False, "hint": "Configura ACM_OLLAMA_URL para usar modelos locales."}
        else:
            models, error = self._detect(ollama)
            out["ollama"] = {
                "configured": True,
                "endpoint": ollama.endpoint,
                "selected": ollama.model,
                "source": sel.source("ollama.model") if sel else "env",
                "available": models,
                "error": error,
            }
        jev = self._engine("jev")
        if jev is None:
            out["jev"] = {"configured": False, "hint": "Configura ACM_JEV_URL (servidor Ollaya) para decisiones JEV."}
        else:
            models, error = self._detect(jev)
            by_purpose = sel.get("jev.models_by_purpose") if sel else {}
            notes = sel.get("jev.model_notes") if sel else {}
            default = jev.model
            for m in models:
                m["default"] = default is not None and model_installed(default, [m["name"]])
                m["purposes"] = sorted(p for p, mod in by_purpose.items() if model_installed(mod, [m["name"]]))
                m["note"] = notes.get(m["name"], "")
                m["guide"] = guide_for(m["name"])  # qué es y para qué sirve (fuente: Ollaya), o None si no se conoce
            out["jev"] = {
                "configured": True,
                "endpoint": jev.endpoint,
                "default_model": default,
                "source": sel.source("jev.default_model") if sel else "env",
                "models_by_purpose": by_purpose,
                "available": models,
                "error": error,
                "guide": overview(),
            }
        return out

    # ------------------------------------------------------------------ selección (US-50.09 / US-22.06)
    def select(
        self,
        principal: str,
        *,
        ollama_model: Any = None,
        jev_default_model: Any = None,
        jev_models_by_purpose: Any = None,
        jev_model_notes: Any = None,
    ) -> dict[str, Any]:
        with self.projects.global_db.read() as conn:
            if self.projects._principal_role(conn, principal) != "admin":
                raise Forbidden("solo un admin puede elegir los modelos")
        sel = self.engines.selection
        if sel is None:
            raise FailedPrecondition("esta instancia no tiene selección de modelos configurable")
        changes: list[tuple[str, Any]] = []
        if ollama_model is not None:
            engine = self._engine("ollama", "generation")
            if engine is None:
                raise FailedPrecondition("Ollama no está configurado (ACM_OLLAMA_URL)")
            installed = [m["name"] for m in self._detect_or_fail(engine, "ollama_model")]
            if ollama_model not in installed:
                raise InvalidArgument(
                    f"{ollama_model!r} no está instalado; detectados: {installed}", field="ollama_model"
                )
            changes.append(("ollama.model", ollama_model))
        if jev_default_model is not None or jev_models_by_purpose is not None or jev_model_notes is not None:
            engine = self._engine("jev")
            if engine is None:
                raise FailedPrecondition("JEV no está configurado (ACM_JEV_URL)")
            installed = [m["name"] for m in self._detect_or_fail(engine, "jev")]

            def check(model: Any, field: str) -> str:
                if not isinstance(model, str) or not model_installed(model, installed):
                    raise InvalidArgument(
                        f"{model!r} no está instalado en Ollaya; detectados: {installed}", field=field
                    )
                return model

            if jev_default_model is not None:
                changes.append(("jev.default_model", check(jev_default_model, "jev_default_model")))
            if jev_models_by_purpose is not None:
                if not isinstance(jev_models_by_purpose, dict):
                    raise InvalidArgument("debe ser un objeto {propósito: modelo}", field="jev_models_by_purpose")
                clean = {}
                for purpose, model in jev_models_by_purpose.items():
                    if not isinstance(purpose, str) or not 1 <= len(purpose) <= 100:
                        raise InvalidArgument(
                            "cada propósito debe ser un texto de 1 a 100", field="jev_models_by_purpose"
                        )
                    clean[purpose] = check(model, f"jev_models_by_purpose.{purpose}")
                changes.append(("jev.models_by_purpose", clean))
            if jev_model_notes is not None:
                if not isinstance(jev_model_notes, dict) or any(
                    not isinstance(v, str) or len(v) > 500 for v in jev_model_notes.values()
                ):
                    raise InvalidArgument("debe ser un objeto {modelo: nota ≤ 500}", field="jev_model_notes")
                for model in jev_model_notes:
                    check(model, f"jev_model_notes.{model}")
                changes.append(("jev.model_notes", {k: v.strip() for k, v in jev_model_notes.items() if v.strip()}))
        if not changes:
            raise InvalidArgument("indica al menos un cambio", field="changes")
        for key, value in changes:  # todo validado antes de guardar nada
            sel.set(principal, key, value)
        self.projects.events.append(
            "models.changed",
            principal=principal,
            entity_type="models",
            entity_id="selection",
            data={"changed": [k for k, _ in changes]},
        )
        self.engines.registry.refresh()
        return self.catalog(principal)

    @staticmethod
    def _detect_or_fail(engine: Any, field: str) -> list[dict[str, Any]]:
        try:
            return engine.client.list_details()
        except AcmError as exc:
            raise FailedPrecondition(f"no se pudieron detectar los modelos: {exc.message}", field=field) from exc
