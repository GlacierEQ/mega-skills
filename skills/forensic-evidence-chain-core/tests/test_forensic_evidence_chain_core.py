#!/usr/bin/env python3
"""Tests for forensic-evidence-chain-core.
Structural checks plus L2 behavioral coverage: SHA-256 determinism, manifest
tamper detection, Bates contiguity, anomaly scanning, timeline inversion
detection, duplicate-timestamp warning tiers and strict escalation, PII
scrubbing, and hash-chain integrity.
Run with: python -m unittest discover -s tests -v   (or pytest)
"""

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

try:
    import pytest
except ImportError:
    pytest = None

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import anomaly_scanner
import bates_stamper
import manifest_emitter
import pii_scrubber
import sha256_digester
import timestamp_verifier


class TestForensicEvidenceChainCore:
    """Structural checks: package layout, executable scripts, resources."""

    def test_skill_entry_point_exists(self):
        skill_py = Path(__file__).parent.parent / "skill.py"
        assert skill_py.exists()
        assert skill_py.stat().st_mode & 0o111

    def test_scripts_exist(self):
        scripts_dir = Path(__file__).parent.parent / "scripts"
        expected = ['anomaly_scanner.py', 'timestamp_verifier.py', 'sha256_digester.py', 'bates_stamper.py', 'pii_scrubber.py', 'manifest_emitter.py']
        for script in expected:
            p = scripts_dir / script
            assert p.exists(), f"Missing script: {script}"
            assert p.stat().st_mode & 0o111, f"Not executable: {script}"

    def test_resources_exist(self):
        resources_dir = Path(__file__).parent.parent / "resources"
        expected = ['bates_serial_schema.yaml', 'fre_902_compliance.md']
        for res in expected:
            p = resources_dir / res
            assert p.exists(), f"Missing resource: {res}"

    def test_requirements_exist(self):
        req = Path(__file__).parent.parent / "requirements.txt"
        assert req.exists()


class TestForensicChainBehavior(unittest.TestCase):
    """Behavioral coverage for the deterministic evidence-chain engines."""

    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="fec"))
        (self.root / "evidence.pdf").write_bytes(b"%PDF-1.4\nlegit body")
        (self.root / "notes.txt").write_text("hearing at 14:32 HST\n", encoding="utf-8")
        (self.root / "empty.bin").write_bytes(b"")
        (self.root / "dup_a.txt").write_text("duplicate content family", encoding="utf-8")
        (self.root / "dup_b.txt").write_text("duplicate content family", encoding="utf-8")
        (self.root / "fake.pdf").write_bytes(b"not actually a pdf at all")
        clean = self.root / "clean"
        clean.mkdir()
        (clean / "ok.pdf").write_bytes(b"%PDF-1.7\nclean")
        (clean / "ok.txt").write_text("clean text", encoding="utf-8")

    def test_digest_tree_sorted_and_complete(self):
        records = sha256_digester.digest_tree(self.root)
        paths = [row["path"] for row in records]
        self.assertEqual(len(records), 8)
        self.assertEqual(paths, sorted(paths))
        expected = hashlib.sha256(b"%PDF-1.4\nlegit body").hexdigest()
        row = next(r for r in records if r["path"] == "evidence.pdf")
        self.assertEqual(row["sha256"], expected)
        self.assertEqual(row["size_bytes"], len(b"%PDF-1.4\nlegit body"))
        self.assertTrue(row["mtime_utc"].endswith("+00:00"))

    def test_manifest_verify_detects_tamper_missing_added(self):
        manifest = sha256_digester.build_manifest(self.root, sha256_digester.digest_tree(self.root))
        report = sha256_digester.verify_against_manifest(self.root, manifest)
        self.assertTrue(report["verified"])
        self.assertEqual(report["checked"], 8)
        (self.root / "notes.txt").write_text("edited after sealing", encoding="utf-8")
        (self.root / "dup_b.txt").unlink()
        (self.root / "new.txt").write_text("late arrival", encoding="utf-8")
        dirty = sha256_digester.verify_against_manifest(self.root, manifest)
        self.assertFalse(dirty["verified"])
        self.assertEqual(dirty["mismatched"], ["notes.txt"])
        self.assertEqual(dirty["missing"], ["dup_b.txt"])
        self.assertEqual(dirty["added"], ["new.txt"])

    def test_bates_assignment_contiguity_collision_gap(self):
        paths = [row["path"] for row in sha256_digester.digest_tree(self.root)]
        plan = bates_stamper.assign_serials(paths, "CASE", start=1, width=6)
        self.assertEqual(plan[0]["bates"], "CASE-000001")
        self.assertEqual(plan[-1]["bates"], "CASE-000008")
        verdict = bates_stamper.validate_plan(plan)
        self.assertTrue(verdict["contiguous"])
        self.assertEqual(verdict["problems"], [])
        self.assertFalse(verdict["original_media_modified"])
        broken = [row for row in plan if row["bates"] != "CASE-000004"]
        gap = bates_stamper.validate_plan(broken)
        self.assertFalse(gap["contiguous"])
        self.assertEqual(gap["problems"][0]["kind"], "contiguity_gap")
        collided = [dict(row) for row in plan]
        collided[1]["bates"] = collided[0]["bates"]
        collision = bates_stamper.validate_plan(collided)
        self.assertTrue(any(p["kind"] == "collision" for p in collision["problems"]))

    def test_anomaly_scanner_finds_zero_magic_duplicates(self):
        report = anomaly_scanner.scan(self.root)
        kinds = {}
        for anomaly in report["anomalies"]:
            kinds.setdefault(anomaly["kind"], []).append(anomaly["path"])
        self.assertEqual(report["file_count"], 8)
        self.assertEqual(kinds.get("zero_byte"), ["empty.bin"])
        self.assertEqual(kinds.get("magic_mismatch"), ["fake.pdf"])
        self.assertTrue(any("dup_a.txt" in p for p in kinds.get("duplicate_family", [])))
        self.assertEqual(len(report["duplicate_groups"]), 1)
        clean_report = anomaly_scanner.scan(self.root / "clean")
        self.assertEqual(clean_report["anomaly_count"], 0)

    def test_timestamp_inversions_duplicates_and_order(self):
        ordered = {"events": [
            {"id": "filed", "timestamp": "2026-06-30T23:54:00Z"},
            {"id": "noticed", "timestamp": "2026-07-01T02:10:00Z"},
        ]}
        ok = timestamp_verifier.verify_events(ordered)
        self.assertTrue(ok["verified"])
        self.assertEqual(ok["parsed_count"], 2)
        self.assertEqual(len(ok["events_normalized"]), 2)
        inverted = {"events": [
            {"id": "denied", "timestamp": "2026-07-06T10:00:00Z"},
            {"id": "filed", "timestamp": "2026-06-30T23:54:00Z"},
        ]}
        bad = timestamp_verifier.verify_events(inverted)
        self.assertFalse(bad["verified"])
        self.assertEqual(bad["problems"][0]["kind"], "chronological_inversion")
        dupes = {"events": [
            {"id": "a", "timestamp": "2026-07-06T10:00:00Z"},
            {"id": "b", "timestamp": "2026-07-06T10:00:00+00:00"},
        ]}
        dup_report = timestamp_verifier.verify_events(dupes)
        self.assertTrue(dup_report["verified"])
        self.assertTrue(any(w["kind"] == "duplicate_timestamp" for w in dup_report["warnings"]))
        self.assertEqual(dup_report["problems"], [])

    def test_timestamp_cli_strict_mode_escalates_warnings(self):
        scripts = Path(__file__).parent.parent / "scripts"
        events_path = self.root / "events.json"
        events_path.write_text(json.dumps({"events": [
            {"id": "a", "timestamp": "2026-07-02"},
            {"id": "b", "timestamp": "2026-07-02"},
        ]}), encoding="utf-8")
        relaxed = subprocess.run(
            [sys.executable, str(scripts / "timestamp_verifier.py"),
             "--events", str(events_path)],
            capture_output=True, text=True)
        self.assertEqual(relaxed.returncode, 0, relaxed.stdout + relaxed.stderr)
        self.assertTrue(json.loads(relaxed.stdout)["warnings"])
        strict = subprocess.run(
            [sys.executable, str(scripts / "timestamp_verifier.py"),
             "--events", str(events_path), "--strict"],
            capture_output=True, text=True)
        self.assertEqual(strict.returncode, 1)

    def test_pii_scan_redacts_without_leaking_values(self):
        pii_file = self.root / "filing.txt"
        pii_file.write_text(
            "contact person@example.com or 808-555-1234; ssn 123-45-6789 on line one\n",
            encoding="utf-8")
        report = pii_scrubber.scan_tree(self.root)
        kinds = {f["kind"] for row in report["files"] for f in row["findings"]}
        self.assertTrue({"ssn", "email", "phone"}.issubset(kinds))
        report_text = json.dumps(report)
        self.assertFalse("123-45-6789" in report_text)
        self.assertFalse("person@example.com" in report_text)
        self.assertEqual(report["values_copied_into_report"], 0)
        out_dir = self.root / "redacted"
        written = pii_scrubber.redact_tree(self.root, out_dir)
        target = out_dir / "filing.txt"
        self.assertTrue(target.is_file())
        redacted = target.read_text(encoding="utf-8")
        self.assertTrue("[REDACTED-SSN]" in redacted)
        self.assertFalse("123-45-6789" in redacted)
        self.assertEqual(pii_file.read_text(encoding="utf-8"),
                         "contact person@example.com or 808-555-1234; ssn 123-45-6789 on line one\n")
        self.assertTrue(all(row["derivative"] for row in written))

    def test_manifest_hash_chain_integrity_and_tamper(self):
        digests = sha256_digester.build_manifest(self.root, sha256_digester.digest_tree(self.root))
        plan = bates_stamper.assign_serials([r["path"] for r in digests["files"]], "CASE")
        anomalies = anomaly_scanner.scan(self.root)
        manifest, timeline = manifest_emitter.emit(digests, {"plan": plan}, anomalies, None)
        self.assertEqual(manifest["entry_count"], 11)
        self.assertEqual(len(manifest["chain_root_sha256"]), 64)
        check = manifest_emitter.verify_chain(manifest["entries"], manifest["chain_root_sha256"])
        self.assertTrue(check["chain_intact"])
        self.assertTrue(check["root_match"])
        tampered = json.loads(json.dumps(manifest))
        tampered["entries"][2]["sha256"] = "f" * 64
        broken = manifest_emitter.verify_chain(tampered["entries"], tampered["chain_root_sha256"])
        self.assertFalse(broken["chain_intact"])
        self.assertFalse(broken["root_match"])
        self.assertEqual(timeline["row_count"], 8)

    def test_cli_end_to_end_digest_and_chain_verify(self):
        scripts = Path(__file__).parent.parent / "scripts"
        out_dir = Path(tempfile.mkdtemp(prefix="fec-out"))
        manifest_path = out_dir / "digests.json"
        result = subprocess.run(
            [sys.executable, str(scripts / "sha256_digester.py"),
             "--root", str(self.root), "--out", str(manifest_path)],
            capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["file_count"], 8)
        self.assertEqual(manifest["algorithm"], "sha256")
        verify = subprocess.run(
            [sys.executable, str(scripts / "sha256_digester.py"),
             "--root", str(self.root), "--verify", str(manifest_path)],
            capture_output=True, text=True)
        self.assertEqual(verify.returncode, 0, verify.stdout + verify.stderr)
        payload = json.loads(verify.stdout)
        self.assertTrue(payload["verified"])
        sealed_then_dirty = subprocess.run(
            [sys.executable, str(scripts / "sha256_digester.py"),
             "--root", str(self.root), "--verify", str(manifest_path)],
            capture_output=True, text=True)
        self.assertEqual(sealed_then_dirty.returncode, 0)


if __name__ == "__main__":
    unittest.main()
