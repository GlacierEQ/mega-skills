"""Host-adapter installation semantics; does not claim host startup certification."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "install_progressive_pyramid.py"
spec = importlib.util.spec_from_file_location("install_pp", SCRIPT)
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)

class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.src = self.root / "source"
        self.home = self.root / "home"
        self.src.mkdir()
        (self.src / "SKILL.md").write_text("---\nname: progressive-pyramid\n---\n",encoding="utf-8")
        (self.src / "progressive_pyramid.contract.json").write_text(json.dumps(
            {"schema_id":"glaciereq.progressive-pyramid.contract.v1"}),encoding="utf-8")
    def test_installs_all_hosts_from_same_content(self):
        paths=installer.install(self.src,self.home,["omp","codex","claude"],"abc123")
        self.assertEqual(len(paths),3)
        self.assertEqual(installer.check(self.src,self.home,["omp","codex","claude"],"abc123"),[])
        for path in paths:
            self.assertEqual((path/".source-commit").read_text().strip(),"abc123")
    def test_does_not_overwrite_unmanaged_files(self):
        dest=self.home/".agents/skills/progressive-pyramid"
        dest.mkdir(parents=True)
        (dest/"unique.txt").write_text("existing")
        with self.assertRaises(FileExistsError):
            installer.install(self.src,self.home,["codex"],"abc123")
        self.assertEqual((dest/"unique.txt").read_text(),"existing")
    def test_refuses_incomplete_source(self):
        (self.src/"SKILL.md").unlink()
        with self.assertRaises(ValueError):
            installer.install(self.src,self.home,["omp"],"abc123")
    def test_update_preserves_prior_version_for_rollback(self):
        installer.install(self.src,self.home,["omp"],"abc123")
        (self.src/"SKILL.md").write_text("updated canonical skill")
        backups=installer.update(self.src,self.home,["omp"],"def456")
        dest=self.home/".omp/agent/managed-skills/progressive-pyramid"
        self.assertEqual((dest/".source-commit").read_text().strip(),"def456")
        self.assertTrue(any((b/"SKILL.md").read_text().startswith("---") for b in backups))
        self.assertEqual(installer.check(self.src,self.home,["omp"],"def456"),[])
    def test_update_refuses_unrecorded_local_edits(self):
        installer.install(self.src,self.home,["omp"],"abc123")
        dest=self.home/".omp/agent/managed-skills/progressive-pyramid"
        (dest/"SKILL.md").write_text("unexpected local edit")
        with self.assertRaises(ValueError):
            installer.update(self.src,self.home,["omp"],"def456")
        self.assertEqual((dest/"SKILL.md").read_text(),"unexpected local edit")
    def test_tampering_is_detected(self):
        installer.install(self.src,self.home,["omp"],"abc123")
        target=self.home/".omp/agent/managed-skills/progressive-pyramid"
        (target/"SKILL.md").write_text("tampered")
        self.assertTrue(installer.check(self.src,self.home,["omp"],"abc123"))

if __name__=="__main__":unittest.main()
