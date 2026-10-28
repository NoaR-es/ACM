# Reglas operativas del agente

1. La constitución es `/CLAUDE.md`. No existe ni se crea `gemini.md`: donde la constitución dice `gemini.md`, léase `CLAUDE.md` (indicación del operador, 2026-09-30).
2. Flujo de lectura al entrar: `CLAUDE.md` → `control/INDEX.md` → `03_ESTADO/current_state.md` → `03_ESTADO/active_context.md` → índice especializado.
3. Antes de editar `current_state.md`/`active_context.md`, comprobar `LAST_UPDATED` y `LOCK` (multi-agente, CLAUDE.md §55.2).
4. Después de tocar `backlog_completo_v*.md` o `product_definition_v*.md`, regenerar inventarios y ejecutar `derive_backlog.py --check`.
5. Desarrollar en la rama asignada por la sesión; no hacer push a `main` sin autorización.
6. `control/` es la fuente de verdad del **desarrollo** de ACM: el agente lo mantiene siempre actualizado en el mismo commit que el cambio que lo motiva (ADR-011). No se confunde con la fuente de verdad del **producto**, que es SQLite.
