#!/usr/bin/env python3
"""Install/check one pinned GitHub Progressive Pyramid Skill across agent hosts.

Source is the checked-out GlacierEQ/mega-skills repository, not local copies.
Installs never replace unrelated or existing material without manual review.
Host filesystem installation does NOT certify that a running agent loaded it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

HOSTS = {
    "omp": Path(".omp/agent/managed-skills/progressive-pyramid"),
    "codex": Path(".agents/skills/progressive-pyramid"),
    "claude": Path(".claude/skills/progressive-pyramid"),
}
SOURCE_ID = "glaciereq.progressive-pyramid.contract.v1"
SOURCE = Path(__file__).resolve().parents[1] / "skills" / "progressive-pyramid"


def validate_source(source: Path) -> None:
    if not (source / "SKILL.md").is_file():
        raise ValueError("missing canonical SKILL.md")
    path = source / "progressive_pyramid.contract.json"
    if not path.is_file():
        raise ValueError("missing canonical contract")
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError("invalid canonical contract") from exc
    if document.get("schema_id") != SOURCE_ID:
        raise ValueError("canonical contract identity mismatch")


def source_files(source: Path) -> dict[str, str]:
    files = {}
    for path in sorted(source.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts or path.name in {".DS_Store", ".source-commit", ".source-repository", ".source-manifest.json"}:
            continue
        files[path.relative_to(source).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return files


def install(source: Path, home: Path, targets: list[str], commit: str) -> list[Path]:
    validate_source(source)
    if not commit or not all(c in "0123456789abcdef" for c in commit.lower()):
        raise ValueError("source commit must be a Git SHA")
    destinations = [home / HOSTS[t] for t in targets]
    for dest in destinations:
        if dest.exists() or dest.is_symlink():
            raise FileExistsError(f"refuse to overwrite existing installation: {dest}")
    made = []
    try:
        for dest in destinations:
            dest.parent.mkdir(parents=True, exist_ok=True)
            # Copy, then record the verified source revision for future readback.
            shutil.copytree(source, dest, ignore=shutil.ignore_patterns("__pycache__", ".DS_Store"))
            made.append(dest)
            (dest / ".source-commit").write_text(commit + "\n", encoding="utf-8")
            (dest / ".source-repository").write_text(
                "GlacierEQ/mega-skills:skills/progressive-pyramid\n", encoding="utf-8")
            (dest / ".source-manifest.json").write_text(
                json.dumps(source_files(source), sort_keys=True) + "\n", encoding="utf-8")
        return made
    except Exception:
        for dest in reversed(made):
            shutil.rmtree(dest)
        raise


def update(source: Path, home: Path, targets: list[str], commit: str) -> list[Path]:
    """Upgrade only recognized untampered installations; retain rollback backups."""
    validate_source(source)
    if not commit or not all(c in "0123456789abcdef" for c in commit.lower()):
        raise ValueError("source commit must be a Git SHA")
    planned = []
    for t in targets:
        dest = home / HOSTS[t]
        if not dest.is_dir() or dest.is_symlink():
            raise ValueError(f"{t}: installed managed directory required")
        origin = dest / ".source-repository"
        revision = dest / ".source-commit"
        if not origin.is_file() or origin.read_text().strip() != "GlacierEQ/mega-skills:skills/progressive-pyramid":
            raise ValueError(f"{t}: not a managed canonical installation")
        if not revision.is_file():
            raise ValueError(f"{t}: missing prior revision")
        old = revision.read_text().strip()
        manifest = dest / ".source-manifest.json"
        expected_old = json.loads(manifest.read_text()) if manifest.is_file() else source_files(source)
        if source_files(dest) != expected_old:
            raise ValueError(f"{t}: local changes must be preserved before updating")
        backup = dest.with_name(dest.name + ".backup-" + old[:8])
        suffix = 1
        while backup.exists():
            backup = dest.with_name(dest.name + ".backup-" + old[:8] + f"-{suffix}")
            suffix += 1
        planned.append((dest, backup))
    made = []
    staged = []
    try:
        for dest, backup in planned:
            temp = dest.with_name(dest.name + ".staging-update")
            suffix = 1
            while temp.exists():
                temp = dest.with_name(dest.name + f".staging-update-{suffix}")
                suffix += 1
            shutil.copytree(source, temp, ignore=shutil.ignore_patterns("__pycache__", ".DS_Store"))
            staged.append(temp)
            (temp / ".source-commit").write_text(commit + "\n", encoding="utf-8")
            (temp / ".source-repository").write_text(
                "GlacierEQ/mega-skills:skills/progressive-pyramid\n", encoding="utf-8")
            (temp / ".source-manifest.json").write_text(
                json.dumps(source_files(source), sort_keys=True) + "\n", encoding="utf-8")
        for (dest, backup), temp in zip(planned, staged):
            dest.rename(backup)
            try:
                temp.rename(dest)
            except Exception:
                backup.rename(dest)
                raise
            made.append((dest, backup))
        return [backup for _, backup in made]
    except Exception:
        for dest, backup in reversed(made):
            if dest.exists():
                shutil.rmtree(dest)
            backup.rename(dest)
        raise
    finally:
        for temp in staged:
            if temp.exists():
                shutil.rmtree(temp)


def check(source: Path, home: Path, targets: list[str], commit: str) -> list[str]:
    validate_source(source)
    expected = source_files(source)
    issues = []
    for t in targets:
        dest = home / HOSTS[t]
        if not dest.is_dir():
            issues.append(f"{t}: not installed")
            continue
        if not (dest / ".source-commit").is_file() or (dest / ".source-commit").read_text().strip() != commit:
            issues.append(f"{t}: source revision mismatch")
        if source_files(dest) != expected:
            issues.append(f"{t}: installed content differs from canonical Skill")
    return issues


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    action = p.add_mutually_exclusive_group(required=True)
    action.add_argument("--install", action="store_true")
    action.add_argument("--check", action="store_true")
    action.add_argument("--update", action="store_true")
    p.add_argument("--source", type=Path, default=SOURCE)
    p.add_argument("--home", type=Path, default=Path.home())
    p.add_argument("--targets", nargs="+", choices=sorted(HOSTS), default=list(HOSTS))
    p.add_argument("--commit", default=None, help="Verified GitHub checkout SHA")
    args = p.parse_args()
    commit = args.commit
    if commit is None:
        try:
            commit = subprocess.check_output(
                ["git", "-C", str(args.source), "rev-parse", "HEAD"],
                text=True, stderr=subprocess.DEVNULL).strip()
        except (OSError, subprocess.CalledProcessError) as exc:
            p.error("cannot derive source SHA; pass --commit for a verified checkout")
    try:
        if args.install:
            result = install(args.source, args.home, args.targets, commit)
            print(json.dumps({"installed": [str(x) for x in result], "source_sha": commit}))
            return 0
        if args.update:
            backups = update(args.source, args.home, args.targets, commit)
            print(json.dumps({"updated": args.targets, "rollback_backups": [str(b) for b in backups], "source_sha": commit}))
            return 0
        issues = check(args.source, args.home, args.targets, commit)
        print(json.dumps({"valid": not issues, "issues": issues, "source_sha": commit}))
        return 1 if issues else 0
    except (ValueError, FileExistsError, KeyError) as exc:
        print(f"INSTALLER_ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
