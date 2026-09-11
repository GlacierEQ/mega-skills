#!/usr/bin/env python3
"""
Synthesize non-conflicting commits into main with provenance trailers
Part of fleet-git-harmonizer-core skill.
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path


def synthesize_commit_message(title: str, body: str, author: str = "GlacierEQ Harmonizer", evidence_hash: str = None) -> dict:
    """Synthesize commit message with provenance and audit trailers."""
    trailers = [
        f"Signed-off-by: {author} <operations@glaciereq.internal>",
    ]
    if evidence_hash:
        trailers.append(f"Evidence-Receipt: sha256:{evidence_hash}")
    else:
        sha = hashlib.sha256(f"{title}\n{body}".encode("utf-8")).hexdigest()
        trailers.append(f"Evidence-Receipt: sha256:{sha}")

    full_message = f"{title.strip()}\n\n{body.strip()}\n\n" + "\n".join(trailers)
    return {
        "title": title,
        "body": body,
        "trailers": trailers,
        "full_message": full_message,
        "provenance_hash": trailers[-1].split(":")[-1],
    }


def main():
    parser = argparse.ArgumentParser(description="Synthesize commits with provenance trailers")
    parser.add_argument("--title", default="feat: harmonize upstream capabilities", help="Commit title")
    parser.add_argument("--body", default="Clean automated reconciliation of non-conflicting AST updates.", help="Commit body")
    args = parser.parse_args()

    result = synthesize_commit_message(args.title, args.body)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

