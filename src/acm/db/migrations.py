"""Migrador de esquema versionado (US-18.03, TECH-007).

Cada migración es una lista de sentencias (no `executescript`, que hace COMMIT implícito) y se aplica en
su propia transacción `BEGIN IMMEDIATE` junto con su fila en `schema_migrations`: si una sentencia
falla, ni sus cambios ni su registro persisten (CA-03).
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime

from acm.db.connection import Database
from acm.domain.errors import MigrationError

_BOOKKEEPING = (
    "CREATE TABLE IF NOT EXISTS schema_migrations ("
    " version INTEGER PRIMARY KEY, name TEXT NOT NULL, applied_at TEXT NOT NULL)"
)


@dataclass(frozen=True)
class Migration:
    version: int
    name: str
    statements: tuple[str, ...]


def validate_catalog(catalog: tuple[Migration, ...]) -> None:
    versions = [m.version for m in catalog]
    if versions != list(range(1, len(catalog) + 1)):
        raise MigrationError(f"catálogo inválido: las versiones deben ser consecutivas desde 1 (hay {versions})")
    for m in catalog:
        if not m.name or not m.statements:
            raise MigrationError(f"catálogo inválido: la migración {m.version} necesita nombre y sentencias")


def current_version(db: Database) -> int:
    with db.read() as conn:
        exists = conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='schema_migrations'").fetchone()
        if not exists:
            return 0
        return int(conn.execute("SELECT COALESCE(MAX(version), 0) FROM schema_migrations").fetchone()[0])


def migrate(db: Database, catalog: tuple[Migration, ...]) -> list[int]:
    """Aplica en orden las migraciones pendientes y devuelve las versiones aplicadas."""
    validate_catalog(catalog)
    latest = catalog[-1].version if catalog else 0
    with db.write() as conn:
        conn.execute(_BOOKKEEPING)
    if current_version(db) > latest:
        raise MigrationError(
            f"{db.path}: versión de esquema {current_version(db)} mayor que la última conocida ({latest}); "
            "la base pertenece a una versión más nueva de ACM"
        )
    applied: list[int] = []
    for migration in catalog:
        with db.write() as conn:
            # Se vuelve a comprobar dentro de la transacción: otro proceso pudo aplicarla (caso límite concurrente).
            done = conn.execute("SELECT 1 FROM schema_migrations WHERE version = ?", (migration.version,)).fetchone()
            if done:
                continue
            for statement in migration.statements:
                try:
                    conn.execute(statement)
                except sqlite3.Error as exc:
                    raise MigrationError(
                        f"migración {migration.version} ({migration.name}) falló en: {statement[:80]!r}: {exc}"
                    ) from exc
            conn.execute(
                "INSERT INTO schema_migrations(version, name, applied_at) VALUES (?, ?, ?)",
                (migration.version, migration.name, datetime.now(UTC).isoformat()),
            )
        applied.append(migration.version)
    return applied
