# Pruebas de contrato

- `tests/test_realtime.py::test_us3001_ca01_us3002_contrato_documentado` compara las rutas publicadas en OpenAPI con las esperadas y exige las respuestas 400/401/403/404/409 en cada una.
- `test_us3001_ca02_ca04_entradas_invalidas_formato_consistente` comprueba el formato de error en todos los casos.
- MCP: `tests/test_mcp.py::test_us1405_ca01_ca02_descubrir_herramientas` fija el inventario exacto de herramientas y `tests/test_skills.py::test_us1508_*` que la skill acm-schema lo documenta.
