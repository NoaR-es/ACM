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
| `ACM_PRINCIPAL` | `local-admin` | Identidad del llamante hasta EPIC-20 (se da de alta como admin) |
| `ACM_HOST` / `ACM_PORT` | `127.0.0.1` / `8765` | Escucha de `acm serve` |
| `ACM_SQLITE_SYNCHRONOUS` | `FULL` | Durabilidad de la base global (ADR-013) |
| `ACM_OLLAMA_URL` / `ACM_OLLAMA_MODEL` | sin valor | Motor de generación Ollama (EPIC-22). Deben ir juntos; sin ellos, solo reglas |

Comandos: `acm serve`, `acm mcp-stdio` (ver `/README.md`).
