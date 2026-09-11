#!/usr/bin/env python3
"""
Inspect source AST and type signatures in origin floor
Part of polyglot-rosetta-core skill.
"""

import argparse
import ast
import json
import sys
from pathlib import Path


def inspect_signatures(source_code: str) -> dict:
    """Inspect Python AST and extract function type signatures."""
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

    return {
        "valid": True,
        "total_functions": len(functions),
        "functions": functions,
    }


def main():
    parser = argparse.ArgumentParser(description="Inspect source AST and type signatures")
    parser.add_argument("--file", type=Path, help="Python source file to inspect")
    args = parser.parse_args()

    code = args.file.read_text(encoding="utf-8") if args.file and args.file.is_file() else "def add(a: int, b: int) -> int:\n    return a + b\n"
    result = inspect_signatures(code)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

