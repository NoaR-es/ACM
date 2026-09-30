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
    events_keep: int = 10_000  # ADR-018: eventos conservados para reanudar clientes WebSocket
    watchdog_interval_s: float = 600.0  # US-13.06: auditoría periódica de todos los proyectos; 0 la desactiva
    allowed_hosts: tuple[
        str, ...
    ] = ()  # nombres extra aceptados en la cabecera Host (TD-002; p. ej. tras un proxy TLS)

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
            "events_keep": int(os.environ.get("ACM_EVENTS_KEEP", 10_000)),
            "watchdog_interval_s": float(os.environ.get("ACM_WATCHDOG_INTERVAL_S", 600)),
            "allowed_hosts": tuple(h.strip() for h in os.environ.get("ACM_ALLOWED_HOSTS", "").split(",") if h.strip()),
        }
        values.update({k: v for k, v in overrides.items() if v is not None})
        values["data_dir"] = Path(values["data_dir"])  # type: ignore[arg-type]
        return cls(**values)  # type: ignore[arg-type]
