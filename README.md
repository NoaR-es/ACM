# ACM — Agile Context Manager

[![CI](https://github.com/NoaR-es/ACM/actions/workflows/ci.yml/badge.svg)](https://github.com/NoaR-es/ACM/actions/workflows/ci.yml)

**[English](#english) · [Español](#español)**

---

<a id="english"></a>

## English

### Table of contents
- [What is ACM?](#what-is-acm)
- [Features](#features)
- [How it works](#how-it-works)
- [Quick start](#quick-start)
- [Connecting AI agents (MCP)](#connecting-ai-agents-mcp)
- [Local models: Ollama and JEV (Ollaya)](#local-models-ollama-and-jev-ollaya)
- [Saving agent tokens](#saving-agent-tokens)
- [Autonomous agile supervisor](#autonomous-agile-supervisor)
- [Web interface](#web-interface)
- [Configuration](#configuration)
- [Security](#security)
- [Development](#development)
- [Project status](#project-status)
- [License](#license)

### What is ACM?
ACM is the **state memory, governance and traceability layer for AI coding agents**. Agents (Claude Code, Cursor,
any MCP client) keep the whole agile project in ACM instead of in their own context window:
requirements, epics, features, user stories with acceptance criteria, sprints, the Kanban board, and the audit trail.

- **SQLite is the source of truth**: one database per project plus a global one.
- ACM runs **its own MCP server**, which also distributes skills that teach agents how to use it.
- It uses **local models** as a "second brain" so agents spend fewer tokens:
  - **JEV** decision models served by [Ollaya](https://github.com/ollaya-dev/ollaya), for typed decisions with calibrated probabilities;
  - **Ollama**, for summaries, conversation and an internal agent.
- ACM **supervises itself**: it reviews stories, sprints and the board with those models, reports what is done, pending
  or inconsistent, and applies only safe, reversible changes.
- Humans see and operate everything from a **real-time web interface**.

### Features
| Area | What you get |
|------|--------------|
| Backlog | Requirements → epics → features → stories → acceptance criteria, with full traceability and a READY quality gate |
| Workflow | Story status flow with history; DONE only from VERIFIED |
| Sprints | Goal, dates and capacity; overload check before starting; closing with carry-over and a stored summary |
| Kanban | One or many projects at once, colour per project, lanes, drag and drop or keyboard, sprint boards |
| Governance | SQLite integrity checks, quarantine of damaged projects, traffic-light status, audit history |
| Autonomous supervisor | Quality review (INVEST, verifiable criteria, size), sprint risk, WIP, stale work; reports; safe actions |
| Second brain | Compact story context, typed decisions (`acm_decide`), local chat threads with an internal agent |
| Models | Discovers the models in Ollama and Ollaya; choose one Ollama model and several Ollaya models per purpose |
| Identity | Opaque per-principal tokens, admin/user roles, owner/member project roles, instant revocation |
| Audit | Every MCP call and REST write recorded (who, which token, arguments with secrets redacted, result, duration) |
| Web UI | Everything above, live over WebSocket, WCAG AA contrast in light and dark themes |
| APIs | MCP (59 tools + Skills extension), REST v1 with OpenAPI (`/api/v1/docs`), WebSocket events |

### How it works
```text
 AI agent ── MCP (HTTP + token / stdio) ─┐                        ┌── Ollama  (local LLM: summaries, chat,
 Browser ─── REST v1 + WebSocket ────────┼──► ACM (one process) ──┤            internal agent, uncalibrated decisions)
 CLI ────────────────────────────────────┘     │                  └── Ollaya  (JEV decision models: calibrated
                                               │                               choice / score / yes-no)
                                               ├── SQLite: acm.db (global) + projects/<id>/project.db
                                               └── domain events table → WebSocket → live UI
```
- One Python process (FastAPI + uvicorn) serves the web UI at `/`, REST at `/api/v1`, the WebSocket at
  `/api/v1/ws` and MCP at `/mcp`.
- `acm mcp-stdio` runs the same MCP server over stdio for local agents.
- Every confirmed change becomes a domain event, so every connected screen updates live, even when an agent in another process made the change.
- Inference goes through two ports: decision and generation. A router tries, in the order configured per project:
  1. deterministic rules;
  2. JEV;
  3. Ollama.
  Each call is logged with the model that answered.

Design decisions and the full operational record live in [`control/`](control/INDEX.md) (ADR-001…022).

### Quick start
Requirements: Python ≥ 3.11. Node is **not** needed to run ACM (the web UI ships pre-built).

```bash
git clone https://github.com/NoaR-es/ACM.git && cd ACM
python3 -m venv .venv && .venv/bin/pip install -e .
.venv/bin/acm token create local-admin --name my-laptop --data-dir ./.acm-data   # prints the token ONCE
.venv/bin/acm serve --data-dir ./.acm-data                                      # http://127.0.0.1:8765/
```
Open `http://127.0.0.1:8765/`, paste the token and create your first project from the dashboard (**+ New project**).

### Connecting AI agents (MCP)
Give each agent its own principal and token, so everything it does is attributable and revocable:
```bash
.venv/bin/acm principal create claude --kind agent --data-dir ./.acm-data
.venv/bin/acm token create claude --name claude-code --data-dir ./.acm-data
```
Claude Code over HTTP:
```bash
claude mcp add --transport http acm http://127.0.0.1:8765/mcp/ --header "Authorization: Bearer acm_…"
```
Or over stdio. There is no network in this mode; the identity is `ACM_PRINCIPAL`:
```bash
claude mcp add acm -- /path/to/ACM/.venv/bin/acm mcp-stdio --data-dir /path/to/ACM/.acm-data
```
The agent should first read the `acm-schema` skill (served by ACM itself). It explains the data model, the workflow and which of the 59 tools to use. Every project tool takes an explicit `project_id`.

### Local models: Ollama and JEV (Ollaya)
Both are optional; without them ACM works with its deterministic rules.

**Ollama** (generative, local):
```bash
ollama pull qwen2.5:3b          # any model you like
export ACM_OLLAMA_URL=http://127.0.0.1:11434
```
**JEV decision models via Ollaya** (port 11435):
```bash
curl -fsSL https://ollaya.dev/install.sh | sh     # from the Ollaya README
ollaya pull laya                                 # CPU-friendly router; `winnow:e4b` is Ollaya's recommendation with a GPU
ollaya serve
export ACM_JEV_URL=http://127.0.0.1:11435        # ACM_JEV_API_KEY if the server uses OLLAYA_API_KEY
```
Start `acm serve` and open **System → Models**. ACM lists every model each runtime reports; it never offers one that
is not installed. There you choose:
- **one Ollama model**;
- a **default Ollaya model** and **one per purpose**: e.g. `decider` for `agile.sprint_review`, `laya` for everything else;
- a note on what each model is for.

Each Ollaya model also shows a built-in guide (what it is, what it is best for), taken from the Ollaya README.
Choices apply immediately, without a restart, and take precedence over `ACM_OLLAMA_MODEL` / `ACM_JEV_MODEL`.
The order of decision engines is set per project in **Configuration → `decision.engine_order`**.

| Engine | Answers | Probabilities | Used by |
|--------|---------|---------------|---------|
| Rules | Only the checks it knows (`story.quality`) | Exact | READY gate, Watchdog |
| JEV (Ollaya) | Any typed question: `choice`, `score`, `noul` (yes/no) | Calibrated | `acm_decide`, supervisor reviews, sprint risk |
| Ollama | Any typed question, choosing only among the options (JSON schema) | None (uncalibrated) | Fallback for decisions; summaries, reports, chat |

A gate never accepts an uncalibrated answer: Ollama can inform, not decide on its own.

> Status: both adapters follow the documented APIs and are tested against simulated servers. They have **not yet been
> verified against real Ollama/Ollaya instances** (the development environment has no access to them; IMP-004).

### Saving agent tokens
Agents get more done with fewer tokens by delegating to ACM:

| Instead of… | The agent calls… | What it saves |
|-------------|------------------|---------------|
| Reading the story, epic, requirements and sibling stories one by one | `acm_context_compact` | A single compact context with sources; support sections summarised by Ollama when over budget. The reply measures the tokens saved |
| Reasoning through a classification, yes/no check or score | `acm_decide` (JEV, optionally `model=`) | Answered in milliseconds by a decision model, with probabilities |
| Finding out which models exist and what they are for | `acm_models_list` | Models, details, purposes, operator notes and usage guide |
| Re-sending context to a local model on every turn | `acm_chat` with `thread_id` | ACM keeps the thread; only the new message is sent |
| Reading the whole project to answer a question | `acm_chat` | The internal Ollama agent queries ACM itself with read-only tools (`backlog_overview`, `get_story`, `search_stories`, `trace_requirement`, `list_sprints`, `governance`, `story_context`) using the caller's permissions |

Saved tokens are reported per agent and project in **System** (`acm_savings_report`).

### Autonomous agile supervisor
Every Watchdog run includes a review ACM does on its own. Runs happen on demand and every
`ACM_WATCHDOG_INTERVAL_S`, 10 minutes by default.
- **Stories:** INVEST, verifiable acceptance criteria and size, judged by JEV or Ollama. A review is reused until the story changes.
- **Sprints:** overdue, overloaded or empty sprints; unrefined or cancelled stories inside a sprint; risk of missing the goal (JEV).
- **Kanban:** WIP limit (`kanban.wip_limit`), stale work (`supervisor.stale_days`), work in progress outside the active sprint.
- **Report:** done, pending, inconsistencies and actions. Ollama writes it; without Ollama, ACM composes it.

Per project, `supervisor.mode` is `off`, `propose` or `apply_safe` (default). In `apply_safe` ACM applies by itself
**only** reversible actions from a closed list:
- move a complete, well-judged story to READY;
- send a READY story with vague criteria back to PLANNED;
- remove a cancelled story from a sprint.

An action is applied only when a calibrated engine (rules or JEV) decides it with confidence ≥
`supervisor.min_confidence_pct` (85 % by default). Each one is audited as the agent `acm-supervisor` and can be
undone from **Project → Governance**. Anything else is a proposal. ACM never marks DONE, cancels or deletes.

### Web interface
Log in with a token. What you get:
- **Dashboard:** all your projects with traffic light and live changes, plus **+ New project**.
- **Kanban:** one or many projects.
- **Project tabs:**
  - Summary, Backlog (create requirements, epics, features and stories; link, confirm coverage, split), Requirements, Stories;
  - Sprints, Kanban, Governance (supervisor report, applied actions with *Undo*, proposals, findings);
  - **Assistant** (chat with the local model), Members, Configuration.
- **Documentation:** skills, workflow, OpenAPI.
- **Activity:** live tool calls and a filterable audit.
- **System:** health, models, engines, token savings, principals, tokens (shown once), revocation.

### Configuration
| Variable | Default | Purpose |
|----------|---------|---------|
| `ACM_DATA_DIR` | `./.acm-data` | SQLite databases |
| `ACM_HOST` / `ACM_PORT` | `127.0.0.1` / `8765` | Listen address |
| `ACM_PRINCIPAL` | `local-admin` | Local admin (stdio and CLI identity) |
| `ACM_OLLAMA_URL` / `ACM_OLLAMA_MODEL` | — | Ollama runtime / initial model (choose in the UI) |
| `ACM_JEV_URL` / `ACM_JEV_MODEL` / `ACM_JEV_API_KEY` | — | Ollaya runtime / initial default model / bearer key |
| `ACM_WATCHDOG_INTERVAL_S` | `600` | Periodic governance + supervisor run (`0` disables) |
| `ACM_EVENTS_KEEP` | `10000` | Events kept for WebSocket resume |
| `ACM_ALLOWED_HOSTS` | — | Extra host names accepted behind a proxy |
| `ACM_SQLITE_SYNCHRONOUS` | `FULL` | Durability of the global database |

Per-project settings, editable in the UI:
- `context.max_tokens`;
- `decision.engine_order`;
- `supervisor.mode`, `supervisor.min_confidence_pct`, `supervisor.stale_days`;
- `kanban.wip_limit`;
- `sqlite.synchronous`.

### Security
- **Tokens:** every HTTP request needs a token. Tokens are stored only as SHA-256 hashes and are never logged or sent in events.
- **Isolation:** projects the caller cannot access answer `NOT_FOUND`.
- **Web UI:** strict CSP, sanitised Markdown, and the token kept in `sessionStorage`.
- **Network:** ACM listens on `127.0.0.1` by default. **ACM does not terminate TLS**: expose it only behind a TLS proxy
  and set `ACM_ALLOWED_HOSTS`.
- **Local models:** Ollama/Ollaya URLs and keys come only from the environment, never from the web UI.

### Development
```bash
.venv/bin/pip install -e ".[dev]"
.venv/bin/pytest                                  # unit, integration and e2e (Chromium via Playwright)
.venv/bin/ruff check src tests
python3 control/tools/derive_backlog.py --check   # backlog integrity
python3 control/tools/code_inventory.py --check   # code inventory in control/05_CODIGO up to date
cd web && npm ci && npm test && npm run build     # frontend (React + TypeScript + Vite); build goes to src/acm/webui
```
CI (GitHub Actions) runs all of the above.
- End-to-end tests are mandatory in CI.
- The committed web bundle must match the sources.

### Project status
Pre-release (`0.8.0.dev0`). The product definition, backlog, sprints, architecture decisions, test evidence and known
issues are kept in [`control/`](control/INDEX.md), which is the operational source of truth of the project.

Current state and next steps: [`control/03_ESTADO/current_state.md`](control/03_ESTADO/current_state.md).

### License
No open-source license has been chosen yet: `pyproject.toml` declares **Proprietary**, and all rights are reserved by
the owner.

---

<a id="español"></a>

## Español

### Índice
- [¿Qué es ACM?](#qué-es-acm)
- [Funcionalidades](#funcionalidades)
- [Cómo funciona](#cómo-funciona)
- [Inicio rápido](#inicio-rápido)
- [Conectar agentes IA (MCP)](#conectar-agentes-ia-mcp)
- [Modelos locales: Ollama y JEV (Ollaya)](#modelos-locales-ollama-y-jev-ollaya)
- [Ahorrar tokens a los agentes](#ahorrar-tokens-a-los-agentes)
- [Supervisor ágil autónomo](#supervisor-ágil-autónomo)
- [Interfaz web](#interfaz-web)
- [Configuración](#configuración)
- [Seguridad](#seguridad)
- [Desarrollo](#desarrollo)
- [Estado del proyecto](#estado-del-proyecto)
- [Licencia](#licencia)

### ¿Qué es ACM?
ACM es la **memoria de estado, gobernanza y trazabilidad de los agentes IA que desarrollan software**. Los agentes
(Claude Code, Cursor o cualquier cliente MCP) guardan todo el proyecto ágil en ACM en lugar de en su propio contexto:
requisitos, épicas, features, historias con criterios de aceptación, sprints, el Kanban y la auditoría.

- **SQLite es la fuente de verdad**: una base por proyecto y una global.
- ACM tiene **su propio servidor MCP**, que además distribuye las skills que enseñan a los agentes a usarlo.
- Usa **modelos locales** como «segundo cerebro» para que los agentes gasten menos tokens:
  - modelos de decisión **JEV** servidos por [Ollaya], para decisiones tipadas con probabilidades calibradas;
  - **Ollama**, para resúmenes, conversación y un agente interno.
- ACM **se supervisa a sí mismo**: revisa historias, sprints y el tablero con esos modelos, informa de lo hecho, lo
  pendiente y lo incongruente, y aplica solo cambios seguros y reversibles.
- Las personas lo ven y lo operan todo desde una **interfaz web en tiempo real**.

[Ollaya]: https://github.com/ollaya-dev/ollaya

### Funcionalidades
| Área | Qué ofrece |
|------|------------|
| Backlog | Requisitos → épicas → features → historias → criterios, con trazabilidad completa y gate de calidad READY |
| Flujo | Estados de historia con historial; DONE solo desde VERIFIED |
| Sprints | Objetivo, fechas y capacidad; control de sobrecarga antes de iniciar; cierre con traslado y resumen guardado |
| Kanban | Uno o varios proyectos a la vez, color por proyecto, carriles, arrastrar o teclado, tablero por sprint |
| Gobernanza | Integridad SQLite, cuarentena de proyectos dañados, semáforo, histórico de auditorías |
| Supervisor autónomo | Calidad (INVEST, criterios verificables, tamaño), riesgo del sprint, WIP, trabajo estancado; informes; acciones seguras |
| Segundo cerebro | Contexto compacto de una historia, decisiones tipadas (`acm_decide`), hilos de chat con un agente interno local |
| Modelos | Descubre los modelos de Ollama y Ollaya; eliges uno de Ollama y varios de Ollaya según su propósito |
| Identidad | Tokens opacos por principal, roles admin/user y owner/member, revocación inmediata |
| Auditoría | Cada llamada MCP y escritura REST registrada (quién, con qué token, argumentos sin secretos, resultado, duración) |
| Interfaz web | Todo lo anterior, en vivo por WebSocket, con contraste WCAG AA en tema claro y oscuro |
| APIs | MCP (59 herramientas + extensión Skills), REST v1 con OpenAPI (`/api/v1/docs`), eventos por WebSocket |

### Cómo funciona
```text
 Agente IA ── MCP (HTTP + token / stdio) ─┐                        ┌── Ollama  (LLM local: resúmenes, chat,
 Navegador ── REST v1 + WebSocket ────────┼──► ACM (un proceso) ───┤            agente interno, decisiones sin calibrar)
 CLI ─────────────────────────────────────┘     │                  └── Ollaya  (modelos de decisión JEV: choice /
                                                │                               score / sí-no calibrados)
                                                ├── SQLite: acm.db (global) + projects/<id>/project.db
                                                └── tabla de eventos → WebSocket → interfaz en vivo
```
- Un solo proceso Python (FastAPI + uvicorn) sirve la interfaz en `/`, REST en `/api/v1`, el WebSocket en
  `/api/v1/ws` y MCP en `/mcp`.
- `acm mcp-stdio` es el mismo servidor MCP por stdio para agentes locales.
- Cada cambio confirmado genera un evento, así que todas las pantallas conectadas se actualizan al instante, aunque el cambio lo haga un agente en otro proceso.
- La inferencia pasa por dos puertos: decisión y generación. Un router prueba, en el orden que fija cada proyecto:
  1. reglas deterministas;
  2. JEV;
  3. Ollama.
  Cada llamada queda registrada con el modelo que respondió.

Las decisiones de diseño y el registro operativo completo están en [`control/`](control/INDEX.md) (ADR-001…022).

### Inicio rápido
Requisitos: Python ≥ 3.11. **No** hace falta Node para usar ACM: la interfaz viene compilada.

```bash
git clone https://github.com/NoaR-es/ACM.git && cd ACM
python3 -m venv .venv && .venv/bin/pip install -e .
.venv/bin/acm token create local-admin --name mi-portatil --data-dir ./.acm-data   # muestra el token UNA vez
.venv/bin/acm serve --data-dir ./.acm-data                                        # http://127.0.0.1:8765/
```
Abre `http://127.0.0.1:8765/`, pega el token y crea tu primer proyecto desde el panel (**+ Nuevo proyecto**).

### Conectar agentes IA (MCP)
Da a cada agente su propio principal y token: todo lo que haga será atribuible y revocable.
```bash
.venv/bin/acm principal create claude --kind agent --data-dir ./.acm-data
.venv/bin/acm token create claude --name claude-code --data-dir ./.acm-data
```
Claude Code por HTTP:
```bash
claude mcp add --transport http acm http://127.0.0.1:8765/mcp/ --header "Authorization: Bearer acm_…"
```
O por stdio. En este modo no hay red y la identidad es `ACM_PRINCIPAL`:
```bash
claude mcp add acm -- /ruta/a/ACM/.venv/bin/acm mcp-stdio --data-dir /ruta/a/ACM/.acm-data
```
Lo primero que debe hacer el agente es leer la skill `acm-schema`, que sirve el propio ACM. Explica el modelo de datos, el flujo de trabajo y cuál de las 59 herramientas usar en cada momento. Toda herramienta de proyecto recibe un `project_id` explícito.

### Modelos locales: Ollama y JEV (Ollaya)
Ambos son opcionales: sin ellos ACM funciona con sus reglas deterministas.

**Ollama** (generativo, local):
```bash
ollama pull qwen2.5:3b          # el modelo que prefieras
export ACM_OLLAMA_URL=http://127.0.0.1:11434
```
**Modelos de decisión JEV con Ollaya** (puerto 11435):
```bash
curl -fsSL https://ollaya.dev/install.sh | sh     # según el README de Ollaya
ollaya pull laya                                 # enrutador apto para CPU; con GPU, Ollaya recomienda `winnow:e4b`
ollaya serve
export ACM_JEV_URL=http://127.0.0.1:11435        # ACM_JEV_API_KEY si el servidor usa OLLAYA_API_KEY
```
Arranca `acm serve` y abre **Sistema → Modelos**. ACM muestra los modelos que declara cada runtime y nunca ofrece uno
que no esté instalado. Ahí eliges:
- **un modelo de Ollama**;
- un **modelo de Ollaya por defecto** y **uno por propósito**: p. ej. `decider` para `agile.sprint_review` y `laya` para lo demás;
- una nota sobre para qué sirve cada modelo.

Cada modelo de Ollaya muestra además una guía integrada (qué es y para qué es mejor), tomada del README de Ollaya.
La elección se aplica al momento, sin reiniciar, y tiene prioridad sobre `ACM_OLLAMA_MODEL` / `ACM_JEV_MODEL`.
El orden de los motores de decisión se fija por proyecto en **Configuración → `decision.engine_order`**.

| Motor | Responde | Probabilidades | Lo usan |
|-------|----------|----------------|---------|
| Reglas | Solo las comprobaciones que conoce (`story.quality`) | Exactas | Gate READY, Watchdog |
| JEV (Ollaya) | Cualquier pregunta tipada: `choice`, `score`, `noul` (sí/no) | Calibradas | `acm_decide`, revisiones del supervisor, riesgo del sprint |
| Ollama | Cualquier pregunta tipada, eligiendo solo entre las opciones (esquema JSON) | No (sin calibrar) | Respaldo para decisiones; resúmenes, informes, chat |

Un gate nunca acepta una respuesta sin calibrar: Ollama puede informar, pero no decide por su cuenta.

> Estado: ambos adaptadores siguen las APIs documentadas y se prueban contra servidores simulados. **Aún no se han
> verificado contra un Ollama o un Ollaya reales**: el entorno de desarrollo no tiene acceso a ellos (IMP-004).

### Ahorrar tokens a los agentes
Los agentes hacen más con menos tokens delegando en ACM:

| En vez de… | El agente llama a… | Qué ahorra |
|------------|--------------------|------------|
| Leer historia, épica, requisitos e historias hermanas uno a uno | `acm_context_compact` | Un solo contexto compacto con fuentes; las secciones de apoyo se resumen con Ollama si superan el presupuesto. La respuesta mide los tokens ahorrados |
| Razonar una clasificación, una comprobación sí/no o una puntuación | `acm_decide` (JEV, opcionalmente `model=`) | Lo responde en milisegundos un modelo de decisión, con probabilidades |
| Averiguar qué modelos hay y para qué sirven | `acm_models_list` | Modelos, detalles, propósitos, notas del operador y guía de uso |
| Reenviar el contexto al modelo local en cada turno | `acm_chat` con `thread_id` | ACM conserva el hilo: solo se envía el mensaje nuevo |
| Leer todo el proyecto para responder una pregunta | `acm_chat` | El agente interno de Ollama consulta él mismo ACM con herramientas de solo lectura (`backlog_overview`, `get_story`, `search_stories`, `trace_requirement`, `list_sprints`, `governance`, `story_context`) y los permisos de quien pregunta |

Los tokens ahorrados se ven por agente y proyecto en **Sistema** (`acm_savings_report`).

### Supervisor ágil autónomo
Cada auditoría del Watchdog incluye una revisión que ACM hace por sí mismo. Se ejecuta a demanda y cada
`ACM_WATCHDOG_INTERVAL_S`, 10 minutos por defecto.
- **Historias:** INVEST, criterios verificables y tamaño, juzgados por JEV u Ollama. La revisión se reutiliza mientras la historia no cambie.
- **Sprints:** vencidos, sobrecargados o vacíos; historias sin refinar o canceladas dentro de un sprint; riesgo de no cumplir el objetivo (JEV).
- **Kanban:** límite WIP (`kanban.wip_limit`), trabajo estancado (`supervisor.stale_days`), trabajo en curso fuera del sprint activo.
- **Informe:** hecho, pendiente, incongruencias y acciones. Lo redacta Ollama; sin Ollama, lo compone ACM.

Por proyecto, `supervisor.mode` puede ser `off`, `propose` o `apply_safe` (por defecto). En `apply_safe` ACM aplica
por sí solo **únicamente** acciones reversibles de una lista cerrada:
- pasar a READY una historia completa y bien juzgada;
- devolver a PLANNED una historia READY con criterios vagos;
- sacar de un sprint una historia cancelada.

Una acción solo se aplica si la decide un motor calibrado (reglas o JEV) con confianza ≥
`supervisor.min_confidence_pct` (85 % por defecto). Cada una queda auditada como el agente `acm-supervisor` y se puede
deshacer en **Proyecto → Gobernanza**. Todo lo demás son propuestas. ACM nunca marca DONE, ni cancela, ni borra.

### Interfaz web
Entras con un token. Esto es lo que ofrece:
- **Panel:** todos tus proyectos con semáforo y cambios en vivo, y **+ Nuevo proyecto**.
- **Kanban:** uno o varios proyectos.
- **Pestañas de proyecto:**
  - Resumen, Backlog (crear requisitos, épicas, features e historias; enlazar, confirmar cobertura, dividir), Requisitos, Historias;
  - Sprints, Kanban, Gobernanza (informe del supervisor, acciones aplicadas con *Deshacer*, propuestas, hallazgos);
  - **Asistente** (chat con el modelo local), Miembros, Configuración.
- **Documentación:** skills, flujo, OpenAPI.
- **Actividad:** herramientas en vivo y auditoría filtrable.
- **Sistema:** salud, modelos, motores, ahorro de tokens, principales, tokens (el secreto se muestra una vez), revocación.

### Configuración
| Variable | Por defecto | Uso |
|----------|-------------|-----|
| `ACM_DATA_DIR` | `./.acm-data` | Bases SQLite |
| `ACM_HOST` / `ACM_PORT` | `127.0.0.1` / `8765` | Dirección de escucha |
| `ACM_PRINCIPAL` | `local-admin` | Admin local (identidad en stdio y CLI) |
| `ACM_OLLAMA_URL` / `ACM_OLLAMA_MODEL` | — | Runtime Ollama / modelo inicial (se elige en la interfaz) |
| `ACM_JEV_URL` / `ACM_JEV_MODEL` / `ACM_JEV_API_KEY` | — | Runtime Ollaya / modelo por defecto inicial / clave Bearer |
| `ACM_WATCHDOG_INTERVAL_S` | `600` | Auditoría y supervisor periódicos (`0` los desactiva) |
| `ACM_EVENTS_KEEP` | `10000` | Eventos conservados para reanudar el WebSocket |
| `ACM_ALLOWED_HOSTS` | — | Nombres de host extra detrás de un proxy |
| `ACM_SQLITE_SYNCHRONOUS` | `FULL` | Durabilidad de la base global |

Parámetros por proyecto, editables en la interfaz:
- `context.max_tokens`;
- `decision.engine_order`;
- `supervisor.mode`, `supervisor.min_confidence_pct`, `supervisor.stale_days`;
- `kanban.wip_limit`;
- `sqlite.synchronous`.

### Seguridad
- **Tokens:** toda petición HTTP necesita un token. Solo se guarda su hash SHA-256 y nunca aparece en logs ni en eventos.
- **Aislamiento:** los proyectos ajenos responden `NOT_FOUND`.
- **Interfaz web:** CSP estricta, Markdown saneado y token guardado en `sessionStorage`.
- **Red:** ACM escucha en `127.0.0.1` por defecto. **ACM no termina TLS**: exponlo solo detrás de un proxy TLS y declara `ACM_ALLOWED_HOSTS`.
- **Modelos locales:** las URL y claves de Ollama/Ollaya solo se configuran en el entorno, nunca desde la web.

### Desarrollo
```bash
.venv/bin/pip install -e ".[dev]"
.venv/bin/pytest                                  # unitarios, integración y e2e (Chromium con Playwright)
.venv/bin/ruff check src tests
python3 control/tools/derive_backlog.py --check   # integridad del backlog
python3 control/tools/code_inventory.py --check   # inventario de código de control/05_CODIGO al día
cd web && npm ci && npm test && npm run build     # frontend (React + TypeScript + Vite); el build va a src/acm/webui
```
La CI (GitHub Actions) ejecuta todo lo anterior.
- Los e2e son obligatorios en la CI.
- El bundle web versionado debe coincidir con las fuentes.

### Estado del proyecto
Versión previa (`0.8.0.dev0`). La definición de producto, el backlog, los sprints, las decisiones de arquitectura, la
evidencia de tests y los problemas conocidos están en [`control/`](control/INDEX.md), la fuente de verdad operativa del
proyecto.

Estado actual y siguientes pasos: [`control/03_ESTADO/current_state.md`](control/03_ESTADO/current_state.md).

### Licencia
Todavía no se ha elegido una licencia de código abierto: `pyproject.toml` declara **Proprietary** y todos los derechos
están reservados a su propietario.
