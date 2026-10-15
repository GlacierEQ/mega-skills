"""Regression: stages that only write local run artifacts must not carry approval gates.

External effects remain governed by the firewall approval_required_for list and the
runner's forbidden command tokens; deploy-gate stages keep their approval flag.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCAL_STAGE_SCRIPTS = ("scripts/strong_smart_stage.py", "scripts/deep_work_stage.py")


class LocalStageApprovalTest(unittest.TestCase):
    def test_local_artifact_stages_are_not_approval_gated(self):
        for path in sorted((ROOT / "pipelines").glob("*.json")):
            spec = json.loads(path.read_text())
            for stage in spec["stages"]:
                if stage.get("phase", stage["id"]) == "deploy-gate":
                    continue
                cmd = " ".join(stage.get("command", []))
                if any(s in cmd for s in LOCAL_STAGE_SCRIPTS):
                    self.assertFalse(
                        stage.get("approval_required", False),
                        f"{path.name}:{stage['id']} writes local artifacts only but is approval-gated",
                    )


if __name__ == "__main__":
    unittest.main()
