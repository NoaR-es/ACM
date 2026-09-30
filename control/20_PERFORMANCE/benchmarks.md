# Benchmarks

## SPIKE-001 — Concurrencia de SQLite desde Python (2026-09-30)

- **Script:** `spikes/spike_001_sqlite/bench.py`. **Datos brutos:** `spikes/spike_001_sqlite/results.json`.
- **Entorno:** Python 3.11.15, SQLite 3.45.1, 4 CPU, Linux-6.18.44-fc-v50-x86_64-with-glibc2.39, ext4 del contenedor de desarrollo.
- **Aviso:** los números absolutos dependen del disco y no representan el hardware de despliegue. Lo que se toma como resultado son las **comparaciones** y los **comportamientos** (bloqueos, errores, consistencia).
- **Método:** procesos reales (`multiprocessing`), transacciones cortas (1 INSERT + 1 UPDATE), `busy_timeout=5000` y `isolation_level=None` con transacciones explícitas.

### E1 — Escritores concurrentes (1000 transacciones por proceso)
| journal | synchronous | procesos | confirmadas | errores BUSY | consistente | tx/s |
|---------|-------------|----------|-------------|--------------|-------------|------|
| DELETE | FULL | 1 | 1000 | 0 | sí | 1.125 |
| DELETE | FULL | 4 | 4000 | 0 | sí | 1.058 |
| DELETE | FULL | 8 | 7999 | 1 | sí | 1.070 |
| DELETE | NORMAL | 1 | 1000 | 0 | sí | 1.173 |
| DELETE | NORMAL | 4 | 4000 | 0 | sí | 1.049 |
| DELETE | NORMAL | 8 | 7998 | 2 | sí | 1.116 |
| WAL | FULL | 1 | 1000 | 0 | sí | 4.607 |
| WAL | FULL | 4 | 4000 | 0 | sí | 4.530 |
| WAL | FULL | 8 | 8000 | 0 | sí | 5.028 |
| WAL | NORMAL | 1 | 1000 | 0 | sí | 21.188 |
| WAL | NORMAL | 4 | 4000 | 0 | sí | 25.358 |
| WAL | NORMAL | 8 | 8000 | 0 | sí | 21.364 |

### E2 — Lectores mientras un escritor mantiene una transacción grande (caché de 10 páginas, 1,5 s)
| journal | lecturas | OK | bloqueadas | latencia máx. (ms) |
|---------|----------|----|------------|--------------------|
| DELETE | 4×50 | 172 | 28 | 204.04 |
| WAL | 4×50 | 200 | 0 | 0.9 |

### E3 — Leer y después escribir en la misma transacción (8 procesos, WAL)
| BEGIN | procesos | confirmadas | errores | actualizaciones perdidas | latencia máx. (s) |
|-------|----------|-------------|---------|--------------------------|-------------------|
| DEFERRED | 8 | 1 | 7 (error: database is locked) | 0 | 0.052 |
| IMMEDIATE | 8 | 8 | 0 (—) | 0 | 0.581 |

### E4 — Reclamación optimista de una tarea (`UPDATE … WHERE status='READY' AND version=0`)
8 procesos × 50 rondas → rondas con exactamente un ganador: **50/50** (violaciones: 0).

### E5 — Claves foráneas
| Caso | Resultado |
|------|-----------|
| `PRAGMA foreign_keys` por defecto | 0 (desactivadas); inserción huérfana **accepted** |
| `PRAGMA foreign_keys=ON` con una transacción abierta (modo implícito de `sqlite3`) | valor 0: **no-op**; inserción huérfana **accepted** |
| `PRAGMA foreign_keys=ON` al abrir la conexión | inserción huérfana **rejected** |

### Conclusiones (→ ADR-013)
1. WAL es imprescindible: en DELETE los lectores se bloquean (E2), el rendimiento es entre 4 y 20 veces menor (E1) y aparecen errores BUSY aun con `busy_timeout`.
2. **Toda transacción de escritura debe usar `BEGIN IMMEDIATE`.** Con DEFERRED, subir de lectura a escritura falla al instante con "database is locked" y el `busy_timeout` no ayuda (E3).
3. La reclamación con `UPDATE` condicional garantiza un único ganador (E4): sirve para US-19.03 y para reclamar tareas.
4. Las claves foráneas deben activarse al abrir cada conexión y fuera de transacción; si no, la integridad referencial no existe (E5).
5. `synchronous=FULL` en WAL da unas 4.500–5.000 tx/s en este entorno, sobrado para ACM. `NORMAL` multiplica el rendimiento por unas 5 a cambio de poder perder las últimas transacciones confirmadas si se corta la corriente.

### Incidencias del propio experimento (corregidas antes de dar resultados)
- La primera versión de E2 no distinguía modos: un escritor en `BEGIN IMMEDIATE` sin volcado a disco solo toma el lock RESERVED. Se corrigió forzando el volcado.
- Los lectores de E2 fallaban al ejecutar `PRAGMA journal_mode` (también requiere lock). Se corrigió dejando que solo lean.
- La primera versión de E5 ejecutaba el PRAGMA dentro de una transacción implícita. El resultado erróneo reveló la trampa que ahora documenta E5.
