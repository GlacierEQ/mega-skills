from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ASPEN_TOKEN_AWARE = "https://github.com/GlacierEQ/aspen-grove-core/blob/main/TOKEN_AWARE_EXECUTION.md"


def test_apex_runtime_points_to_canonical_token_aware_doctrine():
    text = (ROOT / "skills/apex-sovereign-runtime/SKILL.md").read_text(encoding="utf-8")
    assert ASPEN_TOKEN_AWARE in text
    assert "depth is not verbosity" in text.lower()
    assert "executable frontier is exhausted" in text.lower()
    assert "do not duplicate" in text.lower()


def test_orchestration_applies_depth_allocation_above_compression():
    text = (ROOT / "skills/apex-orchestration/SKILL.md").read_text(encoding="utf-8")
    assert ASPEN_TOKEN_AWARE in text
    assert "depth is not verbosity" in text.lower()
    assert "criticality" in text.lower()
    assert "verification burden" in text.lower()
    assert "adaptive compression" in text.lower()
    assert "executable frontier is exhausted" in text.lower()
