#!/usr/bin/env python3
"""Deriva los inventarios de backlog de control/01_PRODUCTO a partir de la
definición de producto (fuente de verdad del alcance).

Uso:
    python3 control/tools/derive_backlog.py          # regenera los inventarios
    python3 control/tools/derive_backlog.py --check  # falla (exit 1) si están desincronizados

Entrada:  control/01_PRODUCTO/product_definition_v2.md
Salidas:  control/01_PRODUCTO/{epics,features,user_stories,backlog,technical_stories}.md

Invariantes verificadas (exit 2 si fallan):
    - IDs de épica, feature e historia únicos.
    - Cada FEAT-XX.YY pertenece a EPIC-XX y cada US-XX.YY a EPIC-XX.
    - Toda épica tiene al menos una feature y toda feature al menos una historia.
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "01_PRODUCTO" / "product_definition_v2.md"
OUT_DIR = ROOT / "01_PRODUCTO"
SOURCE_REL = "01_PRODUCTO/product_definition_v2.md"

# Clasificación MVP / POST-MVP (ADR-009, supersede a ADR-007 y ADR-003). Decidida por
# el agente con delegación explícita del operador, a partir de las secciones 12 y 13.
MVP_EPICS = {1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 13, 15, 16, 18, 19, 20, 21, 22, 23, 27, 43}
POST_MVP_FEATURES = {
    "FEAT-02.03",  # Discovery Socrático (inteligencia generativa interna)
    "FEAT-02.04",  # Matriz de riesgo
    "FEAT-03.03",  # Gobierno arquitectónico multiagente
    "FEAT-06.03",  # Predicción / simulación de sprint
    "FEAT-07.02",  # Descomposición automática (inteligencia generativa interna)
    "FEAT-11.03",  # AutoRoot
    "FEAT-13.03",  # Protección avanzada (depende de EPIC-16 completo)
    "FEAT-19.04",  # Panel multi-proyecto global
    "FEAT-21.03",  # Reranking
    "FEAT-21.04",  # Caché RAG
    "FEAT-21.05",  # Auditoría RAG
    "FEAT-22.02",  # Selección dinámica de skills
    "FEAT-22.03",  # Auditoría de skills
    "FEAT-22.04",  # Sandbox de skills
    "FEAT-23.03",  # Supervisión de recursos
    "FEAT-23.04",  # Failover
}

EPIC_RE = re.compile(r"^# (EPIC-(\d{2})) — (.+)$")
FEAT_RE = re.compile(r"^### (FEAT-(\d{2})\.\d{2}) — (.+)$")
US_RE = re.compile(r"^#### (US-(\d{2})\.\d{2})\s*$")
TECH_RE = re.compile(r"^## (TECH-\d{3}) — (.+)$")
SPIKE_RE = re.compile(r"^### (SPIKE-\d{3}) — (.+)$")
OBJ_RE = re.compile(r"^\*\*Objetivo:\*\*\s*(.+)$")
VALUE_RE = re.compile(r"^\*\*Valor:\*\*\s*(.+)$")
BOLD_RE = re.compile(r"^\*\*(.+)\*\*$")


@dataclass
class Story:
    id: str
    epic: str
    feature: str
    text: str = ""
    criteria: list[str] = field(default_factory=list)


@dataclass
class Feature:
    id: str
    epic: str
    title: str
    stories: list[Story] = field(default_factory=list)


@dataclass
class Epic:
    id: str
    num: int
    title: str
    objective: str = ""
    value: str = ""
    features: list[Feature] = field(default_factory=list)


@dataclass
class Item:
    id: str
    title: str
    description: str = ""


def parse(text: str) -> tuple[list[Epic], list[Item], list[Item]]:
    epics: list[Epic] = []
    techs: list[Item] = []
    spikes: list[Item] = []
    story: Story | None = None
    item: Item | None = None
    in_criteria = False
    for raw in text.splitlines():
        line = raw.rstrip()
        if m := EPIC_RE.match(line):
            epics.append(Epic(m.group(1), int(m.group(2)), m.group(3)))
            story, item, in_criteria = None, None, False
            continue
        if m := FEAT_RE.match(line):
            epics[-1].features.append(Feature(m.group(1), f"EPIC-{m.group(2)}", m.group(3)))
            story, item, in_criteria = None, None, False
            continue
        if m := US_RE.match(line):
            feat = epics[-1].features[-1]
            story = Story(m.group(1), f"EPIC-{m.group(2)}", feat.id)
            feat.stories.append(story)
            item, in_criteria = None, False
            continue
        if m := TECH_RE.match(line):
            item = Item(m.group(1), m.group(2))
            techs.append(item)
            story = None
            continue
        if m := SPIKE_RE.match(line):
            item = Item(m.group(1), m.group(2))
            spikes.append(item)
            story = None
            continue
        if line.startswith("# ") or line.startswith("---"):
            # Un nuevo bloque de primer nivel o separador cierra historia/ítem.
            if line.startswith("# ") and not EPIC_RE.match(line):
                story, item = None, None
            in_criteria = False
            continue
        if epics and not epics[-1].features:
            if m := OBJ_RE.match(line):
                epics[-1].objective = m.group(1)
            elif m := VALUE_RE.match(line):
                epics[-1].value = m.group(1)
        if story is not None:
            if not story.text and (m := BOLD_RE.match(line)):
                story.text = m.group(1)
            elif line.strip() == "Criterios:":
                in_criteria = True
            elif in_criteria and line.startswith("* "):
                story.criteria.append(line[2:].strip())
        elif item is not None and line.strip() and not item.description:
            item.description = line.strip()
    return epics, techs, spikes


def validate(epics: list[Epic]) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for e in epics:
        for ident in [e.id] + [f.id for f in e.features] + [s.id for f in e.features for s in f.stories]:
            if ident in seen:
                errors.append(f"ID duplicado: {ident}")
            seen.add(ident)
        if not e.features:
            errors.append(f"{e.id} no tiene features")
        for f in e.features:
            if f.epic != e.id:
                errors.append(f"{f.id} no pertenece a {e.id}")
            if not f.stories:
                errors.append(f"{f.id} no tiene historias")
            for s in f.stories:
                if s.epic != e.id:
                    errors.append(f"{s.id} no pertenece a {e.id}")
                if not s.text:
                    errors.append(f"{s.id} sin enunciado")
    return errors


def scope(epic: Epic, feature_id: str | None = None) -> str:
    if epic.num not in MVP_EPICS:
        return "POST-MVP"
    if feature_id and feature_id in POST_MVP_FEATURES:
        return "POST-MVP"
    return "MVP"


def priority(sc: str) -> str:
    return "P1" if sc == "MVP" else "P3"


HEADER = (
    "<!-- GENERADO por control/tools/derive_backlog.py desde {src}. "
    "No editar a mano: editar la fuente y regenerar. -->\n\n"
).format(src=SOURCE_REL)


def render_epics(epics: list[Epic]) -> str:
    out = [HEADER, "# Épicas\n\n",
           f"Fuente: `{SOURCE_REL}` · Total: **{len(epics)}**\n\n",
           "| ID | Título | Alcance | Prioridad | Estado | Features | Historias |\n",
           "|----|--------|---------|-----------|--------|----------|-----------|\n"]
    for e in epics:
        sc = scope(e)
        n_us = sum(len(f.stories) for f in e.features)
        out.append(f"| {e.id} | {e.title} | {sc} | {priority(sc)} | PLANNED | {len(e.features)} | {n_us} |\n")
    out.append("\n## Objetivo y valor declarados\n\n")
    for e in epics:
        if e.objective or e.value:
            out.append(f"- **{e.id}** — Objetivo: {e.objective or 'no declarado'}"
                       f"{' · Valor: ' + e.value if e.value else ''}\n")
    missing = [e.id for e in epics if not e.objective]
    out.append(f"\nÉpicas sin objetivo explícito en la fuente ({len(missing)}): {', '.join(missing)}\n")
    return "".join(out)


def render_features(epics: list[Epic]) -> str:
    feats = [f for e in epics for f in e.features]
    out = [HEADER, "# Features\n\n",
           f"Fuente: `{SOURCE_REL}` · Total: **{len(feats)}**\n\n",
           "| ID | Épica | Título | Alcance | Estado | Historias |\n",
           "|----|-------|--------|---------|--------|-----------|\n"]
    for e in epics:
        for f in e.features:
            out.append(f"| {f.id} | {e.id} | {f.title} | {scope(e, f.id)} | PLANNED | "
                       f"{', '.join(s.id for s in f.stories)} |\n")
    return "".join(out)


def render_stories(epics: list[Epic]) -> str:
    stories = [s for e in epics for f in e.features for s in f.stories]
    with_ac = [s for s in stories if s.criteria]
    out = [HEADER, "# User Stories\n\n",
           f"Fuente: `{SOURCE_REL}` · Total: **{len(stories)}** · "
           f"Con criterios de aceptación: **{len(with_ac)}** · "
           f"Sin criterios: **{len(stories) - len(with_ac)}**\n\n",
           "> Estado READY exige criterios de aceptación binarios (Regla 3 del producto, §15 CLAUDE.md).\n"
           "> Las historias sin criterios permanecen en PLANNED hasta su refinamiento (ver BUG/gap `GAP-001`).\n\n"]
    for e in epics:
        out.append(f"## {e.id} — {e.title}\n\n")
        for f in e.features:
            sc = scope(e, f.id)
            out.append(f"### {f.id} — {f.title}\n\n")
            for s in f.stories:
                out.append(f"#### {s.id}\n\n")
                out.append(f"- Enunciado: {s.text}\n")
                out.append(f"- Épica: {e.id} · Feature: {f.id} · Alcance: {sc} · Prioridad: {priority(sc)}\n")
                out.append("- Sprint: — · Estado: PLANNED · Estimación: —\n")
                if s.criteria:
                    out.append("- Criterios de aceptación:\n")
                    out.extend(f"  - [ ] {c}\n" for c in s.criteria)
                else:
                    out.append("- Criterios de aceptación: MISSING (pendiente de refinamiento)\n")
                out.append("- Creada: 2026-09-30 · Última actualización: 2026-09-30\n\n")
    return "".join(out)


def render_backlog(epics: list[Epic], techs: list[Item], spikes: list[Item]) -> str:
    stories = [(e, f, s) for e in epics for f in e.features for s in f.stories]
    mvp = [x for x in stories if scope(x[0], x[1].id) == "MVP"]
    out = [HEADER, "# Product Backlog (resumen)\n\n",
           "| Tipo | Total | MVP | POST-MVP |\n|------|-------|-----|----------|\n",
           f"| EPIC | {len(epics)} | {sum(1 for e in epics if scope(e) == 'MVP')} | "
           f"{sum(1 for e in epics if scope(e) != 'MVP')} |\n",
           f"| FEATURE | {sum(len(e.features) for e in epics)} | "
           f"{sum(1 for e in epics for f in e.features if scope(e, f.id) == 'MVP')} | "
           f"{sum(1 for e in epics for f in e.features if scope(e, f.id) != 'MVP')} |\n",
           f"| USER_STORY | {len(stories)} | {len(mvp)} | {len(stories) - len(mvp)} |\n",
           f"| TECH (historia técnica) | {len(techs)} | — | — |\n",
           f"| SPIKE | {len(spikes)} | — | — |\n\n",
           "Detalle: `epics.md`, `features.md`, `user_stories.md`, `technical_stories.md`.\n",
           "Clasificación MVP: ADR-009.\n\n",
           "## Historias MVP por épica\n\n"]
    for e in epics:
        ids = [s.id for (ee, f, s) in mvp if ee.id == e.id]
        if ids:
            out.append(f"- **{e.id}** ({len(ids)}): {', '.join(ids)}\n")
    return "".join(out)


def render_tech(techs: list[Item], spikes: list[Item]) -> str:
    out = [HEADER, "# Historias técnicas transversales y Spikes\n\n",
           "> Los IDs `TECH-XXX` de la definición de producto designan **historias técnicas**, no deuda técnica.\n"
           "> La deuda técnica se registra como `TD-XXX` en `13_BUGS/`/`01_PRODUCTO/backlog.md` (ADR-002).\n\n",
           "## Historias técnicas\n\n| ID | Título | Descripción | Estado |\n|----|--------|-------------|--------|\n"]
    out.extend(f"| {t.id} | {t.title} | {t.description} | PLANNED |\n" for t in techs)
    out.append("\n## Spikes\n\n| ID | Título | Pregunta | Estado |\n|----|--------|----------|--------|\n")
    out.extend(f"| {s.id} | {s.title} | {s.description} | PLANNED |\n" for s in spikes)
    return "".join(out)


def main() -> int:
    check = "--check" in sys.argv[1:]
    epics, techs, spikes = parse(SOURCE.read_text(encoding="utf-8"))
    errors = validate(epics)
    if errors:
        print("ERRORES DE INTEGRIDAD:\n  " + "\n  ".join(errors), file=sys.stderr)
        return 2
    outputs = {
        "epics.md": render_epics(epics),
        "features.md": render_features(epics),
        "user_stories.md": render_stories(epics),
        "backlog.md": render_backlog(epics, techs, spikes),
        "technical_stories.md": render_tech(techs, spikes),
    }
    stale = []
    for name, content in outputs.items():
        path = OUT_DIR / name
        if check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                stale.append(name)
        else:
            path.write_text(content, encoding="utf-8")
    n_us = sum(len(f.stories) for e in epics for f in e.features)
    n_ft = sum(len(e.features) for e in epics)
    print(f"epics={len(epics)} features={n_ft} stories={n_us} tech={len(techs)} spikes={len(spikes)}")
    if stale:
        print("DESINCRONIZADOS: " + ", ".join(stale), file=sys.stderr)
        return 1
    print("OK" + (" (check)" if check else " (regenerado)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
