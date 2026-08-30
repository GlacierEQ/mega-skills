#!/usr/bin/env python3
"""
Epistemic Verification Receipt Generator
Produces cryptographic verification receipts with SHA-256 digests and timestamps.
"""

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


def get_git_info(root: Path) -> Dict:
    """Extract git commit, branch, status."""
    info = {}
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, cwd=root
        )
        if result.returncode == 0:
            info["commit"] = result.stdout.strip()
    except Exception:
        pass
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True, cwd=root
        )
        if result.returncode == 0:
            info["branch"] = result.stdout.strip()
    except Exception:
        pass
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, cwd=root
        )
        if result.returncode == 0:
            info["clean"] = result.stdout.strip() == ""
            info["changes"] = result.stdout.strip().split("\n") if result.stdout.strip() else []
    except Exception:
        pass
    return info


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def generate_receipt(
    target: Path,
    tier: str,
    authorized: bool,
    evidence: List[str],
    gaps: List[str],
    forbidden: List[str],
    extra: Optional[Dict] = None
) -> Dict:
    """Generate cryptographic verification receipt."""
    receipt = {
        "version": "1.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "target": str(target),
        "target_sha256": compute_sha256(target) if target.exists() else "NOT_FOUND",
        "epistemic_tier": tier,
        "authorized": authorized,
        "evidence": evidence,
        "gaps": gaps,
        "forbidden_patterns": forbidden,
        "git": get_git_info(target.parent.parent),
    }
    if extra:
        receipt.update(extra)
    return receipt


def main():
    if len(sys.argv) < 2:
        print("Usage: receipt_generator.py <target> [--tier TIER] [--authorized true|false] [--evidence '...'] [--output receipt.json]")
        sys.exit(1)
    
    target = Path(sys.argv[1])
    tier = "L2"
    authorized = False
    evidence = []
    gaps = []
    forbidden = []
    output = None
    
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--tier" and i + 1 < len(sys.argv):
            tier = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--authorized" and i + 1 < len(sys.argv):
            authorized = sys.argv[i + 1].lower() == "true"
            i += 2
        elif sys.argv[i] == "--evidence" and i + 1 < len(sys.argv):
            evidence = sys.argv[i + 1].split("|")
            i += 2
        elif sys.argv[i] == "--gap" and i + 1 < len(sys.argv):
            gaps = sys.argv[i + 1].split("|")
            i += 2
        elif sys.argv[i] == "--forbidden" and i + 1 < len(sys.argv):
            forbidden = sys.argv[i + 1].split("|")
            i += 2
        elif sys.argv[i] == "--output" and i + 1 < len(sys.argv):
            output = Path(sys.argv[i + 1])
            i += 2
        else:
            i += 1
    
    receipt = generate_receipt(target, tier, authorized, evidence, gaps, forbidden)
    
    if output:
        output.write_text(json.dumps(receipt, indent=2))
        print(f"Receipt written to {output}")
    else:
        print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
