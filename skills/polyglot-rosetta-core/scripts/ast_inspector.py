#!/usr/bin/env python3
"""
Inspect source AST and type signatures across polyglot floors.
Supports Python (stdlib ast), plus Rust/Go/Java/C/C++/JS/TS via tree-sitter
when available. Falls back gracefully to regex-based signature extraction.
Part of polyglot-rosetta-core skill.
"""

import argparse
import ast
import json
import re
import sys
from pathlib import Path

try:
    import tree_sitter  # noqa: F401
    _TS_AVAILABLE = True
except Exception:
    _TS_AVAILABLE = False

_LANGUAGE_ALIASES = {
    "py": "python", "python": "python",
    "rs": "rust", "rust": "rust",
    "go": "go", "golang": "go",
    "java": "java",
    "c": "c",
    "cpp": "cpp", "c++": "cpp", "cc": "cpp", "cxx": "cpp",
    "js": "javascript", "javascript": "javascript",
    "ts": "typescript", "typescript": "typescript",
    "tsx": "tsx",
}

_TS_LANGS = {}
if _TS_AVAILABLE:
    try:
        import tree_sitter_python as tspy
        _TS_LANGS["python"] = tspy.language()
    except Exception:
        pass
    try:
        import tree_sitter_rust as tsrs
        _TS_LANGS["rust"] = tsrs.language()
    except Exception:
        pass
    try:
        import tree_sitter_go as tsgo
        _TS_LANGS["go"] = tsgo.language()
    except Exception:
        pass
    try:
        import tree_sitter_java as tsjava
        _TS_LANGS["java"] = tsjava.language()
    except Exception:
        pass
    try:
        import tree_sitter_c as tsc
        _TS_LANGS["c"] = tsc.language()
    except Exception:
        pass
    try:
        import tree_sitter_cpp as tscpp
        _TS_LANGS["cpp"] = tscpp.language()
    except Exception:
        pass
    try:
        import tree_sitter_javascript as tsjs
        _TS_LANGS["javascript"] = tsjs.language()
    except Exception:
        pass
    try:
        import tree_sitter_typescript as tsts
        _TS_LANGS["typescript"] = tsts.language_typescript()
        _TS_LANGS["tsx"] = tsts.language_tsx()
    except Exception:
        pass


def _detect_language(path: Path, explicit: str | None) -> str:
    if explicit:
        return _LANGUAGE_ALIASES.get(explicit.lower(), explicit.lower())
    suffix = path.suffix.lstrip(".").lower()
    return _LANGUAGE_ALIASES.get(suffix, suffix or "python")


def inspect_python(source_code: str) -> dict:
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        return {"valid": False, "error": str(e), "functions": []}
    functions = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = []
            for arg in node.args.args:
                anno = ast.unparse(arg.annotation) if arg.annotation else "Any"
                args.append({"name": arg.arg, "type": anno})
            ret = ast.unparse(node.returns) if node.returns else "None"
            functions.append({
                "name": node.name,
                "args": args,
                "return_type": ret,
                "line": node.lineno,
                "is_async": isinstance(node, ast.AsyncFunctionDef),
            })
    return {"valid": True, "language": "python", "total_functions": len(functions), "functions": functions}


_TS_QUERY_PATTERNS = {
    "rust": re.compile(r"(?m)^\s*(?:pub\s+)?(?:async\s+)?fn\s+(\w+)\s*\(([^)]*)\)(?:\s*->\s*([^\{]+))?"),
    "go": re.compile(r"(?m)^func\s+(?:\([^)]*\)\s*)?(\w+)\s*\(([^)]*)\)(?:\s*([^\{]+))?"),
    "java": re.compile(r"(?m)(?:public|private|protected|static|\s)+[\w<>\[\]]+\s+(\w+)\s*\(([^)]*)\)"),
    "c": re.compile(r"(?m)^(?:\w[\w\s\*]*?)\s+(\w+)\s*\(([^)]*)\)\s*\{"),
    "cpp": re.compile(r"(?m)^(?:\w[\w\s\*:<>,]*?)\s+(\w+)\s*\(([^)]*)\)\s*(?:const)?\s*\{"),
    "javascript": re.compile(r"(?m)(?:function\s+(\w+)\s*\(([^)]*)\)|(\w+)\s*=\s*(?:async\s*)?\(([^)]*)\)\s*=>|(\w+)\s*\(([^)]*)\)\s*\{)"),
    "typescript": re.compile(r"(?m)(?:function\s+(\w+)\s*\(([^)]*)\)(?:\s*:\s*([^\{]+))?|(\w+)\s*=\s*(?:async\s*)?\(([^)]*)\)\s*(?::\s*([^\{=]+))?\s*=>)"),
}


def _parse_params(param_str: str, language: str = "python") -> list[dict]:
    params = []
    for part in param_str.split(","):
        part = part.strip()
        if not part:
            continue
        if ":" in part:
            name, typ = part.split(":", 1)
            params.append({"name": name.strip().lstrip("..."), "type": typ.strip() or "Any"})
        else:
            toks = part.split()
            if len(toks) >= 2:
                if language == "go":
                    params.append({"name": toks[0], "type": " ".join(toks[1:])})
                else:
                    params.append({"name": toks[-1].lstrip("*&"), "type": " ".join(toks[:-1])})
            elif toks:
                params.append({"name": toks[0], "type": "Any"})
    return params


def inspect_regex(language: str, source_code: str) -> dict:
    pat = _TS_QUERY_PATTERNS.get(language)
    if not pat:
        return {"valid": False, "error": f"No inspector for language: {language}", "functions": []}
    functions = []
    for m in pat.finditer(source_code):
        groups = m.groups()
        # pick first non-None name group
        name = None
        params = ""
        ret = "Any"
        # rust/go style: (name, params, ret)
        if len(groups) >= 3 and groups[0] and groups[1] is not None:
            name = groups[0]
            params = groups[1]
            ret = (groups[2] or "").strip() or "Any"
        elif len(groups) >= 2 and groups[0] and groups[1] is not None:
            name = groups[0]
            params = groups[1]
        elif len(groups) >= 4:
            # js/ts multi-alternative
            for i in range(0, len(groups), 2):
                if groups[i]:
                    name = groups[i]
                    params = groups[i + 1] or ""
                    break
        if not name:
            continue
        functions.append({
            "name": name,
            "args": _parse_params(params, language),
            "return_type": ret,
            "line": source_code[:m.start()].count("\n") + 1,
            "is_async": "async" in source_code[max(0, m.start() - 20):m.start()],
        })
    return {"valid": True, "language": language, "total_functions": len(functions), "functions": functions}


def inspect_tree_sitter(language: str, source_code: str) -> dict:
    if language not in _TS_LANGS:
        return inspect_regex(language, source_code)
    try:
        from tree_sitter import Parser
    except Exception:
        return inspect_regex(language, source_code)
    try:
        parser = Parser(_TS_LANGS[language])
        tree = parser.parse(source_code.encode("utf-8"))
    except Exception as e:
        return inspect_regex(language, source_code)
    # generic: count function-like nodes
    func_node_types = {
        "function_definition", "function_item", "function_declaration",
        "method_declaration", "method_definition", "func_literal",
        "arrow_function",
    }
    functions = []

    def walk(node, depth=0):
        if node.type in func_node_types:
            name = None
            for c in node.children:
                if c.type in ("identifier", "name", "field_identifier", "property_identifier"):
                    name = source_code[c.start_byte:c.end_byte]
                    break
            if name:
                functions.append({
                    "name": name,
                    "args": [],
                    "return_type": "Any",
                    "line": node.start_point[0] + 1,
                    "is_async": "async" in source_code[node.start_byte:node.start_byte + 12],
                })
        for c in node.children:
            walk(c, depth + 1)

    walk(tree.root_node)
    if not functions:
        return inspect_regex(language, source_code)
    return {"valid": True, "language": language, "total_functions": len(functions), "functions": functions, "engine": "tree-sitter"}


def inspect_signatures(source_code: str, language: str | None = None) -> dict:
    lang = _detect_language(Path("x.py"), language) if language else "python"
    # If no explicit language and code looks like python, default python
    if language is None:
        language = "python"
    lang = _LANGUAGE_ALIASES.get(language.lower(), language.lower())
    if lang == "python":
        return inspect_python(source_code)
    if _TS_AVAILABLE and lang in _TS_LANGS:
        return inspect_tree_sitter(lang, source_code)
    return inspect_regex(lang, source_code)


def main():
    parser = argparse.ArgumentParser(description="Inspect source AST and type signatures")
    parser.add_argument("--file", type=Path, help="Source file to inspect")
    parser.add_argument("--lang", default=None, help="Language override")
    args = parser.parse_args()

    code = args.file.read_text(encoding="utf-8") if args.file and args.file.is_file() else "def add(a: int, b: int) -> int:\n    return a + b\n"
    result = inspect_signatures(code, language=args.lang)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
