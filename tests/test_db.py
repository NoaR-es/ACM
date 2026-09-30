"""US-18.01 (persistencia) y US-18.02 (transacciones) — ver control/01_PRODUCTO/refinements/."""

from __future__ import annotations

import json
import multiprocessing as mp
import signal
import sqlite3
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest

from acm.db.connection import Database, NestedTransactionError
from acm.domain.errors import StorageError
from acm.domain.projects import ProjectService
from tests.conftest import ADMIN


def _db_with_table(path: Path, **kw) -> Database:
    db = Database(path, **kw)
    with db.write() as conn:
        conn.execute("CREATE TABLE t (id INTEGER PRIMARY KEY, v TEXT NOT NULL)")
        conn.execute("CREATE TABLE child (id INTEGER PRIMARY KEY, t_id INTEGER NOT NULL REFERENCES t(id))")
        conn.execute("CREATE TABLE counter (id INTEGER PRIMARY KEY CHECK (id = 1), n INTEGER NOT NULL)")
        conn.execute("INSERT INTO counter VALUES (1, 0)")
    return db


def test_pragmas_adr013_activos(tmp_path: Path) -> None:
    db = Database(tmp_path / "x.db")
    p = db.pragmas()
    assert p["journal_mode"].lower() == "wal"
    assert p["synchronous"] == "FULL"
    assert p["foreign_keys"] is True
    assert p["busy_timeout_ms"] == 5000
    db.close()


# ---------------------------------------------------------------- US-18.01
def test_us1801_ca01_estado_relevante_almacenado(service: ProjectService, data_dir: Path) -> None:
    service.create(ADMIN, "alpha", "Alpha")
    service.set_config(ADMIN, "alpha", {"context.max_tokens": 4000})
    g = sqlite3.connect(data_dir / "acm.db")
    assert g.execute("SELECT id, name FROM projects").fetchall() == [("alpha", "Alpha")]
    assert g.execute("SELECT project_id, principal_id, role FROM project_members").fetchall() == [
        ("alpha", ADMIN, "owner")
    ]
    p = sqlite3.connect(data_dir / "projects" / "alpha" / "project.db")
    assert p.execute("SELECT value FROM project_meta WHERE key='project_id'").fetchone() == ("alpha",)
    assert p.execute("SELECT value_json FROM config WHERE key='context.max_tokens'").fetchone() == ("4000",)
    g.close()
    p.close()


def test_us1801_ca02_ca03_reinicio_reconstruye_desde_sqlite(data_dir: Path) -> None:
    svc = ProjectService(data_dir)
    svc.ensure_principal(ADMIN, "admin")
    svc.create(ADMIN, "alpha", "Alpha", "desc")
    svc.set_config(ADMIN, "alpha", {"decision.engine_order": ["jev", "rules"]})
    before = svc.open(ADMIN, "alpha")
    svc.close()
    # Un proceso nuevo (reinicio) reconstruye el estado solo desde SQLite.
    code = (
        "import json,sys; from acm.domain.projects import ProjectService;"
        f"s=ProjectService({str(data_dir)!r}); print(json.dumps(s.open({ADMIN!r}, 'alpha'))); s.close()"
    )
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True).stdout
    assert json.loads(out) == before


def test_us1801_ca04_escritura_fallida_no_deja_inconsistencias(tmp_path: Path) -> None:
    db = _db_with_table(tmp_path / "x.db")
    with pytest.raises(sqlite3.IntegrityError):
        with db.write() as conn:
            conn.execute("INSERT INTO t(id, v) VALUES (1, 'a')")
            conn.execute("INSERT INTO child(t_id) VALUES (999)")  # viola la clave foránea
    with db.read() as conn:
        assert conn.execute("SELECT COUNT(*) FROM t").fetchone()[0] == 0
        assert conn.execute("SELECT COUNT(*) FROM child").fetchone()[0] == 0
    db.close()


def test_us1801_transaccion_no_confirmada_desaparece_si_el_proceso_muere(tmp_path: Path) -> None:
    path = tmp_path / "x.db"
    _db_with_table(path).close()
    code = (
        "import sys; from acm.db.connection import Database;"
        f"db=Database({str(path)!r}); cm=db.write(); conn=cm.__enter__();"
        "conn.execute(\"INSERT INTO t(v) VALUES ('perdida')\"); print('ready', flush=True); sys.stdin.read()"
    )
    child = subprocess.Popen([sys.executable, "-c", code], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    assert child.stdout.readline().strip() == "ready"
    child.send_signal(signal.SIGKILL)
    child.wait(timeout=10)
    db = Database(path)
    with db.read() as conn:
        assert conn.execute("SELECT COUNT(*) FROM t").fetchone()[0] == 0
    db.close()


# ---------------------------------------------------------------- US-18.02
def test_us1802_ca01_operacion_valida_se_confirma(tmp_path: Path) -> None:
    db = _db_with_table(tmp_path / "x.db")
    with db.write() as conn:
        conn.execute("INSERT INTO t(id, v) VALUES (1, 'a')")
        conn.execute("INSERT INTO child(t_id) VALUES (1)")
    other = sqlite3.connect(tmp_path / "x.db")
    assert other.execute("SELECT COUNT(*) FROM child").fetchone()[0] == 1
    other.close()
    db.close()


@pytest.mark.parametrize("exc", [ValueError("fallo"), KeyboardInterrupt()])
def test_us1802_ca02_ca03_fallo_revierte_todo(tmp_path: Path, exc: BaseException) -> None:
    db = _db_with_table(tmp_path / "x.db")
    with pytest.raises(type(exc)):
        with db.write() as conn:
            conn.execute("INSERT INTO t(id, v) VALUES (1, 'a')")
            conn.execute("INSERT INTO t(id, v) VALUES (2, 'b')")
            conn.execute("UPDATE counter SET n = 99")
            raise exc
    with db.read() as conn:
        assert conn.execute("SELECT COUNT(*) FROM t").fetchone()[0] == 0
        assert conn.execute("SELECT n FROM counter").fetchone()[0] == 0
        assert not conn.in_transaction
    db.close()


def test_us1802_anidamiento_detectado(tmp_path: Path) -> None:
    db = _db_with_table(tmp_path / "x.db")
    with pytest.raises(NestedTransactionError):
        with db.write():
            with db.write():
                pass
    with db.read() as conn:
        assert not conn.in_transaction
    db.close()


def _increment(args: tuple[str, int]) -> None:
    path, n = args
    db = Database(path)
    for _ in range(n):
        with db.write() as conn:
            value = conn.execute("SELECT n FROM counter").fetchone()[0]  # lectura seguida de escritura
            conn.execute("UPDATE counter SET n = ?", (value + 1,))
    db.close()


def test_us1802_escritores_concurrentes_sin_perdidas(tmp_path: Path) -> None:
    path = tmp_path / "x.db"
    _db_with_table(path).close()
    with mp.get_context("spawn").Pool(4) as pool:
        pool.map(_increment, [(str(path), 100)] * 4)
    db = Database(path)
    with db.read() as conn:
        assert conn.execute("SELECT n FROM counter").fetchone()[0] == 400
    db.close()


def _hold_lock(path: Path, seconds: float, ready: threading.Event) -> None:
    conn = sqlite3.connect(path, isolation_level=None)
    conn.execute("BEGIN IMMEDIATE")
    ready.set()
    time.sleep(seconds)
    conn.execute("COMMIT")
    conn.close()


def test_us1802_reintento_ante_bloqueo_transitorio(tmp_path: Path) -> None:
    path = tmp_path / "x.db"
    _db_with_table(path).close()
    db = Database(path, busy_timeout_ms=10)
    ready = threading.Event()
    holder = threading.Thread(target=_hold_lock, args=(path, 0.15, ready))
    holder.start()
    ready.wait(5)
    with db.write() as conn:  # agota el busy_timeout y lo logra con los reintentos (50/100/200 ms)
        conn.execute("INSERT INTO t(v) VALUES ('tras reintento')")
    holder.join()
    ready2 = threading.Event()
    holder2 = threading.Thread(target=_hold_lock, args=(path, 1.0, ready2))
    holder2.start()
    ready2.wait(5)
    with pytest.raises(StorageError, match="ocupada"):
        with db.write():
            pass
    holder2.join()
    db.close()
