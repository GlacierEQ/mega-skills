#!/usr/bin/env python3
"""
Deterministic SHA-256 Verifier
Computes NIST-standard SHA-256 digests in 64KB chunks across artifacts.
"""

import hashlib
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


CHUNK_SIZE = 65536  # 64KB per NIST standard


def compute_sha256(path: Path) -> str:
    """Compute deterministic SHA-256 in 64KB chunks."""
    h = hashlib.sha256()
    try:
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        return f"ERROR: {e}"


def verify_sha256(path: Path, expected: str) -> Tuple[bool, str]:
    """Verify file matches expected SHA-256."""
    actual = compute_sha256(path)
    return actual == expected, actual


def compute_tree_hash(root: Path, pattern: str = "**/*") -> Dict[str, str]:
    """Compute SHA-256 for all files matching pattern under root."""
    digests = {}
    for path in root.glob(pattern):
        if path.is_file():
            rel = path.relative_to(root)
            digests[str(rel)] = compute_sha256(path)
    return digests


def write_manifest(digests: Dict[str, str], output: Path):
    """Write SHA-256 manifest as JSON."""
    manifest = {
        "algorithm": "SHA-256",
        "chunk_size": CHUNK_SIZE,
        "file_count": len(digests),
        "digests": digests,
    }
    output.write_text(json.dumps(manifest, indent=2, sort_keys=True))


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  sha256_verifier.py <file>                    # Compute single file hash")
        print("  sha256_verifier.py <file> <expected_hash>    # Verify against expected")
        print("  sha256_verifier.py --tree <dir> [--pattern glob] [--output manifest.json]")
        sys.exit(1)
    
    if sys.argv[1] == "--tree":
        if len(sys.argv) < 3:
            print("Usage: sha256_verifier.py --tree <dir> [--pattern glob] [--output manifest.json]")
            sys.exit(1)
        root = Path(sys.argv[2])
        pattern = "**/*"
        output = None
        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == "--pattern" and i + 1 < len(sys.argv):
                pattern = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--output" and i + 1 < len(sys.argv):
                output = Path(sys.argv[i + 1])
                i += 2
            else:
                i += 1
        digests = compute_tree_hash(root, pattern)
        if output:
            write_manifest(digests, output)
            print(f"Manifest written to {output} ({len(digests)} files)")
        else:
            print(json.dumps(digests, indent=2))
        return
    
    # Single file mode
    target = Path(sys.argv[1])
    if not target.exists():
        print(f"File not found: {target}")
        sys.exit(1)
    
    if len(sys.argv) >= 3:
        # Verify mode
        expected = sys.argv[2]
        match, actual = verify_sha256(target, expected)
        print(f"Expected: {expected}")
        print(f"Actual:   {actual}")
        print(f"Match:    {match}")
        sys.exit(0 if match else 1)
    else:
        # Compute mode
        digest = compute_sha256(target)
        print(digest)


if __name__ == "__main__":
    main()
