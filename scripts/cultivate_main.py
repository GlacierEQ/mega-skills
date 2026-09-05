#!/usr/bin/env python3
"""Assess branches/PRs and cultivate main without waiting on Casey.

main is grown by merge commits. Force-push, reset, history rewrite, and
Casey-class hazards stay blocked.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CASEY_PATH_MARKERS = (
    ".env",
    "credentials.json",
    "secrets.",
    "id_rsa",
    ".pem",
    ".p12",
)

CASEY_TEXT_MARKERS = (
    "BEGIN PRIVATE KEY",
    "AKIA",
    "ghp_",
    "github_pat_",
    "xai-",
    "sk-proj-",
)

CASEY_FILE_GLOBS = (
    "legal-filing",
    "jefs",
    "privilege",
)

AUTO_PATH_PREFIXES = (
    "docs/",
    "schemas/",
    "pipelines/",
    "tests/",
    "scripts/",
    "combo-skills/",
    "mega-skills/",
    "governance/",
    "readiness/",
    "registry/",
    ".buildkite/",
    ".github/",
    "skills/",
)

FORBIDDEN_ACTIONS = (
    "git push --force",
    "git reset --hard origin/main",
    "git checkout -B main",
    "git branch -D main",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def classify_files(files: list[str]) -> dict[str, Any]:
    casey = []
    auto = []
    other = []
    for name in files:
        lowered = name.lower()
        if any(marker in lowered for marker in CASEY_PATH_MARKERS + CASEY_FILE_GLOBS):
            casey.append(name)
        elif any(name.startswith(prefix) or name == prefix.rstrip("/") for prefix in AUTO_PATH_PREFIXES) or name in {
            "README.md",
            "HIERARCHY.md",
            "OWNERSHIP.md",
            "COMPATIBILITY.md",
            ".gitignore",
        }:
            auto.append(name)
        else:
            other.append(name)
    return {"casey": casey, "auto": auto, "other": other}


def scan_patch_for_secrets(patch: str | None) -> list[str]:
    if not patch:
        return []
    hits = []
    for marker in CASEY_TEXT_MARKERS:
        if marker in patch:
            hits.append(marker)
    return hits


def assess_change(
    *,
    title: str,
    files: list[str],
    patch: str | None = None,
    ahead_by: int | None = None,
    behind_by: int | None = None,
    mergeable: bool | None = None,
    deletes_registry_entry: bool = False,
    replaces_main: bool = False,
    force_push: bool = False,
    draft: bool = False,
    already_in_main: bool = False,
) -> dict[str, Any]:
    buckets = classify_files(files)
    secrets = scan_patch_for_secrets(patch)
    reasons: list[str] = []
    decision = "AUTO_MERGE"

    if replaces_main or force_push:
        decision = "CASEY"
        reasons.append("force-push and main replacement are forbidden")
    elif secrets or buckets["casey"]:
        decision = "CASEY"
        reasons.append("secret or Casey-path hazard")
    elif already_in_main or (ahead_by == 0 and behind_by == 0):
        decision = "REDUNDANT"
        reasons.append("no unique commits versus main")
    elif draft:
        decision = "PRESERVE"
        reasons.append("draft workstream still open")
    elif deletes_registry_entry:
        decision = "HARVEST"
        reasons.append("registry deletion must be harvested, not blindly merged")
    elif behind_by and behind_by > 0 and mergeable is False:
        decision = "HARVEST"
        reasons.append("behind main and currently unmergeable; update then reassess")
    elif buckets["other"] and not buckets["auto"]:
        decision = "HARVEST"
        reasons.append("unique paths outside the auto-merge surface")
    elif mergeable is False:
        decision = "HARVEST"
        reasons.append("conflicts or missing mergeability; harvest onto current main")
    elif ahead_by and ahead_by > 0:
        decision = "AUTO_MERGE"
        reasons.append("additive unique work on the auto-merge surface")
    else:
        decision = "AUTO_MERGE"
        reasons.append("no Casey hazard; cultivate into main")

    return {
        "schema_version": 1,
        "title": title,
        "decision": decision,
        "operator": "assessor" if decision != "CASEY" else "casey",
        "merge_method": "merge" if decision == "AUTO_MERGE" else None,
        "reasons": reasons,
        "files": buckets,
        "secret_markers": secrets,
        "ahead_by": ahead_by,
        "behind_by": behind_by,
        "mergeable": mergeable,
        "main_cultivation_rule": "merge-commit-into-main; never reset or replace main",
    }


def load_local_report(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def gh_json(args: list[str]) -> Any:
    proc = subprocess.run(["gh", *args], check=False, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or f"gh failed: {' '.join(args)}")
    return json.loads(proc.stdout) if proc.stdout.strip() else None


def assess_repo(owner: str, repo: str) -> dict[str, Any]:
    pulls = gh_json(
        [
            "pr",
            "list",
            "--repo",
            f"{owner}/{repo}",
            "--state",
            "open",
            "--json",
            "number,title,isDraft,mergeable,headRefName,additions,deletions,files,url,headRefOid",
        ]
    )
    assessments = []
    for pull in pulls or []:
        files = [item["path"] for item in pull.get("files") or []]
        deletes = any(item.get("deletions", 0) > 0 and "registry/" in item.get("path", "") for item in pull.get("files") or [])
        result = assess_change(
            title=pull["title"],
            files=files,
            mergeable=True if pull.get("mergeable") == "MERGEABLE" else False if pull.get("mergeable") == "CONFLICTING" else None,
            deletes_registry_entry=deletes,
            draft=bool(pull.get("isDraft")),
        )
        result.update(
            {
                "number": pull["number"],
                "url": pull.get("url"),
                "head": pull.get("headRefName"),
                "sha": pull.get("headRefOid"),
            }
        )
        assessments.append(result)
    return {
        "schema_version": 1,
        "generated_at": utc_now(),
        "repository": f"{owner}/{repo}",
        "baseline": "main",
        "assessments": assessments,
        "summary": {
            "open": len(assessments),
            "auto_merge": sum(item["decision"] == "AUTO_MERGE" for item in assessments),
            "harvest": sum(item["decision"] == "HARVEST" for item in assessments),
            "preserve": sum(item["decision"] == "PRESERVE" for item in assessments),
            "redundant": sum(item["decision"] == "REDUNDANT" for item in assessments),
            "casey": sum(item["decision"] == "CASEY" for item in assessments),
        },
    }


def apply_auto_merges(report: dict[str, Any], *, dry_run: bool = False) -> dict[str, Any]:
    applied = []
    for item in report["assessments"]:
        if item["decision"] != "AUTO_MERGE" or not item.get("number"):
            continue
        record = {"number": item["number"], "title": item["title"], "decision": item["decision"]}
        if dry_run:
            record["status"] = "DRY_RUN"
        else:
            proc = subprocess.run(
                [
                    "gh",
                    "pr",
                    "merge",
                    str(item["number"]),
                    "--repo",
                    report["repository"],
                    "--merge",
                    "--delete-branch=false",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            record["status"] = "MERGED" if proc.returncode == 0 else "BLOCKED"
            record["stderr"] = proc.stderr.strip()
            record["stdout"] = proc.stdout.strip()
        applied.append(record)
    return {"applied": applied, "finished_at": utc_now()}


def write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default="GlacierEQ/mega-skills")
    parser.add_argument("--report", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output", type=Path, default=Path("missions/cultivate-main/ASSESSMENT.json"))
    args = parser.parse_args(argv)
    owner, repo = args.repo.split("/", 1)
    report = assess_repo(owner, repo)
    if args.apply:
        report["apply"] = apply_auto_merges(report, dry_run=args.dry_run)
    write_report(args.output, report)
    print(json.dumps({"status": "COMPLETE", "summary": report["summary"], "output": str(args.output)}, indent=2))
    casey_only = report["summary"]["open"] > 0 and report["summary"]["auto_merge"] == 0 and report["summary"]["harvest"] == 0
    if casey_only:
        print("No auto-merge or harvest work; Casey-class or empty.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
