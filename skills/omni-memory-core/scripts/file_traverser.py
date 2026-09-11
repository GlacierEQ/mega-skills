#!/usr/bin/env python3
"""
Traverse cloud file trees, parse multi-modal document contents
Part of omni-memory-core skill.
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

SUPPORTED_EXTENSIONS = {".txt", ".md", ".json", ".py", ".ts", ".js", ".csv", ".yaml", ".yml"}


def traverse_files(root_dir: Path, max_files: int = 50) -> list[dict]:
    """Traverse file trees and parse multi-modal document contents."""
    root = root_dir.resolve()
    records = []

    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        if len(records) >= max_files:
            break
        try:
            stat = path.stat()
            content = path.read_text(encoding="utf-8", errors="ignore")
            sha = hashlib.sha256(content.encode("utf-8")).hexdigest()
            records.append({
                "path": str(path.relative_to(root)),
                "size_bytes": stat.st_size,
                "sha256": sha,
                "lines": len(content.splitlines()),
                "snippet": content[:200],
            })
        except Exception:
            continue

    return records


def main():
    parser = argparse.ArgumentParser(description="Traverse file trees and parse documents")
    parser.add_argument("--dir", type=Path, default=Path.cwd(), help="Root directory to traverse")
    parser.add_argument("--max", type=int, default=10, help="Max files to index")
    args = parser.parse_args()

    files = traverse_files(args.dir, max_files=args.max)
    print(json.dumps({"total": len(files), "files": files}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

