# Registro de decisiones (ADR)

## ADR-001 — Stack conceptual base
Fecha: 2026-09-30
Estado: ACCEPTED
Contexto: La definición de producto v1 fija las tecnologías base.
Problema: Registrar el stack oficial para que ningún agente use tecnologías no autorizadas (US-03.03).
Alternativas consideradas: ninguna evaluada por el agente; decisión del operador.
Decisión: SQLite (persistencia, por proyecto), base vectorial + RAG, Ollama (inferencia local), JEV (decisional, futuro), React (web), WebSockets (tiempo real), MCP (interfaz de agentes).
Motivo: Definido por el operador en la definición de producto.
Consecuencias: Runtime/lenguaje backend **no decidido** (IMP-001); vector DB concreto pendiente (SPIKE-003).
Trade-offs: SQLite simplifica despliegue y aislamiento por proyecto a costa de concurrencia de escritura (SPIKE-001).

## ADR-002 — Convención de IDs: TECH = historia técnica, TD = deuda técnica
Fecha: 2026-09-30
Estado: ACCEPTED
Contexto: `CLAUDE.md` §33 usa `TECH-XXX` para deuda técnica; la definición de producto usa `TECH-001..030` para historias técnicas transversales.
Problema: Colisión de identificadores.
Alternativas consideradas: (a) renombrar las historias técnicas; (b) usar otro prefijo para la deuda.
Decisión: (b) Se conservan `TECH-NNN` de la definición como historias técnicas; la deuda técnica usa `TD-NNN`.
Motivo: No alterar IDs de la fuente de producto; la deuda aún no existe, cambiar su prefijo no rompe nada.
Consecuencias: Desviación documentada respecto a CLAUDE.md §33 (solo en el prefijo; el formato de campos se mantiene).
Trade-offs: Ninguno relevante.

## ADR-003 — Clasificación MVP / POST-MVP por épica y feature (provisional)
Fecha: 2026-09-30
Estado: ACCEPTED (provisional; pendiente de validación del operador — TASK-000-06)
Contexto: La definición (§12, §13) lista capacidades MVP y POST-MVP, pero no las asigna a épicas.
Problema: El backlog necesita alcance y prioridad por historia.
Alternativas consideradas: (a) todo P1; (b) clasificación por historia individual; (c) por épica con exclusiones por feature.
Decisión: (c). MVP: EPIC-01, 02, 03, 04, 06, 07, 08, 09, 10, 11, 13, 15, 16, 18, 19, 20, 21, 23, 27, 43; excepto FEAT-02.04, 03.03, 06.03, 11.03, 13.03, 19.04, 21.03, 21.04, 21.05, 23.03, 23.04 (POST-MVP). MVP → P1, POST-MVP → P3.
Motivo: Correspondencia directa con §12 (p. ej. "RAG básico" = FEAT-21.01/21.02; reranking, AutoRoot y failover aparecen en §13).
Consecuencias: 155 historias MVP / 197 POST-MVP. Codificado en `derive_backlog.py`.
Trade-offs: EPIC-02 entra entera salvo la matriz de riesgo; EPIC-05 (INVEST/tribunal) queda POST-MVP aunque "Watchdog básico" es MVP (cubierto por EPIC-10). Revisable.

## ADR-004 — Inventarios de backlog derivados por script
Fecha: 2026-09-30
Estado: ACCEPTED
Contexto: 352 historias; transcribirlas a mano introduce errores y deriva.
Problema: Mantener sincronía fuente ↔ inventarios de forma verificable.
Alternativas consideradas: copia manual; un archivo por historia.
Decisión: `control/tools/derive_backlog.py` genera los inventarios; `--check` detecta desincronización.
Motivo: Determinismo y verificabilidad (CLAUDE.md §4, §41).
Consecuencias: Los archivos generados no se editan a mano. Refinamientos futuros deben entrar por la fuente (o por un mecanismo de anexos a decidir).
Trade-offs: El formato de la definición pasa a ser un contrato del parser.

## ADR-005 — Python como lenguaje del backend
Fecha: 2026-09-30
Estado: ACCEPTED
Contexto: ADR-001 dejó sin decidir el runtime del backend (IMP-001 / GAP-002).
Problema: Elegir el lenguaje del núcleo, servidor MCP, API, WebSockets, Watchdog, RAG y adaptadores de modelos.
Alternativas consideradas: TypeScript/Node (mismo lenguaje que el frontend React, SDK MCP oficial); Python.
Decisión: **Python (≥ 3.11)** para todo el backend, incluido el servidor MCP. El frontend sigue siendo React (ADR-001).
Motivo: Decisión del operador. Encaja con el dominio: `sqlite3` en stdlib, SDK MCP oficial para Python, ecosistema RAG/embeddings/vector stores y cliente Ollama maduros, y coherencia con el tooling existente (`derive_backlog.py`).
Consecuencias:
- El frontend (React) y el backend quedan en lenguajes distintos: los contratos API/WebSocket deben definirse explícitamente (esquemas compartidos, contract tests — `06_API/contract_tests.md`).
- Framework HTTP/WebSocket, cliente SQLite (sync/async) y gestión de paquetes se fijan en ADRs posteriores tras SPIKE-001 (concurrencia SQLite) y SPIKE-002 (MCP multi-proyecto).
- Tooling del frontend React (bundler, TypeScript o no) sigue abierto (GAP-002, reducido).
Trade-offs: Concurrencia limitada por el GIL y por SQLite en escrituras; se mitiga con asyncio/procesos y se mide en SPIKE-001/SPIKE-005.
