#!/usr/bin/env python3
import importlib.util
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MODULE=ROOT/"scripts"/"career_evidence_backbone.py"
spec=importlib.util.spec_from_file_location("career_evidence_backbone",MODULE)
m=importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(m)

class CareerEvidenceBackboneTests(unittest.TestCase):
    def target(self):
        return {
            "company":"Anthropic",
            "role_family":"Applied AI",
            "primary_role":"Applied AI Architect",
            "identity":"Forward Deployed AI Architect",
            "snapshot_date":"2026-09-02",
            "freshness":{"max_source_age_days":30,"max_target_age_days":14},
            "competency_domains":["architecture","customer discovery"],
            "requirements":[
                {"id":"architecture","label":"Architecture","competencies":["architecture"],"weight":1.0,"hard_gate":True,"minimum_strength":0.55},
                {"id":"customer","label":"Customer discovery","competencies":["customer discovery"],"weight":1.0,"hard_gate":True,"minimum_strength":0.55}
            ]
        }

    def test_verified_tested_source_satisfies(self):
        src={"sources":[{"source_id":"a","state":"VERIFIED","source_kind":"source_and_tests","observed_at":"2026-09-02","locator":"x","artifact":"a@1","verification":"tested","claims":[{"claim":"built","competencies":["architecture"],"hiring_signal":5,"public_safe":True}]}]}
        ledger=m.build(self.target(),src,"2026-09-02")
        self.assertEqual(ledger["requirements"]["architecture"]["status"],"SATISFIED")

    def test_candidate_narrative_does_not_satisfy_hard_gate(self):
        src={"sources":[{"source_id":"n","state":"CANDIDATE","source_kind":"candidate_narrative","observed_at":"2026-09-02","locator":"x","artifact":"n@1","verification":"narrative","claims":[{"claim":"discovery positioning","competencies":["customer discovery"],"hiring_signal":5,"public_safe":False}]}]}
        ledger=m.build(self.target(),src,"2026-09-02")
        self.assertEqual(ledger["requirements"]["customer"]["status"],"PARTIAL")
        self.assertGreater(ledger["summary"]["hard_gates_open"],0)

    def test_stale_source_decays(self):
        src={"sources":[{"source_id":"a","state":"VERIFIED","source_kind":"source_and_tests","observed_at":"2026-01-01","locator":"x","artifact":"a@1","verification":"tested","claims":[{"claim":"built","competencies":["architecture"],"hiring_signal":5,"public_safe":True}]}]}
        ledger=m.build(self.target(),src,"2026-09-02")
        self.assertEqual(ledger["source_health"][0]["freshness_state"],"STALE")
        self.assertLess(ledger["records"][0]["proof_strength"],0.92)

    def test_private_source_cannot_enter_public_projection(self):
        src={"sources":[{"source_id":"private","state":"VERIFIED","source_kind":"runtime_receipt","observed_at":"2026-09-02","locator":"x","artifact":"p@1","verification":"receipt","project":{"name":"Private","public_safe":False},"claims":[{"claim":"secret proof","competencies":["architecture"],"hiring_signal":5,"public_safe":False}]}]}
        ledger=m.build(self.target(),src,"2026-09-02")
        p=m.project(self.target(),ledger)
        self.assertFalse(any(x["source_id"]=="private" for x in p["featured_projects"]))
        self.assertFalse(any(x["source_id"]=="private" for x in p["proof_points"]))


    def test_correlated_claims_do_not_double_count(self):
        src={"sources":[
            {"source_id":"a","independence_group":"same","state":"VERIFIED","source_kind":"source_and_tests","observed_at":"2026-09-02","locator":"x","artifact":"a@1","verification":"tested","claims":[
                {"claim":"built one","competencies":["architecture"],"hiring_signal":5,"public_safe":True},
                {"claim":"built two","competencies":["architecture"],"hiring_signal":5,"public_safe":True}
            ]}
        ]}
        ledger=m.build(self.target(),src,"2026-09-02")
        req=ledger["requirements"]["architecture"]
        self.assertAlmostEqual(req["proof_strength"],0.92,places=4)
        self.assertEqual(req["independent_groups"],["same"])

    def test_target_freshness_fails_stale_snapshot(self):
        t=self.target()
        result=m.target_check(t,"2026-10-01")
        self.assertEqual(result["status"],"STALE")

if __name__=="__main__":
    unittest.main()
