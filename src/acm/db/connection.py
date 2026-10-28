"""Conexiones y transacciones SQLite según ADR-013 (evidencia: SPIKE-001).

Invariantes:
- `journal_mode=WAL`, `foreign_keys=ON` y `busy_timeout` se aplican al abrir cada conexión, fuera de
  transacción (E5 de SPIKE-001: el PRAGMA de claves foráneas es un no-op dentro de una transacción).
- Toda escritura pasa por `Database.write()`, que usa `BEGIN IMMEDIATE` (E3: con DEFERRED, subir de
  lectura a escritura falla al instante y el busy_timeout no ayuda).
- Una conexión por hilo (threading.local); las llamadas desde asyncio van en hilos
  de trabajo (`anyio.to_thread`).
"""

from __future__ import annotations

import sqlite3
import threading
import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from acm.domain.errors import StorageError

SYNCHRONOUS_MODES = ("FULL", "NORMAL")
_SYNC_NAMES = {0: "OFF", 1: "NORMAL", 2: "FULL", 3: "EXTRA"}
RETRY_DELAYS_S = (0.05, 0.1, 0.2)  # US-18.02: reintentos ante bloqueo transitorio al iniciar la escritura


class NestedTransactionError(RuntimeError):
    """Se intentó abrir `write()` dentro de otra transacción en la misma conexión (error de programación)."""


def _is_lock_error(exc: sqlite3.OperationalError) -> bool:
    text = str(exc).lower()
    return "locked" in text or "busy" in text


class Database:
    def __init__(self, path: Path | str, *, synchronous: str = "FULL", busy_timeout_ms: int = 5000):
        self.path = Path(path)
        self._busy_timeout_ms = busy_timeout_ms
        self._local = threading.local()
        self._lock = threading.Lock()
        self._connections: list[sqlite3.Connection] = []
        self._closed = False
        self.set_synchronous(synchronous)

    # ------------------------------------------------------------------ conexión
    def set_synchronous(self, mode: str) -> None:
        """Afecta a las conexiones que se abran a partir de ahora (parámetro con recarga, US-01.03)."""
        if mode not in SYNCHRONOUS_MODES:
            raise ValueError(f"synchronous debe ser uno de {SYNCHRONOUS_MODES}")
        self.synchronous = mode

    def connection(self) -> sqlite3.Connection:
        if self._closed:
            raise StorageError(f"base cerrada: {self.path}")
        conn: sqlite3.Connection | None = getattr(self._local, "conn", None)
        if conn is None:
            conn = self._open()
            self._local.conn = conn
            with self._lock:
                self._connections.append(conn)
        return conn

    def _open(self) -> sqlite3.Connection:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            # check_same_thread=False solo para poder cerrar todas las conexiones desde close(): cada conexión
            # la usa exclusivamente el hilo que la creó (threading.local).
            conn = sqlite3.connect(
                self.path, timeout=self._busy_timeout_ms / 1000, isolation_level=None, check_same_thread=False
            )
            conn.row_factory = sqlite3.Row
            mode = self._enable_wal(conn)
            conn.execute(f"PRAGMA synchronous={self.synchronous}")
            conn.execute("PRAGMA foreign_keys=ON")
            conn.execute(f"PRAGMA busy_timeout={int(self._busy_timeout_ms)}")
        except sqlite3.Error as exc:
            raise StorageError(f"no se pudo abrir la base {self.path}: {exc}") from exc
        if str(mode).lower() != "wal" or conn.execute("PRAGMA foreign_keys").fetchone()[0] != 1:
            conn.close()
            raise StorageError(f"la base {self.path} no aceptó WAL/foreign_keys (ADR-013)")
        return conn

    def _enable_wal(self, conn: sqlite3.Connection) -> str:
        """Activa WAL reintentando mientras la base esté bloqueada (BUG-001).

        Pasar una base nueva a WAL exige un lock exclusivo y SQLite puede devolver SQLITE_BUSY sin invocar el
        busy handler cuando varios procesos la abren a la vez; se reintenta hasta agotar `busy_timeout`.
        """
        deadline = time.monotonic() + self._busy_timeout_ms / 1000
        delay = 0.005
        while True:
            try:
                return conn.execute("PRAGMA journal_mode=WAL").fetchone()[0]
            except sqlite3.OperationalError as exc:
                if ("locked" not in str(exc) and "busy" not in str(exc)) or time.monotonic() >= deadline:
                    raise
                time.sleep(delay)
                delay = min(delay * 2, 0.1)

    def pragmas(self) -> dict[str, object]:
        conn = self.connection()
        return {
            "journal_mode": conn.execute("PRAGMA journal_mode").fetchone()[0],
            "synchronous": _SYNC_NAMES[conn.execute("PRAGMA synchronous").fetchone()[0]],
            "foreign_keys": conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1,
            "busy_timeout_ms": conn.execute("PRAGMA busy_timeout").fetchone()[0],
        }

    # ------------------------------------------------------------ transacciones
    @contextmanager
    def write(self) -> Iterator[sqlite3.Connection]:
        """Transacción de escritura: BEGIN IMMEDIATE → COMMIT, o ROLLBACK ante cualquier excepción."""
        conn = self.connection()
        if conn.in_transaction:
            raise NestedTransactionError("write() anidado en una transacción abierta")
        self._begin_immediate(conn)
        try:
            yield conn
        except BaseException:
            if conn.in_transaction:
                conn.execute("ROLLBACK")
            raise
        else:
            try:
                conn.execute("COMMIT")
            except sqlite3.Error as exc:
                if conn.in_transaction:
                    conn.execute("ROLLBACK")
                raise StorageError(f"fallo al confirmar la transacción: {exc}") from exc

    def _begin_immediate(self, conn: sqlite3.Connection) -> None:
        for attempt in range(len(RETRY_DELAYS_S) + 1):
            try:
                conn.execute("BEGIN IMMEDIATE")
                return
            except sqlite3.OperationalError as exc:
                if not _is_lock_error(exc) or attempt == len(RETRY_DELAYS_S):
                    raise StorageError(f"base de datos ocupada tras {attempt + 1} intentos: {exc}") from exc
                time.sleep(RETRY_DELAYS_S[attempt])

    @contextmanager
    def read(self) -> Iterator[sqlite3.Connection]:
        """Lecturas en autocommit: en WAL no bloquean ni son bloqueadas por un escritor (SPIKE-001 E2)."""
        conn = self.connection()
        yield conn

    def close(self) -> None:
        with self._lock:
            self._closed = True
            for conn in self._connections:
                try:
                    conn.close()
                except sqlite3.Error:
                    pass
            self._connections.clear()
        self._local = threading.local()
