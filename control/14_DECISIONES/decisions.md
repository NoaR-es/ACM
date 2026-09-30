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
Estado: SUPERSEDED por ADR-007 (2026-09-30)
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

## ADR-006 — JEV: modelos de decisión servidos localmente con Ollaya
Fecha: 2026-09-30
Estado: ACCEPTED
Contexto: La definición cita "JEV" como motor decisional sin definirlo (GAP-003). El operador aclara: modelos de decisión que viven en servidores Ollaya, análogos a Ollama. Investigación del agente en fuentes públicas (2026-09-30), detalle en `10_IA/inference_engines.md`.
Problema: Fijar qué es JEV y cómo se integra ACM con él.
Hechos verificados (fuentes públicas, no probado en este entorno):
- **Jev** es el primer modelo "System One" de TypeSafe (lanzado 2026-09-15): recibe un estado (texto/JSON) y preguntas tipadas (`choice`, `score`, `noul`) y devuelve respuestas tipadas con probabilidades calibradas en una sola pasada, sin generar texto. API hospedada: `POST https://api.typesafe.ai/v1/systemone`.
- **Ollaya** (github.com/ollaya-dev/ollaya, Apache-2.0, v0.7.5 del 2026-09-28) es un runtime local "tipo Ollama" para modelos de decisión abiertos estilo Jev (laya, decider, kev, winnow, nli, gliclass…). Daemon en el puerto **11435**, CLI `pull/run/list/ps/serve`, API nativa `POST /api/decide` y endpoints compatibles con TypeSafe (`/v1/systemone`, `/v1/decisions`, `/v1/models`).
Alternativas consideradas: (a) solo API hospedada de TypeSafe; (b) solo Ollaya local; (c) adaptador único con backend configurable.
Decisión: (c). ACM implementará un único adaptador de decisión (TECH-020) contra el contrato wire de TypeSafe System One. Destino por defecto: Ollaya local; la API hospedada de TypeSafe es alternativa configurable (misma forma de petición). La API nativa `/api/decide` se usa cuando se necesite `routing` y tiempos para telemetría (EPIC-27).
Motivo: Coherencia con la filosofía local de Ollama (ADR-001), datos del proyecto sin salir de la máquina, latencia de milisegundos, y un solo contrato para dos destinos.
Consecuencias:
- Ollama = tareas generativas; Ollaya/JEV = decisiones tipadas (clasificación, puntuación, sí/no). Encaja con US-24.03.
- El Watchdog puede usar decisiones tipadas con umbrales de confianza (EPIC-10, 36, US-24.07) en lugar de parsear texto de un LLM.
- Riesgo ALTO de inestabilidad: Ollaya tiene ~2 semanas y publica varias versiones al día. Mitigación: fijar versión, contract tests del adaptador (SPIKE-006), degradar con elegancia si Ollaya no está disponible.
- Riesgo de seguridad: la instalación oficial es `curl | sh`; en ACM se preferirá la imagen Docker fijada por versión y `OLLAYA_API_KEY`.
Trade-offs: Un tercer motor de inferencia (Ollama + Ollaya + vector) añade operación; se acepta porque JEV sigue POST-MVP.

## ADR-007 — Alcance del MVP (supersede a ADR-003)
Fecha: 2026-09-30
Estado: ACCEPTED
Contexto: El operador delega en el agente la decisión del MVP.
Problema: Delimitar un MVP entregable y coherente con §12 de la definición.
Alternativas consideradas: (a) mantener ADR-003; (b) MVP mínimo (solo backlog + MCP, sin tiempo real ni IA); (c) ADR-003 ajustado.
Decisión: (c). Principio rector: **el MVP es ACM como memoria de estado y gobernanza, operado por agentes externos vía MCP**. La inteligencia generativa interna de ACM queda POST-MVP, salvo lo que §12 lista explícitamente (Ollama básico, RAG básico, context loading).
- MVP: EPIC-01, 02, 03, 04, 06, 07, 08, 09, 10, 11, 13, 15, 16, 18, 19, 20, 21, 23, 27, 43.
- Excluidas del MVP dentro de esas épicas: FEAT-02.03 (Discovery Socrático), FEAT-02.04, FEAT-03.03, FEAT-06.03, FEAT-07.02 (descomposición automática), FEAT-11.03, FEAT-13.03, FEAT-19.04, FEAT-21.03, FEAT-21.04, FEAT-21.05, FEAT-23.03, FEAT-23.04.
- JEV (EPIC-24) sigue POST-MVP, como fija §13; ADR-006 prepara su integración.
Motivo: Cambios respecto a ADR-003: FEAT-02.03 y FEAT-07.02 exigen que ACM razone con LLM propio, lo que §12 no pide (§12 pide "crear módulos/funcionalidades/tareas", no descubrirlas o descomponerlas). Un agente externo puede hacerlo a través de MCP. La detección de tareas huérfanas (US-07.07) sigue cubierta en MVP por US-10.03.
Consecuencias: MVP = 20 épicas, 53 features, 147 historias (antes 55 / 155); POST-MVP = 97 features, 205 historias. Fuente: `01_PRODUCTO/backlog.md` (generado).
Trade-offs: El MVP sigue siendo grande (20 épicas). Se entregará en incrementos según `01_PRODUCTO/roadmap.md`; revisable al cerrar la Fase 1.
