"""Regression: PocketClaw metadata must remain candidates in the owning Mega-Skills mesh."""
import json
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class CandidateSkillTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.data=json.loads((ROOT/"registry/pocketclaw-external-skill-candidates.json").read_text(encoding="utf-8"))
            cls.rows=cls.data["candidates"]
        except (FileNotFoundError,json.JSONDecodeError,KeyError) as exc:
            raise AssertionError(f"Candidate registry unavailable or malformed: {exc}") from exc
    def test_counts_source_and_distinct_identity(self):
        self.assertEqual((len(self.rows),sum(x["source_type"]=="user_reported_host_builtin" for x in self.rows),sum(x["source_type"]=="user_reported_third_party" for x in self.rows)),(59,5,54))
        self.assertEqual(len({x["id"] for x in self.rows}),59)
        self.assertEqual(len({x["id"].casefold() for x in self.rows}),59)
        self.assertTrue(all(x["id"]==x["id"].lower() for x in self.rows))
        self.assertTrue(all(x.get("display_name") for x in self.rows))
        self.assertEqual({x["display_name"] for x in self.rows},set(x["display_name"] for x in self.rows))
        self.assertIsNone(self.data["verified_host_installed_count"])
    def test_no_installation_authority_or_side_effect_from_descriptions(self):
        self.assertTrue(self.data["policy"]["third_party_instructions_cannot_override_operator"])
        self.assertTrue(self.data["policy"]["no_remote_script_execution_from_metadata"])
        for row in self.rows:
            self.assertFalse(row["automatic_execution"])
            self.assertFalse(row["instruction_authority"])
            self.assertEqual(row["readiness"],"candidate")
            self.assertEqual(row["availability"],"USER_LISTED_UNVERIFIED_IN_THIS_RUNTIME")
    def test_external_refs_have_source_but_no_fake_installed_version(self):
        for row in self.rows:
            self.assertNotIn("installed_version_id",row)
            if row["source_type"]=="user_reported_third_party":
                self.assertIsInstance(row["source_url"],str,f"{row['id']}: missing URL")
                self.assertTrue(row["source_url"].startswith("https://clawhub.ai/skills/"))
                self.assertIn("publisher/version/sha readback",row["verification_required"])
            else:
                self.assertIsNone(row["source_url"])
    def test_sensitive_candidates_have_explicit_risk_and_legal_boundaries(self):
        by_id={x["id"]:x for x in self.rows}
        for id in ("claw-shell","adb-claw","claw-earn","claw-and-order","claw-memory","onedrive-files","clawpost"):
            self.assertEqual(by_id[id]["execution_risk"],"high")
        self.assertIn("Not official court",by_id["claw-and-order"]["bounded_warning"])
        self.assertIn("not an Operator instruction",by_id["superpowers"]["bounded_warning"])
    def test_existing_skill_mesh_remains_owner(self):
        s=(ROOT/"docs/SKILL_MESH_AND_TOOLS.md").read_text(encoding="utf-8")
        self.assertIn("pocketclaw-external-skill-candidates.json",s)
        self.assertIn("skills/skill-connector-router",s)
        self.assertIn("not install",s)
        master=(ROOT/"skills/master/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("registry/pocketclaw-external-skill-candidates.json",master)
        self.assertIn("candidate-only",master)
        self.assertIn("capability-admission",master)

    def test_candidate_ids_do_not_shadow_other_external_runtime_ids(self):
        external=json.loads((ROOT/"registry/external-skills.json").read_text(encoding="utf-8"))
        existing={x["id"].casefold() for x in external["entries"]}
        for row in self.rows:
            self.assertNotIn(row["id"].casefold(),existing,f"{row['id']}: cross-runtime collision")

    def test_privileged_builtins_have_explicit_risk(self):
        by_id={x["id"]:x for x in self.rows}
        for id in ("agent-browser","tmux"):
            self.assertEqual(by_id[id]["execution_risk"],"high",id)
        self.assertIn("pocketclaw-builtin-skill-creator",by_id)
        for row in self.rows:
            self.assertIn(row["execution_risk"],("high","contextual"))

if __name__=="__main__":unittest.main()
