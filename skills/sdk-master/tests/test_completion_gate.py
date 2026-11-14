"""Adversarial acceptance-gate tests. Synthetic fixture receipts do not imply provider execution."""
import hashlib
import importlib.util
import json
import pathlib
import tempfile
import unittest

p = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "completion_gate.py"
spec = importlib.util.spec_from_file_location("completion_gate", p)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)
REV = "a" * 40


class GateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        (self.root / "evidence").mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def valid(self):
        criteria = {}
        for key in g.REQUIRED:
            kind = "runtime" if key in g.OPERATIONAL else "test"
            receipt = {"criterion": key, "revision": REV, "status": "passed", "kind": kind,
                       "executor": "unit-test-fixture", "run_id": "synthetic-positive", "finished_at": "2026-10-23T22:00:00Z",
                       "command": "fixture", "exit_code": 0}
            data = json.dumps(receipt, sort_keys=True).encode()
            rel = f"evidence/{key}.json"
            (self.root / rel).write_bytes(data)
            criteria[key] = {"status": "passed", "revision": REV, "kind": kind,
                             "evidence": {"path": rel, "sha256": hashlib.sha256(data).hexdigest()}}
        return {"state": "VERIFIED", "revision": REV, "ci": "passed",
                "criteria": criteria, "outstanding_actions": [], "unresolved_defects": []}

    def decision(self, mission):
        return g.decide(mission, receipt_root=self.root)

    def test_positive_acceptance_fixture(self):
        self.assertTrue(self.decision(self.valid())["accepted"])

    def test_open_state_cannot_complete(self):
        m = self.valid(); m["state"] = "OPEN"
        self.assertFalse(self.decision(m)["accepted"])

    def test_forged_receipt_string_cannot_complete(self):
        m = self.valid(); m["criteria"]["real_execution"]["evidence"] = "receipt://imaginary"
        self.assertFalse(self.decision(m)["accepted"])

    def test_missing_criterion(self):
        m = self.valid(); del m["criteria"]["integration"]
        self.assertFalse(self.decision(m)["accepted"])

    def test_static_integration_rejected(self):
        m = self.valid(); m["criteria"]["integration"]["kind"] = "static"
        self.assertFalse(self.decision(m)["accepted"])

    def test_mock_only_rejected(self):
        m = self.valid(); m["criteria"]["real_execution"]["kind"] = "mock"
        self.assertFalse(self.decision(m)["accepted"])

    def test_receipt_tamper_rejected(self):
        m = self.valid(); (self.root / "evidence/tests.json").write_text('{"forged":true}')
        self.assertIn("RECEIPT_HASH_MISMATCH:tests", self.decision(m)["reasons"])

    def test_path_traversal_rejected(self):
        m = self.valid(); m["criteria"]["tests"]["evidence"]["path"] = "evidence/../../secret.json"
        self.assertFalse(self.decision(m)["accepted"])

    def test_wrong_revision_inside_receipt_rejected(self):
        m = self.valid(); path = self.root / "evidence/tests.json"; body = json.loads(path.read_text()); body["revision"] = "b"*40
        data = json.dumps(body).encode(); path.write_bytes(data)
        m["criteria"]["tests"]["evidence"]["sha256"] = hashlib.sha256(data).hexdigest()
        self.assertIn("RECEIPT_BINDING_MISMATCH:tests", self.decision(m)["reasons"])

    def test_missing_provider_readback(self):
        m = self.valid(); m["provider_mutation"] = True
        self.assertFalse(self.decision(m)["accepted"])

    def test_failed_ci(self):
        m = self.valid(); m["ci"] = "failed"
        self.assertFalse(self.decision(m)["accepted"])

    def test_stale_revision(self):
        m = self.valid(); m["criteria"]["tests"]["revision"] = "b"*40
        self.assertFalse(self.decision(m)["accepted"])

    def test_unresolved_defect(self):
        m = self.valid(); m["unresolved_defects"] = ["broken retry"]
        self.assertFalse(self.decision(m)["accepted"])

    def test_interrupted(self):
        m = self.valid(); m["interrupted"] = True
        self.assertFalse(self.decision(m)["accepted"])

    def test_ambiguous_mutation(self):
        m = self.valid(); m["ambiguous_mutation"] = True
        self.assertFalse(self.decision(m)["accepted"])

    def test_draft_not_deployed(self):
        m = self.valid(); m["claims_complete"] = True; m["draft_only"] = True
        self.assertFalse(self.decision(m)["accepted"])

    def test_missing_deployment_readback(self):
        m = self.valid(); m["deployed"] = True
        self.assertFalse(self.decision(m)["accepted"])

    def test_outstanding_actions(self):
        m = self.valid(); m["outstanding_actions"] = ["live provider readback"]
        self.assertFalse(self.decision(m)["accepted"])

    def test_malformed_evidence_record(self):
        m = self.valid(); m["criteria"]["tests"]["evidence"] = {"path":"evidence/tests.json", "sha256": "123"}
        self.assertFalse(self.decision(m)["accepted"])

    def test_missing_receipt_file(self):
        m = self.valid(); (self.root / "evidence/tests.json").unlink()
        self.assertFalse(self.decision(m)["accepted"])

    def test_no_receipt_root(self):
        self.assertFalse(g.decide(self.valid())["accepted"])


if __name__ == "__main__":
    unittest.main()
