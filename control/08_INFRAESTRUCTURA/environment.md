# Entornos

## Desarrollo (contenedor del agente, 2026-09-30)
| Elemento | Valor |
|----------|-------|
| SO | Linux 6.18 x86_64 (glibc 2.39), 4 CPU, ext4 |
| Python | 3.11.15 |
| SQLite | 3.45.1 |
| Gestor de entornos | `uv` (`/root/.local/bin/uv`) |
| Entorno de spikes | `spikes/.venv` (ignorado por Git; ver `spikes/README.md`) |
| Ollama / modelos | **No disponibles**: `registry.ollama.ai`, `ollama.com` y `huggingface.co` devuelven 403 en el proxy (IMP-004) |

Producción / despliegue: MISSING (sin definir; EPIC-18/CI-CD).

## Ejecución local del producto (2026-09-30)
| Variable | Por defecto | Uso |
|----------|-------------|-----|
| `ACM_DATA_DIR` | `./.acm-data` | Directorio de las bases SQLite |
| `ACM_PRINCIPAL` | `local-admin` | Admin local: identidad en stdio y en el CLI; se da de alta como admin. En HTTP la identidad sale del token (ADR-017) |
| `ACM_HOST` / `ACM_PORT` | `127.0.0.1` / `8765` | Escucha de `acm serve` |
| `ACM_SQLITE_SYNCHRONOUS` | `FULL` | Durabilidad de la base global (ADR-013) |
| `ACM_OLLAMA_URL` / `ACM_OLLAMA_MODEL` | sin valor | Motor de generación Ollama (EPIC-22). Deben ir juntos; sin ellos, solo reglas |
| `ACM_EVENTS_KEEP` | `10000` | Eventos conservados para reanudar clientes WebSocket (ADR-018) |
| `ACM_WATCHDOG_INTERVAL_S` | `600` | Intervalo de la auditoría periódica de todos los proyectos en `acm serve` (US-13.06); `0` la desactiva |
| `ACM_ALLOWED_HOSTS` | sin valor | Nombres extra aceptados en la cabecera Host (p. ej. `acm.midominio.com` tras un proxy TLS). Sin él, otro Host → 421 (TD-002) |

Comandos: `acm serve`, `acm mcp-stdio` (ver `/README.md`).
