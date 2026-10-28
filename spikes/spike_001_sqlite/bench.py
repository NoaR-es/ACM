#!/usr/bin/env python3
"""SPIKE-001 — Concurrencia de SQLite desde Python (stdlib sqlite3).

Mide con procesos reales (multiprocessing) las preguntas del spike:

  E1  Escritores concurrentes: modo de journal (DELETE vs WAL) × synchronous (FULL vs NORMAL).
      Throughput de transacciones cortas y errores SQLITE_BUSY con busy_timeout.
  E2  Lectores concurrentes con un escritor activo (WAL vs DELETE): ¿se bloquean los lectores?
  E3  Transacción DEFERRED que lee y luego escribe frente a BEGIN IMMEDIATE:
      ¿aparece SQLITE_BUSY sin que el busy_timeout ayude?
  E4  Reclamación optimista de tareas (US-07.03 / US-19.03): N procesos compiten por la misma
      tarea con UPDATE condicional; debe ganar exactamente uno.
  E5  Claves foráneas: ¿vienen activadas por defecto en sqlite3?

Uso:  python3 bench.py [--quick] [--out results.json]
El resultado se imprime como JSON y se guarda en --out (por defecto results.json junto al script).
"""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import os
import platform
import sqlite3
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent


def connect(path: str, journal: str, sync: str, busy_ms: int = 5000) -> sqlite3.Connection:
    # isolation_level=None: control explícito de transacciones (BEGIN/COMMIT) sin el modo implícito del módulo.
    conn = sqlite3.connect(path, timeout=busy_ms / 1000, isolation_level=None)
    conn.execute(f"PRAGMA journal_mode={journal}")
    conn.execute(f"PRAGMA synchronous={sync}")
    conn.execute(f"PRAGMA busy_timeout={busy_ms}")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db(path: str, journal: str) -> None:
    conn = connect(path, journal, "NORMAL")
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY, worker INTEGER, payload TEXT, ts REAL);
        CREATE TABLE IF NOT EXISTS counter(id INTEGER PRIMARY KEY CHECK (id = 1), n INTEGER NOT NULL);
        INSERT OR IGNORE INTO counter(id, n) VALUES (1, 0);
        CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY, status TEXT NOT NULL, owner INTEGER, version INTEGER NOT NULL DEFAULT 0);
    """)
    conn.close()


# ---------------------------------------------------------------- E1
def _writer(args):
    path, journal, sync, worker, n_tx, start_at = args
    conn = connect(path, journal, sync)
    while time.time() < start_at:
        time.sleep(0.001)
    ok = busy = 0
    t0 = time.perf_counter()
    for i in range(n_tx):
        try:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute("INSERT INTO events(worker, payload, ts) VALUES (?, ?, ?)", (worker, "x" * 200, time.time()))
            conn.execute("UPDATE counter SET n = n + 1 WHERE id = 1")
            conn.execute("COMMIT")
            ok += 1
        except sqlite3.OperationalError as e:
            if "locked" in str(e) or "busy" in str(e):
                busy += 1
                if conn.in_transaction:
                    conn.execute("ROLLBACK")
            else:
                raise
    elapsed = time.perf_counter() - t0
    conn.close()
    return ok, busy, elapsed


def e1_writers(tmp: str, journal: str, sync: str, workers: int, n_tx: int) -> dict:
    path = os.path.join(tmp, f"e1_{journal}_{sync}_{workers}.db")
    init_db(path, journal)
    start_at = time.time() + 0.5
    with mp.Pool(workers) as pool:
        t0 = time.perf_counter()
        res = pool.map(_writer, [(path, journal, sync, w, n_tx, start_at) for w in range(workers)])
        wall = time.perf_counter() - t0 - 0.5
    conn = sqlite3.connect(path)
    counter = conn.execute("SELECT n FROM counter").fetchone()[0]
    rows = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    conn.close()
    ok = sum(r[0] for r in res)
    busy = sum(r[1] for r in res)
    return {"journal": journal, "synchronous": sync, "workers": workers, "tx_per_worker": n_tx,
            "committed": ok, "busy_errors": busy, "consistent": counter == rows == ok,
            "wall_s": round(wall, 3), "tx_per_s": round(ok / wall, 1) if wall > 0 else None}


# ---------------------------------------------------------------- E2
def _long_writer(args):
    path, journal, hold_s, ready = args
    conn = connect(path, journal, "NORMAL")
    # Caché mínima: la transacción grande obliga a volcar páginas a disco antes del COMMIT. En modo
    # DELETE eso exige el lock EXCLUSIVE (bloquea lectores); en WAL las páginas van al -wal y los
    # lectores siguen leyendo la última instantánea confirmada.
    conn.execute("PRAGMA cache_size=10")
    conn.execute("BEGIN IMMEDIATE")
    conn.executemany("INSERT INTO events(worker, payload, ts) VALUES (-1, ?, 0)", [("y" * 500,)] * 20000)
    ready.set()
    time.sleep(hold_s)  # mantiene la transacción abierta tras el volcado
    conn.execute("COMMIT")
    conn.close()


def _reader(args):
    path, journal, n = args
    # El lector solo lee: no cambia el modo de journal (eso también requiere lock).
    conn = sqlite3.connect(path, timeout=0.2, isolation_level=None)
    ok = blocked = 0
    lat = []
    for _ in range(n):
        t0 = time.perf_counter()
        try:
            conn.execute("SELECT COUNT(*) FROM events").fetchone()
            ok += 1
        except sqlite3.OperationalError:
            blocked += 1
        lat.append(time.perf_counter() - t0)
    conn.close()
    return ok, blocked, max(lat)


def e2_readers(tmp: str, journal: str, readers: int, n: int) -> dict:
    path = os.path.join(tmp, f"e2_{journal}.db")
    init_db(path, journal)
    c = connect(path, journal, "NORMAL")
    c.executemany("INSERT INTO events(worker, payload, ts) VALUES (0, 'seed', 0)", [()] * 1000)
    c.close()
    mgr = mp.Manager()
    ready = mgr.Event()
    w = mp.Process(target=_long_writer, args=((path, journal, 1.5, ready),))
    w.start()
    ready.wait(5)
    with mp.Pool(readers) as pool:
        res = pool.map(_reader, [(path, journal, n)] * readers)
    w.join()
    return {"journal": journal, "readers": readers, "reads_each": n,
            "reads_ok": sum(r[0] for r in res), "reads_blocked": sum(r[1] for r in res),
            "max_read_latency_ms": round(max(r[2] for r in res) * 1000, 2),
            "writer_held_lock_s": 1.5}


# ---------------------------------------------------------------- E3
def _upgrader(args):
    path, mode, start_at = args
    conn = connect(path, "WAL", "NORMAL", busy_ms=5000)
    while time.time() < start_at:
        time.sleep(0.001)
    t0 = time.perf_counter()
    try:
        conn.execute("BEGIN IMMEDIATE" if mode == "immediate" else "BEGIN DEFERRED")
        n = conn.execute("SELECT n FROM counter WHERE id = 1").fetchone()[0]  # lectura
        time.sleep(0.05)  # ventana para que otro proceso también lea
        conn.execute("UPDATE counter SET n = ? WHERE id = 1", (n + 1,))  # escritura: upgrade del lock
        conn.execute("COMMIT")
        return "ok", round(time.perf_counter() - t0, 3)
    except sqlite3.OperationalError as e:
        if conn.in_transaction:
            conn.execute("ROLLBACK")
        return f"error: {e}", round(time.perf_counter() - t0, 3)
    finally:
        conn.close()


def e3_upgrade(tmp: str, mode: str, workers: int) -> dict:
    path = os.path.join(tmp, f"e3_{mode}.db")
    init_db(path, "WAL")
    start_at = time.time() + 0.5
    with mp.Pool(workers) as pool:
        res = pool.map(_upgrader, [(path, mode, start_at)] * workers)
    conn = sqlite3.connect(path)
    final = conn.execute("SELECT n FROM counter").fetchone()[0]
    conn.close()
    oks = [r for r in res if r[0] == "ok"]
    errs = sorted({r[0] for r in res if r[0] != "ok"})
    return {"begin": mode, "workers": workers, "committed": len(oks), "errors": len(res) - len(oks),
            "error_kinds": errs, "final_counter": final, "lost_updates": len(oks) - final,
            "max_latency_s": max(r[1] for r in res),
            "fastest_error_s": min((r[1] for r in res if r[0] != "ok"), default=None)}


# ---------------------------------------------------------------- E4
def _claimer(args):
    path, worker, start_at = args
    conn = connect(path, "WAL", "NORMAL")
    while time.time() < start_at:
        time.sleep(0.0005)
    cur = conn.execute(
        "UPDATE tasks SET status='IN_PROGRESS', owner=?, version=version+1 WHERE id=1 AND status='READY' AND version=0",
        (worker,))
    won = cur.rowcount == 1
    conn.close()
    return won


def e4_claim(tmp: str, workers: int, rounds: int) -> dict:
    path = os.path.join(tmp, "e4.db")
    init_db(path, "WAL")
    violations = 0
    for _ in range(rounds):
        c = connect(path, "WAL", "NORMAL")
        c.execute("DELETE FROM tasks")
        c.execute("INSERT INTO tasks(id, status, version) VALUES (1, 'READY', 0)")
        c.close()
        start_at = time.time() + 0.2
        with mp.Pool(workers) as pool:
            winners = sum(pool.map(_claimer, [(path, w, start_at) for w in range(workers)]))
        if winners != 1:
            violations += 1
    return {"workers": workers, "rounds": rounds, "rounds_with_exactly_one_winner": rounds - violations,
            "violations": violations}


# ---------------------------------------------------------------- E5
def _orphan_insert(conn: sqlite3.Connection) -> str:
    try:
        conn.execute("INSERT INTO c(p) VALUES (99)")
        return "accepted"
    except sqlite3.IntegrityError:
        return "rejected"


def e5_foreign_keys() -> dict:
    ddl = "CREATE TABLE p(id INTEGER PRIMARY KEY); CREATE TABLE c(id INTEGER PRIMARY KEY, p INTEGER REFERENCES p(id));"
    # a) Valor por defecto.
    a = sqlite3.connect(":memory:", isolation_level=None)
    a.executescript(ddl)
    default = a.execute("PRAGMA foreign_keys").fetchone()[0]
    r_default = _orphan_insert(a)
    # b) PRAGMA ejecutado dentro de una transacción abierta (el modo implícito de sqlite3 abre una al hacer INSERT).
    b = sqlite3.connect(":memory:")  # isolation_level por defecto ("" = transacciones implícitas)
    b.executescript(ddl)
    b.execute("INSERT INTO p(id) VALUES (1)")  # abre transacción implícita
    b.execute("PRAGMA foreign_keys=ON")        # no-op dentro de una transacción
    in_tx_value = b.execute("PRAGMA foreign_keys").fetchone()[0]
    r_in_tx = _orphan_insert(b)
    # c) PRAGMA al abrir la conexión, fuera de transacción.
    c = sqlite3.connect(":memory:", isolation_level=None)
    c.execute("PRAGMA foreign_keys=ON")
    c.executescript(ddl)
    r_on = _orphan_insert(c)
    return {"foreign_keys_default": default, "orphan_insert_default": r_default,
            "pragma_inside_open_tx_value": in_tx_value, "orphan_insert_pragma_inside_tx": r_in_tx,
            "orphan_insert_pragma_at_connect": r_on}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--out", default=str(HERE / "results.json"))
    a = ap.parse_args()
    n_tx = 200 if a.quick else 1000
    results = {"env": {"python": platform.python_version(), "sqlite": sqlite3.sqlite_version,
                       "cpus": os.cpu_count(), "platform": platform.platform()},
               "e1_writers": [], "e2_readers": [], "e3_upgrade": [], "e4_claim": None, "e5_foreign_keys": None}
    with tempfile.TemporaryDirectory() as tmp:
        for journal in ("DELETE", "WAL"):
            for sync in ("FULL", "NORMAL"):
                for workers in (1, 4, 8):
                    results["e1_writers"].append(e1_writers(tmp, journal, sync, workers, n_tx))
        for journal in ("DELETE", "WAL"):
            results["e2_readers"].append(e2_readers(tmp, journal, 4, 50))
        for mode in ("deferred", "immediate"):
            results["e3_upgrade"].append(e3_upgrade(tmp, mode, 8))
        results["e4_claim"] = e4_claim(tmp, 8, 20 if a.quick else 50)
    results["e5_foreign_keys"] = e5_foreign_keys()
    Path(a.out).write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
