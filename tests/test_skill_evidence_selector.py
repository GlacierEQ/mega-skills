"""Fixture proof for the evidence-aware OMP selector versus static baselines."""
from __future__ import annotations

import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SELECTOR_PATH = ROOT / "scripts" / "skill_evidence_selector.py"
SYNC_PATH = ROOT / "scripts" / "sync_runtime_skills.py"
FIXTURE_PATH = ROOT / "tests" / "fixtures" / "skill_selection_tasks.json"
LEDGER_PATH = ROOT / "evidence" / "skill-selection" / "ledger.json"
APPLE = {
    "desktop-commander-overview",
    "re-apple-bundles",
    "swiftui-patterns",
    "swift-concurrency-6-2",
    "xcode-project-setup",
    "mobile-design",
    "foundation-models-on-device",
    "ios-icon-gen",
}


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None or not hasattr(spec.loader, "exec_module"):
        raise RuntimeError(f"unable to load module {name!r} from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SELECTOR = load_module("skill_evidence_selector", SELECTOR_PATH)
SYNC = load_module("skill_sync_for_selector", SYNC_PATH)


def flatten(coalition: dict) -> list[str]:
    return [skill_id for layer in ("atomic", "compound", "mega") for skill_id in coalition[layer]]


def static_ids(selection: dict) -> list[str]:
    return [skill_id for layer in ("atomic", "compound", "mega") for skill_id in selection[layer]]


def expected_ids(match: str) -> list[str]:
    coalition = SELECTOR.b1_coalition()
    if match == "B1":
        return flatten(coalition)
    if match.startswith("B1+"):
        skill_id = match[3:]
        coalition[_layer_of(skill_id)].append(skill_id)
        return flatten(coalition)
    if match.startswith("B1-"):
        skill_id = match[3:]
        for layer in coalition:
            coalition[layer] = [item for item in coalition[layer] if item != skill_id]
        return flatten(coalition)
    raise AssertionError(match)


def _layer_of(skill_id: str) -> str:
    registry = load_registry()
    found = registry.resolve(skill_id)
    if not isinstance(found, SELECTOR.SkillRecord):
        raise AssertionError(skill_id)
    return found.layer


_REGISTRY = None


def load_registry():
    global _REGISTRY
    if _REGISTRY is None:
        needed = set(SELECTOR.b1_ids()) | APPLE | {
            "lint-and-validate",
            "mega-gcp-data-engineering",
            "long-horizon-core",
            "not-in-registry-skill",
        }
        _REGISTRY = SELECTOR.materialize(SELECTOR.load_registry(ROOT), needed)
    return _REGISTRY


def pr_counts(predicted: set[str], gold: set[str]) -> tuple[int, int, int]:
    true_positive = len(predicted & gold)
    return true_positive, len(predicted), len(gold)


def ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


class SkillEvidenceSelectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger_bytes = LEDGER_PATH.read_bytes()
        cls.ledger = json.loads(cls.ledger_bytes)
        cls.fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        cls.registry = load_registry()
        cls.receipts = {}
        for task in cls.fixture["tasks"]:
            if task.get("expect", {}).get("error"):
                continue
            cls.receipts[task["id"]] = SELECTOR.select_coalition(task, cls.ledger, cls.registry)

    def tearDown(self):
        self.assertEqual(LEDGER_PATH.read_bytes(), self.ledger_bytes)

    def test_duplicate_task_id_is_not_reported_as_missing(self):
        task = {
            "id": "same-id",
            "intent": "Repair a failing Python unit test.",
            "domain_tags": ["python", "repair"],
            "required_artifacts": ["tests/test_widget.py"],
            "task_family": "python-repair",
        }
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "tasks.json"
            path.write_text(json.dumps({"tasks": [task, dict(task)]}), encoding="utf-8")
            with self.assertRaises(ValueError) as duplicate:
                SELECTOR.load_task(path, "same-id")
            self.assertIn("duplicate task id: same-id", str(duplicate.exception))
            self.assertNotIn("not found", str(duplicate.exception))
            with self.assertRaises(ValueError) as missing:
                SELECTOR.load_task(path, "absent-id")
            self.assertIn("task id not found: absent-id", str(missing.exception))

    def test_ledger_is_fixture_seed_only(self):
        self.assertEqual(self.ledger["schema_version"], 1)
        self.assertTrue(self.ledger["append_only"])
        self.assertFalse(self.ledger["production_outcomes"])
        self.assertGreaterEqual(len(self.ledger["entries"]), 8)
        self.assertEqual(len(self.ledger["entries"]), len({row["entry_id"] for row in self.ledger["entries"]}))
        for row in self.ledger["entries"]:
            self.assertEqual(row["provenance"], "fixture-seed")
            self.assertFalse(row["production_outcome"])
            self.assertIn("not a production outcome", row["label"])
            SELECTOR.reject_skill_id(row["skill_id"])

    def test_labeled_tasks_match_gold_and_report_precision_recall(self):
        self.assertGreaterEqual(len(self.fixture["tasks"]), 8)
        self.assertLessEqual(len(self.fixture["tasks"]), 12)
        b1 = set(SELECTOR.b1_ids())
        b2 = set(static_ids(SYNC.OMP_POWER_SELECTION))
        self.assertEqual(len(b1), 30)
        self.assertEqual(len(b2), 38)
        self.assertEqual(b2 - b1, APPLE)
        totals = {name: [0, 0, 0] for name in ("B1", "T1", "B2")}
        scored = 0
        generic = self.receipts["py-repair-generic"]["skill_ids"]
        followup = self.receipts["py-repair-followup"]["skill_ids"]
        self.assertEqual(generic, followup)
        self.assertEqual(self.receipts["python-lint-win"]["skill_ids"], self.receipts["python-lint-reuse"]["skill_ids"])
        for task in self.fixture["tasks"]:
            expect = task["expect"]
            if expect.get("error"):
                with self.assertRaises(ValueError) as caught:
                    SELECTOR.select_coalition(task, self.ledger, self.registry)
                self.assertIn(expect["error"], str(caught.exception))
                continue
            receipt = self.receipts[task["id"]]
            gold = expected_ids(expect["match"])
            self.assertEqual(receipt["decision"], expect["decision"])
            self.assertEqual(receipt["skill_ids"], gold)
            self.assertEqual(receipt["profile_writes"], 0)
            self.assertLessEqual(len(receipt["skill_ids"]), len(b1) + expect.get("allowed_extra", 0))
            withheld = {item["id"] for item in receipt["withheld"]}
            self.assertTrue(set(expect.get("withhold", [])).issubset(withheld))
            self.assertEqual(sorted(item["id"] for item in receipt["excluded"]), sorted(expect.get("exclude", [])))
            if "task_family" in expect:
                self.assertEqual(receipt["task_family"], expect["task_family"])
            if "refuse" in expect:
                refused = {item["id"] for item in receipt["refused"]}
                self.assertTrue(set(expect["refuse"]).issubset(refused))
                for skill_id in expect["refuse"]:
                    self.assertNotIn(skill_id, receipt["skill_ids"])
            if not task.get("score", True):
                continue
            scored += 1
            predicted = {
                "B1": b1,
                "T1": set(receipt["skill_ids"]),
                "B2": b2,
            }
            gold_set = set(gold)
            for name, chosen in predicted.items():
                true_positive, predicted_count, gold_count = pr_counts(chosen, gold_set)
                totals[name][0] += true_positive
                totals[name][1] += predicted_count
                totals[name][2] += gold_count
        self.assertGreaterEqual(scored, 8)
        metrics = {}
        for name, (true_positive, predicted_count, gold_count) in totals.items():
            metrics[name] = {
                "precision": ratio(true_positive, predicted_count),
                "recall": ratio(true_positive, gold_count),
                "true_positive": true_positive,
                "predicted": predicted_count,
                "gold": gold_count,
            }
        print(
            "FIXTURE_METRICS "
            f"tasks={scored} "
            f"B1 precision={metrics['B1']['precision']:.6f} recall={metrics['B1']['recall']:.6f} "
            f"tp={metrics['B1']['true_positive']}/{metrics['B1']['predicted']} gold={metrics['B1']['gold']} "
            f"T1 precision={metrics['T1']['precision']:.6f} recall={metrics['T1']['recall']:.6f} "
            f"tp={metrics['T1']['true_positive']}/{metrics['T1']['predicted']} gold={metrics['T1']['gold']} "
            f"B2 precision={metrics['B2']['precision']:.6f} recall={metrics['B2']['recall']:.6f} "
            f"tp={metrics['B2']['true_positive']}/{metrics['B2']['predicted']} gold={metrics['B2']['gold']}"
        )
        self.assertEqual(metrics["T1"]["precision"], 1)
        self.assertEqual(metrics["T1"]["recall"], 1)
        self.assertLess(metrics["B1"]["precision"], 1)
        self.assertLess(metrics["B1"]["recall"], 1)
        self.assertLess(metrics["B2"]["precision"], metrics["T1"]["precision"])
        self.assertLess(metrics["B2"]["recall"], 1)

    def test_generic_repair_does_not_inflate_past_b1(self):
        receipt = self.receipts["py-repair-generic"]
        self.assertEqual(receipt["coalition"], SELECTOR.b1_coalition())
        self.assertEqual(receipt["added"], [])
        self.assertEqual(receipt["decision"], "evidence")
        self.assertEqual(len(receipt["skill_ids"]), 30)

    def test_same_family_reuses_ledger_without_a_new_bundle(self):
        self.assertEqual(
            self.receipts["py-repair-generic"]["coalition"],
            self.receipts["py-repair-followup"]["coalition"],
        )
        self.assertEqual(
            self.receipts["python-lint-win"]["added"],
            self.receipts["python-lint-reuse"]["added"],
        )

    def test_irrelevant_large_specialists_are_withheld(self):
        receipt = self.receipts["py-withhold-specialists"]
        chosen = set(receipt["skill_ids"])
        self.assertNotIn("desktop-commander-overview", chosen)
        self.assertNotIn("mega-gcp-data-engineering", chosen)
        self.assertTrue(APPLE.isdisjoint(chosen))
        reasons = {item["id"]: item["reason"] for item in receipt["withheld"]}
        self.assertEqual(reasons["mega-gcp-data-engineering"], "no positive benefit")
        self.assertEqual(reasons["desktop-commander-overview"], "no positive benefit")
        raw = json.loads(self.ledger_bytes)
        prestige = [row for row in raw["entries"] if row["skill_id"] == "mega-gcp-data-engineering"]
        self.assertTrue(all(row.get("catalog_prestige", 0) >= 90 for row in prestige))

    def test_macos_task_adds_one_apple_atomic_already_on_main(self):
        receipt = self.receipts["macos-swiftui"]
        extra = set(receipt["skill_ids"]) - set(SELECTOR.b1_ids())
        self.assertEqual(extra, {"swiftui-patterns"})
        self.assertEqual(set(receipt["added"]), {"swiftui-patterns"})
        self.assertIn("swiftui-patterns", APPLE)
        self.assertTrue(isinstance(self.registry.resolve("swiftui-patterns", "atomic"), SELECTOR.SkillRecord))
        self.assertTrue(self.registry.resolve("swiftui-patterns", "atomic").native_description)

    def test_harmful_skill_is_excluded(self):
        receipt = self.receipts["harmful-exclusion"]
        self.assertEqual([item["id"] for item in receipt["excluded"]], ["make-it-heavy"])
        self.assertNotIn("make-it-heavy", receipt["skill_ids"])
        self.assertEqual(len(receipt["skill_ids"]), 29)
        self.assertEqual(receipt["decision"], "evidence")

    def test_insufficient_evidence_falls_back_to_b1_and_records_no_evidence(self):
        receipt = self.receipts["evidence-insufficient"]
        self.assertEqual(receipt["decision"], "no evidence")
        self.assertEqual(receipt["coalition"], SELECTOR.b1_coalition())
        self.assertEqual(receipt["skill_ids"], SELECTOR.b1_ids())
        self.assertEqual(receipt["added"], [])
        self.assertEqual(receipt["excluded"], [])
        self.assertEqual(receipt["evidence_rows_used"], 0)

    def test_path_escape_and_missing_source_are_refused(self):
        for raw in ("../secrets", "/tmp/foo", "fake/child", "-x", "Bad Name", "skills/power-skill"):
            with self.subTest(skill_id=raw):
                with self.assertRaises(ValueError):
                    SELECTOR.reject_skill_id(raw)
                with self.assertRaises(ValueError):
                    SYNC.sync_omp_skills(Path(tempfile.mkdtemp()) / "skills",
                                         selection={"atomic": [raw], "compound": [], "mega": []},
                                         apply=False)
        poisoned = json.loads(self.ledger_bytes)
        poisoned["entries"] = list(poisoned["entries"]) + [{
            "entry_id": "seed-path-escape",
            "provenance": "fixture-seed",
            "production_outcome": False,
            "label": "fixture seed, not a production outcome",
            "task_family": "python-repair",
            "skill_id": "../secrets",
            "outcome": "pass",
            "regressions": 0,
            "wall_time_ms": 1,
        }]
        with self.assertRaises(ValueError):
            SELECTOR.validate_ledger(poisoned)
        missing = self.receipts["missing-source"]
        self.assertEqual(missing["decision"], "no evidence")
        self.assertEqual(missing["coalition"], SELECTOR.b1_coalition())
        self.assertIn({"id": "not-in-registry-skill", "reason": "not_in_registry"}, missing["refused"])
        target = Path(tempfile.mkdtemp()) / "omp-skills"
        result = SYNC.sync_omp_skills(
            target,
            selection={"atomic": ["not-in-registry-skill"], "compound": [], "mega": []},
            apply=True,
        )
        self.assertTrue(result["blocked_preflight"])
        self.assertEqual(result["items"][0]["status"], "missing_source")
        self.assertFalse((target / "not-in-registry-skill").exists())

    def test_profile_collision_still_blocks_apply(self):
        receipt = self.receipts["profile-collision"]
        self.assertEqual(receipt["coalition"], SELECTOR.b1_coalition())
        target = Path(tempfile.mkdtemp()) / "omp-skills"
        existing = target / "power-skill"
        existing.mkdir(parents=True)
        (existing / "SKILL.md").write_text("operator owned profile skill", encoding="utf-8")
        result = SYNC.sync_omp_skills(target, selection=receipt["coalition"], apply=True)
        self.assertTrue(result["blocked_preflight"])
        self.assertEqual((existing / "SKILL.md").read_text(encoding="utf-8"), "operator owned profile skill")
        self.assertEqual(result["counts"].get("created", 0), 0)
        self.assertFalse((target / "systematic-debugging").exists())

    def test_append_only_guard_and_ambiguous_id(self):
        rows = self.ledger["entries"]
        SELECTOR.assert_append_only(rows, list(rows))
        extra = dict(rows[-1])
        extra["entry_id"] = "seed-appended-observation"
        SELECTOR.assert_append_only(rows, list(rows) + [extra])
        changed = list(rows)
        changed[0] = dict(changed[0], outcome="fail")
        with self.assertRaises(ValueError):
            SELECTOR.assert_append_only(rows, changed)
        with self.assertRaises(ValueError):
            SELECTOR.assert_append_only(rows, rows[:-1])
        task = {
            "id": "ambiguous-skill",
            "intent": "Do not add an id that exists in two registry layers.",
            "domain_tags": ["python"],
            "required_artifacts": ["src/helper.py"],
            "task_family": "ambiguous-layer",
        }
        ledger = {
            "schema_version": 1,
            "append_only": True,
            "entries": [{
                "entry_id": "seed-ambiguous-long-horizon",
                "provenance": "fixture-seed",
                "production_outcome": False,
                "label": "fixture seed, not a production outcome",
                "task_family": "ambiguous-layer",
                "skill_id": "long-horizon-core",
                "outcome": "pass",
                "regressions": 0,
                "wall_time_ms": 10,
            }],
        }
        receipt = SELECTOR.select_from_documents(ROOT, task, ledger)
        self.assertEqual(receipt["decision"], "no evidence")
        self.assertEqual(receipt["coalition"], SELECTOR.b1_coalition())
        self.assertIn({"id": "long-horizon-core", "reason": "ambiguous_registry_id"}, receipt["refused"])
        mega = self.registry.resolve("far-away-party", "mega")
        self.assertIsInstance(mega, SELECTOR.SkillRecord)
        self.assertEqual(mega.cost_bytes, (ROOT / "mega-skills" / "far-away-party" / "MEGA.md").stat().st_size)

    def test_size_and_prestige_do_not_replace_a_measured_benefit(self):
        records = []
        for layer, skill_ids in SELECTOR.B1_COALITION.items():
            for skill_id in skill_ids:
                records.append(SELECTOR.SkillRecord(
                    id=skill_id, layer=layer, contract_ref=f"{layer}/{skill_id}",
                    cost_bytes=100, native_description=True,
                ))
        records.append(SELECTOR.SkillRecord(
            id="mega-gcp-data-engineering", layer="atomic", contract_ref="skills/mega-gcp-data-engineering/SKILL.md",
            cost_bytes=177578, native_description=True,
        ))
        registry = SELECTOR.Registry(records)

        def observe(outcome: str, wall_time_ms: int, regressions: int, **flags):
            ledger = {
                "schema_version": 1,
                "entries": [{
                    "entry_id": "seed-size-probe",
                    "provenance": "fixture-seed",
                    "production_outcome": False,
                    "label": "fixture seed, not a production outcome",
                    "task_family": "size-probe",
                    "skill_id": "mega-gcp-data-engineering",
                    "outcome": outcome,
                    "regressions": regressions,
                    "wall_time_ms": wall_time_ms,
                    "catalog_prestige": 1000,
                    **flags,
                }],
            }
            task = {
                "intent": "Probe whether size or prestige can buy admission.",
                "domain_tags": ["python"],
                "required_artifacts": ["src/helper.py"],
                "task_family": "size-probe",
            }
            return SELECTOR.select_coalition(task, ledger, registry)

        clean = observe("pass", 100, 0)
        self.assertEqual(clean["added"], ["mega-gcp-data-engineering"])
        failed = observe("fail", 30000, 1)
        self.assertEqual(failed["added"], [])
        self.assertEqual(failed["withheld"][0]["reason"], "no positive benefit")
        slow = observe("pass", 250000, 0)
        self.assertEqual(slow["added"], [])
        regressing = observe("pass", 10, 3)
        self.assertEqual(regressing["added"], [])
        harmful = observe("pass", 10, 0, harmful=True)
        self.assertEqual(harmful["added"], [])
        self.assertEqual(harmful["withheld"][0]["reason"], "harmful")

    def test_cost_proxy_matches_selected_contract_bytes(self):
        receipt = self.receipts["evidence-insufficient"]
        expected = 0
        for layer, directory, document in (
            ("atomic", "skills", "SKILL.md"),
            ("compound", "combo-skills", "COMBO.md"),
            ("mega", "mega-skills", "MEGA.md"),
        ):
            for skill_id in SELECTOR.B1_COALITION[layer]:
                expected += (ROOT / directory / skill_id / document).stat().st_size
        self.assertEqual(receipt["cost_bytes"], expected)
        macos = self.receipts["macos-swiftui"]
        swiftui_bytes = (ROOT / "skills" / "swiftui-patterns" / "SKILL.md").stat().st_size
        self.assertEqual(macos["cost_bytes"], expected + swiftui_bytes)
        self.assertGreater(
            (ROOT / "skills" / "mega-gcp-data-engineering" / "SKILL.md").stat().st_size,
            swiftui_bytes,
        )

    def test_opt_in_evidence_path_reuses_installer_and_default_stays_static(self):
        with tempfile.TemporaryDirectory() as temp:
            static_dir = Path(temp) / "static"
            evidence_dir = Path(temp) / "evidence"
            static_out = io.StringIO()
            with redirect_stdout(static_out):
                SYNC.main(["--runtime", "omp", "--omp-skills-dir", str(static_dir)])
            static = json.loads(static_out.getvalue())
            self.assertEqual(
                [item["name"] for item in static["items"]],
                static_ids(SYNC.OMP_POWER_SELECTION),
            )
            self.assertNotIn("selector", static)
            self.assertFalse(static_dir.exists())
            evidence_out = io.StringIO()
            with redirect_stdout(evidence_out):
                SYNC.main([
                    "--runtime", "omp",
                    "--omp-skills-dir", str(evidence_dir),
                    "--select", "evidence",
                    "--task-json", str(FIXTURE_PATH),
                    "--task-id", "evidence-insufficient",
                    "--ledger", str(LEDGER_PATH),
                ])
            evidence = json.loads(evidence_out.getvalue())
            self.assertEqual([item["name"] for item in evidence["items"]], SELECTOR.b1_ids())
            self.assertEqual(evidence["selector"]["decision"], "no evidence")
            self.assertEqual(evidence["selector"]["baseline_id"], "B1")
            self.assertEqual(evidence["counts"].get("planned"), 30)
            self.assertFalse(evidence_dir.exists())
            with self.assertRaises(SystemExit):
                SYNC.main(["--select", "evidence", "--task-json", str(FIXTURE_PATH), "--task-id", "evidence-insufficient"])


if __name__ == "__main__":
    unittest.main()
