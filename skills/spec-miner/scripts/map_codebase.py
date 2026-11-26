#!/usr/bin/env python3
"""Extract a structural map from a codebase: modules, exports, and edges.

Static, stdlib-only. Emits JSON describing files, their top-level
definitions, and import edges so a spec can be written from evidence
rather than from guesswork.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
from pathlib import Path

SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "dist",
    "build", ".mypy_cache", ".pytest_cache", "target", "vendor",
}
PY_EXT = {".py"}
JS_EXT = {".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx"}
IMPORT_RE = {
    ".py": re.compile(r"^\s*(?:from\s+([\w.]+)\s+import|import\s+([\w.]+))", re.M),
    ".js": re.compile(r"""(?:from\s+['"]([^'"]+)['"]|require\(\s*['"]([^'"]+)['"]\s*\))"""),
    ".ts": re.compile(r"""(?:from\s+['"]([^'"]+)['"]|require\(\s*['"]([^'"]+)['"]\s*\))"""),
}


def py_defs(text: str) -> list[dict]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    out = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out.append({"kind": "function", "name": node.name, "line": node.lineno})
        elif isinstance(node, ast.ClassDef):
            methods = [
                n.name for n in node.body
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]
            out.append(
                {"kind": "class", "name": node.name, "line": node.lineno, "methods": methods}
            )
    return out


def imports_of(path: Path, text: str) -> list[str]:
    ext = path.suffix
    pat = IMPORT_RE.get(ext)
    if not pat:
        return []
    found = []
    for m in pat.finditer(text):
        spec = m.group(1) or m.group(2)
        if spec:
            found.append(spec)
    return sorted(set(found))


def scan(root: Path) -> dict:
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            p = Path(dirpath) / fn
            if p.suffix not in (PY_EXT | JS_EXT):
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            rel = str(p.relative_to(root))
            files.append(
                {
                    "path": rel,
                    "language": p.suffix.lstrip("."),
                    "lines": text.count("\n") + 1,
                    "defs": py_defs(text) if p.suffix in PY_EXT else [],
                    "imports": imports_of(p, text),
                }
            )
    return {
        "root": str(root),
        "file_count": len(files),
        "total_lines": sum(f["lines"] for f in files),
        "files": files,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Static codebase structural map.")
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    result = scan(Path(a.root))
    if a.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"{result['root']}: {result['file_count']} files, {result['total_lines']} lines")
        for f in sorted(result["files"], key=lambda x: -x["lines"])[:15]:
            defs = ", ".join(d["name"] for d in f["defs"][:4]) or "-"
            print(f"  {f['path']:52} {f['lines']:6} lines  defs: {defs}")
    return 0


if __name__ == "__main__":
    sys.exit(main())