from __future__ import annotations

import importlib.util
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "branch_lifecycle.py"
spec = importlib.util.spec_from_file_location("branch_lifecycle", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)

POLICY = {
    "version": "test",
    "stale_days": 30,
    "minimum_delete_confidence": 95,
    "protected_patterns": ["main", "release/*"],
    "family_prefixes": ["apex/", "feat/", "fix/"],
    "automatic_delete_states": ["MERGED_REDUNDANT", "REACHABLE_REDUNDANT"],
    "fail_closed_on_evidence_error": True,
}

def branch(name, *, ahead=None, protected=False, open_prs=None, merged_prs=None, errors=None, committed="2026-08-01T00:00:00Z"):
    return {
        "name": name,
        "sha": "a" * 40,
        "protected": protected,
        "head_committed_at": committed,
        "ahead_by": ahead,
        "behind_by": 0,
        "compare_status": "ahead" if ahead else "identical",
        "open_prs": open_prs or [],
        "merged_prs": merged_prs or [],
        "closed_unmerged_prs": [],
        "changed_files": [],
        "evidence_errors": errors or [],
    }

def inventory(branches):
    return {
        "schema": "glaciereq.branch-inventory.v1",
        "repository": "GlacierEQ/example",
        "default_branch": "main",
        "generated_at": "2026-09-02T12:00:00Z",
        "branches": branches,
    }

def by_name(plan):
    return {row["branch"]: row for row in plan["branches"]}

def test_merged_pr_is_high_confidence_cleanup_even_if_branch_has_unique_tip():
    plan = module.build_plan(inventory([
        branch("feat/squash-merge", ahead=3, merged_prs=[{"number": 7}]),
    ]), POLICY)
    row = by_name(plan)["feat/squash-merge"]
    assert row["state"] == "MERGED_REDUNDANT"
    assert row["action"] == "DELETE"
    assert row["cleanup_confidence"] == 100

def test_zero_ahead_is_redundant():
    plan = module.build_plan(inventory([branch("fix/already-contained", ahead=0)]), POLICY)
    row = by_name(plan)["fix/already-contained"]
    assert row["state"] == "REACHABLE_REDUNDANT"
    assert row["action"] == "DELETE"

def test_open_pr_overrides_redundancy():
    plan = module.build_plan(inventory([
        branch("feat/live", ahead=0, open_prs=[{"number": 9}]),
    ]), POLICY)
    row = by_name(plan)["feat/live"]
    assert row["state"] == "ACTIVE"
    assert row["action"] == "KEEP"

def test_evidence_error_fails_closed():
    plan = module.build_plan(inventory([
        branch("feat/uncertain", ahead=0, errors=["compare_failed"]),
    ]), POLICY)
    row = by_name(plan)["feat/uncertain"]
    assert row["state"] == "UNKNOWN_BLOCKED"
    assert row["action"] == "BLOCK"

def test_old_divergent_branch_is_review_not_delete():
    plan = module.build_plan(inventory([
        branch("apex/job-restore-old-20260801", ahead=5),
    ]), POLICY)
    row = by_name(plan)["apex/job-restore-old-20260801"]
    assert row["state"] == "STALE_REVIEW"
    assert row["action"] == "REVIEW_CONSOLIDATE"

def test_protected_pattern_never_deletes():
    plan = module.build_plan(inventory([
        branch("release/2026.09", ahead=0),
    ]), POLICY)
    row = by_name(plan)["release/2026.09"]
    assert row["state"] == "PROTECTED"
    assert row["action"] == "KEEP"

def test_family_groups_volatile_suffixes_but_does_not_auto_merge():
    plan = module.build_plan(inventory([
        branch("apex/job-restore-router-20260817", ahead=2, committed="2026-09-01T00:00:00Z"),
        branch("apex/job-restore-router-20260818", ahead=4, committed="2026-09-02T00:00:00Z"),
    ]), POLICY)
    assert len(plan["families"]) == 1
    family = plan["families"][0]
    assert family["consolidation_recommended"] is True
    assert len(family["divergent_members"]) == 2

def test_plan_is_deterministic():
    payload = inventory([
        branch("feat/a", ahead=0),
        branch("feat/b", ahead=2, committed="2026-09-02T00:00:00Z"),
    ])
    first = module.build_plan(payload, POLICY)
    second = module.build_plan(payload, POLICY)
    assert first == second
    assert len(first["plan_sha256"]) == 64
