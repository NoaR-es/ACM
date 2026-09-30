# Impedimentos

| ID | Fecha | Descripción | Bloquea | Responsable | Estado |
|----|-------|-------------|---------|-------------|--------|
| IMP-001 | 2026-09-30 | Runtime/lenguaje del backend (y servidor MCP) no definido en la definición de producto. Es decisión arquitectónica mayor (CLAUDE.md §35). | TASK-000-04 y todo el código | Operador | CLOSED (2026-09-30: Python, ADR-005) |
| IMP-002 | 2026-09-30 | "JEV" no está definido (qué es, contrato, proveedor). | TASK-000-05, EPIC-24, SPIKE-006 (POST-MVP; no bloquea MVP) | Operador | CLOSED (2026-09-30: ADR-006) |
| IMP-003 | 2026-09-30 | Conflictos de requisitos CONF-001 (significado de JEV en EPIC-47) y CONF-002 (fuente de verdad: SQLite frente a `control/`) | Diseño de EPIC-02, EPIC-18 y EPIC-47; no bloquea SPIKE-001/002 | Operador | OPEN |
