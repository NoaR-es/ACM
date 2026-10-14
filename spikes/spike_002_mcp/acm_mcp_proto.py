"""SPIKE-002 — Prototipo del servidor MCP propio de ACM con la extensión MCP Skills (SEP-2640).

No es código de producto: valida con el SDK oficial `mcp` 2.2.0 que ACM puede
  1. anunciar `instructions` en la conexión,
  2. declarar la extensión `io.modelcontextprotocol/skills` en sus capacidades,
  3. servir `skills/list` y `skills/get` y los archivos de cada skill como recursos `skill://acm/...`,
  4. ofrecer herramientas de respaldo para clientes sin la extensión,
  5. convivir en un solo proceso ASGI con una API HTTP y un WebSocket (ver asgi_app.py).
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from mcp.server.extension import Extension, MethodBinding, ResourceBinding
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.resources.types import TextResource
from mcp.shared.exceptions import MCPError
from mcp_types import RequestParams
from mcp_types.jsonrpc import INVALID_PARAMS

SKILLS_EXTENSION = "io.modelcontextprotocol/skills"
SKILL_PREFIX = "skill://acm"
SKILLS_DIR = Path(__file__).resolve().parent / "skills"

INSTRUCTIONS = (
    "Eres un agente conectado a ACM (Agile Context Manager). Antes de operar, descarga y carga TODAS las "
    "skills de ACM: si tu cliente soporta la extensión io.modelcontextprotocol/skills usa skills/list y "
    "resources/read; si no, usa las herramientas acm_skills_list y acm_skill_get. Selecciona siempre el "
    "proyecto de forma explícita."
)


@dataclass(frozen=True)
class SkillFile:
    uri: str
    text: str
    digest: str
    size: int


@dataclass(frozen=True)
class Skill:
    name: str
    frontmatter: dict[str, str]
    files: tuple[SkillFile, ...]

    @property
    def uri(self) -> str:
        return f"{SKILL_PREFIX}/{self.name}/SKILL.md"

    def entry(self) -> dict[str, Any]:
        return {"uri": self.uri, "frontmatter": self.frontmatter,
                "resources": [{"uri": f.uri, "digest": f.digest, "size": f.size} for f in self.files]}


def parse_frontmatter(text: str) -> dict[str, str]:
    """Frontmatter YAML mínimo (clave: valor en una línea), suficiente para el spike."""
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md debe empezar con frontmatter YAML")
    block = text[4:text.index("\n---", 4)]
    out: dict[str, str] = {}
    for line in block.splitlines():
        key, _, value = line.partition(":")
        out[key.strip()] = value.strip()
    return out


def load_skills(root: Path = SKILLS_DIR) -> dict[str, Skill]:
    skills: dict[str, Skill] = {}
    for skill_md in sorted(root.glob("*/SKILL.md")):
        name = skill_md.parent.name
        fm = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
        if fm.get("name") != name or not fm.get("description"):
            raise ValueError(f"{skill_md}: 'name' debe coincidir con la carpeta y 'description' es obligatoria")
        files = []
        for path in sorted(p for p in skill_md.parent.rglob("*") if p.is_file()):
            data = path.read_bytes()
            rel = path.relative_to(skill_md.parent).as_posix()
            files.append(SkillFile(f"{SKILL_PREFIX}/{name}/{rel}", data.decode("utf-8"),
                                   "sha256:" + hashlib.sha256(data).hexdigest(), len(data)))
        skills[name] = Skill(name, fm, tuple(files))
    return skills


class SkillsListParams(RequestParams):
    pass


class SkillsGetParams(RequestParams):
    uri: str


class SkillsExtension(Extension):
    identifier = SKILLS_EXTENSION

    def __init__(self, skills: dict[str, Skill]):
        self._skills = skills
        self._by_uri = {s.uri: s for s in skills.values()}

    def settings(self) -> dict[str, Any]:
        return {"directoryRead": False}

    def resources(self) -> list[ResourceBinding]:
        return [ResourceBinding(TextResource(uri=f.uri, name=f.uri.removeprefix(SKILL_PREFIX + "/"),
                                             mime_type="text/markdown", text=f.text))
                for s in self._skills.values() for f in s.files]

    def methods(self) -> list[MethodBinding]:
        return [MethodBinding("skills/list", SkillsListParams, self._list),
                MethodBinding("skills/get", SkillsGetParams, self._get)]

    async def _list(self, ctx: Any, params: SkillsListParams) -> dict[str, Any]:
        return {"resultType": "complete", "skills": [s.entry() for s in self._skills.values()],
                "ttlMs": 300000, "cacheScope": "public"}

    async def _get(self, ctx: Any, params: SkillsGetParams) -> dict[str, Any]:
        skill = self._by_uri.get(params.uri)
        if skill is None:
            raise MCPError(INVALID_PARAMS, f"Unknown skill: {params.uri}")
        return {"resultType": "complete", "skill": skill.entry(), "ttlMs": 300000, "cacheScope": "public"}


def build_server(skills: dict[str, Skill] | None = None) -> MCPServer:
    skills = load_skills() if skills is None else skills
    server = MCPServer(name="acm", version="0.0.0-spike", instructions=INSTRUCTIONS,
                       extensions=[SkillsExtension(skills)])

    @server.tool()
    def acm_skills_list() -> list[dict[str, Any]]:
        """Respaldo para clientes sin la extensión Skills: lista las skills de ACM con digest y tamaño."""
        return [s.entry() for s in skills.values()]

    @server.tool()
    def acm_skill_get(name: str) -> dict[str, Any]:
        """Respaldo para clientes sin la extensión Skills: devuelve todos los archivos de una skill."""
        if name not in skills:
            raise ValueError(f"Unknown skill: {name}")
        s = skills[name]
        return {"frontmatter": s.frontmatter, "files": {f.uri: f.text for f in s.files}}

    return server


if __name__ == "__main__":
    # Transporte stdio: así lanza el servidor un cliente MCP local (p. ej. un agente en terminal).
    build_server().run()
