# Código de tests

Actualizado: 2026-09-30 (SPRINT-007). Estrategia y resultados: `12_TESTING/`. Recuentos: `file_inventory.md`.

## Convenciones
- **Nombre:** `test_usNNNN_caNN_<qué>` — historia y criterio que prueba. Los refinamientos citan cada test y `derive_backlog --check` falla si el test no existe.
- **Un test por CA** (o varios); los que no cubren un CA concreto nombran la regla (`test_us0602_done_solo_tras_verificar`).
- **Datos reales:**
  - SQLite en un `tmp_path` por test;
  - ACM real por HTTP (`tests/live.py`);
  - un agente stdio real cuando el caso lo exige;
  - Chromium real para la interfaz.
- **Sin mocks del dominio.** Los dobles solo sustituyen sistemas externos: Ollama (`fake_ollama.py`), JEV (`FakeJev`) y el motor de generación (`SpyGen`).

## Fixtures y ayudas
| Nombre | Dónde | Qué da |
|--------|-------|--------|
| `data_dir`, `service` | `conftest.py` | directorio temporal y `ProjectService` con `local-admin` |
| `add_member(data_dir, project, principal, role)` | `conftest.py` | pertenencia escrita directamente en SQLite |
| `acm` | `live.py` (plugin registrado en `conftest.py`) | ACM real por HTTP en un hilo + `service`, `identity`, `token()`, `audit()` |
| `mcp(acm, token)` | `live.py` | cliente MCP por HTTP con token |
| `browser`, `ui`, `login`, `in_thread` | `test_webui.py` | Chromium (Playwright), página con sesión iniciada, agentes MCP async en otro hilo |
| `FakeOllama` | `fake_ollama.py` | Ollama simulado como servidor HTTP |

## Ejecución
- `.venv/bin/pytest -q` — toda la suite de Python, incluidos los e2e si hay Chromium (local: `/opt/pw-browsers/chromium`).
- `ACM_E2E_REQUIRED=1` (CI): los e2e **no pueden saltarse**; sin navegador, la suite falla.
- `cd web && npm test` — tests unitarios del frontend (vitest).
- Pruebas de mutación: manuales por sprint, con el resultado en `12_TESTING/test_results.md` (automatizarlas está pendiente).
