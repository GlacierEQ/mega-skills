#!/usr/bin/env python3
"""Executable support layer for the Desktop Commander operator skill."""

from __future__ import annotations

import json
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILL_MD = ROOT / "SKILL.md"
REQUIRED_MARKERS = (
    "name: desktop-commander-overview",
    "ORIENT → ACQUIRE → EXECUTE → VERIFY → PRESERVE → CONTINUE",
    "No readback = no verified mutation.",
    "pin calls to an explicit `deviceId`",
    "## Failure ladder",
    "## Continuity recovery",
    "## Pass-through intelligence",
    "IDENTIFY → ACQUIRE → NORMALIZE → ENRICH → ROUTE → RECEIPT → VERIFY DESTINATION",
)


def emit(payload: dict) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def validate_skill() -> tuple[bool, list[str]]:
    if not SKILL_MD.exists():
        return False, ["SKILL.md missing"]
    text = SKILL_MD.read_text(encoding="utf-8")
    missing = [marker for marker in REQUIRED_MARKERS if marker not in text]
    return not missing, missing

def git_context(cwd: Path) -> dict:
    result = subprocess.run(
        ["git", "-C", str(cwd), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return {"inside_git_repo": False}
    root = result.stdout.strip()
    status = subprocess.run(
        ["git", "-C", root, "status", "--short"],
        capture_output=True,
        text=True,
        check=False,
    )
    lines = [line for line in status.stdout.splitlines() if line.strip()]
    return {
        "inside_git_repo": True,
        "git_root": root,
        "dirty_entries": len(lines),
    }


def classify_cloud_surface(name: str) -> str:
    lowered = name.lower()
    if lowered.startswith("dropbox"):
        return "Dropbox"
    if lowered.startswith("onedrive"):
        return "OneDrive"
    if lowered.startswith("googledrive"):
        return "Google Drive"
    return "Unknown cloud provider"


def cloud_surfaces(home: Path | None = None) -> dict:
    base = (home or Path.home()).resolve()
    root = base / "Library" / "CloudStorage"
    surfaces = []
    if root.is_dir():
        for entry in sorted(root.iterdir(), key=lambda item: item.name.lower()):
            if entry.name.startswith("."):
                continue
            surfaces.append({
                "provider": classify_cloud_surface(entry.name),
                "mount_name": entry.name,
                "path": str(entry),
                "surface_type": "local_cloud_mount",
            })
    return {"root": str(root), "available": root.is_dir(), "count": len(surfaces), "surfaces": surfaces}


def preflight() -> dict:
    cwd = Path.cwd().resolve()
    valid, missing = validate_skill()
    return {
        "skill": "desktop-commander-overview",
        "status": "ready" if valid else "invalid_skill",
        "skill_valid": valid,
        "missing_markers": missing,
        "platform": platform.platform(),
        "python": platform.python_version(),
        "cwd": str(cwd),
        "git": git_context(cwd),
        "cloud_surfaces": cloud_surfaces(),
        "note": "Device identity/config must still be resolved through Desktop Commander MCP before remote execution.",
    }

def main() -> int:
    command = sys.argv[1] if len(sys.argv) > 1 else "manifest"
    if command in {"preflight", "--execute"}:
        payload = preflight()
        emit(payload)
        return 0 if payload["skill_valid"] else 2
    if command == "check":
        valid, missing = validate_skill()
        emit({"skill": "desktop-commander-overview", "valid": valid, "missing": missing})
        return 0 if valid else 2
    if command in {"topology", "surfaces"}:
        emit({"skill": "desktop-commander-overview", "cloud_surfaces": cloud_surfaces()})
        return 0
    if command == "manifest":
        emit({
            "skill": "desktop-commander-overview",
            "capability": "verified Desktop Commander machine execution",
            "commands": ["manifest", "check", "preflight", "topology", "surfaces"],
            "execution_loop": "ORIENT→ACQUIRE→EXECUTE→VERIFY→PRESERVE→CONTINUE",
        })
        return 0
    emit({"skill": "desktop-commander-overview", "error": f"unknown command: {command}"})
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
