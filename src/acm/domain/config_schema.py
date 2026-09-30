"""Esquema de configuración de proyecto, versión 1 (US-01.03; tabla en `refinements/US-01.03.md`)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from acm.domain.errors import DataIntegrityError, InvalidArgument

DECISION_ENGINES = ("rules", "jev", "ollama")  # ADR-015


@dataclass(frozen=True)
class Parameter:
    key: str
    type: str
    default: Any
    allowed: str
    requires_reload: bool
    description: str
    consumer: str
    validate: Callable[[Any], str | None]  # devuelve el motivo del rechazo, o None si es válido

    def describe(self, current: Any) -> dict[str, Any]:
        return {
            "key": self.key,
            "value": current,
            "default": self.default,
            "type": self.type,
            "allowed": self.allowed,
            "requires_reload": self.requires_reload,
            "description": self.description,
            "consumer": self.consumer,
        }


def _enum(*options: str) -> Callable[[Any], str | None]:
    def check(value: Any) -> str | None:
        return None if isinstance(value, str) and value in options else f"debe ser uno de {list(options)}"

    return check


def _int_range(lo: int, hi: int) -> Callable[[Any], str | None]:
    def check(value: Any) -> str | None:
        if not isinstance(value, int) or isinstance(value, bool):
            return "debe ser un entero"
        return None if lo <= value <= hi else f"debe estar entre {lo} y {hi}"

    return check


def _engine_order(value: Any) -> str | None:
    if not isinstance(value, list) or not value:
        return "debe ser una lista no vacía"
    if any(not isinstance(v, str) or v not in DECISION_ENGINES for v in value):
        return f"solo admite valores de {list(DECISION_ENGINES)}"
    if len(set(value)) != len(value):
        return "no admite valores repetidos"
    return None


PARAMETERS: dict[str, Parameter] = {
    p.key: p
    for p in (
        Parameter(
            "sqlite.synchronous",
            "enum",
            "FULL",
            "FULL | NORMAL",
            True,
            "Durabilidad de las escrituras de la base del proyecto (ADR-013).",
            "capa de datos (se aplica a las conexiones nuevas)",
            _enum("FULL", "NORMAL"),
        ),
        Parameter(
            "context.max_tokens",
            "int",
            8000,
            "256..200000",
            False,
            "Presupuesto de tokens del contexto compacto que ACM entrega al agente (segundo cerebro).",
            "pendiente: servicio de contexto (US-35.08)",
            _int_range(256, 200_000),
        ),
        Parameter(
            "decision.engine_order",
            "list",
            ["rules", "jev", "ollama"],
            "subconjunto sin repetidos de rules, jev, ollama; no vacío",
            False,
            "Orden de preferencia de motores de decisión del router (ADR-015).",
            "pendiente: router de inferencia (ADR-015)",
            _engine_order,
        ),
    )
}


def validate_changes(changes: Any) -> dict[str, Any]:
    """Valida todos los cambios antes de guardar ninguno (CA-02). Lanza InvalidArgument con el primer error."""
    if not isinstance(changes, dict):
        raise InvalidArgument("debe ser un objeto {parámetro: valor}", field="changes")
    for key, value in changes.items():
        param = PARAMETERS.get(key)
        if param is None:
            raise InvalidArgument(f"parámetro desconocido; válidos: {sorted(PARAMETERS)}", field=key)
        reason = param.validate(value)
        if reason:
            raise InvalidArgument(reason, field=key)
    return dict(changes)


def check_stored(key: str, value: Any) -> Any:
    """Valida un valor leído de la base: un valor corrupto es un error de integridad, no se ignora."""
    param = PARAMETERS.get(key)
    if param is None or param.validate(value):
        raise DataIntegrityError(f"valor de configuración inválido en la base: {key}={value!r}")
    return value
