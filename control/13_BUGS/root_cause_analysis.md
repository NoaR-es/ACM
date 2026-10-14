# Root cause analysis

## BUG-001 — `database is locked` al abrir una base nueva en paralelo (2026-09-30)

- **Síntoma:** `Database._open` lanza `StorageError(... database is locked)` aunque la conexión tiene `timeout` = `busy_timeout` (5 s).
- **Causa raíz:** el primer `PRAGMA journal_mode=WAL` sobre una base sin WAL necesita un lock exclusivo. En la carrera entre procesos que la abren a la vez, SQLite devuelve SQLITE_BUSY en ese paso **sin invocar el busy handler**, así que el `timeout` de la conexión no se aplica. ADR-013 ya preveía reintentos para `BEGIN IMMEDIATE`, pero no para la activación de WAL.
- **Por qué no lo detectamos antes:** el test de migración concurrente usa 4 procesos y la carrera es poco probable (pasó 40/40 en local y en CI run #1). Además, tras el push de `445f09c` no se comprobó la CI, a pesar de que la retrospectiva de SPRINT-001 lo pedía. El fallo se vio al comprobar la CI de SPRINT-002.
- **Corrección:** reintento acotado de la activación de WAL (`_enable_wal`). Test de regresión con 12 procesos sincronizados por barrera y 10 rondas.
- **Prevención:** comprobar la CI después de **cada** push, no solo del commit principal del sprint.

## BUG-002 — Recargar una vista de administrador volvía al panel (2026-10-06)
- **Síntoma:** al recargar `#/system`, un administrador acababa en `#/`.
- **Causa raíz:** `adminOnly` decidía con `isAdmin` mientras `/me` aún no había respondido. En el primer render `isAdmin` era `false` y `<Navigate to="/">` se ejecutaba antes de conocer la identidad. Navegando desde el panel no ocurría, porque `/me` ya estaba en caché.
- **Por qué no lo detectamos antes:** los e2e de SPRINT-007 siempre llegaban a `/system` por navegación, nunca por recarga.
- **Corrección:** `adminOnly` muestra «Cargando identidad» hasta tener `me` y solo después decide.
- **Prevención:** los e2e de vistas con permisos incluyen una recarga directa de la ruta.
