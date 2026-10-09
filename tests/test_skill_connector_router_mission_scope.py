"""Regression contract for the mirrored mission-preserving connector router."""
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1] / "skills/skill-connector-router/SKILL.md"


def test_mirror_preserves_full_mission_composition_and_no_three_skill_ceiling():
    policy = SKILL.read_text(encoding="utf-8")
    for forbidden in (
        "Max active specialist skills per turn — 3",
        "select ≤ 3 skills",
        "Parse user intent into 1–3 mission tags",
        "Smallest sufficient set wins",
    ):
        assert forbidden not in policy
    assert "No fixed maximum on active specialists." in policy
    assert "strongest coherent mission-bearing set" in policy
    assert "every reachable authorized branch" in policy


def test_mirror_never_promotes_plan_only_or_local_block_to_completion():
    policy = SKILL.read_text(encoding="utf-8")
    assert "A plan-only result is partial" in policy
    assert "continue after any local block" in policy
    assert "provider/readback receipts" in policy
