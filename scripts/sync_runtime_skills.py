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



# Native OMP is an additive target.  Its skill selection is a mission-starting
# coalition, NOT a cap: the full canonical hierarchy remains available for
# further mission-specific composition.
OMP_POWER_SELECTION = {
    "atomic": (
        "power-skill", "skill-connector-router", "casey-operator-execution-kernel",
        "genius-mastery", "codemaster", "capability-admission",
        "strong-smart-routing-kernel", "apex-aspen-grove-bootup",
        "unified-memory-connect", "agent-memory-systems", "apex-meta-skill-kernel",
        "systematic-debugging", "test-driven-development",
        "verification-before-completion", "spiral-promotion-gate",
        "progressive-pyramid", "computer-user-core",
        "apex-universal-mcp-powerhouse", "make-it-heavy", "mcp-architect",
    ),
    "compound": (
        "genius-epistemic-engineering", "apex-mesh-dispatch",
        "strong-smart-execution-stack", "cross-cloud-memory-synthesis",
    ),
    "mega": (
        "apex-genius-mastery", "apex-strong-smart-execution-engine",
        "apex-dev-fork-orchestrator", "apex-orchestrator-mesh",
        "far-away-party", "apex-self-healing-forge",
    ),
}


def sync_omp_skills(runtime_root: Path, *, selection=None, apply: bool = False) -> dict:
    """Preview or add source-bound native OMP Skills without replacing profile state.

    Atomic Skills are direct directory symlinks. Compound/Mega Skills receive
    compatible SKILL.md adapters while their source contract stays linked.
    Existing targets, including different symlinks, are NEVER silently replaced.
    """
    import hashlib
    import re
    from collections import Counter

    layers = {
        "atomic": (SKILLS_DIR, "SKILL.md", None),
        "compound": (COMBOS_DIR, "COMBO.md", "Combo Skill"),
        "mega": (MEGAS_DIR, "MEGA.md", "Mega Skill"),
    }
    chosen = selection if selection is not None else OMP_POWER_SELECTION
    allowed_id = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    all_ids = [name for layer in layers for name in chosen.get(layer, ())]
    if len(set(all_ids)) != len(all_ids):
        raise ValueError("A selected skill name is duplicated across layers")
    if any(not isinstance(name, str) or not allowed_id.fullmatch(name) for name in all_ids):
        raise ValueError("Skill names must be canonical kebab-case identifiers")
    if any(layer not in layers for layer in chosen):
        raise ValueError("Unknown Skill layer")

    runtime_root = Path(runtime_root).expanduser()
    results = []
    for layer, (root, document_name, adapter_kind) in layers.items():
        for name in chosen.get(layer, ()):
            source = root / name
            document = source / document_name
            target = runtime_root / name
            item = {"layer": layer, "name": name, "source": str(source),
                    "target": str(target), "sha256": ""}
            if not source.is_dir() or not document.is_file():
                item["status"] = "missing_source"
            else:
                item["sha256"] = hashlib.sha256(document.read_bytes()).hexdigest()
                present = target.is_symlink() or target.exists()
                if present:
                    if adapter_kind is None:
                        identical = target.is_symlink() and target.resolve() == source.resolve()
                    else:
                        rendered = render_adapter(document, name, adapter_kind)
                        link = target / document_name
                        wrapper = target / "SKILL.md"
                        identical = (
                            target.is_dir() and not target.is_symlink()
                            and link.is_symlink() and link.resolve() == document.resolve()
                            and wrapper.is_file() and wrapper.read_text(encoding="utf-8") == rendered
                        )
                    item["status"] = "already_present" if identical else "conflict"
                elif not apply:
                    item["status"] = "planned"
                else:
                    try:
                        runtime_root.mkdir(parents=True, exist_ok=True)
                        if adapter_kind is None:
                            target.symlink_to(source, target_is_directory=True)
                        else:
                            # mkdir is exclusive: never silently replace a concurrent target.
                            target.mkdir()
                            try:
                                (target / document_name).symlink_to(document)
                                (target / "SKILL.md").write_text(
                                    render_adapter(document, name, adapter_kind), encoding="utf-8"
                                )
                            except Exception:
                                # Roll back only the entries this invocation created.
                                for child in target.iterdir():
                                    child.unlink()
                                target.rmdir()
                                raise
                        item["status"] = "created"
                    except (OSError, UnicodeError) as exc:
                        item["status"] = "install_error"
                        item["error"] = type(exc).__name__
            results.append(item)
    return {"runtime": "omp", "apply": apply, "profile_skills_dir": str(runtime_root),
            "counts": dict(sorted(Counter(item["status"] for item in results).items())),
            "items": results}


def main() -> None:
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Synchronize canonical Skills into agent runtimes")
    parser.add_argument("--runtime", choices=("legacy", "omp"), default="legacy")
    parser.add_argument("--omp-skills-dir", type=Path,
                        default=Path.home() / ".omp" / "agent" / "skills")
    parser.add_argument("--apply", action="store_true", help="Install only absent skills; never overwrite")
    args = parser.parse_args()
    if args.runtime == "legacy":
        if args.apply:
            parser.error("OMP activation flags require --runtime omp")
        sync_all()
        return
    result = sync_omp_skills(args.omp_skills_dir, apply=args.apply)
    print(json.dumps(result, indent=2))
    if result["counts"].get("missing_source", 0) or result["counts"].get("conflict", 0) or result["counts"].get("install_error", 0):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
