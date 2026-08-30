#!/usr/bin/env python3
"""Synchronize canonical Skills, Combos, and Megas into runtime targets.

Atomic Skills remain directory symlinks. Combo and Mega sources remain canonical
COMBO.md/MEGA.md documents; runtimes receive generated SKILL.md adapters outside
the repository so compatibility packaging cannot recreate committed layer copies.
"""

from __future__ import annotations

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


def reset_target(target: Path) -> None:
    if target.is_symlink() or target.is_file():
        target.unlink()
    elif target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)


def create_symlink(source: Path, target: Path) -> str:
    if target.is_symlink() and target.resolve() == source.resolve():
        return "exists"
    reset_target(target)
    target.unlink()
    target.symlink_to(source, target_is_directory=True)
    return "created"


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
    reset_target(target)
    document = source / document_name
    (target / document_name).symlink_to(document)
    (target / "SKILL.md").write_text(render_adapter(document, name, kind), encoding="utf-8")


def sync_all() -> None:
    print(f"Canonical Source: {ROOT}")
    stats = {name: {"linked": 0, "adapted": 0} for name in RUNTIMES}
    for runtime_root in RUNTIMES.values():
        runtime_root.mkdir(parents=True, exist_ok=True)

    skills = sorted(path for path in SKILLS_DIR.iterdir() if path.is_dir())
    combos = sorted(path for path in COMBOS_DIR.iterdir() if path.is_dir() and not path.name.startswith("_"))
    megas = sorted(path for path in MEGAS_DIR.iterdir() if path.is_dir())
    for source in skills:
        if "quarantine" in source.name:
            continue
        for name, runtime_root in RUNTIMES.items():
            create_symlink(source, runtime_root / source.name)
            stats[name]["linked"] += 1
    for source in combos:
        for name, runtime_root in RUNTIMES.items():
            install_contract_package(source, runtime_root, source.name, "COMBO.md", "Combo Skill")
            stats[name]["adapted"] += 1
    for source in megas:
        for name, runtime_root in RUNTIMES.items():
            install_contract_package(source, runtime_root, source.name, "MEGA.md", "Mega Skill")
            stats[name]["adapted"] += 1
    for name, counts in stats.items():
        print(f"{name}: {counts['linked']} atomic symlinks, {counts['adapted']} contract adapters")


if __name__ == "__main__":
    sync_all()
