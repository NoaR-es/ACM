# Estrategia de pruebas (2026-09-30)

- **Herramienta:** pytest (+ el plugin de anyio para los tests asíncronos).
- **Unidad de verificación: el criterio de aceptación.** Cada CA de una historia en sprint tiene al menos un test con nombre `test_usNNNN_caNN_*`, citado en la sección *Pruebas* de su refinamiento. `derive_backlog.py --check` comprueba que cada test citado existe.
- **Niveles:**
  - servicio (SQLite real en `tmp_path`);
  - frontera MCP (cliente oficial del SDK en proceso);
  - proceso real (uvicorn + HTTP, y stdio con subproceso);
  - concurrencia real (multiprocessing / threads);
  - caída de proceso (SIGKILL).
- **Sin mocks de SQLite:** los fallos de almacenamiento se inyectan en puntos concretos con `monkeypatch` (US-01.01 CA-04).
- **Pruebas de mutación manuales** de las invariantes críticas (retrospectiva SPRINT-001): todas detectadas. Automatizarlas está pendiente.
- **Evidencia por sprint:** `sprint_001_evidence.md` (CA ↔ test ↔ resultado, desde JUnit).
- **Cobertura de líneas:** no medida (no hay herramienta configurada).
