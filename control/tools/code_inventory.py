#!/usr/bin/env python3
"""Inventario de código de ACM → `control/05_CODIGO/code_reference.md` (generado; no editar a mano).

Recorre el código real:
- Python (`src/acm`, `tests`, `control/tools`) con `ast`: módulos, clases (métodos públicos), funciones (firma y primera
  línea del docstring), constantes, herramientas MCP (`@server.tool()`) y rutas REST (`@r.get/post(...)`).
- TypeScript (`web/src`): exportaciones (componentes, hooks, funciones, tipos, constantes) y el comentario inicial.

Con `--check` comprueba que el archivo generado está al día y que **cada archivo de código tiene su entrada en
`05_CODIGO/file_inventory.md`** (regla del operador, SPRINT-007: el control del código se mantiene con el código) y
**una cabecera que diga para qué existe** (docstring de módulo en Python, comentario en la primera línea en TypeScript;
convenciones en `05_CODIGO/file_documentation.md`).
Uso: `python3 control/tools/code_inventory.py [--check]`.
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "control" / "05_CODIGO" / "code_reference.md"
INVENTORY = ROOT / "control" / "05_CODIGO" / "file_inventory.md"
PY_DIRS = ("src/acm", "tests", "control/tools")
TS_DIR = "web/src"
SKIP_PARTS = {"__pycache__", "webui", "node_modules"}
HEADER = (
    "<!-- GENERADO por control/tools/code_inventory.py a partir del código. No editar a mano: "
    "cambia el código (y sus docstrings) y regenera. -->\n\n"
)


def rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


def first_line(doc: str | None) -> str:
    return (doc or "").strip().split("\n")[0].strip().replace("|", "/")


def signature(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    args = [a.arg for a in fn.args.posonlyargs + fn.args.args if a.arg not in ("self", "cls")]
    if fn.args.vararg:
        args.append("*" + fn.args.vararg.arg)
    elif fn.args.kwonlyargs:
        args.append("*")
    args += [a.arg for a in fn.args.kwonlyargs]
    if fn.args.kwarg:
        args.append("**" + fn.args.kwarg.arg)
    prefix = "async " if isinstance(fn, ast.AsyncFunctionDef) else ""
    return f"{prefix}{fn.name}({', '.join(args)})"


def decorator_route(fn: ast.AST) -> tuple[str, str] | None:
    for d in getattr(fn, "decorator_list", []):
        if isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute):
            attr = d.func.attr
            if attr == "tool":
                return ("mcp", fn.name)  # type: ignore[attr-defined]
            if attr in ("get", "post", "put", "delete", "websocket") and d.args and isinstance(d.args[0], ast.Constant):
                return (attr.upper(), str(d.args[0].value))
    return None


def python_file(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out = [f"### `{rel(path)}`\n\n{first_line(ast.get_docstring(tree)) or '_(sin docstring de módulo)_'}\n\n"]
    rows: list[str] = []
    tools: list[str] = []
    routes: list[str] = []
    tests: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            methods = [
                n
                for n in node.body
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                and (not n.name.startswith("_") or n.name == "__init__")
            ]
            bases = ", ".join(ast.unparse(b) for b in node.bases) or "—"
            rows.append(f"| clase | `{node.name}` ({bases}) | {node.lineno} | {first_line(ast.get_docstring(node))} |")
            for m in methods:
                doc = first_line(ast.get_docstring(m))
                rows.append(f"| método | `{node.name}.{signature(m)}` | {m.lineno} | {doc} |")
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith("test_"):
                tests.append(node.name)
                continue
            rows.append(f"| función | `{signature(node)}` | {node.lineno} | {first_line(ast.get_docstring(node))} |")
            for inner in ast.walk(node):
                if inner is node or not isinstance(inner, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                route = decorator_route(inner)
                if route and route[0] == "mcp":
                    tools.append(f"| `{inner.name}` | {inner.lineno} | {first_line(ast.get_docstring(inner))} |")
                elif route:
                    routes.append(
                        f"| {route[0]} | `{route[1]}` | `{inner.name}` | {inner.lineno} | "
                        f"{first_line(ast.get_docstring(inner))} |"
                    )
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for t in targets:
                if isinstance(t, ast.Name) and re.fullmatch(r"[A-Z][A-Z0-9_]+", t.id):
                    rows.append(f"| constante | `{t.id}` | {node.lineno} | |")
    if rows:
        out.append("| Tipo | Nombre | Línea | Descripción |\n|------|--------|-------|-------------|\n")
        out.append("\n".join(rows) + "\n\n")
    if tools:
        out.append(
            f"Herramientas MCP ({len(tools)}):\n\n| Herramienta | Línea | Descripción |\n"
            "|-------------|-------|-------------|\n" + "\n".join(tools) + "\n\n"
        )
    if routes:
        out.append(
            f"Rutas ({len(routes)}, relativas a su montaje):\n\n"
            "| Método | Ruta | Función | Línea | Descripción |\n"
            "|--------|------|---------|-------|-------------|\n" + "\n".join(routes) + "\n\n"
        )
    if tests:
        out.append(f"Tests ({len(tests)}): " + ", ".join(f"`{t}`" for t in tests) + "\n\n")
    return out


TS_EXPORT = re.compile(
    r"^export\s+(?:default\s+)?(async\s+)?(function|const|class|type|interface)\s+([A-Za-z_][A-Za-z0-9_]*)", re.M
)


def ts_kind(kind: str, name: str, path: Path) -> str:
    if kind in ("type", "interface"):
        return "tipo"
    if name.startswith("use") and name[3:4].isupper():
        return "hook"
    if kind == "function" and name[:1].isupper() and path.suffix == ".tsx":
        return "componente"
    if kind == "class":
        return "clase"
    return "función" if kind == "function" else "constante"


def ts_file(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    purpose = next((ln.lstrip("/ ").strip() for ln in lines[:3] if ln.startswith("//")), "")
    out = [f"### `{rel(path)}`\n\n{purpose or '_(sin comentario inicial)_'}\n\n"]
    rows = []
    for m in TS_EXPORT.finditer(text):
        line = text.count("\n", 0, m.start()) + 1
        rows.append(f"| {ts_kind(m.group(2), m.group(3), path)} | `{m.group(3)}` | {line} |")
    tests = re.findall(r"^\s*it\(\s*[`\"'](.+?)[`\"']", text, re.M)
    if rows:
        out.append("| Tipo | Nombre | Línea |\n|------|--------|-------|\n" + "\n".join(rows) + "\n\n")
    if tests:
        out.append(f"Tests ({len(tests)}): " + "; ".join(tests) + "\n\n")
    return out


def code_files() -> list[Path]:
    files: list[Path] = []
    for d in PY_DIRS:
        files += [p for p in (ROOT / d).rglob("*.py") if not SKIP_PARTS & set(p.parts)]
    files += [p for p in (ROOT / TS_DIR).rglob("*") if p.suffix in (".ts", ".tsx") and not SKIP_PARTS & set(p.parts)]
    return sorted(files)


def render() -> str:
    files = code_files()
    out = [
        HEADER,
        "# Referencia de código (generada)\n\n",
        f"{len(files)} archivos. Documentación narrativa (responsabilidades, invariantes, efectos): "
        "`modules.md`, `services.md`, `classes.md`, `functions.md`, `components.md`, `hooks.md`, `frontend.md`, "
        "`tests.md`.\n\n",
    ]
    sections = {
        "src/acm": "## Backend (`src/acm`)\n\n",
        "web/src": "## Frontend (`web/src`)\n\n",
        "tests": "## Tests (`tests`)\n\n",
        "control/tools": "## Herramientas de control (`control/tools`)\n\n",
    }
    for prefix, title in sections.items():
        out.append(title)
        for p in files:
            if rel(p).startswith(prefix + "/"):
                out += python_file(p) if p.suffix == ".py" else ts_file(p)
    return "".join(out)


def undocumented() -> list[str]:
    inventory = INVENTORY.read_text(encoding="utf-8")
    return [rel(p) for p in code_files() if f"`{rel(p)}`" not in inventory and p.name != "__init__.py"]


def headerless() -> list[str]:
    out = []
    for p in code_files():
        if p.name == "__init__.py":
            continue
        text = p.read_text(encoding="utf-8")
        ok = bool(ast.get_docstring(ast.parse(text))) if p.suffix == ".py" else text.startswith(("//", "/*"))
        if not ok:
            out.append(rel(p))
    return out


def main() -> int:
    content = render()
    missing = undocumented()
    if "--check" in sys.argv[1:]:
        errors = []
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != content:
            errors.append(f"{rel(OUT)} desactualizado: ejecuta python3 control/tools/code_inventory.py")
        errors += [f"sin entrada en 05_CODIGO/file_inventory.md: {m}" for m in missing]
        errors += [f"sin cabecera (docstring o comentario inicial): {m}" for m in headerless()]
        if errors:
            print("ERRORES:\n  " + "\n  ".join(errors), file=sys.stderr)
            return 1
        print(f"OK (check): {len(code_files())} archivos inventariados")
        return 0
    OUT.write_text(content, encoding="utf-8")
    print(f"OK (regenerado): {len(code_files())} archivos")
    if missing:
        print("Sin entrada en file_inventory.md:\n  " + "\n  ".join(missing), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
