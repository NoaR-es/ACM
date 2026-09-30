"""Configuración de proceso de ACM (variables de entorno).

La configuración *de cada proyecto* vive en su base SQLite (US-01.03); esta es la del proceso.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_HOST = "127.0.0.1"  # sin autenticación hasta EPIC-20: solo interfaz local por defecto
DEFAULT_PORT = 8765


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    principal: str = "local-admin"
    host: str = DEFAULT_HOST
    port: int = DEFAULT_PORT
    sqlite_synchronous: str = "FULL"  # ADR-013: FULL por defecto en la base global
    ollama_url: str | None = None  # EPIC-22: sin URL no se registra ningún motor Ollama
    ollama_model: str | None = None  # modelo de generación (contexto compacto, US-35.08)

    @classmethod
    def from_env(cls, **overrides: object) -> Settings:
        values: dict[str, object] = {
            "data_dir": Path(os.environ.get("ACM_DATA_DIR", Path.cwd() / ".acm-data")),
            "principal": os.environ.get("ACM_PRINCIPAL", "local-admin"),
            "host": os.environ.get("ACM_HOST", DEFAULT_HOST),
            "port": int(os.environ.get("ACM_PORT", DEFAULT_PORT)),
            "sqlite_synchronous": os.environ.get("ACM_SQLITE_SYNCHRONOUS", "FULL"),
            "ollama_url": os.environ.get("ACM_OLLAMA_URL") or None,
            "ollama_model": os.environ.get("ACM_OLLAMA_MODEL") or None,
        }
        values.update({k: v for k, v in overrides.items() if v is not None})
        values["data_dir"] = Path(values["data_dir"])  # type: ignore[arg-type]
        return cls(**values)  # type: ignore[arg-type]
