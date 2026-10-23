"""Prove OMP skill activation preserves existing profiles and source authority."""
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

MODULE = Path(__file__).resolve().parents[1] / "scripts" / "sync_runtime_skills.py"
spec = importlib.util.spec_from_file_location("skill_sync", MODULE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class OmpNativeSyncTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.skills = root / "canonical" / "skills"
        self.combos = root / "canonical" / "combo-skills"
        self.megas = root / "canonical" / "mega-skills"
        self.target = root / "omp-profile" / "skills"
        for base, name, doc in [(self.skills, "power-skill", "SKILL.md"), (self.combos, "genius-epistemic-engineering", "COMBO.md"), (self.megas, "apex-genius-mastery", "MEGA.md")]:
            d = base / name
            d.mkdir(parents=True)
            (d / doc).write_text((f"---\nname: {name}\ndescription: Mission-specific skill execution\n---\n\n" if doc == "SKILL.md" else "") + f"# {name} authoritative source\n", encoding="utf-8")
        for name, value in [("SKILLS_DIR", self.skills), ("COMBOS_DIR", self.combos), ("MEGAS_DIR", self.megas)]:
            p = patch.object(mod, name, value)
            p.start()
            self.addCleanup(p.stop)
        self.selection = {"atomic": ["power-skill"], "compound": ["genius-epistemic-engineering"], "mega": ["apex-genius-mastery"]}

    def run_sync(self, **kwargs):
        return mod.sync_omp_skills(self.target, selection=self.selection, **kwargs)

    def test_preview_does_not_create_target_or_touch_existing_files(self):
        result = self.run_sync(apply=False)
        self.assertFalse(self.target.exists())
        self.assertEqual([item["status"] for item in result["items"]], ["planned"] * 3)
        self.assertTrue(all(item["sha256"] for item in result["items"]))

    def test_apply_installs_source_link_and_native_compound_mega_adapters(self):
        result = self.run_sync(apply=True)
        self.assertEqual(result["counts"].get("created"), 3)
        self.assertTrue((self.target / "power-skill").is_symlink())
        self.assertEqual((self.target / "power-skill").resolve(), (self.skills / "power-skill").resolve())
        for layer, name, doc in [("compound", "genius-epistemic-engineering", "COMBO.md"), ("mega", "apex-genius-mastery", "MEGA.md")]:
            adapter = self.target / name / "SKILL.md"
            self.assertTrue(adapter.is_file())
            self.assertIn(f"name: {name}", adapter.read_text())
            self.assertTrue((self.target / name / doc).is_symlink())

    def test_existing_profile_skill_is_preserved_and_reported_conflict(self):
        existing = self.target / "power-skill"
        existing.mkdir(parents=True)
        (existing / "SKILL.md").write_text("Original operator skill", encoding="utf-8")
        result = self.run_sync(apply=True)
        self.assertEqual((existing / "SKILL.md").read_text(), "Original operator skill")
        self.assertIn("conflict", [item["status"] for item in result["items"]])
        self.assertTrue(result["blocked_preflight"])
        self.assertEqual(result["counts"].get("created", 0), 0)
        self.assertFalse((self.target / "genius-epistemic-engineering").exists())
        self.assertFalse((self.target / "apex-genius-mastery").exists())

    def test_conflict_cannot_cause_partial_install(self):
        (self.target / "apex-genius-mastery").mkdir(parents=True)
        result = self.run_sync(apply=True)
        self.assertTrue(result["blocked_preflight"])
        self.assertFalse((self.target / "power-skill").exists())
        self.assertFalse((self.target / "genius-epistemic-engineering").exists())

    def test_apply_error_rolls_back_additions_without_touching_preexisting(self):
        neighbor = self.target / "custom" / "SKILL.md"
        neighbor.parent.mkdir(parents=True)
        neighbor.write_text("Operator owned", encoding="utf-8")
        original_symlink_to = Path.symlink_to

        def fails_at_second_layer(path, target, *args, **kwargs):
            if path.name == "COMBO.md":
                raise OSError("simulated disk denial")
            return original_symlink_to(path, target, *args, **kwargs)

        with patch.object(Path, "symlink_to", autospec=True, side_effect=fails_at_second_layer):
            result = self.run_sync(apply=True)
        self.assertTrue(result["verification_failed"])
        self.assertFalse((self.target / "power-skill").exists())
        self.assertFalse((self.target / "genius-epistemic-engineering").exists())
        self.assertFalse((self.target / "apex-genius-mastery").exists())
        self.assertEqual(neighbor.read_text(encoding="utf-8"), "Operator owned")
        self.assertGreaterEqual(result["counts"].get("rolled_back", 0), 1)

    def test_readback_rejects_native_skill_drift_and_rolls_back(self):
        real = mod.has_native_omp_description
        checks = {"seen": 0}

        def changed_between_reads(document):
            checks["seen"] += 1
            if checks["seen"] == 3:  # after initial planning and actual write
                return False
            return real(document)

        with patch.object(mod, "has_native_omp_description", side_effect=changed_between_reads):
            result = self.run_sync(apply=True)
        self.assertTrue(result["verification_failed"])
        self.assertFalse((self.target / "power-skill").exists())
        self.assertFalse((self.target / "genius-epistemic-engineering").exists())
        self.assertFalse((self.target / "apex-genius-mastery").exists())

    def test_idempotence_never_rewrites_identical_adapters(self):
        self.run_sync(apply=True)
        path = self.target / "apex-genius-mastery" / "SKILL.md"
        original = path.stat().st_mtime_ns
        second = self.run_sync(apply=True)
        self.assertEqual(second["counts"].get("already_present"), 3)
        self.assertEqual(path.stat().st_mtime_ns, original)

    def test_missing_source_never_manifests_a_fake_skill(self):
        selection = {"atomic": ["missing-skill"], "compound": [], "mega": []}
        result = mod.sync_omp_skills(self.target, selection=selection, apply=True)
        self.assertEqual(result["items"][0]["status"], "missing_source")
        self.assertFalse((self.target / "missing-skill").exists())

    def test_unrelated_profile_entries_survive_apply(self):
        neighbor = self.target / "operator-custom" / "SKILL.md"
        neighbor.parent.mkdir(parents=True)
        neighbor.write_text("Must survive", encoding="utf-8")
        self.run_sync(apply=True)
        self.assertEqual(neighbor.read_text(), "Must survive")

    def test_rejects_path_escape_or_ambiguous_selection(self):
        for name in ["../secrets", "/tmp/foo", "fake/child", "-x", "Bad Name"]:
            with self.subTest(name=name):
                selection = {"atomic": [name], "compound": [], "mega": []}
                with self.assertRaises(ValueError):
                    mod.sync_omp_skills(self.target, selection=selection, apply=False)

    def test_changed_canonical_adapter_is_detected_not_silently_rewritten(self):
        self.run_sync(apply=True)
        (self.combos / "genius-epistemic-engineering" / "COMBO.md").write_text("# revised authority\n")
        after = self.run_sync(apply=True)
        self.assertIn("conflict", [item["status"] for item in after["items"]])
        self.assertIn("authoritative source", (self.target / "genius-epistemic-engineering" / "SKILL.md").read_text())

    def test_other_symlink_is_not_replaced(self):
        foreign = Path(self.temp.name) / "unrelated"
        foreign.mkdir()
        self.target.mkdir(parents=True)
        (self.target / "power-skill").symlink_to(foreign, target_is_directory=True)
        after = self.run_sync(apply=True)
        self.assertEqual((self.target / "power-skill").resolve(), foreign.resolve())
        self.assertIn("conflict", [item["status"] for item in after["items"]])

    def test_atomic_without_native_omp_description_is_reported_instead_of_installed(self):
        (self.skills / "power-skill" / "SKILL.md").write_text("---\nname: power-skill\n---\n\n# content\n")
        result = self.run_sync(apply=True)
        self.assertEqual(result["items"][0]["status"], "invalid_source")
        self.assertFalse((self.target / "power-skill").exists())

    def test_native_multiline_description_is_accepted(self):
        (self.skills / "power-skill" / "SKILL.md").write_text("---\nname: power-skill\ndescription: >\n  Native agent skill in OMP\n---\n# content\n")
        result = self.run_sync(apply=False)
        self.assertEqual(result["items"][0]["status"], "planned")

    def test_default_power_coalition_is_not_arbitrarily_skill_capped(self):
        ids = [x for layer in mod.OMP_POWER_SELECTION.values() for x in layer]
        self.assertGreaterEqual(len(ids), 20)
        for name in ["power-skill", "genius-mastery", "strong-smart-routing-kernel", "systematic-debugging", "apex-genius-mastery", "far-away-party"]:
            self.assertIn(name, ids)
        self.assertIn("apex-dev-fork-orchestrator", ids)
        self.assertIn("apex-orchestrator-mesh", ids)
        self.assertNotIn("apex-repository-continuity-steward", ids)
        self.assertEqual(len(ids), len(set(ids)))


if __name__ == "__main__":
    unittest.main()
