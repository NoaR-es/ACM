"""Modelos elegidos en ACM (US-50.09, US-22.06, US-22.07): un modelo de Ollama y, en Ollaya, uno por defecto y uno
por propósito.

La elección vive en la base global (`inference_settings`) y tiene prioridad sobre las variables de arranque
(`ACM_OLLAMA_MODEL`, `ACM_JEV_MODEL`). Los motores la leen en cada llamada, así que un cambio hecho desde la interfaz o
por MCP se aplica sin reiniciar y también en otros procesos de ACM (stdio) que compartan la base. Se cachea un segundo
para no leer SQLite en cada pregunta de una misma revisión.
"""

from __future__ import annotations

import json
import time
from datetime import UTC, datetime
from typing import Any

from acm.domain.projects import ProjectService

CACHE_S = 1.0
KEYS = ("ollama.model", "jev.default_model", "jev.models_by_purpose", "jev.model_notes")


class ModelSelection:
    def __init__(self, projects: ProjectService, *, ollama_model: str | None = None, jev_model: str | None = None):
        self.projects = projects
        self.env = {"ollama.model": ollama_model, "jev.default_model": jev_model}
        self._cache: tuple[float, dict[str, Any]] = (0.0, {})

    def _stored(self) -> dict[str, Any]:
        at, values = self._cache
        if time.monotonic() - at < CACHE_S:
            return values
        with self.projects.global_db.read() as conn:
            values = {r["key"]: json.loads(r["value_json"]) for r in conn.execute("SELECT * FROM inference_settings")}
        self._cache = (time.monotonic(), values)
        return values

    def get(self, key: str) -> Any:
        stored = self._stored()
        if key in stored:
            return stored[key]
        if key in ("jev.models_by_purpose", "jev.model_notes"):
            return {}
        return self.env.get(key)

    def source(self, key: str) -> str:
        """De dónde sale el valor: elegido en ACM, variable de arranque o sin valor."""
        if key in self._stored():
            return "acm"
        return "env" if self.env.get(key) else "none"

    def set(self, principal: str, key: str, value: Any) -> None:
        if key not in KEYS:
            raise KeyError(key)
        now = datetime.now(UTC).isoformat()
        with self.projects.global_db.write() as conn:
            conn.execute(
                "INSERT INTO inference_settings(key, value_json, updated_at, updated_by) VALUES (?, ?, ?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value_json = excluded.value_json, updated_at = excluded.updated_at, "
                "updated_by = excluded.updated_by",
                (key, json.dumps(value, ensure_ascii=False), now, principal),
            )
        self._cache = (0.0, {})

    # ------------------------------------------------------------------ lo que usan los motores
    def ollama_model(self) -> str | None:
        return self.get("ollama.model")

    def jev_model(self, purpose: str | None = None) -> str | None:
        """US-22.07: el modelo de Ollaya asignado al propósito o, si no hay, el modelo por defecto."""
        by_purpose = self.get("jev.models_by_purpose")
        return by_purpose.get(purpose) if purpose in by_purpose else self.get("jev.default_model")
