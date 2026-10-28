# Acuerdos de trabajo

- Idioma de `control/` y de la comunicación: español.
- Identificadores: se conservan los de la definición de producto (`EPIC-NN`, `FEAT-NN.MM`, `US-NN.MM`, `TECH-NNN`, `SPIKE-NNN`).
  Tareas: `TASK-<sprint>-<nn>`. Deuda técnica: `TD-NNN` (ADR-002). Bugs: `BUG-NNN`. Huecos de control: `GAP-NNN`.
- Los inventarios de backlog son **derivados**: se edita la fuente y se ejecuta `python3 control/tools/derive_backlog.py`.
- Todo commit referencia la Task/Story (ver `17_GIT/commit_conventions.md`).
- Decisiones que requieren al operador: las listadas en `/CLAUDE.md` §35.
- Fecha de acuerdo: 2026-09-30.
