#!/usr/bin/env python3
"""
AST-level syntactic invariant validator and defect sentinel.
Parses Python source code and validates AST invariants.
"""
from __future__ import annotations
import ast
import json
import sys
from pathlib import Path
from typing import Any, Dict, List


class ASTInvariantVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.defects: List[Dict[str, Any]] = []
        self.node_count: int = 0

    def visit(self, node: ast.AST) -> None:
        self.node_count += 1
        super().visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        if node.type is None:
            self.defects.append({
                "type": "bare_except",
                "line": getattr(node, "lineno", 0),
                "message": "Bare except clause detected; specify explicit exception class",
            })
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec"}:
            self.defects.append({
                "type": "unsafe_call",
                "line": getattr(node, "lineno", 0),
                "message": f"Unsafe dynamic evaluation call '{node.func.id}' detected",
            })
        self.generic_visit(node)


def validate_ast_invariants(source_code: str, filename: str = "<source>") -> Dict[str, Any]:
    """Parse source and validate syntactic and AST-level safety invariants."""
    try:
        tree = ast.parse(source_code, filename=filename)
    except SyntaxError as e:
        return {
            "valid": False,
            "syntax_error": True,
            "filename": filename,
            "line": e.lineno,
            "message": str(e),
            "defects": [{"type": "syntax_error", "line": e.lineno, "message": str(e)}],
            "node_count": 0,
        }

    visitor = ASTInvariantVisitor()
    visitor.visit(tree)
    return {
        "valid": len(visitor.defects) == 0,
        "syntax_error": False,
        "filename": filename,
        "defects": visitor.defects,
        "node_count": visitor.node_count,
    }


def main() -> int:
    if len(sys.argv) > 1:
        target = Path(sys.argv[1])
        if target.is_file():
            res = validate_ast_invariants(target.read_text(encoding="utf-8"), str(target))
            print(json.dumps(res, indent=2))
            return 0 if res["valid"] else 1
    print(json.dumps({"status": "ready", "module": "ast_sentinel"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
