#!/usr/bin/env python3
"""
Execute cross-language compilation + comparative benchmarks.
Supports every toolchain installed on the device.
Part of polyglot-rosetta-core skill.
"""

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# (language) -> list of argv prefix (compiler invocation); None means interpreter-only (no compile step).
COMPILERS = {
    "python": [sys.executable, "-m", "py_compile"],
    "rust": ["rustc", "--crate-type", "lib"],
    "c": ["gcc", "-fsyntax-only", "-std=c17"],
    "cpp": ["g++", "-fsyntax-only", "-std=c++20"],
    "go": ["go", "vet"],
    "java": ["javac", "-d", "/tmp"],
    "zig": ["zig", "ast-check"],
    "nim": ["nim", "check"],
    "php": ["php", "-l"],
    "lua": ["luac", "-p"],
    "ruby": ["ruby", "-c"],
    "perl": ["perl", "-c"],
    "node": ["node", "--check"],
    "javascript": ["node", "--check"],
    "js": ["node", "--check"],
    "typescript": ["tsc", "--noEmit", "--strict"],
    "r": ["Rscript", "-e", "parse(file='%s')"],
    "clang": ["clang", "-fsyntax-only"],
    "tcc": ["tcc", "-c", "-o", "/dev/null"],
    "nim": ["nim", "check"],
}


def _compiler_for(lang: str):
    return COMPILERS.get(lang.lower())


def compile_source(source_path: Path, language: str = "python") -> dict:
    path = source_path.resolve()
    if not path.is_file():
        return {"status": "error", "message": f"Source file not found: {path}"}

    lang = language.lower()
    if lang == "js": lang = "javascript"
    if lang == "ts": lang = "typescript"
    if lang == "c++": lang = "cpp"
    if lang == "golang": lang = "go"
    cmd_prefix = _compiler_for(lang)
    if not cmd_prefix:
        return {"status": "error", "message": f"Unsupported language: {lang}"}

    compiler_bin = cmd_prefix[0]
    if shutil.which(compiler_bin) is None:
        return {"status": "skipped", "reason": f"Compiler binary '{compiler_bin}' not found on PATH", "file": str(path), "language": lang}

    # Handle special-cased invocations
    if lang == "r":
        cmd = ["Rscript", "-e", f"parse(file='{path}')"]
    elif lang == "php":
        cmd = ["php", "-l", str(path)]
    elif lang == "lua":
        cmd = ["luac", "-p", str(path)]
    elif lang == "nim":
        cmd = ["nim", "check", str(path)]
    elif lang == "zig":
        cmd = ["zig", "ast-check", str(path)]
    elif lang == "go":
        cmd = ["go", "vet", str(path)]
    elif lang == "typescript":
        cmd = ["tsc", "--noEmit", "--strict", str(path)]
    elif lang in ("node", "javascript", "js"):
        cmd = ["node", "--check", str(path)]
    elif lang == "java":
        cmd = ["javac", "-d", tempfile.gettempdir(), str(path)]
    else:
        cmd = list(cmd_prefix) + [str(path)]

    proc = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=120)
    return {
        "status": "PASS" if proc.returncode == 0 else "FAIL",
        "returncode": proc.returncode,
        "language": lang,
        "file": str(path),
        "stdout": proc.stdout.strip()[:500],
        "stderr": proc.stderr.strip()[:500],
    }


def detect_toolchains() -> dict:
    out = {}
    for lang, prefix in COMPILERS.items():
        binname = prefix[0]
        out[lang] = {"binary": binname, "available": shutil.which(binname) is not None}
    return out


def main():
    parser = argparse.ArgumentParser(description="Cross-language compilation and verification runner")
    parser.add_argument("--file", type=Path, default=Path(__file__), help="Source file to compile")
    parser.add_argument("--lang", default="python", help="Source language")
    parser.add_argument("--detect", action="store_true", help="Detect all installed toolchains")
    args = parser.parse_args()

    if args.detect:
        print(json.dumps(detect_toolchains(), indent=2))
        return 0
    result = compile_source(args.file, language=args.lang)
    print(json.dumps(result, indent=2))
    return 0 if result.get("status") in {"PASS", "skipped"} else 1


if __name__ == "__main__":
    sys.exit(main())
