#!/usr/bin/env python3
"""Tests for audio-forensic-core.
Structural checks plus L2 behavioral coverage: custody chaining, exhibit
pagination, court transcript formatting, ENF continuity (series and WAV
screening), alignment verification, diarization verification, and fail-closed
capability gates.
Run with: python -m unittest discover -s tests -v   (or pytest)
"""

import json
import math
import struct
import subprocess
import sys
import tempfile
import unittest
import wave
from pathlib import Path

try:
    import pytest
except ImportError:
    pytest = None

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import bates_stamper
import enf_extractor
import sha256_audit
import speaker_diarize
import transcript_formatter
import whisperx_align


def _alignment():
    return {"segments": [
        {"speaker": "SPEAKER_1", "start": 0.0, "end": 4.0, "words": [
            {"w": "Aloha", "start": 0.0, "end": 0.5},
            {"w": "court", "start": 0.6, "end": 1.0},
            {"w": "this", "start": 1.2, "end": 1.5},
            {"w": "is", "start": 1.6, "end": 1.8},
            {"w": "Casey", "start": 1.9, "end": 2.4},
            {"w": "speaking", "start": 2.5, "end": 3.0},
            {"w": "clearly", "start": 3.1, "end": 3.6},
            {"w": "today", "start": 3.7, "end": 4.0},
        ]},
        {"speaker": "SPEAKER_2", "start": 4.5, "end": 8.0, "words": [
            {"w": "Response", "start": 4.5, "end": 5.0},
            {"w": "given", "start": 5.1, "end": 5.4},
            {"w": "under", "start": 5.5, "end": 5.8},
            {"w": "oath", "start": 5.9, "end": 6.3},
            {"w": "and", "start": 6.4, "end": 6.6},
            {"w": "recorded", "start": 6.7, "end": 7.2},
            {"w": "fully", "start": 7.3, "end": 7.6},
            {"w": "here", "start": 7.7, "end": 8.0},
        ]},
    ]}


def _write_wav(path, segments, rate=8000):
    frames = []
    for freq, seconds in segments:
        for n in range(int(rate * seconds)):
            frames.append(int(12000 * math.sin(2 * math.pi * freq * n / rate)))
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(rate)
        handle.writeframes(struct.pack(f"<{len(frames)}h", *frames))


class TestAudioForensicCore:
    """Structural checks: package layout, executable scripts, resources."""

    def test_skill_entry_point_exists(self):
        skill_py = Path(__file__).parent.parent / "skill.py"
        assert skill_py.exists()
        assert skill_py.stat().st_mode & 0o111

    def test_scripts_exist(self):
        scripts_dir = Path(__file__).parent.parent / "scripts"
        expected = ['enf_extractor.py', 'whisperx_align.py', 'speaker_diarize.py', 'sha256_audit.py', 'bates_stamper.py', 'transcript_formatter.py']
        for script in expected:
            p = scripts_dir / script
            assert p.exists(), f"Missing script: {script}"
            assert p.stat().st_mode & 0o111, f"Not executable: {script}"

    def test_resources_exist(self):
        resources_dir = Path(__file__).parent.parent / "resources"
        expected = ['enf_regional_db.yaml', 'court_rules_hi_family.yaml']
        for res in expected:
            p = resources_dir / res
            assert p.exists(), f"Missing resource: {res}"

    def test_requirements_exist(self):
        req = Path(__file__).parent.parent / "requirements.txt"
        assert req.exists()


class TestAudioForensicBehavior(unittest.TestCase):
    """Behavioral coverage for the deterministic audio-forensic engines."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="afc"))

    def test_transcript_format_verify_and_word_coverage(self):
        rules = transcript_formatter.load_rules()
        text, meta = transcript_formatter.format_transcript(
            _alignment(), rules, case_number="1FDV-23-0001009",
            caption="Barton v. Barton", date="2026-09-03", source_sha256="ab" * 32)
        self.assertTrue("CASE NO.: 1FDV-23-0001009" in text)
        self.assertTrue("SPEAKER_1:" in text)
        self.assertTrue("TRANSCRIPT CERTIFICATION" in text)
        self.assertGreaterEqual(meta["body_lines"], 2)
        report = transcript_formatter.verify_transcript(text, meta, rules, _alignment())
        self.assertTrue(report["format_compliant"])
        self.assertTrue(report["numbering_sequential"])
        self.assertTrue(report["timestamps_monotonic"])
        self.assertTrue(report["word_coverage_complete"])
        tampered_alignment = _alignment()
        tampered_alignment["segments"][0]["words"].append({"w": "ZEBRA", "start": 3.8, "end": 3.9})
        gap = transcript_formatter.verify_transcript(text, meta, rules, tampered_alignment)
        self.assertFalse(gap["format_compliant"])
        self.assertTrue(any(v["kind"] == "word_coverage_gap" for v in gap["violations"]))

    def test_transcript_pagination_and_timestamp_regression(self):
        rules = transcript_formatter.load_rules()
        long_segment = {"speaker": "SPEAKER_1", "start": 0.0, "end": 60.0, "words": [
            {"w": f"word{n}", "start": float(n), "end": float(n) + 0.5} for n in range(60)
        ]}
        text, meta = transcript_formatter.format_transcript({"segments": [long_segment]}, rules)
        numbered = [line for line in text.splitlines() if line[:4].strip().isdigit()]
        self.assertTrue(len(numbered) > 1)
        self.assertGreaterEqual(meta["pages"], 1)
        regressed = {"segments": [
            {"speaker": "A", "start": 10.0, "end": 11.0, "words": [{"w": "late", "start": 10.0, "end": 10.5}]},
            {"speaker": "B", "start": 2.0, "end": 3.0, "words": [{"w": "early", "start": 2.0, "end": 2.5}]},
        ]}
        text2, meta2 = transcript_formatter.format_transcript(regressed, rules)
        report = transcript_formatter.verify_transcript(text2, meta2, rules, regressed)
        self.assertFalse(report["timestamps_monotonic"])

    def test_whisperx_alignment_verification_clean_and_dirty(self):
        clean = whisperx_align.verify_alignment(_alignment())
        self.assertTrue(clean["aligned"])
        self.assertTrue(clean["zero_drift"])
        self.assertEqual(clean["word_count"], 16)
        dirty = _alignment()
        dirty["segments"][0]["words"][2]["start"] = 0.9
        dirty["segments"][0]["words"][1]["end"] = 1.1
        dirty["segments"][0]["words"][0]["end"] = 9.9
        dirty["segments"][1]["start"] = 3.5
        report = whisperx_align.verify_alignment(dirty)
        self.assertFalse(report["aligned"])
        kinds = {v["kind"] for v in report["violations"]}
        self.assertTrue("non_monotonic_words" in kinds)
        self.assertTrue("outside_segment_bounds" in kinds)
        self.assertTrue("segment_overlap" in kinds)
        self.assertFalse(report["zero_drift"])

    def test_whisperx_extract_text_reading_order(self):
        rendered = whisperx_align.extract_text(_alignment())
        self.assertTrue(rendered.startswith("SPEAKER_1: Aloha court this is Casey speaking clearly today"))
        self.assertTrue("SPEAKER_2: Response given under oath and recorded fully here" in rendered)

    def test_diarization_verification_and_overlap_accounting(self):
        clean = {"segments": [
            {"speaker": "SPEAKER_1", "start": 0.0, "end": 4.0},
            {"speaker": "SPEAKER_2", "start": 4.5, "end": 8.0},
            {"speaker": "SPEAKER_1", "start": 8.5, "end": 10.0},
        ]}
        report = speaker_diarize.verify_segments(clean)
        self.assertTrue(report["valid"])
        self.assertTrue(report["timeline_monotonic"])
        self.assertEqual(report["speaker_count"], 2)
        self.assertAlmostEqual(report["speaking_time_seconds"]["SPEAKER_1"], 5.5)
        self.assertEqual(report["turns"]["SPEAKER_2"], 1)
        self.assertEqual(report["overlap_regions"], [])
        overlapping = {"segments": [
            {"speaker": "SPEAKER_1", "start": 0.0, "end": 5.0},
            {"speaker": "SPEAKER_2", "start": 4.0, "end": 8.0},
        ]}
        overlap_report = speaker_diarize.verify_segments(overlapping)
        self.assertEqual(len(overlap_report["overlap_regions"]), 1)
        self.assertAlmostEqual(overlap_report["total_overlap_seconds"], 1.0)

    def test_enf_series_clean_vs_spliced(self):
        clean_series = [(float(i), 60.0 + 0.001 * math.sin(i)) for i in range(30)]
        clean = enf_extractor.analyze_series(clean_series)
        self.assertEqual(clean["verdict"], "continuous")
        self.assertEqual(clean["violations"], [])
        self.assertAlmostEqual(clean["mean_hz"], 60.0, places=3)
        spliced = [(float(i), 60.0) for i in range(30)]
        spliced[10] = (10.0, 60.5)
        dirty = enf_extractor.analyze_series(spliced)
        self.assertEqual(dirty["verdict"], "tamper_suspected")
        self.assertTrue(any(v["kind"] == "splice_candidate" for v in dirty["violations"]))
        self.assertTrue(any(v["kind"] == "out_of_tolerance" for v in dirty["violations"]))

    def test_enf_wav_screening_tracks_hum_and_flags_splice(self):
        clean_wav = self.tmp / "clean.wav"
        _write_wav(clean_wav, [(60.0, 1), (60.0, 1), (60.0, 1), (60.0, 1)])
        clean = enf_extractor.analyze_wav(clean_wav)
        if clean.get("status") == "capability_blocked":
            self.assertEqual(clean["capability"], "enf-extraction")
            self.assertFalse(clean["fabricated_results"])
            self.assertTrue(clean["missing"])
            self.skipTest("WAV ENF screening requires unavailable numpy/scipy dependencies")
        self.assertEqual(clean["mode"], "wav_screening")
        self.assertFalse(clean["laboratory_certification"])
        self.assertEqual(clean["windows"], 4)
        self.assertEqual(clean["verdict"], "continuous")
        self.assertAlmostEqual(clean["mean_hz"], 60.0, delta=0.02)
        spliced_wav = self.tmp / "spliced.wav"
        _write_wav(spliced_wav, [(60.0, 1), (60.0, 1), (60.4, 1), (60.0, 1)])
        dirty = enf_extractor.analyze_wav(spliced_wav)
        self.assertEqual(dirty["verdict"], "tamper_suspected")
        self.assertTrue(any(v["kind"] == "splice_candidate" for v in dirty["violations"]))

    def test_custody_chain_build_and_tamper_detection(self):
        raw = self.tmp / "raw.m4a"
        raw.write_bytes(b"fake audio bytes for custody test")
        transcript = self.tmp / "transcript.txt"
        transcript.write_text("certified transcript body", encoding="utf-8")
        record = sha256_audit.build_chain([("raw", raw), ("transcript", transcript)])
        self.assertEqual(record["stage_count"], 2)
        self.assertEqual(len(record["chain_root_sha256"]), 64)
        self.assertEqual(record["links"][1]["previous_hash"], record["links"][0]["link_hash"])
        ok = sha256_audit.verify_chain(record)
        self.assertTrue(ok["chain_intact"])
        self.assertTrue(ok["root_match"])
        transcript.write_text("edited after sealing", encoding="utf-8")
        broken = sha256_audit.verify_chain(record)
        self.assertFalse(broken["chain_intact"])
        self.assertTrue(any(p["kind"] == "content_modified" for p in broken["problems"]))
        structural = sha256_audit.verify_chain(record, check_files=False)
        self.assertTrue(structural["chain_intact"])

    def test_bates_exhibit_pagination_plan(self):
        exhibits = {"exhibits": [
            {"id": "EX-2", "transcript_lines": 10, "path": "b.m4a"},
            {"id": "EX-1", "transcript_lines": 137, "path": "a.m4a"},
            {"id": "EX-3", "transcript_lines": 25, "path": "c.m4a"},
        ]}
        plan = bates_stamper.assign_exhibit_serials(exhibits["exhibits"], "CASE-AUDIO")
        self.assertEqual([row["bates"] for row in plan],
                         ["CASE-AUDIO-0001", "CASE-AUDIO-0002", "CASE-AUDIO-0003"])
        paginated = bates_stamper.paginate(plan, lines_per_page=25)
        self.assertEqual((paginated[0]["page_start"], paginated[0]["page_end"]), (1, 6))
        self.assertEqual((paginated[1]["page_start"], paginated[1]["page_end"]), (7, 7))
        self.assertEqual((paginated[2]["page_start"], paginated[2]["page_end"]), (8, 8))
        verdict = bates_stamper.validate_plan(paginated)
        self.assertTrue(verdict["contiguous"])
        self.assertEqual(verdict["total_pages"], 8)
        paginated[1]["page_start"] = 9
        broken = bates_stamper.validate_plan(paginated)
        self.assertTrue(any(p["kind"] == "page_gap_or_overlap" for p in broken["problems"]))

    def test_capability_gates_fail_closed_without_drivers(self):
        scripts = Path(__file__).parent.parent / "scripts"
        for script, capability in (("whisperx_align.py", "whisperx-alignment-execution"),
                                   ("speaker_diarize.py", "pyannote-speaker-diarization")):
            result = subprocess.run(
                [sys.executable, str(scripts / script), "--audio", str(self.tmp / "x.m4a")],
                capture_output=True, text=True)
            if result.returncode == 2:
                payload = json.loads(result.stdout)
                self.assertEqual(payload["status"], "capability_blocked")
                self.assertEqual(payload["capability"], capability)
                self.assertFalse(payload["fabricated_results"])
                self.assertTrue(payload["missing"])
            else:
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
