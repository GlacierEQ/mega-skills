#!/usr/bin/env python3
"""Offline Linear board clustering for cleanup — no network, no secrets."""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _labels(issue: dict[str, Any]) -> list[str]:
    raw = issue.get("labels") or []
    if raw and isinstance(raw[0], dict):
        return [str(x.get("name") or "") for x in raw]
    return [str(x) for x in raw]


def _project(issue: dict[str, Any]) -> str:
    p = issue.get("project")
    if isinstance(p, dict):
        return str(p.get("name") or "none")
    return str(p or "none")


def _priority(issue: dict[str, Any]) -> str:
    p = issue.get("priority")
    if isinstance(p, dict):
        return str(p.get("name") or p.get("value") or "none")
    return str(p if p is not None else "none")


def _age_days(updated: str | None, now: datetime) -> int | None:
    if not updated:
        return None
    try:
        dt = datetime.fromisoformat(updated.replace("Z", "+00:00"))
        return (now - dt).days
    except Exception:
        return None


def analyze_issues(issues: list[dict[str, Any]], now: datetime | None = None) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    by_status: Counter[str] = Counter()
    by_status_type: Counter[str] = Counter()
    by_project: Counter[str] = Counter()
    by_label: Counter[str] = Counter()
    gh_pr: list[dict[str, Any]] = []
    done: list[dict[str, Any]] = []
    in_progress: list[dict[str, Any]] = []
    high_urgent = 0

    for issue in issues:
        st = str(issue.get("status") or "?")
        stt = str(issue.get("statusType") or "?")
        title = str(issue.get("title") or "")
        by_status[st] += 1
        by_status_type[stt] += 1
        by_project[_project(issue)] += 1
        for lab in _labels(issue):
            if lab:
                by_label[lab] += 1
        prio = _priority(issue)
        if str(prio).lower() in {"high", "urgent", "1", "2"}:
            high_urgent += 1
        row = {
            "id": issue.get("id") or issue.get("identifier"),
            "title": title[:120],
            "status": st,
            "statusType": stt,
            "priority": prio,
            "project": _project(issue),
            "labels": _labels(issue),
            "age_days": _age_days(issue.get("updatedAt") or issue.get("updated_at"), now),
        }
        if "[GitHub PR]" in title or re.search(r"GitHub\s+PR", title, re.I):
            gh_pr.append(row)
        if stt == "completed" or st.lower() == "done":
            done.append(row)
        if stt == "started" or st.lower() in {"in progress", "started"}:
            in_progress.append(row)

    open_count = sum(1 for i in issues if str(i.get("statusType")) != "completed")
    high_ratio = (high_urgent / open_count) if open_count else 0.0

    hash_cluster = [
        r
        for r in gh_pr
        if re.search(r"hash|digest|defer expensive", r["title"], re.I)
    ]

    actions: list[str] = []
    if gh_pr:
        actions.append(
            f"Review {len(gh_pr)} GitHub PR mirrors; close merged/duplicate (see hash cluster {len(hash_cluster)})."
        )
    if len(in_progress) > 8:
        actions.append(
            f"WIP high — {len(in_progress)} In Progress; demote hygiene/mirrors to Todo (cap ~8)."
        )
    if high_ratio > 0.4:
        actions.append(
            f"Priority inflation — {high_ratio:.0%} of open issues High/Urgent; deflate mirrors to Low."
        )
    if done:
        actions.append(
            f"{len(done)} Done issues in export — filter completed out of execution views."
        )

    return {
        "scanned": len(issues),
        "by_status": dict(by_status),
        "by_status_type": dict(by_status_type),
        "by_project": dict(by_project.most_common()),
        "by_label": dict(by_label.most_common(20)),
        "github_pr_mirrors": gh_pr,
        "hash_pr_cluster": hash_cluster,
        "done": [{"id": r["id"], "title": r["title"]} for r in done],
        "in_progress_count": len(in_progress),
        "high_urgent_ratio_open": round(high_ratio, 3),
        "recommended_actions": actions,
    }


def analyze_file(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        issues = raw
    elif isinstance(raw, dict):
        issues = raw.get("issues") or raw.get("data") or []
        if isinstance(issues, dict):
            issues = issues.get("issues') or []
    else:
        issues = []
    if not isinstance(issues, list):
        raise ValueError("export must be a list of issues or {issues: [...]}")
    return analyze_issues(issues)


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: analyze_board.py <issues.json>", file=sys.stderr)
        return 2
    result = analyze_file(Path(sys.argv[1]))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
