#!/usr/bin/env python3
"""Synchronize canonical Skills, Combos, and Megas into runtime targets.

Atomic Skills remain directory symlinks. Combo and Mega sources remain canonical
COMBO.md/MEGA.md documents; runtimes receive generated SKILL.md adapters outside
the repository so compatibility packaging cannot recreate committed layer copies.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
COMBOS_DIR = ROOT / "combo-skills"
MEGAS_DIR = ROOT / "mega-skills"
HOME = Path.home()
RUNTIMES = {
    "Antigravity": HOME / ".gemini" / "config" / "skills",
    "Kilo Code": HOME / ".kilo" / "skills",
    "OpenCode Zen": HOME / ".config" / "kilo" / "skills",
    "KiloCode": HOME / ".kilocode" / "skills",
}


def remove_target(target: Path) -> None:
    try:
        if target.is_symlink() or target.is_file():
            target.unlink()
        elif target.exists():
            shutil.rmtree(target)
    except Exception:
        pass


def reset_target_dir(target: Path) -> None:
    remove_target(target)
    target.mkdir(parents=True, exist_ok=True)


def create_symlink(source: Path, target: Path) -> str:
    try:
        if target.is_symlink() and target.resolve() == source.resolve():
            return "exists"
    except Exception:
        pass
    remove_target(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        target.symlink_to(source, target_is_directory=True)
        return "created"
    except Exception as e:
        # Fallback to copy if symlink fails
        if not target.exists():
            shutil.copytree(source, target)
        return "copied"


def render_adapter(document: Path, name: str, kind: str) -> str:
    body = document.read_text(encoding="utf-8").strip()
    return (
        "---\n"
        f"name: {name}\n"
        f"description: {kind} compatibility adapter for the canonical {document.name} contract.\n"
        "---\n\n" + body + "\n"
    )


def install_contract_package(source: Path, runtime_root: Path, name: str, document_name: str, kind: str) -> None:
    target = runtime_root / name
    reset_target_dir(target)
    document = source / document_name
    try:
        (target / document_name).symlink_to(document)
    except Exception:
        shutil.copy2(document, target / document_name)
    (target / "SKILL.md").write_text(render_adapter(document, name, kind), encoding="utf-8")


def sync_all() -> None:
    print(f"Canonical Source: {ROOT}")
    for runtime_name, runtime_root in RUNTIMES.items():
        runtime_root.mkdir(parents=True, exist_ok=True)
        print(f"Syncing runtime: {runtime_name} -> {runtime_root}")

        # Atomic Skills
        if SKILLS_DIR.exists():
            for source in sorted(SKILLS_DIR.iterdir()):
                if source.is_dir() and not source.name.startswith((".", "_")):
                    create_symlink(source, runtime_root / source.name)

        # Combo Skills
        if COMBOS_DIR.exists():
            for source in sorted(COMBOS_DIR.iterdir()):
                if source.is_dir() and not source.name.startswith((".", "_")) and (source / "COMBO.md").is_file():
                    install_contract_package(source, runtime_root, source.name, "COMBO.md", "Combo Skill")

        # Mega Skills
        if MEGAS_DIR.exists():
            for source in sorted(MEGAS_DIR.iterdir()):
                if source.is_dir() and not source.name.startswith((".", "_")) and (source / "MEGA.md").is_file():
                    install_contract_package(source, runtime_root, source.name, "MEGA.md", "Mega Skill")


if __name__ == "__main__":
    sync_all()
