#!/usr/bin/env python3
"""
Execute cross-language compilation + comparative benchmarks
Part of polyglot-rosetta-core skill.
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

COMPILERS = {
    "python": [sys.executable, "-m", "py_compile"],
    "rust": ["rustc", "--crate-type", "lib"],
}


def compile_source(source_path: Path, language: str = "python") -> dict:
    """Compile or validate source file syntax using native toolchains."""
    path = source_path.resolve()
    if not path.is_file():
        return {"status": "error", "message": f"Source file not found: {path}"}

    lang = language.lower()
    cmd_prefix = COMPILERS.get(lang)
    if not cmd_prefix:
        return {"status": "error", "message": f"Unsupported language: {lang}"}

    # Check if compiler executable is installed
    compiler_bin = cmd_prefix[0]
    if shutil.which(compiler_bin) is None:
        return {
            "status": "skipped",
            "reason": f"Compiler binary '{compiler_bin}' not found on PATH",
            "file": str(path),
        }

    proc = subprocess.run(cmd_prefix + [str(path)], capture_output=True, text=True, check=False)
    return {
        "status": "PASS" if proc.returncode == 0 else "FAIL",
        "returncode": proc.returncode,
        "language": lang,
        "file": str(path),
        "stderr": proc.stderr.strip(),
    }


def main():
    parser = argparse.ArgumentParser(description="Cross-language compilation and verification runner")
    parser.add_argument("--file", type=Path, default=Path(__file__), help="Source file to compile")
    parser.add_argument("--lang", default="python", help="Source language")
    args = parser.parse_args()

    result = compile_source(args.file, language=args.lang)
    print(json.dumps(result, indent=2))
    return 0 if result.get("status") in {"PASS", "skipped"} else 1


if __name__ == "__main__":
    sys.exit(main())

