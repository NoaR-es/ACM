# E2e tests

**Estado del área:** ACTIVE (SPRINT-007).

`tests/test_webui.py`: 24 casos (23 funciones, una parametrizada por tema) en Chromium real (Playwright) contra ACM real por HTTP, con agentes MCP reales en otro hilo. Cubren los CA de US-06.06, 06.07, 31.01, 31.02, 31.04, 31.06, 31.07, 31.08, 21.09, 45.02, 45.03, US-01.02 (CA-03 y CA-04), además de «sin errores de consola» y las cabeceras de seguridad. Localmente se saltan sin navegador; en la CI son obligatorios (`ACM_E2E_REQUIRED=1`). Detalle: `../05_CODIGO/tests.md`.
