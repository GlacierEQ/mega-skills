"""Adversarial tests using validated receipts, so failures are not masked by fixtures."""
import unittest

import test_completion_gate


class GateIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.fixture = test_completion_gate.GateTests(methodName="test_positive_acceptance_fixture")
        self.fixture.setUp()
        self.assertTrue(self.fixture.decision(self.fixture.valid())["accepted"])

    def tearDown(self):
        self.fixture.tearDown()

    def decide(self, mission):
        return self.fixture.decision(mission)

    def test_open_state_cannot_claim_complete(self):
        m = self.fixture.valid()
        m["state"] = "OPEN"
        self.assertIn("MISSION_NOT_VERIFIED", self.decide(m)["reasons"])

    def test_failed_state_cannot_claim_complete(self):
        m = self.fixture.valid()
        m["state"] = "FAILED"
        self.assertIn("MISSION_NOT_VERIFIED", self.decide(m)["reasons"])

    def test_boolean_provider_readback_rejected_despite_valid_receipts(self):
        m = self.fixture.valid()
        m.update(provider_mutation=True, provider_readback=True)
        self.assertIn("PROVIDER_UNVERIFIED", self.decide(m)["reasons"])

    def test_boolean_deployment_readback_rejected_despite_valid_receipts(self):
        m = self.fixture.valid()
        m.update(deployed=True, deployment_readback=True)
        self.assertIn("DEPLOYMENT_UNVERIFIED", self.decide(m)["reasons"])

    def test_required_provider_readback_rejected_without_mutation(self):
        m = self.fixture.valid()
        m["require_provider_readback"] = True
        self.assertIn("PROVIDER_UNVERIFIED", self.decide(m)["reasons"])

    def test_revision_mismatched_readback_rejected(self):
        m = self.fixture.valid()
        m.update(provider_mutation=True, provider_readback={
            "status":"confirmed", "source":"provider", "revision":"b"*40,
            "receipt_id":"provider-event-1234", "observed_at":"2026-10-23T22:00:00Z"
        })
        self.assertIn("PROVIDER_UNVERIFIED", self.decide(m)["reasons"])

    def test_structured_provider_readback_positive_fixture(self):
        m = self.fixture.valid()
        m.update(provider_mutation=True, provider_readback={
            "status":"confirmed", "source":"provider", "revision":m["revision"],
            "receipt_id":"provider-event-1234", "observed_at":"2026-10-23T22:00:00Z"
        })
        self.assertTrue(self.decide(m)["accepted"])


if __name__ == "__main__":
    unittest.main()
