# Entornos

## Desarrollo (contenedor del agente, 2026-09-30)
| Elemento | Valor |
|----------|-------|
| SO | Linux 6.18 x86_64 (glibc 2.39), 4 CPU, ext4 |
| Python | 3.11.15 |
| SQLite | 3.45.1 |
| Gestor de entornos | `uv` (`/root/.local/bin/uv`) |
| Entorno de spikes | `spikes/.venv` (ignorado por Git; ver `spikes/README.md`) |
| Node / npm | 22.22.2 / 10.9.7 (solo para cambiar la interfaz, `web/`; CI: Node 22) |
| Navegador e2e | Chromium en `/opt/pw-browsers` (Playwright 1.63.0) |
| Ollama / modelos | **No disponibles**: `registry.ollama.ai`, `ollama.com` y `huggingface.co` devuelven 403 en el proxy (IMP-004) |

Producción / despliegue: MISSING (sin definir; EPIC-18/CI-CD).

## Ejecución local del producto (2026-09-30)
| Variable | Por defecto | Uso |
|----------|-------------|-----|
| `ACM_DATA_DIR` | `./.acm-data` | Directorio de las bases SQLite |
| `ACM_PRINCIPAL` | `local-admin` | Admin local: identidad en stdio y en el CLI; se da de alta como admin. En HTTP la identidad sale del token (ADR-017) |
| `ACM_HOST` / `ACM_PORT` | `127.0.0.1` / `8765` | Escucha de `acm serve` |
| `ACM_SQLITE_SYNCHRONOUS` | `FULL` | Durabilidad de la base global (ADR-013) |
| `ACM_OLLAMA_URL` | sin valor | Servidor Ollama (EPIC-22). Sin URL no se registra ningún motor Ollama |
| `ACM_OLLAMA_MODEL` | sin valor | Modelo de Ollama por defecto. Opcional desde SPRINT-008: el elegido en Sistema → Modelos (`inference_settings`) tiene prioridad (ADR-021) |
| `ACM_JEV_URL` | sin valor | Servidor Ollaya con modelos de decisión JEV (EPIC-50, puerto habitual 11435). Sin URL no se registra |
| `ACM_JEV_MODEL` | sin valor | Modelo JEV por defecto (p. ej. `winnow:e4b` o `laya`); los elegidos por propósito en la interfaz tienen prioridad |
| `ACM_JEV_API_KEY` | sin valor | Clave Bearer si Ollaya usa `OLLAYA_API_KEY`. **Solo por entorno**: nunca se guarda en la base ni se muestra (ADR-021) |
| `ACM_EVENTS_KEEP` | `10000` | Eventos conservados para reanudar clientes WebSocket (ADR-018) |
| `ACM_WATCHDOG_INTERVAL_S` | `600` | Intervalo de la auditoría periódica de todos los proyectos en `acm serve` (US-13.06); `0` la desactiva |
| `ACM_ALLOWED_HOSTS` | sin valor | Nombres extra aceptados en la cabecera Host (p. ej. `acm.midominio.com` tras un proxy TLS). Sin él, otro Host → 421 (TD-002) |

Comandos: `acm serve`, `acm mcp-stdio` (ver `/README.md`). Interfaz web en `/` del mismo puerto (ADR-019).

Tests: `ACM_E2E_REQUIRED=1` convierte en fallo la ausencia de navegador para los e2e (CI).
