"""Catálogo de skills oficiales de ACM (ADR-008; US-15.01, US-15.06, US-15.07).

Las skills viven como archivos versionados con el código (`src/acm/skills/<nombre>/SKILL.md`) y se sirven por
MCP con la extensión Skills (SEP-2640). Una skill inválida no se activa: queda en `rejected` con su motivo.

Frontmatter admitido (subconjunto de YAML): `clave: valor` y listas en línea `clave: [a, b]`.
Obligatorio: `name` (= carpeta), `description`, `version` (semver), `capabilities` (lista no vacía),
`dependencies` (lista, puede ser vacía, de otras skills del catálogo).
"""

from __future__ import annotations

import hashlib
import re
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SKILL_PREFIX = "skill://acm"
DEFAULT_ROOT = Path(__file__).resolve().parent / "skills"
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
FILE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
MAX_FILES = 512  # SEP-2640
MAX_BYTES = 16 * 1024 * 1024  # SEP-2640


@dataclass(frozen=True)
class SkillFile:
    name: str
    uri: str
    text: str
    digest: str
    size: int


@dataclass(frozen=True)
class Skill:
    name: str
    frontmatter: dict[str, Any]
    files: tuple[SkillFile, ...]

    @property
    def uri(self) -> str:
        return f"{SKILL_PREFIX}/{self.name}/SKILL.md"

    def entry(self) -> dict[str, Any]:
        return {
            "uri": self.uri,
            "frontmatter": self.frontmatter,
            "resources": [{"uri": f.uri, "digest": f.digest, "size": f.size} for f in self.files],
        }


class SkillError(ValueError):
    pass


def parse_frontmatter(text: str) -> dict[str, Any]:
    if not text.startswith("---\n") or "\n---" not in text[4:]:
        raise SkillError("SKILL.md debe empezar con un bloque de frontmatter YAML delimitado por ---")
    block = text[4 : text.index("\n---", 4)]
    out: dict[str, Any] = {}
    for line in block.splitlines():
        if not line.strip():
            continue
        key, sep, value = line.partition(":")
        if not sep or not key.strip():
            raise SkillError(f"línea de frontmatter inválida: {line!r}")
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            out[key.strip()] = [v.strip() for v in value[1:-1].split(",") if v.strip()]
        else:
            out[key.strip()] = value
    return out


def _load_one(directory: Path) -> Skill:
    name = directory.name
    if not NAME_RE.match(name):
        raise SkillError(f"nombre de carpeta inválido: {name!r}")
    skill_md = directory / "SKILL.md"
    if not skill_md.is_file():
        raise SkillError("falta SKILL.md")
    fm = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
    if fm.get("name") != name:
        raise SkillError("'name' del frontmatter debe coincidir con la carpeta")
    if not isinstance(fm.get("description"), str) or not fm["description"]:
        raise SkillError("'description' es obligatoria")
    if not isinstance(fm.get("version"), str) or not SEMVER_RE.match(fm["version"]):
        raise SkillError("'version' es obligatoria con formato semver (X.Y.Z)")
    if not isinstance(fm.get("capabilities"), list) or not fm["capabilities"]:
        raise SkillError("'capabilities' debe ser una lista no vacía")
    if not isinstance(fm.get("dependencies"), list):
        raise SkillError("'dependencies' debe ser una lista (puede estar vacía: [])")
    paths = sorted(p for p in directory.iterdir())
    if any(p.is_dir() for p in paths):
        raise SkillError("solo se admiten archivos en la raíz de la skill (sin subcarpetas)")
    if len(paths) > MAX_FILES:
        raise SkillError(f"más de {MAX_FILES} archivos")
    files, total = [], 0
    for p in paths:
        if not FILE_RE.match(p.name):
            raise SkillError(f"nombre de archivo inválido: {p.name!r}")
        data = p.read_bytes()
        total += len(data)
        files.append(
            SkillFile(
                p.name,
                f"{SKILL_PREFIX}/{name}/{p.name}",
                data.decode("utf-8"),
                "sha256:" + hashlib.sha256(data).hexdigest(),
                len(data),
            )
        )
    if total > MAX_BYTES:
        raise SkillError(f"supera {MAX_BYTES} bytes")
    return Skill(name, fm, tuple(files))


class SkillCatalog:
    def __init__(self, root: Path | str = DEFAULT_ROOT):
        self.root = Path(root)
        self._lock = threading.Lock()
        self.skills: dict[str, Skill] = {}
        self.rejected: dict[str, str] = {}
        self.reload()

    def _scan(self) -> tuple[dict[str, Skill], dict[str, str]]:
        loaded: dict[str, Skill] = {}
        rejected: dict[str, str] = {}
        if self.root.is_dir():
            for d in sorted(p for p in self.root.iterdir() if p.is_dir() and not p.name.startswith((".", "_"))):
                try:
                    loaded[d.name] = _load_one(d)
                except (SkillError, UnicodeDecodeError, OSError) as exc:
                    rejected[d.name] = str(exc)
        # Dependencias: se descartan en cascada las skills que dependen de otras no activas.
        changed = True
        while changed:
            changed = False
            for name, skill in list(loaded.items()):
                missing = [d for d in skill.frontmatter["dependencies"] if d not in loaded]
                if missing:
                    rejected[name] = f"dependencias no disponibles: {missing}"
                    del loaded[name]
                    changed = True
        return loaded, rejected

    def reload(self) -> bool:
        """Relee el catálogo. Devuelve True si cambió el conjunto de skills o de digests (US-15.06)."""
        skills, rejected = self._scan()
        with self._lock:
            before = {n: [f.digest for f in s.files] for n, s in self.skills.items()}
            after = {n: [f.digest for f in s.files] for n, s in skills.items()}
            self.skills, self.rejected = skills, rejected
        return before != after

    def get_by_uri(self, uri: str) -> Skill | None:
        with self._lock:
            return next((s for s in self.skills.values() if s.uri == uri), None)

    def file(self, name: str, filename: str) -> SkillFile | None:
        with self._lock:
            skill = self.skills.get(name)
        return next((f for f in skill.files if f.name == filename), None) if skill else None

    def entries(self) -> list[dict[str, Any]]:
        with self._lock:
            return [s.entry() for s in self.skills.values()]
