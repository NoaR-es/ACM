# Sprint activo

## SPRINT-009 — Conexión universal de agentes, unión con aprobación y colaboración

Contexto: el operador pide que ACM se pueda configurar en cualquier agente (Claude Code, Cursor, Codex, Antigravity, Hermes…) desde su propia configuración MCP y que ACM gestione todo con el agente, sin más trabajo suyo que conectarlo. Decisiones del operador (2026-10-06): el agente pregunta a ACM qué proyectos hay y elige entre crear uno o unirse; el operador da permiso en la interfaz; la interfaz arranca sola y sin token en local. Aclaración del operador (2026-10-14): la identidad de un agente no puede ser solo el nombre del cliente, porque puede haber varias sesiones del mismo cliente y desde equipos distintos.

| Campo | Valor |
|-------|-------|
| Sprint ID | SPRINT-009 |
| Objetivo | Cualquier agente se conecta con una entrada MCP estándar; se une a proyectos con aprobación del operador y colabora con otros agentes con trabajo repartido por ACM |
| Inicio | 2026-10-06 |
| Fin | Al cumplir el Sprint Goal (sin timebox; desarrollo por agente) |
| Sprint Goal | **Un agente de cualquier cliente MCP se conecta con una única entrada stdio, sin instalar ni configurar nada más. Crea un proyecto o pide unirse a uno y una persona lo aprueba en la interfaz local, que arranca sola. Varios agentes (también dos sesiones del mismo cliente) colaboran en un proyecto: ACM les reparte el trabajo sin solapes y se ve en el Kanban quién tiene qué. Cada CA está verificado por tests con procesos reales.** |
| Historias | US-14.12, US-14.13, US-14.14, US-14.15, US-14.16, US-14.17 (fuente B: US-15.13..15.18, FEAT-15.05..15.07) |
| Dependencias | SPRINT-008; ADR-017, ADR-018; nuevas ADR-023, ADR-024, ADR-025 |
| Riesgos | Los formatos de configuración de Antigravity, Codex y Hermes no se han podido probar con esos agentes (solo con un cliente MCP real por stdio y `uvx`); `~/.acm` es de un equipo (compartir entre equipos exige servidor con tokens); todos los agentes locales se ejecutan como el usuario del sistema |
| Impedimentos | IMP-004 (abierto; no afecta) |
| Fuera de alcance | Dependencias entre historias (US-05.02 CA-03); verificación con Ollama y Ollaya reales; proceso de instalación de `uv` |
| Velocidad | No se mide |

### Tasks

| ID | Tipo | Título | Historias | Estado |
|----|------|--------|-----------|--------|
| TASK-009-01 | DOCUMENTATION | Definición de producto v1.5 (`product_definition_v6.md`), refinamientos y ADR-023..025 | todas | IN_PROGRESS |
| TASK-009-02 | TASK | Modo local: `~/.acm`, identidad por cliente y sesión, creación abierta, `uvx`, `acm stop` | US-14.12 | IN_PROGRESS |
| TASK-009-03 | TASK | Unión con aprobación: esquema global v9, `AccessService`, MCP, REST y panel de solicitudes | US-14.14, US-14.15 | IN_PROGRESS |
| TASK-009-04 | TASK | Reparto de trabajo: esquema de proyecto v6, `WorkService`, `acm_next_work`, guarda de historias, Kanban con agente | US-14.16, US-14.17 | IN_PROGRESS |
| TASK-009-05 | TASK | Interfaz y supervisor en segundo plano (`acm serve --local`) y entrada sin token | US-14.12 | IN_PROGRESS |
| TASK-009-06 | TASK | Skills por todas las vías, `instructions` breves, prompts MCP y skill `acm-workflow` | US-14.13 | IN_PROGRESS |
| TASK-009-07 | TEST | 50 casos de test nuevos (procesos reales por stdio, interfaz en segundo plano y e2e), 12 mutaciones detectadas de 12 | todas | IN_PROGRESS |
| TASK-009-08 | DOCUMENTATION | README con la configuración de cada agente y cierre de `control/` | — | IN_PROGRESS |

SPRINT-008 cerrado y archivado en `99_ARCHIVO/historical/sprint_008.md` (CI runs #15 y #16 en verde).

### Estado de las historias

| Historia | Estado | Evidencia |
|----------|--------|-----------|
| US-14.12, 14.13, 14.14, 14.15, 14.16, 14.17 | IN_PROGRESS | Tests nuevos en PASS en local; falta la suite completa, la evidencia y la CI (`12_TESTING/sprint_009_evidence.md` aún no existe) |

PAUSADO el 2026-10-14 a petición del operador. VERIFIED = todos los CA con test automático en PASS en la suite completa. DONE requiere además la revisión del operador (merge del PR). Lo que no se ha podido verificar: el comportamiento de cada agente concreto (Antigravity, Codex, Hermes, Cursor) al leer las `instructions` o los prompts, y la interfaz con equipos distintos.
