#!/usr/bin/env python3
"""Deterministic ENF screening helpers for timestamp continuity review."""

from __future__ import annotations

import argparse
import json
import math
import struct
import sys
import wave
from pathlib import Path
from typing import Iterable, Sequence

DEFAULT_FREQUENCY_HZ = 60.0
DEFAULT_TOLERANCE_HZ = 0.1
DEFAULT_JUMP_HZ = 0.25


def _number(value: object, field: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be numeric") from exc
    if not math.isfinite(result):
        raise ValueError(f"{field} must be finite")
    return result


def analyze_series(
    samples: Iterable[Sequence[float]],
    nominal_hz: float = DEFAULT_FREQUENCY_HZ,
    tolerance_hz: float = DEFAULT_TOLERANCE_HZ,
    jump_hz: float = DEFAULT_JUMP_HZ,
) -> dict:
    """Screen timestamp/frequency pairs for ENF continuity.

    This is a screening result, not a laboratory or source-authentication
    conclusion. A large adjacent change is reported separately from a value
    outside the configured nominal band so callers can preserve both facts.
    """
    nominal = _number(nominal_hz, "nominal_hz")
    tolerance = _number(tolerance_hz, "tolerance_hz")
    jump = _number(jump_hz, "jump_hz")
    if tolerance < 0 or jump < 0:
        raise ValueError("tolerance_hz and jump_hz must be non-negative")

    normalized = []
    for index, sample in enumerate(samples):
        if len(sample) != 2:
            raise ValueError(f"sample {index} must contain timestamp and frequency")
        normalized.append({
            "timestamp": _number(sample[0], f"sample {index} timestamp"),
            "frequency_hz": _number(sample[1], f"sample {index} frequency"),
        })

    violations = []
    for index, sample in enumerate(normalized):
        delta = sample["frequency_hz"] - nominal
        if abs(delta) > tolerance:
            violations.append({
                "kind": "out_of_tolerance",
                "index": index,
                "timestamp": sample["timestamp"],
                "frequency_hz": sample["frequency_hz"],
                "nominal_hz": nominal,
                "delta_hz": delta,
            })
        if index:
            previous = normalized[index - 1]
            change = sample["frequency_hz"] - previous["frequency_hz"]
            if abs(change) > jump:
                violations.append({
                    "kind": "splice_candidate",
                    "index": index,
                    "timestamp": sample["timestamp"],
                    "from_hz": previous["frequency_hz"],
                    "to_hz": sample["frequency_hz"],
                    "jump_hz": change,
                })

    frequencies = [sample["frequency_hz"] for sample in normalized]
    mean_hz = sum(frequencies) / len(frequencies) if frequencies else None
    return {
        "mode": "series_screening",
        "sample_count": len(normalized),
        "nominal_hz": nominal,
        "tolerance_hz": tolerance,
        "mean_hz": mean_hz,
        "violations": violations,
        "verdict": "tamper_suspected" if violations else "continuous",
        "laboratory_certification": False,
    }


def _decode_pcm(raw: bytes, sample_width: int) -> list[float]:
    """Decode little-endian PCM into normalized samples."""
    if sample_width == 1:
        return [(byte - 128) / 128.0 for byte in raw]
    if sample_width == 2:
        count = len(raw) // 2
        values = struct.unpack(f"<{count}h", raw[: count * 2])
        return [value / 32768.0 for value in values]
    if sample_width == 3:
        values = []
        for offset in range(0, len(raw) - 2, 3):
            chunk = raw[offset : offset + 3]
            value = int.from_bytes(chunk + (b"\xff" if chunk[2] & 0x80 else b"\x00"), "little", signed=True)
            values.append(value / 8388608.0)
        return values
    if sample_width == 4:
        count = len(raw) // 4
        values = struct.unpack(f"<{count}i", raw[: count * 4])
        return [value / 2147483648.0 for value in values]
    raise ValueError(f"unsupported PCM sample width: {sample_width} bytes")


def _frequency_from_window(samples: Sequence[float], sample_rate: int) -> float | None:
    """Estimate dominant hum with interpolated rising zero crossings."""
    if len(samples) < 4 or sample_rate <= 0:
        return None
    crossings = []
    previous = float(samples[0])
    for index in range(1, len(samples)):
        current = float(samples[index])
        if previous <= 0.0 < current:
            denominator = current - previous
            fraction = (-previous / denominator) if denominator else 0.0
            crossings.append((index - 1) + fraction)
        previous = current
    if len(crossings) < 2:
        return None
    periods = len(crossings) - 1
    span = crossings[-1] - crossings[0]
    if span <= 0:
        return None
    return periods * sample_rate / span


def analyze_wav(
    path: str | Path,
    nominal_hz: float = DEFAULT_FREQUENCY_HZ,
    tolerance_hz: float = DEFAULT_TOLERANCE_HZ,
    jump_hz: float = DEFAULT_JUMP_HZ,
) -> dict:
    """Screen one-second windows of a PCM WAV for ENF continuity."""
    source = Path(path)
    with wave.open(str(source), "rb") as handle:
        channels = handle.getnchannels()
        sample_width = handle.getsampwidth()
        sample_rate = handle.getframerate()
        frame_count = handle.getnframes()
        raw = handle.readframes(frame_count)
    if channels < 1:
        raise ValueError("WAV has no audio channels")
    decoded = _decode_pcm(raw, sample_width)
    if channels > 1:
        decoded = [sum(decoded[i : i + channels]) / channels for i in range(0, len(decoded), channels)]
    window_size = max(1, sample_rate)
    series = []
    for start in range(0, len(decoded), window_size):
        window = decoded[start : start + window_size]
        if len(window) < window_size:
            break
        frequency = _frequency_from_window(window, sample_rate)
        if frequency is not None:
            series.append((start / sample_rate, frequency))
    result = analyze_series(series, nominal_hz, tolerance_hz, jump_hz)
    result.update({
        "mode": "wav_screening",
        "source": str(source),
        "sample_rate_hz": sample_rate,
        "channels": channels,
        "duration_seconds": frame_count / sample_rate if sample_rate else 0.0,
        "windows": len(series),
        "laboratory_certification": False,
    })
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Screen WAV ENF continuity and emit JSON.")
    parser.add_argument("audio", nargs="?", type=Path)
    parser.add_argument("--nominal-hz", type=float, default=DEFAULT_FREQUENCY_HZ)
    parser.add_argument("--tolerance-hz", type=float, default=DEFAULT_TOLERANCE_HZ)
    parser.add_argument("--jump-hz", type=float, default=DEFAULT_JUMP_HZ)
    args = parser.parse_args(argv)
    if args.audio is None:
        parser.error("an audio WAV path is required")
    try:
        report = analyze_wav(args.audio, args.nominal_hz, args.tolerance_hz, args.jump_hz)
    except (OSError, ValueError, wave.Error) as exc:
        print(json.dumps({"status": "input_error", "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())