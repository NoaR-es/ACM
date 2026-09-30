#!/usr/bin/env python3
"""Genera la matriz de evidencia criterio de aceptación ↔ test de un sprint.

Fuentes: los criterios del backlog unificado (derive_backlog.py), las secciones *Pruebas* de los refinamientos
de las historias con `Sprint: <id>` y un informe JUnit de pytest (`pytest --junitxml=...`).

Uso:
    .venv/bin/pytest -q --junitxml=/tmp/junit.xml
    python3 control/tools/evidence.py SPRINT-002 /tmp/junit.xml > control/12_TESTING/sprint_002_evidence.md

Sale con código 1 si algún test citado falló o no aparece en el informe (la matriz se escribe igualmente).
"""

from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import derive_backlog as db  # noqa: E402

REF_LINE = re.compile(r"`tests/([\w/]+)\.py::(\w+)`\s*(?:\(([^)]*)\))?")
PENDING_LINE = re.compile(r"^- (CA-[\d.-]+): PENDIENTE\s*(.*)$")
CA_CODE = re.compile(r"CA-[\d.-]*\d")


def junit_results(path: Path) -> tuple[dict[str, str], int]:
    """({'módulo::test': 'PASS'|'FAIL'|'SKIP'}, nº de casos). Un test parametrizado falla si falla un caso."""
    out: dict[str, str] = {}
    cases = list(ET.parse(path).getroot().iter("testcase"))
    for case in cases:
        module = case.get("classname", "").rsplit(".", 1)[-1]
        name = case.get("name", "").split("[", 1)[0]
        key = f"{module}::{name}"
        if case.find("failure") is not None or case.find("error") is not None:
            out[key] = "FAIL"
        elif case.find("skipped") is not None:
            out.setdefault(key, "SKIP")
        else:
            out.setdefault(key, "PASS")
    return out, len(cases)


def main(sprint: str, junit: Path) -> int:
    a_epics = db.parse_a(db.SRC_A.read_text(encoding="utf-8"))
    b_epics, _, _ = db.parse_b(db.SRC_B.read_text(encoding="utf-8"))
    epics, _, errors = db.unify(a_epics, b_epics)
    db.apply_dedupe(epics, errors)
    db.load_refinements(epics, errors)
    if errors:
        print("ERRORES DE INTEGRIDAD:\n  " + "\n  ".join(errors), file=sys.stderr)
        return 2
    results, n_cases = junit_results(junit)
    stories = sorted((s for e in epics for s in db.stories_of(e) if s.sprint == sprint), key=lambda s: s.id)
    out = [
        f"# Evidencia de {sprint} — criterios de aceptación ↔ tests\n\n",
        f"Generado el {date.today().isoformat()} por `control/tools/evidence.py` a partir de `pytest --junitxml` "
        f"({n_cases} casos) y de las secciones *Pruebas* de `01_PRODUCTO/refinements/`.\n",
        "Instantánea: se regenera al cerrar el sprint.\n",
    ]
    bad = 0
    for s in stories:
        by_ca: dict[str, list[str]] = {}
        extra: list[tuple[str, str]] = []
        pending: dict[str, str] = {}
        for ln in s.refinement.get("Pruebas", []):
            if m := PENDING_LINE.match(ln.strip()):
                pending[m.group(1)] = m.group(2).strip()
                continue
            for mod, fn, label in REF_LINE.findall(ln):
                key = f"{mod.rsplit('/', 1)[-1]}::{fn}"
                codes = CA_CODE.findall(label or "")
                for code in codes:
                    by_ca.setdefault(code, []).append(key)
                if not codes:
                    extra.append((label or "—", key))

        def verdict(keys: list[str]) -> str:
            nonlocal bad
            states = [results.get(k, "AUSENTE") for k in keys]
            if all(st == "PASS" for st in states):
                return "PASS"
            bad += 1
            return " / ".join(sorted(set(states)))

        out.append(f"\n## {s.id}\n\n| CA | Criterio | Tests | Resultado |\n|----|----------|-------|-----------|\n")
        for crit in s.criteria:
            code, _, text = crit.partition(": ")
            keys = by_ca.get(code, [])
            tests = "<br>".join(f"`{k}`" for k in keys) or "—"
            if keys:
                res = verdict(keys)
            elif code in pending:
                res = f"PENDIENTE {pending[code]}".strip()
            else:
                res = "SIN TEST"
            out.append(f"| {code} | {text.replace('|', '/')} | {tests} | {res} |\n")
        for label, key in extra:
            out.append(f"| — | {label} | `{key}` | {verdict([key])} |\n")
    sys.stdout.write("".join(out))
    return 1 if bad else 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1], Path(sys.argv[2])))
