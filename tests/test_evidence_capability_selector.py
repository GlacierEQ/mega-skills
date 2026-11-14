"""Evidence selector vs lexical baseline on a fixed fixture.

Weights are imported from the module under test. These cases lock the
acceptance behavior: degrading skills are not injected, exact ids still
resolve, and the fixed coalition is not treated as task evidence.
"""
from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SELECTOR = load("evidence_capability_selector", ROOT / "scripts" / "evidence_capability_selector.py")
RUNTIME = load("capability_runtime", ROOT / "scripts" / "capability_runtime.py")


def entry(identifier, **overrides):
    packet = {
        "id": identifier,
        "display_name": identifier.replace("-", " ").title(),
        "maturity": "active",
        "version": "1.2.0",
        "ownership": "glaciereq",
        "entrypoint": f"skills/{identifier}/SKILL.md",
        "purpose": overrides.pop("purpose", identifier.replace("-", " ")),
    }
    packet.update(overrides)
    return packet


def assay(identifier, state, **overrides):
    ready = state in {"behavior_verified", "instruction_ready", "composition_ready", "mission_contract_ready"}
    row = {
        "id": identifier,
        "layer": "skill",
        "ready": ready,
        "state": state,
        "instruction_ready": state == "instruction_ready" or state == "behavior_verified",
        "real_implementation_files": ["skills/%s/skill.py" % identifier] if state == "behavior_verified" else [],
        "behavioral_tests": ["skills/%s/tests/test_skill.py" % identifier] if state == "behavior_verified" else [],
        "reasons": [],
    }
    row.update(overrides)
    return row


class EvidenceSelectorTest(unittest.TestCase):
    def setUp(self):
        import tempfile
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        registry = self.root / "registry"
        registry.mkdir()
        skills = {
            "entries": [
                entry("verify-tests-before-claiming-completion", description="verify tests before claiming completion"),
                entry("verification-before-completion", description="check completion claims"),
                entry("test-driven-development", description="write a failing test first"),
                entry("diagnosing-bugs", description="diagnosing bugs quickly"),
                entry("software-development-guide", description="development notes without executable checks"),
                entry("autonomous-software-engineering", description="ship verified software changes"),
            ]
        }
        (registry / "skills.json").write_text(json.dumps(skills), encoding="utf-8")
        (registry / "combo-skills.json").write_text(json.dumps({"entries": [
            entry("genius-epistemic-engineering", entrypoint="combo-skills/genius-epistemic-engineering/COMBO.md")
        ]}), encoding="utf-8")
        (registry / "mega-skills.json").write_text(json.dumps({"entries": []}), encoding="utf-8")
        readiness = {
            "skills": [
                assay("verify-tests-before-claiming-completion", "implementation_missing"),
                assay("verification-before-completion", "behavior_verified"),
                assay("test-driven-development", "behavior_verified"),
                assay("diagnosing-bugs", "implementation_unverified", instruction_ready=False),
                assay("software-development-guide", "instruction_ready"),
                assay("systematic-debugging", "instruction_ready"),
                assay("autonomous-software-engineering", "behavior_verified"),
            ],
            "combos": [assay("genius-epistemic-engineering", "composition_ready", layer="combo")],
            "megas": [],
        }
        (registry / "skill-readiness.json").write_text(json.dumps(readiness), encoding="utf-8")
        for identifier in (
            "verification-before-completion",
            "test-driven-development",
            "systematic-debugging",
            "software-development-guide",
            "autonomous-software-engineering",
        ):
            path = self.root / "skills" / identifier / "SKILL.md"
            path.parent.mkdir(parents=True)
            path.write_text("---\nname: %s\ndescription: fixture\n---\n" % identifier, encoding="utf-8")
        self.coalition = {
            "atomic": ["systematic-debugging", "test-driven-development"],
            "compound": ["genius-epistemic-engineering"],
            "mega": [],
        }

    def tearDown(self):
        self._tmp.cleanup()

    def test_missing_assay_fails_closed(self):
        (self.root / "registry" / "skill-readiness.json").unlink()
        with self.assertRaises(SELECTOR.EvidenceUnavailable):
            SELECTOR.select_evidence_aware(self.root, "verification", runtime=RUNTIME)

    def test_degrading_lexical_winner_is_not_activated(self):
        lexical = RUNTIME.resolve_capabilities(self.root, "verify tests before claiming completion", limit=5)
        self.assertEqual(lexical["capability_packets"][0]["id"], "verify-tests-before-claiming-completion")
        evidence = SELECTOR.select_evidence_aware(self.root, "verify tests before claiming completion", limit=5, runtime=RUNTIME)
        self.assertNotIn("verify-tests-before-claiming-completion", evidence["selected_ids"])
        self.assertEqual(evidence["selected_ids"][0], "verification-before-completion")
        self.assertFalse(evidence["activation_performed"])

    def test_unverified_trap_is_not_injected(self):
        lexical = RUNTIME.resolve_capabilities(self.root, "diagnosing bugs", limit=5)
        self.assertIn("diagnosing-bugs", [item["id"] for item in lexical["capability_packets"]])
        evidence = SELECTOR.select_evidence_aware(self.root, "diagnosing bugs", limit=5, runtime=RUNTIME)
        self.assertNotIn("diagnosing-bugs", evidence["selected_ids"])

    def test_exact_id_override_is_flagged_not_hidden(self):
        evidence = SELECTOR.select_evidence_aware(self.root, "diagnosing-bugs", limit=5, runtime=RUNTIME)
        self.assertEqual(evidence["selected_ids"], ["diagnosing-bugs"])
        self.assertTrue(evidence["selected"][0]["operator_exact_override"])
        self.assertEqual(evidence["selected"][0]["state"], "implementation_unverified")

    def test_missing_source_file_blocks_non_exact_selection(self):
        evidence = SELECTOR.select_evidence_aware(self.root, "verify-tests-before-claiming-completion", limit=3, runtime=RUNTIME)
        self.assertEqual(evidence["selected_ids"], ["verify-tests-before-claiming-completion"])
        self.assertTrue(evidence["selected"][0]["operator_exact_override"])
        broad = SELECTOR.select_evidence_aware(self.root, "verify tests before claiming completion", limit=5, runtime=RUNTIME)
        self.assertNotIn("verify-tests-before-claiming-completion", broad["selected_ids"])

    def test_verified_peer_beats_instruction_only_on_shared_tokens(self):
        evidence = SELECTOR.select_evidence_aware(self.root, "development", limit=5, runtime=RUNTIME)
        self.assertEqual(evidence["selected_ids"][0], "test-driven-development")
        self.assertEqual(evidence["selected"][0]["state"], "behavior_verified")

    def test_fixed_tasks_improve_hit_rate_and_cut_forbidden_injection(self):
        tasks = [
            {"id": "verify", "query": "verify tests before claiming completion", "relevant": ["verification-before-completion"], "forbidden_ids": ["verify-tests-before-claiming-completion"]},
            {"id": "trap", "query": "diagnosing bugs", "relevant": [], "forbidden_ids": ["diagnosing-bugs"]},
            {"id": "outside-coalition", "query": "autonomous software engineering", "relevant": ["autonomous-software-engineering"], "forbidden_ids": []},
            {"id": "tdd", "query": "test driven development", "relevant": ["test-driven-development"], "forbidden_ids": []},
        ]
        report = SELECTOR.compare_tasks(self.root, tasks, limit=5, coalition=self.coalition, runtime=RUNTIME)
        summary = report["summary"]
        self.assertGreaterEqual(summary["evidence_gold_hits"], summary["lexical_gold_hits"])
        self.assertGreater(summary["evidence_gold_hits"], summary["coalition_gold_hits"])
        self.assertLess(summary["evidence_forbidden_total"], summary["lexical_forbidden_total"])
        self.assertLess(summary["evidence_mean_selected"], summary["coalition_selected"])
        trap = next(item for item in report["tasks"] if item["id"] == "trap")
        self.assertEqual(trap["evidence_forbidden"], [])
        self.assertIn("diagnosing-bugs", trap["lexical_forbidden"])

    def test_selection_is_deterministic_and_omp_shaped(self):
        first = SELECTOR.select_evidence_aware(self.root, "engineering", limit=4, runtime=RUNTIME)
        second = SELECTOR.select_evidence_aware(self.root, "engineering", limit=4, runtime=RUNTIME)
        self.assertEqual(first["selected_ids"], second["selected_ids"])
        self.assertEqual(set(first["omp_selection"]), {"atomic", "compound", "mega"})

    def test_empty_query_and_limit_rejected(self):
        with self.assertRaises(ValueError):
            SELECTOR.select_evidence_aware(self.root, "   ", runtime=RUNTIME)
        with self.assertRaises(ValueError):
            SELECTOR.select_evidence_aware(self.root, "engineering", limit=0, runtime=RUNTIME)

    def test_baseline_module_still_ranks_lexically(self):
        lexical = RUNTIME.resolve_capabilities(self.root, "verify tests before claiming completion", limit=1)
        self.assertEqual(lexical["capability_packets"][0]["id"], "verify-tests-before-claiming-completion")
        self.assertGreaterEqual(lexical["capability_packets"][0]["match_score"], 100)


if __name__ == "__main__":
    unittest.main()
