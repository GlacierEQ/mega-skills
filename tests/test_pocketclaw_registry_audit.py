"""Source-bound candidate-only inspection for the existing Mega-Skills master registry."""
import copy
import json
import unittest
from pathlib import Path
from scripts.audit_external_skill_candidates import CatalogIntegrityError, audit_catalog

REGISTRY = Path(__file__).resolve().parents[1] / "registry/pocketclaw-external-skill-candidates.json"


class ExternalSkillCatalogAudit(unittest.TestCase):
    def setUp(self):
        self.catalog=json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_original_inventory_is_not_an_installation_receipt(self):
        report=audit_catalog(self.catalog)
        self.assertEqual(report["candidate_count"],59)
        self.assertEqual(report["builtin_count"],5)
        self.assertEqual(report["third_party_count"],54)
        self.assertEqual(report["runtime_installed_verified_count"],0)
        self.assertEqual(report["effective_permission_changes"],0)
        self.assertEqual(report["state"],"SOURCE_INVENTORY_ONLY")
        self.assertEqual(report["high_risk_count"],26)

    def test_source_display_names_survive_noncolliding_ids(self):
        report=audit_catalog(self.catalog)
        names={x["display_name"] for x in self.catalog["candidates"]}
        self.assertTrue({"Law","legal","Legal","Claw-List"}.issubset(names))
        self.assertEqual(len(report["canonical_ids"]),59)
        self.assertEqual(len({s.casefold() for s in report["canonical_ids"]}),59)

    def test_high_risk_candidates_remain_uneffected(self):
        report=audit_catalog(self.catalog)
        self.assertIn("adb-claw",report["high_risk_candidate_ids"])
        self.assertIn("claw-shell",report["high_risk_candidate_ids"])
        self.assertIn("claw-earn",report["high_risk_candidate_ids"])
        self.assertFalse(report["host_auto_activation_proven"])

    def test_rejects_casefold_collision_without_losing_original_names(self):
        other=copy.deepcopy(self.catalog)
        other["candidates"][1]["id"]=other["candidates"][0]["id"].upper()
        with self.assertRaisesRegex(CatalogIntegrityError,"duplicate"):
            audit_catalog(other)

    def test_rejects_false_installed_claim_and_instruction_authority(self):
        for field,value in [("installed_version_id","sha-aabb"),("automatic_execution",True),("instruction_authority",True),("readiness","active")]:
            other=copy.deepcopy(self.catalog)
            other["candidates"][0][field]=value
            with self.subTest(field=field),self.assertRaises(CatalogIntegrityError):
                audit_catalog(other)

    def test_rejects_null_and_unsafe_remote_urls(self):
        for bad in [None,"http://clawhub.ai/skills/agent-browser","https://clawhub.ai.evil.test/skills/foo","https://clawhub.ai/skills/test?token=secret","https://user:secret@clawhub.ai/skills/x"]:
            other=copy.deepcopy(self.catalog)
            third=next(x for x in other["candidates"] if x["source_type"]=="user_reported_third_party")
            third["source_url"]=bad
            with self.subTest(url=bad),self.assertRaises(CatalogIntegrityError):
                audit_catalog(other)

    def test_refuses_invented_verified_host_count(self):
        other=copy.deepcopy(self.catalog)
        other["verified_host_installed_count"]=59
        with self.assertRaisesRegex(CatalogIntegrityError,"host"):
            audit_catalog(other)

    def test_category_selection_is_observation_not_restricted_skill_ceiling(self):
        report=audit_catalog(self.catalog,categories=("legal","engineering"))
        self.assertEqual(report["candidate_count"],59)
        self.assertGreater(len(report["matching_candidate_ids"]),3)
        self.assertTrue(all(x in report["canonical_ids"] for x in report["matching_candidate_ids"]))
        self.assertFalse(report["host_auto_activation_proven"])

if __name__=="__main__":
    unittest.main()
