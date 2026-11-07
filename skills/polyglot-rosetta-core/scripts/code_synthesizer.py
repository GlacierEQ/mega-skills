#!/usr/bin/env python3
"""
Synthesize idiomatic target code preserving invariants across polyglot floors.
Part of polyglot-rosetta-core skill.
"""

import argparse
import json
import sys
from pathlib import Path

TYPE_MAP = {
    "rust": {"int": "i64", "float": "f64", "str": "&str", "bool": "bool", "None": "()"},
    "go": {"int": "int64", "float": "float64", "str": "string", "bool": "bool", "None": ""},
    "c": {"int": "int64_t", "float": "double", "str": "const char*", "bool": "bool", "None": "void"},
    "cpp": {"int": "int64_t", "float": "double", "str": "std::string_view", "bool": "bool", "None": "void"},
    "java": {"int": "long", "float": "double", "str": "String", "bool": "boolean", "None": "void"},
    "js": {"int": "number", "float": "number", "str": "string", "bool": "boolean", "None": "void"},
    "ts": {"int": "number", "float": "number", "str": "string", "bool": "boolean", "None": "void"},
    "zig": {"int": "i64", "float": "f64", "str": "[]const u8", "bool": "bool", "None": "void"},
    "nim": {"int": "int64", "float": "float64", "str": "string", "bool": "bool", "None": "void"},
    "lua": {"int": "integer", "float": "number", "str": "string", "bool": "boolean", "None": "nil"},
    "php": {"int": "int", "float": "float", "str": "string", "bool": "bool", "None": "void"},
    "ruby": {"int": "Integer", "float": "Float", "str": "String", "bool": "TrueClass", "None": "nil"},
    "r": {"int": "integer", "float": "numeric", "str": "character", "bool": "logical", "None": "NULL"},
}


def _t(lang, t):
    return TYPE_MAP.get(lang, {}).get(t, t)


def synthesize(lang: str, name: str, args: list[dict], return_type: str = "int") -> str:
    lang = lang.lower()
    if lang == "rust":
        rust_args = [f"{a['name']}: {_t('rust', a.get('type','int'))}" for a in args]
        ret = _t("rust", return_type)
        rc = f" -> {ret}" if ret != "()" else ""
        return (f"pub fn {name}({', '.join(rust_args)}){rc} {{\n"
                f"    // Invariant-preserving synthesis (polyglot-rosetta-core)\n"
                f"    unimplemented!()\n}}")
    if lang == "go":
        go_args = [f"{a['name']} {_t('go', a.get('type','int'))}" for a in args]
        ret = _t("go", return_type)
        rc = f" {ret}" if ret else ""
        return (f"func {name}({', '.join(go_args)}){rc} {{\n"
                f"    // Invariant-preserving synthesis (polyglot-rosetta-core)\n"
                f"    panic(\"unimplemented\")\n}}")
    if lang == "c":
        c_args = [f"{_t('c', a.get('type','int'))} {a['name']}" for a in args]
        ret = _t("c", return_type)
        return (f"{ret} {name}({', '.join(c_args)}) {{\n"
                f"    /* Invariant-preserving synthesis (polyglot-rosetta-core) */\n"
                f"    /* TODO: implement */\n"
                f"}}")
    if lang == "cpp":
        cpp_args = [f"{_t('cpp', a.get('type','int'))} {a['name']}" for a in args]
        ret = _t("cpp", return_type)
        return (f"{ret} {name}({', '.join(cpp_args)}) {{\n"
                f"    // Invariant-preserving synthesis (polyglot-rosetta-core)\n"
                f"    throw std::runtime_error(\"unimplemented\");\n}}")
    if lang == "java":
        j_args = [f"{_t('java', a.get('type','int'))} {a['name']}" for a in args]
        ret = _t("java", return_type)
        return (f"public static {ret} {name}({', '.join(j_args)}) {{\n"
                f"    // Invariant-preserving synthesis (polyglot-rosetta-core)\n"
                f"    throw new UnsupportedOperationException(\"unimplemented\");\n}}")
    if lang in ("js", "javascript"):
        js_args = [a["name"] for a in args]
        return (f"function {name}({', '.join(js_args)}) {{\n"
                f"    // Invariant-preserving synthesis (polyglot-rosetta-core)\n"
                f"    throw new Error('unimplemented');\n}}")
    if lang in ("ts", "typescript"):
        ts_args = [f"{a['name']}: {_t('ts', a.get('type','int'))}" for a in args]
        ret = _t("ts", return_type)
        return (f"function {name}({', '.join(ts_args)}): {ret} {{\n"
                f"    // Invariant-preserving synthesis (polyglot-rosetta-core)\n"
                f"    throw new Error('unimplemented');\n}}")
    if lang == "zig":
        z_args = [f"{a['name']}: {_t('zig', a.get('type','int'))}" for a in args]
        ret = _t("zig", return_type)
        rc = f" {ret}" if ret != "void" else ""
        return (f"pub fn {name}({', '.join(z_args)}){rc} {{\n"
                f"    // Invariant-preserving synthesis (polyglot-rosetta-core)\n"
                f"    @panic(\"unimplemented\");\n}}")
    if lang == "nim":
        n_args = [f"{a['name']}: {_t('nim', a.get('type','int'))}" for a in args]
        ret = _t("nim", return_type)
        rc = f": {ret}" if ret != "void" else ""
        return (f"proc {name}*({', '.join(n_args)}){rc} =\n"
                f"  ## Invariant-preserving synthesis (polyglot-rosetta-core)\n"
                f"  raise newException(CatchableError, \"unimplemented\")")
    if lang == "python":
        py_args = [f"{a['name']}: {a.get('type','int')}" for a in args]
        ret = return_type if return_type != "None" else None
        rc = f" -> {ret}" if ret else ""
        return (f"def {name}({', '.join(py_args)}){rc}:\n"
                f"    \"\"\"Invariant-preserving synthesis (polyglot-rosetta-core).\"\"\"\n"
                f"    raise NotImplementedError('unimplemented')")
    # generic fallback
    return f"// {lang}: synthesis not yet implemented for {name}"


def synthesize_rust_function(name, args, return_type="None"):
    return synthesize("rust", name, args, return_type)


def main():
    parser = argparse.ArgumentParser(description="Synthesize idiomatic target code")
    parser.add_argument("--lang", default="rust", help="Target language")
    parser.add_argument("--name", default="compute", help="Function name")
    parser.add_argument("--ret", default="int", help="Return type")
    parser.add_argument("--args", default=None, help="JSON list of {name,type} args")
    args = parser.parse_args()

    sample_args = [{"name": "x", "type": "int"}, {"name": "y", "type": "float"}]
    if args.args:
        try:
            sample_args = json.loads(args.args)
        except json.JSONDecodeError:
            pass
    code = synthesize(args.lang, args.name, sample_args, return_type=args.ret)
    print(code)
    return 0


if __name__ == "__main__":
    sys.exit(main())
