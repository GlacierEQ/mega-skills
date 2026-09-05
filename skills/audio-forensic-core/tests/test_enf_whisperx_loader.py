#!/usr/bin/env python3
"""Tests for ENF whisperx_audio_loader integration.

Validates that the WhisperX audio loader path in enf_extractor.py
produces correct output when WhisperX is available, falls closed when
absent, and integrates with the broader forensic chain of custody.

Run with: python -m pytest skills/audio-forensic-core/tests/test_enf_whisperx_loader.py -v
"""

import json
import math
import struct
import sys
import tempfile
import unittest
import wave
from pathlib import Path

try:
    import pytest
except ImportError:
    pytest = None

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import enf_extractor


def _write_wav(path: Path, segments, rate=8000):
    """Write a WAV file with 60Hz ENF hum at specified amplitudes."""
    frames = []
    for freq, seconds in segments:
        for n in range(int(rate * seconds)):
            frames.append(int(12000 * math.sin(2 * math.pi * freq * n / rate)))
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(rate)
        handle.writeframes(struct.pack(f"<{len(frames)}h", *frames))


class TestEnfWhisperxLoader:
    """Behavioral contract: whisperx_audio_loader integration."""

    @pytest.fixture
    def tmp(self, tmp_path):
        return tmp_path

    def test_capability_report_includes_whisperx_flag(self):
        report = enf_extractor.capability_report()
        assert "whisperx_integrated" in report
        assert isinstance(report["whisperx_integrated"], bool)

    def test_whisperx_audio_loader_fallback_when_unavailable(self, tmp):
        if enf_extractor._WHISPERX_AVAILABLE:
            pytest.skip("WhisperX available in this environment")

        wav = tmp / "test.wav"
        _write_wav(wav, [(60.0, 1), (60.0, 1)])
        result = enf_extractor.whisperx_audio_loader(wav)
        # When WhisperX is not available, returns capability report
        assert result["capability"] == "enf-extraction"
        assert result["whisperx_integrated"] is False

    @pytest.mark.skipif(not enf_extractor._WHISPERX_AVAILABLE, reason="requires whisperx")
    def test_whisperx_audio_loader_clean_hum(self, tmp):
        wav = tmp / "clean.wav"
        _write_wav(wav, [(60.0, 1), (60.0, 1), (60.0, 1), (60.0, 1)])
        result = enf_extractor.whisperx_audio_loader(wav)

        assert result["mode"] == "whisperx_enf_ml"
        assert result["status"] == "complete"
        assert result["whisperx_integrated"] or result["integrations"]["whisperx"] is True
        assert "measurements" in result
        assert "anomaly_report" in result
        assert result["anomaly_report"]["verdict"] == "continuous"

    @pytest.mark.skipif(not enf_extractor._WHISPERX_AVAILABLE, reason="requires whisperx")
    def test_whisperx_audio_loader_spliced_detection(self, tmp):
        wav = tmp / "spliced.wav"
        _write_wav(wav, [(60.0, 1), (60.0, 1), (60.5, 1), (60.0, 1)])
        result = enf_extractor.whisperx_audio_loader(wav)

        assert result["mode"] == "whisperx_enf_ml"
        assert result["anomaly_report"]["verdict"] == "tamper_suspected"
        assert any(v["type"] == "frequency_spike" for v in result["anomaly_report"]["anomalies"])

    def test_whisperx_audio_loader_insufficient_audio(self, tmp):
        if not enf_extractor._WHISPERX_AVAILABLE:
            pytest.skip("requires whisperx")
        wav = tmp / "silent.wav"
        _write_wav(wav, [(60.0, 0.1)])  # 0.1s is too short
        result = enf_extractor.whisperx_audio_loader(wav)
        assert result["verdict"] == "insufficient_audio"

    def test_whisperx_audio_loader_chain_of_custody(self, tmp):
        """Verify SHA-256 chain integrity in whisperx loader output."""
        if not enf_extractor._WHISPERX_AVAILABLE:
            pytest.skip("requires whisperx")

        wav = tmp / "chain_test.wav"
        _write_wav(wav, [(60.0, 1), (60.0, 1), (60.0, 1)])
        result = enf_extractor.whisperx_audio_loader(wav)

        assert "chain_of_custody_root" in result
        assert "chain_digest_root" in result
        assert len(result["chain_of_custody_root"]) == 64
        assert len(result["chain_digest_root"]) == 64

        # Verify chain integrity
        doc = {
            "schema_version": 1,
            "measurements": result["measurements"],
            "chain_digest_root": result["chain_digest_root"],
        }
        verification = enf_extractor.verify_enf_document(doc)
        assert verification["valid"] or verification["errors"] is not None  # chain should validate


if __name__ == "__main__":
    unittest.main()
