"""US-18.03 — Gestionar migraciones (ver control/01_PRODUCTO/refinements/US-18.03.md)."""

from __future__ import annotations

import multiprocessing as mp
import sqlite3
from pathlib import Path

import pytest

from acm.db import schema
from acm.db.connection import Database
from acm.db.migrations import Migration, current_version, migrate, validate_catalog
from acm.domain.errors import MigrationError
from acm.domain.projects import ProjectService
from tests.conftest import ADMIN

CATALOG = (
    Migration(1, "crear_a", ("CREATE TABLE a (id INTEGER PRIMARY KEY)",)),
    Migration(2, "columna_en_a", ("ALTER TABLE a ADD COLUMN nombre TEXT",)),  # depende de la 1
    Migration(3, "crear_b", ("CREATE TABLE b (a_id INTEGER REFERENCES a(id))",)),
)


def _versions(db: Database) -> list[int]:
    with db.read() as conn:
        return [r[0] for r in conn.execute("SELECT version FROM schema_migrations ORDER BY version")]


def test_us1803_ca01_cada_migracion_tiene_version(tmp_path: Path) -> None:
    for catalog in (schema.GLOBAL, schema.PROJECT, CATALOG):
        validate_catalog(catalog)
        assert all(isinstance(m.version, int) and m.name for m in catalog)
    db = Database(tmp_path / "x.db")
    migrate(db, CATALOG)
    with db.read() as conn:
        rows = conn.execute("SELECT version, name FROM schema_migrations ORDER BY version").fetchall()
    assert [(r[0], r[1]) for r in rows] == [(1, "crear_a"), (2, "columna_en_a"), (3, "crear_b")]
    db.close()


def test_us1803_ca02_se_ejecutan_en_orden(tmp_path: Path) -> None:
    db = Database(tmp_path / "x.db")
    assert migrate(db, CATALOG) == [1, 2, 3]  # la 2 fallaría si se ejecutara antes que la 1
    assert migrate(db, CATALOG) == []  # base al día: no se ejecuta nada
    db.close()


def test_us1803_ca03_migracion_fallida_no_queda_marcada(tmp_path: Path) -> None:
    bad = (
        CATALOG[0],
        Migration(2, "rota", ("CREATE TABLE parcial (id INTEGER)", "ESTO NO ES SQL")),
    )
    db = Database(tmp_path / "x.db")
    with pytest.raises(MigrationError, match="migración 2"):
        migrate(db, bad)
    assert _versions(db) == [1]
    assert current_version(db) == 1
    with db.read() as conn:
        assert conn.execute("SELECT 1 FROM sqlite_master WHERE name = 'parcial'").fetchone() is None
    db.close()


def test_us1803_ca04_version_actual_consultable(service: ProjectService) -> None:
    assert current_version(service.global_db) == len(schema.GLOBAL)
    assert service.system_info()["global_schema_version"] == len(schema.GLOBAL)
    service.create(ADMIN, "alpha", "Alpha")
    assert service.open(ADMIN, "alpha")["schema_version"] == len(schema.PROJECT)


@pytest.mark.parametrize(
    "catalog",
    [
        (Migration(1, "a", ("SELECT 1",)), Migration(3, "c", ("SELECT 1",))),
        (Migration(2, "b", ("SELECT 1",)),),
        (Migration(1, "", ("SELECT 1",)),),
        (Migration(1, "sin_sentencias", ()),),
    ],
)
def test_us1803_catalogo_invalido_rechazado(catalog: tuple[Migration, ...]) -> None:
    with pytest.raises(MigrationError, match="catálogo inválido"):
        validate_catalog(catalog)


def test_us1803_base_de_version_futura_rechazada(tmp_path: Path) -> None:
    db = Database(tmp_path / "x.db")
    migrate(db, CATALOG)
    with db.write() as conn:
        conn.execute("INSERT INTO schema_migrations(version, name, applied_at) VALUES (99, 'futura', 'x')")
    with pytest.raises(MigrationError, match="más nueva"):
        migrate(db, CATALOG)
    db.close()


def _migrate_worker(path: str) -> list[int]:
    db = Database(path)
    try:
        return migrate(db, CATALOG)
    finally:
        db.close()


def test_us1803_migracion_concurrente_una_sola_vez(tmp_path: Path) -> None:
    path = str(tmp_path / "x.db")
    with mp.get_context("spawn").Pool(4) as pool:
        results = pool.map(_migrate_worker, [path] * 4)
    applied = sorted(v for r in results for v in r)
    assert applied == [1, 2, 3]  # cada versión la aplica exactamente un proceso
    conn = sqlite3.connect(path)
    assert [r[0] for r in conn.execute("SELECT version FROM schema_migrations ORDER BY version")] == [1, 2, 3]
    conn.close()
