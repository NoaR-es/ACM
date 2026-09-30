"""Errores de dominio de ACM.

Cada error lleva un código estable y un mensaje legible. La frontera MCP los traduce a errores de
herramienta con el texto `"<CODE>: <mensaje>"` para que el agente conozca el motivo (GAP-007).
"""

from __future__ import annotations


class AcmError(Exception):
    code = "INTERNAL"

    def __init__(self, message: str, *, field: str | None = None):
        super().__init__(message)
        self.message = message
        self.field = field

    def __str__(self) -> str:
        prefix = f"{self.field}: " if self.field else ""
        return f"{self.code}: {prefix}{self.message}"


class InvalidArgument(AcmError):
    code = "INVALID_ARGUMENT"


class NotFound(AcmError):
    code = "NOT_FOUND"


class AlreadyExists(AcmError):
    code = "ALREADY_EXISTS"


class Forbidden(AcmError):
    code = "FORBIDDEN"


class StorageError(AcmError):
    code = "STORAGE_ERROR"


class DataIntegrityError(AcmError):
    code = "DATA_INTEGRITY"


class MigrationError(AcmError):
    code = "MIGRATION_ERROR"


class FailedPrecondition(AcmError):
    code = "FAILED_PRECONDITION"


class Unauthenticated(AcmError):
    """Credencial ausente, desconocida o revocada (EPIC-20)."""

    code = "UNAUTHENTICATED"
