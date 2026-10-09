"""Prevent Loki agent routing from downgrading mission scope or minting approval."""
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1] / "skills/loki-mode/SKILL.md"


def test_loki_keeps_operator_mission_and_continuation():
    policy = SKILL.read_text(encoding="utf-8")
    assert "execute multiple independent authorized fronts" in policy
    assert "Both modes:** Recover Operator authority" in policy
    assert "Local responsibility never reduces the parent outcome" in policy
    assert "Scoped checkpoints without mission reduction" in policy


def test_loki_does_not_bypass_permissions_or_auto_approve():
    policy = SKILL.read_text(encoding="utf-8")
    assert "claude --dangerously-skip-permissions" not in policy
    assert "confidence >= 0.95  -->  Auto-approve" not in policy
    assert "**This system runs with ZERO human intervention.**" not in policy
    assert "Missing required authorization --> Request approval" in policy
    assert "executes autonomously within the Operator's authorized mission" in policy
