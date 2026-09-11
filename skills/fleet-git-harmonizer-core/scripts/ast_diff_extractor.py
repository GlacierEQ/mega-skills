#!/usr/bin/env python3
"""
Extract semantic AST diffs from unique commits
Part of fleet-git-harmonizer-core skill.
"""

import argparse
import ast
import json
import sys
from pathlib import Path


def extract_top_level_symbols(code: str) -> dict[str, str]:
    """Extract top-level functions and classes with their AST unparsed definitions."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return {}

    symbols = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            symbols[node.name] = ast.unparse(node)
    return symbols


def compute_ast_diff(old_code: str, new_code: str) -> dict:
    """Compare two versions of Python code and extract added, modified, and removed symbols."""
    old_syms = extract_top_level_symbols(old_code)
    new_syms = extract_top_level_symbols(new_code)

    added = [k for k in new_syms if k not in old_syms]
    removed = [k for k in old_syms if k not in new_syms]
    modified = [k for k in new_syms if k in old_syms and new_syms[k] != old_syms[k]]
    unchanged = [k for k in new_syms if k in old_syms and new_syms[k] == old_syms[k]]

    return {
        "added": added,
        "removed": removed,
        "modified": modified,
        "unchanged": unchanged,
        "semantic_changes_detected": len(added) > 0 or len(removed) > 0 or len(modified) > 0,
    }


def main():
    parser = argparse.ArgumentParser(description="Extract semantic AST diffs between code versions")
    parser.add_argument("--old", type=Path, help="Old version file")
    parser.add_argument("--new", type=Path, help="New version file")
    args = parser.parse_args()

    c1 = args.old.read_text(encoding="utf-8") if args.old and args.old.is_file() else "def foo():\n    return 1\n"
    c2 = args.new.read_text(encoding="utf-8") if args.new and args.new.is_file() else "def foo():\n    return 2\n\ndef bar():\n    pass\n"

    diff = compute_ast_diff(c1, c2)
    print(json.dumps(diff, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

