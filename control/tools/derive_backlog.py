#!/usr/bin/env python3
"""Genera el backlog UNIFICADO de ACM a partir de dos fuentes de producto (ADR-010).

Uso:
    python3 control/tools/derive_backlog.py          # regenera los inventarios
    python3 control/tools/derive_backlog.py --check  # falla (exit 1) si están desincronizados

Fuentes (no se editan a mano; ver ADR-004 y ADR-010):
    A: control/01_PRODUCTO/backlog_completo_v1.md   — columna vertebral (48 épicas con criterios CA-NN)
    B: control/01_PRODUCTO/product_definition_v3.md — definición v1.2 (visión, 48 épicas propias, TECH, SPIKE)

Regla de unificación:
    - Épicas, features e historias de A conservan su ID.
    - Cada feature de B se integra en la épica unificada indicada en FEATURE_MAP y se renumera
      a continuación de las de A (FEAT-NN.k, US-NN.m). Su ID original queda en `id_mapping.md`.
    - Lo que no tiene épica equivalente en A crea las épicas EPIC-49..53 (NEW_EPICS).

Salidas (control/01_PRODUCTO/):
    epics.md, features.md, user_stories.md, backlog.md, technical_stories.md, id_mapping.md

Exit codes: 0 OK · 1 inventarios desincronizados · 2 violación de integridad.
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "01_PRODUCTO"
SRC_A_REL = "01_PRODUCTO/backlog_completo_v1.md"
SRC_B_REL = "01_PRODUCTO/product_definition_v3.md"
SRC_A = ROOT / SRC_A_REL
SRC_B = ROOT / SRC_B_REL
# Estados distintos de PLANNED (historias, TECH, SPIKE). Sin entrada = PLANNED. Solo estados permitidos (CLAUDE.md §4).
STATUS_FILE = Path(__file__).resolve().parent / "item_status.json"
ALLOWED_STATUS = {"PLANNED", "READY", "IN_PROGRESS", "BLOCKED", "IMPLEMENTED", "TESTING", "VERIFIED", "FAILED",
                  "DEPRECATED", "CANCELLED", "DONE"}
STATUS: dict[str, str] = {}
# Fusión de historias duplicadas (GAP-006): {"US-B": {"into": "US-A", "reason": "..."}}.
DEDUPE_FILE = Path(__file__).resolve().parent / "dedupe.json"
# Refinamientos por historia: control/01_PRODUCTO/refinements/US-NN.MM.md (regla READY de la fuente A).
REFINEMENTS_DIR = OUT_DIR / "refinements"
READY_SECTIONS = ("Precondiciones", "Flujo", "Alternativas", "Errores", "Reglas", "Validaciones",
                  "Casos límite", "Tareas", "Pruebas")

# ---------------------------------------------------------------------------
# Épicas nuevas creadas por la unificación (ADR-010): contenido de B sin equivalente en A.
NEW_EPICS = {
    49: ("GESTIÓN DE DEUDA TÉCNICA",
         "Registrar, analizar y limitar la deuda técnica (Debt Gate)."),
    50: ("MODELOS DE DECISIÓN JEV (OLLAYA)",
         "Integrar modelos de decisión tipados estilo Jev servidos por Ollaya o TypeSafe (ADR-006)."),
    51: ("SANDBOX, GEMELO DIGITAL Y USUARIOS SINTÉTICOS",
         "Probar cambios, sprints y flujos de usuario en entornos aislados antes de tocar el proyecto real."),
    52: ("CLI DE ADMINISTRACIÓN",
         "Operar y consultar ACM desde terminal."),
    53: ("EXTENSIONES, PLUGINS Y EXTENSIBILIDAD DEL MOTOR",
         "Ampliar ACM (agentes, herramientas MCP, eventos) sin modificar el núcleo."),
}

# Feature de B (definición v1.1) → épica unificada que la recibe (ADR-010).
FEATURE_MAP = {
    "FEAT-01.01": 1, "FEAT-01.02": 1, "FEAT-01.03": 13, "FEAT-01.04": 1,
    "FEAT-02.01": 17, "FEAT-02.02": 17, "FEAT-02.03": 3, "FEAT-02.04": 3,
    "FEAT-03.01": 25, "FEAT-03.02": 25, "FEAT-03.03": 25,
    "FEAT-04.01": 4, "FEAT-04.02": 4, "FEAT-04.03": 4,
    "FEAT-05.01": 4, "FEAT-05.02": 41, "FEAT-05.03": 41,
    "FEAT-06.01": 5, "FEAT-06.02": 5, "FEAT-06.03": 5,
    "FEAT-07.01": 10, "FEAT-07.02": 10, "FEAT-07.03": 11,
    "FEAT-08.01": 10, "FEAT-08.02": 10, "FEAT-08.03": 10,
    "FEAT-09.01": 28, "FEAT-09.02": 28, "FEAT-09.03": 28,
    "FEAT-10.01": 13, "FEAT-10.02": 13, "FEAT-10.03": 13,
    "FEAT-11.01": 29, "FEAT-11.02": 29, "FEAT-11.03": 29,
    "FEAT-12.01": 49, "FEAT-12.02": 49, "FEAT-12.03": 49,
    "FEAT-13.01": 12, "FEAT-13.02": 12, "FEAT-13.03": 12,
    "FEAT-14.01": 25, "FEAT-14.02": 25, "FEAT-14.03": 25,
    "FEAT-15.01": 14, "FEAT-15.02": 14, "FEAT-15.03": 14, "FEAT-15.04": 15,
    "FEAT-16.01": 20, "FEAT-16.02": 20, "FEAT-16.03": 20, "FEAT-16.04": 20,
    "FEAT-17.01": 19, "FEAT-17.02": 19, "FEAT-17.03": 41, "FEAT-17.04": 41,
    "FEAT-18.01": 21, "FEAT-18.02": 21, "FEAT-18.03": 21,
    "FEAT-19.01": 6, "FEAT-19.02": 31, "FEAT-19.03": 26, "FEAT-19.04": 45,
    "FEAT-20.01": 27, "FEAT-20.02": 27, "FEAT-20.03": 27,
    "FEAT-21.01": 16, "FEAT-21.02": 16, "FEAT-21.03": 16, "FEAT-21.04": 16, "FEAT-21.05": 16,
    "FEAT-22.01": 15, "FEAT-22.02": 15, "FEAT-22.03": 15, "FEAT-22.04": 15,
    "FEAT-23.01": 22, "FEAT-23.02": 22, "FEAT-23.03": 22, "FEAT-23.04": 39,
    "FEAT-24.01": 50, "FEAT-24.02": 50, "FEAT-24.03": 50, "FEAT-24.04": 50,
    "FEAT-25.01": 51, "FEAT-25.02": 51, "FEAT-25.03": 51, "FEAT-25.04": 51,
    "FEAT-26.01": 24, "FEAT-26.02": 44, "FEAT-26.03": 44,
    "FEAT-27.01": 44, "FEAT-27.02": 26,
    "FEAT-28.01": 23, "FEAT-28.02": 23, "FEAT-28.03": 20,
    "FEAT-29.01": 46, "FEAT-29.02": 46, "FEAT-29.03": 46,
    "FEAT-30.01": 32, "FEAT-30.02": 32,
    "FEAT-31.01": 52, "FEAT-31.02": 52,
    "FEAT-32.01": 53, "FEAT-32.02": 53,
    "FEAT-33.01": 17, "FEAT-33.02": 17, "FEAT-33.03": 17,
    "FEAT-34.01": 18, "FEAT-34.02": 18, "FEAT-34.03": 18,
    "FEAT-35.01": 25, "FEAT-35.02": 25,
    "FEAT-36.01": 27, "FEAT-36.02": 27,
    "FEAT-37.01": 29, "FEAT-37.02": 29, "FEAT-37.03": 29,
    "FEAT-38.01": 43, "FEAT-38.02": 43, "FEAT-38.03": 43, "FEAT-38.04": 43,
    "FEAT-39.01": 41, "FEAT-39.02": 41, "FEAT-39.03": 41,
    "FEAT-40.01": 15, "FEAT-40.02": 15, "FEAT-40.03": 46,
    "FEAT-41.01": 40, "FEAT-41.02": 40, "FEAT-41.03": 40,
    "FEAT-42.01": 48, "FEAT-42.02": 48, "FEAT-42.03": 48,
    "FEAT-43.01": 35, "FEAT-43.02": 35, "FEAT-43.03": 35, "FEAT-43.04": 35, "FEAT-43.05": 35,
    "FEAT-44.01": 7, "FEAT-44.02": 7, "FEAT-44.03": 7,
    "FEAT-45.01": 32, "FEAT-45.02": 32,
    "FEAT-46.01": 17, "FEAT-46.02": 17, "FEAT-46.03": 17, "FEAT-46.04": 17,
    "FEAT-47.01": 51, "FEAT-47.02": 51, "FEAT-47.03": 51,
    "FEAT-48.01": 53, "FEAT-48.02": 53, "FEAT-48.03": 53,
}

# ---------------------------------------------------------------------------
# Alcance MVP (ADR-010, enmendado por ADR-012: EPIC-47/US-47.01 al MVP; FEAT-43.04/05 de B v1.2 en MVP).
# Historias de A: MVP si su épica está en MVP_EPICS y no está en POST_MVP_A_STORIES.
MVP_EPICS = {1, 2, 3, 4, 5, 6, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22,
             24, 25, 26, 27, 28, 29, 30, 31, 35, 44, 47}
POST_MVP_A_STORIES = {
    "US-12.03",  # recuperación automática tras fallo de agente (requiere orquestador interno)
    "US-13.01", "US-13.02",  # ejecuciones bloqueadas del orquestador interno
    "US-14.01", "US-14.02", "US-14.03",  # ACM como cliente de servidores MCP externos
    "US-15.02",  # asignar skills a agentes internos
    "US-16.03",  # memoria privada por instancia de agente interno
    "US-24.02",  # recursos compartidos entre proyectos
    "US-25.01", "US-25.03",  # generación/detección documental automática
    "US-28.03",  # informe de calidad
    "US-31.03",  # inspección de agentes internos
    "US-47.02",  # entornos de ejecución (US-47.01, abstracción preparada para JEV, sí es MVP)
}
# Historias de B: conservan su clasificación de ADR-009.
B_MVP_EPICS = {1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 13, 15, 16, 18, 19, 20, 21, 22, 23, 27, 43}
B_POST_MVP_FEATURES = {
    "FEAT-02.03", "FEAT-02.04", "FEAT-03.03", "FEAT-06.03", "FEAT-07.02", "FEAT-11.03",
    "FEAT-13.03", "FEAT-19.04", "FEAT-21.03", "FEAT-21.04", "FEAT-21.05",
    "FEAT-22.02", "FEAT-22.03", "FEAT-22.04", "FEAT-23.03", "FEAT-23.04",
}
DUP_THRESHOLD = 0.20  # Jaccard mínimo para señalar "posible solapamiento" (heurística, GAP-006)


# ---------------------------------------------------------------------------
@dataclass
class Story:
    id: str
    title: str = ""
    como: str = ""
    quiero: str = ""
    para: str = ""
    text: str = ""          # enunciado de una línea (fuente B)
    criteria: list[str] = field(default_factory=list)
    sections: dict[str, list[str]] = field(default_factory=dict)
    origin: str = ""
    scope: str = ""
    dup: str = ""
    merged_into: str = ""                                   # fusionada en otra historia (dedupe.json)
    merged_from: list[str] = field(default_factory=list)
    refinement: dict[str, list[str]] = field(default_factory=dict)
    refinement_file: str = ""
    sprint: str = ""


@dataclass
class Feature:
    id: str
    title: str
    origin: str = ""
    stories: list[Story] = field(default_factory=list)


@dataclass
class Epic:
    id: str
    num: int
    title: str
    objective: str = ""
    origin: str = ""
    features: list[Feature] = field(default_factory=list)


@dataclass
class Item:
    id: str
    title: str
    description: str = ""


# ------------------------------ Fuente A -----------------------------------
A_EPIC = re.compile(r"^# (EPIC-(\d{2})) — (.+)$")
A_FEAT = re.compile(r"^#{2,3} (FEAT-\d{2}\.\d{2}) — (.+)$")
A_US = re.compile(r"^### (US-\d{2}\.\d{2}) — (.+)$")
A_CA = re.compile(r"^\* \*\*(CA-\d{2}):\*\*\s*(.+)$")
A_SECTION = re.compile(r"^\*\*(Precondiciones|Flujo|Errores|Tareas|Criterios de aceptación)\*\*\s*$")
A_ROLE = re.compile(r"^\*\*(Como|quiero|para)\*\*\s*(.+)$")


def parse_a(text: str) -> list[Epic]:
    epics: list[Epic] = []
    story: Story | None = None
    section = ""
    want_objective = False
    for raw in text.splitlines():
        line = raw.rstrip()
        if m := A_EPIC.match(line):
            epics.append(Epic(m.group(1), int(m.group(2)), m.group(3), origin="A"))
            story, section, want_objective = None, "", False
            continue
        if not epics:
            continue
        if line == "## Objetivo":
            want_objective = True
            continue
        if want_objective and line.strip():
            epics[-1].objective = line.strip()
            want_objective = False
            continue
        if m := A_FEAT.match(line):
            epics[-1].features.append(Feature(m.group(1), m.group(2), origin=f"A:{m.group(1)}"))
            story, section = None, ""
            continue
        if m := A_US.match(line):
            story = Story(m.group(1), title=m.group(2), origin=f"A:{m.group(1)}")
            epics[-1].features[-1].stories.append(story)
            section = ""
            continue
        if line.startswith("# ") or line.startswith("---"):
            if line.startswith("# "):
                story = None
            section = ""
            continue
        if story is None:
            continue
        if m := A_ROLE.match(line):
            setattr(story, {"Como": "como", "quiero": "quiero", "para": "para"}[m.group(1)], m.group(2).strip())
        elif m := A_SECTION.match(line):
            section = m.group(1)
        elif m := A_CA.match(line):
            story.criteria.append(f"{m.group(1)}: {m.group(2)}")
        elif section and section != "Criterios de aceptación" and line.strip():
            story.sections.setdefault(section, []).append(line.strip())
    return epics


# ------------------------------ Fuente B -----------------------------------
B_EPIC = re.compile(r"^# (EPIC-(\d{2})) — (.+)$")
B_FEAT = re.compile(r"^### (FEAT-(\d{2})\.\d{2}) — (.+)$")
B_US = re.compile(r"^#### (US-(\d{2})\.\d{2})\s*$")
B_TECH = re.compile(r"^## (TECH-\d{3}) — (.+)$")
B_SPIKE = re.compile(r"^### (SPIKE-\d{3}) — (.+)$")
BOLD = re.compile(r"^\*\*(.+)\*\*$")


def parse_b(text: str) -> tuple[list[Epic], list[Item], list[Item]]:
    epics: list[Epic] = []
    techs: list[Item] = []
    spikes: list[Item] = []
    story: Story | None = None
    item: Item | None = None
    in_criteria = False
    for raw in text.splitlines():
        line = raw.rstrip()
        if m := B_EPIC.match(line):
            epics.append(Epic(m.group(1), int(m.group(2)), m.group(3), origin="B"))
            story, item, in_criteria = None, None, False
            continue
        if m := B_FEAT.match(line):
            epics[-1].features.append(Feature(m.group(1), m.group(3), origin=f"B:{m.group(1)}"))
            story, item, in_criteria = None, None, False
            continue
        if m := B_US.match(line):
            story = Story(m.group(1), origin=f"B:{m.group(1)}")
            epics[-1].features[-1].stories.append(story)
            item, in_criteria = None, False
            continue
        if m := B_TECH.match(line):
            item = Item(m.group(1), m.group(2))
            techs.append(item)
            story = None
            continue
        if m := B_SPIKE.match(line):
            item = Item(m.group(1), m.group(2))
            spikes.append(item)
            story = None
            continue
        if line.startswith("# ") or line.startswith("---"):
            if line.startswith("# ") and not B_EPIC.match(line):
                story, item = None, None
            in_criteria = False
            continue
        if story is not None:
            if not story.text and (m := BOLD.match(line)):
                story.text = m.group(1)
            elif line.strip() == "Criterios:":
                in_criteria = True
            elif in_criteria and line.startswith("* "):
                story.criteria.append(f"CA-{len(story.criteria) + 1:02d}: {line[2:].strip()}")
        elif item is not None and line.strip() and not item.description:
            item.description = line.strip()
    return epics, techs, spikes


# ------------------------------ Unificación --------------------------------
STOP = set("como quiero para una unos unas que del los las por con sin sus cada este esta cuando antes "
           "despues sobre entre desde hasta donde otro otra puede pueda debe estado sistema agente agentes "
           "operador usuario proyecto".split())


def words(s: str) -> set[str]:
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return {w for w in re.findall(r"[a-z0-9]+", s) if len(w) > 3 and w not in STOP}


def jaccard(a: set[str], b: set[str]) -> float:
    return len(a & b) / len(a | b) if a and b else 0.0


def unify(a_epics: list[Epic], b_epics: list[Epic]):
    errors: list[str] = []
    epics: dict[int, Epic] = {e.num: e for e in a_epics}
    for num, (title, objective) in NEW_EPICS.items():
        if num in epics:
            errors.append(f"EPIC-{num:02d} nueva colisiona con fuente A")
        epics[num] = Epic(f"EPIC-{num:02d}", num, title, objective=objective, origin="ADR-010")
    b_ids = {f.id for e in b_epics for f in e.features}
    if set(FEATURE_MAP) != b_ids:
        errors.append(f"FEATURE_MAP no cubre exactamente las features de B: "
                      f"faltan {sorted(b_ids - set(FEATURE_MAP))}, sobran {sorted(set(FEATURE_MAP) - b_ids)}")
    mapping: list[tuple[str, str, str]] = []  # (tipo, id B, id unificado)
    for e in a_epics:
        for f in e.features:
            for s in f.stories:
                s.scope = "POST-MVP" if (e.num not in MVP_EPICS or s.id in POST_MVP_A_STORIES) else "MVP"
    for be in b_epics:
        for bf in be.features:
            target = epics.get(FEATURE_MAP.get(bf.id, -1))
            if target is None:
                continue
            nf = Feature(f"FEAT-{target.num:02d}.{len(target.features) + 1:02d}", bf.title, origin=f"B:{bf.id}")
            b_mvp = be.num in B_MVP_EPICS and bf.id not in B_POST_MVP_FEATURES
            if b_mvp and target.num not in MVP_EPICS:
                errors.append(f"{bf.id} es MVP en B pero su épica destino EPIC-{target.num:02d} no es MVP")
            mapping.append(("FEAT", bf.id, nf.id))
            base = sum(len(f.stories) for f in target.features)
            for bs in bf.stories:
                ns = Story(f"US-{target.num:02d}.{base + len(nf.stories) + 1:02d}", text=bs.text,
                           criteria=list(bs.criteria), origin=f"B:{bs.id}", scope="MVP" if b_mvp else "POST-MVP")
                nf.stories.append(ns)
                mapping.append(("US", bs.id, ns.id))
            target.features.append(nf)
    ordered = [epics[n] for n in sorted(epics)]
    # Posibles solapamientos: historias de B frente a historias de A de la misma épica.
    for e in ordered:
        a_stories = [s for f in e.features for s in f.stories if s.origin.startswith("A:")]
        for f in e.features:
            for s in f.stories:
                if not s.origin.startswith("B:"):
                    continue
                ws = words(s.text)
                best = max(((jaccard(ws, words(f"{a.title} {a.quiero} {a.para}")), a.id) for a in a_stories),
                           default=(0.0, ""))
                if best[0] >= DUP_THRESHOLD:
                    s.dup = best[1]
    # Integridad
    seen: set[str] = set()
    for e in ordered:
        for ident in [e.id] + [f.id for f in e.features] + [s.id for f in e.features for s in f.stories]:
            if ident in seen:
                errors.append(f"ID duplicado: {ident}")
            seen.add(ident)
        if not e.features:
            errors.append(f"{e.id} sin features")
        for f in e.features:
            if not f.id.startswith(f"FEAT-{e.num:02d}."):
                errors.append(f"{f.id} fuera de {e.id}")
            if not f.stories:
                errors.append(f"{f.id} sin historias")
            for s in f.stories:
                if not s.id.startswith(f"US-{e.num:02d}."):
                    errors.append(f"{s.id} fuera de {e.id}")
                if not (s.text or s.quiero):
                    errors.append(f"{s.id} sin enunciado")
    return ordered, mapping, errors


# ------------------------------ Fusión y refinamiento ----------------------
def apply_dedupe(epics: list[Epic], errors: list[str]) -> None:
    by_id = {s.id: s for e in epics for s in stories_of(e)}
    for src_id, spec in json.loads(DEDUPE_FILE.read_text(encoding="utf-8")).items():
        target_id = spec.get("into", "")
        src, dst = by_id.get(src_id), by_id.get(target_id)
        if src is None or dst is None:
            errors.append(f"dedupe.json: {src_id} → {target_id}: historia inexistente")
            continue
        if src_id[:5] != target_id[:5]:
            errors.append(f"dedupe.json: {src_id} y {target_id} deben pertenecer a la misma épica")
        if dst.merged_into or src is dst:
            errors.append(f"dedupe.json: destino inválido para {src_id}")
            continue
        if not spec.get("reason"):
            errors.append(f"dedupe.json: {src_id} sin 'reason'")
        src.merged_into, src.dup = target_id, ""
        src.scope = "CANCELLED"
        dst.merged_from.append(src_id)
        for i, c in enumerate(src.criteria, 1):
            dst.criteria.append(f"CA-{src_id[3:]}-{i:02d}: {c.split(': ', 1)[-1]} (de {src.origin}, fusionada)")
        if dst.dup == src_id:
            dst.dup = ""


def load_refinements(epics: list[Epic], errors: list[str]) -> None:
    by_id = {s.id: s for e in epics for s in stories_of(e)}
    for path in sorted(REFINEMENTS_DIR.glob("US-*.md")) if REFINEMENTS_DIR.exists() else []:
        s = by_id.get(path.stem)
        if s is None or s.merged_into:
            errors.append(f"refinements/{path.name}: historia inexistente o fusionada")
            continue
        current = ""
        for raw in path.read_text(encoding="utf-8").splitlines():
            if raw.startswith("## "):
                current = raw[3:].strip()
                s.refinement.setdefault(current, [])
            elif raw.startswith("Sprint:"):
                s.sprint = raw.split(":", 1)[1].strip()
            elif current and raw.strip():
                s.refinement[current].append(raw.rstrip())
        s.refinement_file = f"refinements/{path.name}"
        extra_ca = s.refinement.pop("Criterios de aceptación", [])
        if extra_ca:
            if s.criteria:
                errors.append(f"refinements/{path.name}: la historia ya tiene criterios en su fuente; no se pueden redefinir")
            for ln in extra_ca:
                m = re.match(r"^- (CA-\d{2}): (.+)$", ln)
                if not m:
                    errors.append(f"refinements/{path.name}: criterio mal formado: {ln!r}")
                    continue
                s.criteria.append(f"{m.group(1)}: {m.group(2)} (definido en refinamiento)")
        unknown = set(s.refinement) - set(READY_SECTIONS)
        if unknown:
            errors.append(f"refinements/{path.name}: secciones desconocidas {sorted(unknown)}")


REPO_ROOT = ROOT.parent
TEST_REF = re.compile(r"`(tests/[\w/]+\.py)::(\w+)`")


def check_test_refs(epics: list[Epic], errors: list[str]) -> int:
    """Trazabilidad historia → test: cada test citado en "Pruebas" debe existir en el repositorio."""
    count = 0
    for s in (s for e in epics for s in stories_of(e) if s.refinement_file):
        for ln in s.refinement.get("Pruebas", []):
            for rel, fn in TEST_REF.findall(ln):
                path = REPO_ROOT / rel
                count += 1
                if not path.is_file() or not re.search(rf"^(async )?def {fn}\(", path.read_text(encoding="utf-8"), re.M):
                    errors.append(f"{s.refinement_file}: test inexistente {rel}::{fn}")
    return count


def missing_sections(s: Story) -> list[str]:
    return [sec for sec in READY_SECTIONS if not s.refinement.get(sec)]


def status_of(s: Story) -> str:
    """Estado efectivo: explícito en item_status.json > fusionada (CANCELLED) > READY calculado > PLANNED."""
    if s.id in STATUS:
        return STATUS[s.id]
    if s.merged_into:
        return "CANCELLED"
    if s.refinement_file and s.criteria and not missing_sections(s):
        return "READY"
    return "PLANNED"


# ------------------------------ Render -------------------------------------
HEADER = (f"<!-- GENERADO por control/tools/derive_backlog.py desde {SRC_A_REL} (A) y {SRC_B_REL} (B). "
          "No editar a mano: editar las fuentes o el mapeo del script y regenerar. -->\n\n")


def stories_of(e: Epic) -> list[Story]:
    return [s for f in e.features for s in f.stories]


def active(stories: list[Story]) -> list[Story]:
    """Historias vivas: excluye las fusionadas por duplicado (sus criterios ya están en la historia destino)."""
    return [s for s in stories if not s.merged_into]


def epic_scope(e: Epic) -> str:
    return "MVP" if any(s.scope == "MVP" for s in stories_of(e)) else "POST-MVP"


def feat_scope(f: Feature) -> str:
    return "MVP" if any(s.scope == "MVP" for s in f.stories) else "POST-MVP"


def origin_label(e: Epic) -> str:
    if e.origin == "ADR-010":
        return "B (nueva, ADR-010)"
    return "A+B" if any(f.origin.startswith("B:") for f in e.features) else "A"


def render_epics(epics: list[Epic]) -> str:
    out = [HEADER, "# Épicas (backlog unificado)\n\n",
           f"Total: **{len(epics)}** · Fuentes: A=`{SRC_A_REL}`, B=`{SRC_B_REL}` · Regla: ADR-010\n\n",
           "| ID | Título | Origen | Alcance | Estado | Features | Historias | CA |\n",
           "|----|--------|--------|---------|--------|----------|-----------|----|\n"]
    for e in epics:
        st = active(stories_of(e))
        out.append(f"| {e.id} | {e.title} | {origin_label(e)} | {epic_scope(e)} | PLANNED | {len(e.features)} | "
                   f"{len(st)} | {sum(len(s.criteria) for s in st)} |\n")
    out.append("\n## Objetivos declarados\n\n")
    for e in epics:
        if e.objective:
            out.append(f"- **{e.id}** — {e.objective}\n")
    missing = [e.id for e in epics if not e.objective]
    out.append(f"\nÉpicas sin objetivo explícito ({len(missing)}): {', '.join(missing)} (GAP-004)\n")
    return "".join(out)


def render_features(epics: list[Epic]) -> str:
    feats = [f for e in epics for f in e.features]
    out = [HEADER, "# Features (backlog unificado)\n\n", f"Total: **{len(feats)}**\n\n",
           "| ID | Épica | Título | Origen | Alcance | Historias |\n",
           "|----|-------|--------|--------|---------|-----------|\n"]
    for e in epics:
        for f in e.features:
            out.append(f"| {f.id} | {e.id} | {f.title} | {f.origin} | {feat_scope(f)} | "
                       f"{', '.join(s.id for s in f.stories)} |\n")
    return "".join(out)


def render_stories(epics: list[Epic]) -> str:
    st = active([s for e in epics for s in stories_of(e)])
    with_ca = sum(1 for s in st if s.criteria)
    out = [HEADER, "# User Stories (backlog unificado)\n\n",
           f"Total activas: **{len(st)}** · Con criterios de aceptación: **{with_ca}** · Sin criterios: **{len(st) - with_ca}** · "
           f"Posibles solapamientos señalados: **{sum(1 for s in st if s.dup)}**\n\n",
           "> READY exige la cadena completa de la *Regla de aceptación del backlog* (fuente A): precondiciones, flujo,\n"
           "> alternativas, errores, reglas, validaciones, casos límite, CA, tareas y pruebas. Se documenta en\n"
           "> `refinements/US-NN.MM.md`; el script calcula READY cuando están todas las secciones y hay CA.\n\n"
           f"READY: **{sum(1 for s in st if status_of(s) == 'READY')}** · Fusionadas (CANCELLED): "
           f"**{sum(1 for s in st if s.merged_into)}**\n\n"]
    for e in epics:
        out.append(f"## {e.id} — {e.title}\n\n")
        for f in e.features:
            out.append(f"### {f.id} — {f.title} · origen {f.origin}\n\n")
            for s in f.stories:
                out.append(f"#### {s.id}{' — ' + s.title if s.title else ''}\n\n")
                if s.quiero:
                    out.append(f"- **Como** {s.como} **quiero** {s.quiero} **para** {s.para}\n")
                else:
                    out.append(f"- Enunciado: {s.text}\n")
                out.append(f"- Origen: {s.origin} · Épica: {e.id} · Feature: {f.id} · Alcance: {s.scope} · "
                           f"Prioridad: {'P1' if s.scope == 'MVP' else ('P3' if s.scope == 'POST-MVP' else '—')} · "
                           f"Estado: {status_of(s)}{' · Sprint: ' + s.sprint if s.sprint else ''}\n")
                if s.merged_into:
                    out.append(f"- Fusionada en {s.merged_into} (duplicado; sus criterios se añadieron allí, GAP-006)\n")
                if s.merged_from:
                    out.append(f"- Absorbe a: {', '.join(s.merged_from)}\n")
                if s.refinement_file:
                    miss = missing_sections(s)
                    out.append(f"- Refinamiento: `{s.refinement_file}` — "
                               + ("completo (regla READY de A)" if not miss else f"faltan: {', '.join(miss)}") + "\n")
                if s.dup:
                    out.append(f"- ⚠ Posible solapamiento con {s.dup}: revisar si es duplicado, detalle o historia distinta (GAP-006)\n")
                for name, lines in s.sections.items():
                    out.append(f"- {name}:\n")
                    out.extend(f"  - {ln.lstrip('*0123456789. ').strip()}\n" for ln in lines)
                if s.criteria:
                    out.append("- Criterios de aceptación:\n")
                    out.extend(f"  - [ ] {c}\n" for c in s.criteria)
                else:
                    out.append("- Criterios de aceptación: MISSING\n")
                out.append("\n")
    return "".join(out)


def render_backlog(epics: list[Epic], techs: list[Item], spikes: list[Item]) -> str:
    all_st = [s for e in epics for s in stories_of(e)]
    st = active(all_st)
    feats = [f for e in epics for f in e.features]

    def cnt(items, pred):
        return sum(1 for x in items if pred(x))

    out = [HEADER, "# Product Backlog unificado (resumen)\n\n",
           "| Tipo | Total | MVP | POST-MVP | Origen A | Origen B |\n|------|-------|-----|----------|----------|----------|\n",
           f"| EPIC | {len(epics)} | {cnt(epics, lambda e: epic_scope(e) == 'MVP')} | "
           f"{cnt(epics, lambda e: epic_scope(e) != 'MVP')} | {cnt(epics, lambda e: e.origin == 'A')} | "
           f"{cnt(epics, lambda e: e.origin != 'A')} nuevas |\n",
           f"| FEATURE | {len(feats)} | {cnt(feats, lambda f: feat_scope(f) == 'MVP')} | "
           f"{cnt(feats, lambda f: feat_scope(f) != 'MVP')} | {cnt(feats, lambda f: f.origin.startswith('A:'))} | "
           f"{cnt(feats, lambda f: f.origin.startswith('B:'))} |\n",
           f"| USER_STORY (activas) | {len(st)} | {cnt(st, lambda s: s.scope == 'MVP')} | "
           f"{cnt(st, lambda s: s.scope == 'POST-MVP')} | "
           f"{cnt(st, lambda s: s.origin.startswith('A:'))} | {cnt(st, lambda s: s.origin.startswith('B:'))} |\n",
           f"| Criterios de aceptación | {sum(len(s.criteria) for s in st)} | — | — | "
           f"{sum(len(s.criteria) for s in st if s.origin.startswith('A:'))} | "
           f"{sum(len(s.criteria) for s in st if s.origin.startswith('B:'))} |\n",
           f"| TECH (historia técnica, B) | {len(techs)} | — | — | — | {len(techs)} |\n",
           f"| SPIKE (B) | {len(spikes)} | — | — | — | {len(spikes)} |\n\n",
           f"Posibles solapamientos B↔A pendientes (heurística Jaccard ≥ {DUP_THRESHOLD}, GAP-006): **{cnt(st, lambda s: bool(s.dup))}** · "
           f"Historias fusionadas por duplicado (`tools/dedupe.json`): **{cnt(all_st, lambda s: bool(s.merged_into))}** · "
           f"READY: **{cnt(st, lambda s: status_of(s) == 'READY')}**.\n",
           "Correspondencia de IDs de la definición v1.1: `id_mapping.md`. Alcance MVP: ADR-010.\n\n",
           "## Historias MVP por épica\n\n"]
    for e in epics:
        ids = [s.id for s in stories_of(e) if s.scope == "MVP"]
        if ids:
            out.append(f"- **{e.id}** ({len(ids)}): {', '.join(ids)}\n")
    return "".join(out)


def render_tech(techs: list[Item], spikes: list[Item]) -> str:
    out = [HEADER, "# Historias técnicas transversales y Spikes (fuente B)\n\n",
           "> Los IDs `TECH-XXX` designan **historias técnicas**, no deuda técnica (la deuda usa `TD-NNN`, ADR-002).\n\n",
           "## Historias técnicas\n\n| ID | Título | Descripción | Estado |\n|----|--------|-------------|--------|\n"]
    out.extend(f"| {t.id} | {t.title} | {t.description} | {STATUS.get(t.id, 'PLANNED')} |\n" for t in techs)
    out.append("\n## Spikes\n\n| ID | Título | Pregunta | Estado |\n|----|--------|----------|--------|\n")
    out.extend(f"| {s.id} | {s.title} | {s.description} | {STATUS.get(s.id, 'PLANNED')} |\n" for s in spikes)
    return "".join(out)


def render_mapping(b_epics: list[Epic], mapping: list[tuple[str, str, str]]) -> str:
    out = [HEADER, "# Correspondencia de IDs: definición v1.1 (B) → backlog unificado\n\n",
           "Los IDs de la fuente A no cambian. Los documentos de `control/` anteriores a ADR-010 (p. ej. ADR-003..009)\n"
           "usan la numeración de B: tradúcelos con esta tabla (notación `B:US-15.09`).\n\n",
           "## Épicas de B → épicas unificadas que reciben sus features\n\n"
           "| Épica B | Título B | Destino(s) |\n|---------|----------|------------|\n"]
    for e in b_epics:
        dest = sorted({FEATURE_MAP[f.id] for f in e.features})
        out.append(f"| {e.id} | {e.title} | {', '.join(f'EPIC-{d:02d}' for d in dest)} |\n")
    out.append("\n## Features\n\n| ID B | ID unificado |\n|------|--------------|\n")
    out.extend(f"| {b} | {u} |\n" for t, b, u in mapping if t == "FEAT")
    out.append("\n## Historias\n\n| ID B | ID unificado |\n|------|--------------|\n")
    out.extend(f"| {b} | {u} |\n" for t, b, u in mapping if t == "US")
    return "".join(out)


def main() -> int:
    check = "--check" in sys.argv[1:]
    a_epics = parse_a(SRC_A.read_text(encoding="utf-8"))
    b_epics, techs, spikes = parse_b(SRC_B.read_text(encoding="utf-8"))
    epics, mapping, errors = unify(a_epics, b_epics)
    apply_dedupe(epics, errors)
    load_refinements(epics, errors)
    test_refs = check_test_refs(epics, errors)
    STATUS.update(json.loads(STATUS_FILE.read_text(encoding="utf-8")))
    known = {s.id for e in epics for s in stories_of(e)} | {t.id for t in techs} | {s.id for s in spikes}
    for ident, st in STATUS.items():
        if ident not in known:
            errors.append(f"item_status.json: {ident} no existe en el backlog")
        if st not in ALLOWED_STATUS:
            errors.append(f"item_status.json: estado no permitido {st!r} para {ident}")
    if len(a_epics) != 48:
        errors.append(f"fuente A: se esperaban 48 épicas, hay {len(a_epics)}")
    if errors:
        print("ERRORES DE INTEGRIDAD:\n  " + "\n  ".join(errors), file=sys.stderr)
        return 2
    outputs = {
        "epics.md": render_epics(epics),
        "features.md": render_features(epics),
        "user_stories.md": render_stories(epics),
        "backlog.md": render_backlog(epics, techs, spikes),
        "technical_stories.md": render_tech(techs, spikes),
        "id_mapping.md": render_mapping(b_epics, mapping),
    }
    stale = []
    for name, content in outputs.items():
        path = OUT_DIR / name
        if check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                stale.append(name)
        else:
            path.write_text(content, encoding="utf-8")
    all_st = [s for e in epics for s in stories_of(e)]
    st = active(all_st)
    print(f"epics={len(epics)} features={sum(len(e.features) for e in epics)} stories={len(st)} "
          f"(A={sum(1 for s in st if s.origin.startswith('A:'))} B={sum(1 for s in st if s.origin.startswith('B:'))}) "
          f"criteria={sum(len(s.criteria) for s in st)} mvp={sum(1 for s in st if s.scope == 'MVP')} "
          f"overlaps={sum(1 for s in st if s.dup)} merged={sum(1 for s in all_st if s.merged_into)} "
          f"ready={sum(1 for s in st if status_of(s) == 'READY')} test_refs={test_refs} tech={len(techs)} "
          f"spikes={len(spikes)}")
    if stale:
        print("DESINCRONIZADOS: " + ", ".join(stale), file=sys.stderr)
        return 1
    print("OK" + (" (check)" if check else " (regenerado)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
