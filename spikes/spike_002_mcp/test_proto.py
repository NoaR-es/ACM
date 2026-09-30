"""SPIKE-002 — Pruebas del prototipo con el cliente oficial del SDK (conexión en proceso).

Ejecutar:  spikes/.venv/bin/python spikes/spike_002_mcp/test_proto.py
Cada comprobación imprime PASS/FAIL; el proceso termina con código 1 si alguna falla.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import sys
from typing import Any, Literal

from pydantic import TypeAdapter

from mcp import Client
from mcp.shared.exceptions import MCPError
from mcp_types import Request

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from acm_mcp_proto import SKILLS_EXTENSION, SkillsGetParams, SkillsListParams, build_server  # noqa: E402

RESULTS: list[tuple[str, bool, str]] = []
INFO: list[str] = []


def check(name: str, cond: bool, detail: Any = "") -> None:
    RESULTS.append((name, bool(cond), str(detail)[:300]))


class SkillsListRequest(Request[SkillsListParams, Literal["skills/list"]]):
    method: Literal["skills/list"] = "skills/list"
    params: SkillsListParams = SkillsListParams()


class SkillsGetRequest(Request[SkillsGetParams, Literal["skills/get"]]):
    method: Literal["skills/get"] = "skills/get"
    params: SkillsGetParams


ANY = TypeAdapter(dict[str, Any])


async def main() -> None:
    server = build_server()
    async with Client(server) as client:
        # 1. instructions en la conexión
        check("instructions anunciadas al conectar", client.instructions and "skills" in client.instructions,
              client.instructions)
        # 2. capacidades
        caps = client.server_capabilities
        ext = (caps.extensions or {}) if hasattr(caps, "extensions") else {}
        check("capabilities.extensions incluye io.modelcontextprotocol/skills", SKILLS_EXTENSION in ext, ext)
        check("capabilities.resources declarada", caps.resources is not None, caps.resources)
        INFO.append(f"versión de protocolo negociada: {getattr(client.session, 'protocol_version', '?')}")
        # 3. skills/list
        listed = await client.session.send_request(SkillsListRequest(), ANY)
        names = sorted(s["frontmatter"]["name"] for s in listed["skills"])
        check("skills/list devuelve las skills", names == ["acm-invest", "acm-schema"], names)
        check("skills/list: cada recurso con digest sha256 y size",
              all(r["digest"].startswith("sha256:") and r["size"] > 0 for s in listed["skills"] for r in s["resources"]),
              json.dumps(listed["skills"][0]["resources"]))
        # 4. descargar cada archivo con resources/read y verificar el digest
        ok_digest = True
        for s in listed["skills"]:
            for r in s["resources"]:
                rr = await client.read_resource(r["uri"])
                text = rr.contents[0].text
                if "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest() != r["digest"]:
                    ok_digest = False
        check("resources/read de cada archivo skill:// coincide con su digest", ok_digest)
        # 5. skills/get válido e inexistente
        got = await client.session.send_request(
            SkillsGetRequest(params=SkillsGetParams(uri="skill://acm/acm-schema/SKILL.md")), ANY)
        check("skills/get devuelve la skill pedida", got["skill"]["frontmatter"]["name"] == "acm-schema", got["skill"]["uri"])
        try:
            await client.session.send_request(
                SkillsGetRequest(params=SkillsGetParams(uri="skill://acm/no-existe/SKILL.md")), ANY)
            check("skills/get de skill inexistente devuelve -32602", False, "no error")
        except MCPError as e:
            check("skills/get de skill inexistente devuelve -32602", e.code == -32602, f"{e.code} {e.message}")
        # 6. herramientas de respaldo
        tools = sorted(t.name for t in (await client.list_tools()).tools)
        check("herramientas de respaldo publicadas", {"acm_skill_get", "acm_skills_list"} <= set(tools), tools)
        res = await client.call_tool("acm_skill_get", {"name": "acm-invest"})
        payload = res.structured_content or json.loads(res.content[0].text)
        payload = payload.get("result", payload)
        check("acm_skill_get devuelve los archivos de la skill",
              "skill://acm/acm-invest/SKILL.md" in payload.get("files", {}), list(payload.get("files", {})))


async def stdio_check() -> None:
    from mcp import StdioServerParameters
    proto = str(__import__("pathlib").Path(__file__).resolve().parent / "acm_mcp_proto.py")
    async with Client(StdioServerParameters(command=sys.executable, args=[proto])) as client:
        listed = await client.session.send_request(SkillsListRequest(), ANY)
        check("transporte stdio: conecta, instructions y skills/list",
              bool(client.instructions) and len(listed["skills"]) == 2, len(listed["skills"]))


if __name__ == "__main__":
    asyncio.run(main())
    asyncio.run(stdio_check())
    for name, ok, detail in RESULTS:
        print(f"{'PASS' if ok else 'FAIL'}  {name}  {('— ' + detail) if detail else ''}")
    for line in INFO:
        print(f"INFO  {line}")
    failed = sum(1 for _, ok, _ in RESULTS if not ok)
    print(f"\n{len(RESULTS) - failed}/{len(RESULTS)} PASS")
    sys.exit(1 if failed else 0)
