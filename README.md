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
| APIs | MCP (65 tools + Skills extension), REST v1 with OpenAPI (`/api/v1/docs`), WebSocket events |

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

Design decisions and the full operational record live in [`control/`](control/INDEX.md) (ADR-001…025).

### Quick start
Requirements: [`uv`](https://docs.astral.sh/uv/) (it runs ACM; install it with `curl -LsSf https://astral.sh/uv/install.sh | sh`,
or `pip install uv`). Node is **not** needed: the web UI ships pre-built.

There is nothing to install, clone or configure. Add **one MCP server entry** to your agent and that is all:

```json
{ "mcpServers": { "acm": { "command": "uvx", "args": ["--from", "git+https://github.com/NoaR-es/ACM", "acm", "mcp-stdio"] } } }
```

ACM starts when the agent connects, keeps its data in `~/.acm` and opens its web UI at `http://127.0.0.1:8765/`
(no token needed on your own computer). From there the agent works by itself; you only approve who may join a project.

### Connecting AI agents (MCP)
Every agent uses the **same entry** (`uvx --from git+https://github.com/NoaR-es/ACM acm mcp-stdio`). Only the file and the syntax change:

| Agent | Where | Entry |
|-------|-------|-------|
| **Claude Code** | its CLI | `claude mcp add acm -- uvx --from git+https://github.com/NoaR-es/ACM acm mcp-stdio` |
| **Cursor** | `~/.cursor/mcp.json` (or `.cursor/mcp.json`) | JSON above |
| **Antigravity** | `~/.gemini/config/mcp_config.json` | JSON above |
| **Codex** | `~/.codex/config.toml` | `[mcp_servers.acm]` with `command = "uvx"` and `args = ["--from", "git+https://github.com/NoaR-es/ACM", "acm", "mcp-stdio"]` |
| **Hermes** | `~/.hermes/config.yaml` | `mcp_servers:` → `acm:` → `command: "uvx"` and `args: [--from, git+https://github.com/NoaR-es/ACM, acm, mcp-stdio]` |

Add `@<tag-or-branch>` after the repository URL to pin a version. If your agent's configuration format changed, use its
documentation for "add an MCP server (stdio)": the command and arguments are always the same.

**How agents and people work together**
1. **Who is who.** Each agent is a principal named after its client and computer (`claude-code.laptop`), or after
   `ACM_AGENT` if you set it. Each connection is also its own *session* (`claude-code.laptop#3f9a`), so two Claude Code
   windows are two different workers.
2. **Projects.** The agent calls `acm_project_directory`, asks you whether to create a project or join an existing one,
   and either creates it (no approval needed) or asks to join (`acm_project_join`). **A request stays pending until you
   approve it** in the UI (Dashboard → *Access requests*: with write access, read-only, or reject). Until then the agent
   cannot see the project. Agents can never give access to other agents. You can remove an agent at any time (Members).
3. **Teamwork.** The agent reads the `acm-workflow` skill (ACM serves it by tool, resource, MCP prompt or the skills
   extension) and loops on `acm_next_work`. ACM decides what comes next (refine, plan the sprint, implement, verify,
   close the sprint), assigns it to that agent and never gives the same work to another one. Assignments expire after
   30 minutes without activity. The Kanban shows who holds each story.

**Several computers.** `~/.acm` belongs to one computer. To share projects between computers, run one server
(`acm serve`, see below) and connect every agent to it over HTTP with its own token.

Useful variables in an agent's entry: `ACM_AGENT` (agent name), `ACM_DATA_DIR` (state folder), `ACM_UI=0` (no background UI).
`acm stop` stops the background web UI. Setting `ACM_PRINCIPAL` keeps the old behaviour: one admin identity.

**Server with tokens (teams, shared machines).**
```bash
git clone https://github.com/NoaR-es/ACM.git && cd ACM
python3 -m venv .venv && .venv/bin/pip install -e .
.venv/bin/acm token create local-admin --name my-laptop --data-dir ./.acm-data   # prints the token ONCE
.venv/bin/acm serve --data-dir ./.acm-data                                      # http://127.0.0.1:8765/
.venv/bin/acm principal create claude --kind agent --role admin --data-dir ./.acm-data
.venv/bin/acm token create claude --name claude-code --data-dir ./.acm-data
claude mcp add --transport http acm http://127.0.0.1:8765/mcp/ --header "Authorization: Bearer acm_…"
```
Here the web UI asks for a token and every HTTP request needs one. The agent's role is `admin` only because projects can
only be created by admins in this mode.

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
| `ACM_DATA_DIR` | `~/.acm` | SQLite databases (one state per user) |
| `ACM_AGENT` | — | Agent name in local mode (default: its MCP client and this computer) |
| `ACM_UI` | `1` | `0`: do not start the background web UI in local mode |
| `ACM_HOST` / `ACM_PORT` | `127.0.0.1` / `8765` | Listen address |
| `ACM_PRINCIPAL` | `local-admin` | Local admin for the CLI. If set explicitly for stdio: one admin identity, no local mode |
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
- **Local mode:** with the `uvx` entry, every agent runs as *your* operating-system user, so the approval of project
  access is a safeguard (it stops an agent from entering a project by mistake or on its own initiative), **not** a
  security boundary against a malicious agent that can read `~/.acm` or run commands. For real isolation use the server
  with tokens. The local UI gets its token from `/api/local-session`, which only answers requests from the same computer
  that carry a custom header and a local host name (so a web page or a DNS-rebinding attack cannot obtain it).

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
Pre-release (`0.9.0.dev0`). The product definition, backlog, sprints, architecture decisions, test evidence and known
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
| APIs | MCP (65 herramientas + extensión Skills), REST v1 con OpenAPI (`/api/v1/docs`), eventos por WebSocket |

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

Las decisiones de diseño y el registro operativo completo están en [`control/`](control/INDEX.md) (ADR-001…025).

### Inicio rápido
Requisitos: [`uv`](https://docs.astral.sh/uv/) (es lo que ejecuta ACM; se instala con `curl -LsSf https://astral.sh/uv/install.sh | sh`
o `pip install uv`). **No** hace falta Node: la interfaz viene compilada.

No hay nada que instalar, clonar ni configurar. Añade **una entrada de servidor MCP** a tu agente y ya está:

```json
{ "mcpServers": { "acm": { "command": "uvx", "args": ["--from", "git+https://github.com/NoaR-es/ACM", "acm", "mcp-stdio"] } } }
```

ACM arranca cuando el agente se conecta, guarda sus datos en `~/.acm` y abre su interfaz web en `http://127.0.0.1:8765/`
(sin token en tu propio equipo). Desde ahí el agente trabaja solo; tú solo apruebas quién puede unirse a un proyecto.

### Conectar agentes IA (MCP)
Todos los agentes usan la **misma entrada** (`uvx --from git+https://github.com/NoaR-es/ACM acm mcp-stdio`). Solo cambian el archivo y la sintaxis:

| Agente | Dónde | Entrada |
|--------|-------|---------|
| **Claude Code** | su CLI | `claude mcp add acm -- uvx --from git+https://github.com/NoaR-es/ACM acm mcp-stdio` |
| **Cursor** | `~/.cursor/mcp.json` (o `.cursor/mcp.json`) | el JSON de arriba |
| **Antigravity** | `~/.gemini/config/mcp_config.json` | el JSON de arriba |
| **Codex** | `~/.codex/config.toml` | `[mcp_servers.acm]` con `command = "uvx"` y `args = ["--from", "git+https://github.com/NoaR-es/ACM", "acm", "mcp-stdio"]` |
| **Hermes** | `~/.hermes/config.yaml` | `mcp_servers:` → `acm:` → `command: "uvx"` y `args: [--from, git+https://github.com/NoaR-es/ACM, acm, mcp-stdio]` |

Añade `@<etiqueta-o-rama>` tras la URL del repositorio para fijar una versión. Si el formato de configuración de tu agente
ha cambiado, usa su documentación de «añadir un servidor MCP (stdio)»: el comando y los argumentos son siempre los mismos.

**Cómo trabajan juntos agentes y personas**
1. **Quién es quién.** Cada agente es un principal con el nombre de su cliente y su equipo (`claude-code.portatil`), o el de
   `ACM_AGENT` si lo fijas. Cada conexión es además su propia *sesión* (`claude-code.portatil#3f9a`): dos ventanas de
   Claude Code son dos trabajadores distintos.
2. **Proyectos.** El agente llama a `acm_project_directory`, te pregunta si crear un proyecto o unirse a uno existente, y
   lo crea (sin aprobación) o pide unirse (`acm_project_join`). **La petición queda pendiente hasta que la apruebes** en
   la interfaz (Panel → *Solicitudes de acceso*: con escritura, solo lectura o rechazar). Hasta entonces el agente no ve
   el proyecto. Un agente nunca puede dar acceso a otros agentes. Puedes retirar a un agente cuando quieras (Miembros).
3. **Trabajo en equipo.** El agente lee la skill `acm-workflow` (ACM la sirve por herramienta, recurso, prompt MCP o la
   extensión de skills) y repite `acm_next_work`. ACM decide qué toca (refinar, planificar el sprint, implementar,
   verificar, cerrar el sprint), se lo asigna a ese agente y nunca da el mismo trabajo a otro. Las asignaciones caducan a
   los 30 minutos sin actividad. El Kanban muestra quién tiene cada historia.

**Varios equipos.** `~/.acm` es de un solo equipo. Para compartir proyectos entre equipos, deja un servidor (`acm serve`,
más abajo) y conecta cada agente a él por HTTP con su propio token.

Variables útiles en la entrada de un agente: `ACM_AGENT` (nombre del agente), `ACM_DATA_DIR` (carpeta de estado),
`ACM_UI=0` (sin interfaz en segundo plano). `acm stop` para la interfaz web en segundo plano. Con `ACM_PRINCIPAL` se
conserva el comportamiento anterior: una única identidad admin.

**Servidor con tokens (equipos, máquinas compartidas).**
```bash
git clone https://github.com/NoaR-es/ACM.git && cd ACM
python3 -m venv .venv && .venv/bin/pip install -e .
.venv/bin/acm token create local-admin --name mi-portatil --data-dir ./.acm-data   # muestra el token UNA vez
.venv/bin/acm serve --data-dir ./.acm-data                                        # http://127.0.0.1:8765/
.venv/bin/acm principal create claude --kind agent --role admin --data-dir ./.acm-data
.venv/bin/acm token create claude --name claude-code --data-dir ./.acm-data
claude mcp add --transport http acm http://127.0.0.1:8765/mcp/ --header "Authorization: Bearer acm_…"
```
Aquí la interfaz pide un token y toda petición HTTP lo necesita. El agente tiene rol `admin` solo porque en este modo
únicamente los admin crean proyectos.

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
| `ACM_DATA_DIR` | `~/.acm` | Bases SQLite (un estado por usuario) |
| `ACM_AGENT` | — | Nombre del agente en modo local (por defecto: su cliente MCP y este equipo) |
| `ACM_UI` | `1` | `0`: no arrancar la interfaz web en segundo plano en modo local |
| `ACM_HOST` / `ACM_PORT` | `127.0.0.1` / `8765` | Dirección de escucha |
| `ACM_PRINCIPAL` | `local-admin` | Admin local de la CLI. Si se fija explícitamente en stdio: una sola identidad admin, sin modo local |
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
- **Modo local:** con la entrada `uvx`, todos los agentes se ejecutan como *tu* usuario del sistema, así que la
  aprobación de acceso a proyectos es una salvaguarda (evita que un agente entre en un proyecto por error o por iniciativa
  propia), **no** una barrera de seguridad frente a un agente malicioso que pueda leer `~/.acm` o ejecutar comandos. Para
  aislamiento real usa el servidor con tokens. La interfaz local obtiene su token de `/api/local-session`, que solo
  responde a peticiones de este mismo equipo con una cabecera propia y un nombre de servidor local (una página web o un
  ataque de DNS rebinding no pueden conseguirlo).

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
Versión previa (`0.9.0.dev0`). La definición de producto, el backlog, los sprints, las decisiones de arquitectura, la
evidencia de tests y los problemas conocidos están en [`control/`](control/INDEX.md), la fuente de verdad operativa del
proyecto.

Estado actual y siguientes pasos: [`control/03_ESTADO/current_state.md`](control/03_ESTADO/current_state.md).

### Licencia
Todavía no se ha elegido una licencia de código abierto: `pyproject.toml` declara **Proprietary** y todos los derechos
están reservados a su propietario.
