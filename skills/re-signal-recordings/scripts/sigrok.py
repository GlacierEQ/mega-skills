#!/usr/bin/env python3
"""Sigrok session (.sr) reading: metadata, edges, UART decode.

REA's signal lane (inspect_signal_recording et al.) requires a
caller-supplied sigrok-cli 0.7.2 via REA_SIGROK_COMMAND; where that tool
is absent, this module carries the lane locally: a .sr file is a zip
holding a `metadata` file (samplerate, unitsize, probe names) and raw
`logic-1-<n>` chunks. From the raw samples it extracts per-probe edges
and decodes asynchronous serial (UART) bytes at a stated baud. Decoded
bytes are what the waveform carries, at the stated sample rate - a wrong
baud or rate yields wrong bytes, so both are recorded with the result.
"""
from __future__ import annotations

import configparser
import io
import zipfile


def parse_sr(data: bytes) -> dict:
    """Read a sigrok session's metadata and raw logic samples."""
    archive = zipfile.ZipFile(io.BytesIO(data))
    names = archive.namelist()
    meta_text = archive.read("metadata").decode("utf-8", "replace")
    config = configparser.ConfigParser()
    config.read_string(meta_text)
    device = config["device 1"] if config.has_section("device 1") else {}
    samplerate = device.get("samplerate", "0")
    rate_hz = _parse_rate(samplerate)
    unitsize = int(device.get("unitsize", "1"))
    probes = {}
    for key, value in device.items():
        if key.startswith("probe"):
            probes[int(key[5:])] = value
    logic = b""
    for name in sorted(n for n in names if n.startswith("logic-1-")):
        logic += archive.read(name)
    return {
        "format": "sigrok",
        "samplerate_hz": rate_hz,
        "unitsize": unitsize,
        "probes": probes,
        "total_probes": int(device.get("total probes", "0") or 0),
        "samples": len(logic) // unitsize if unitsize else 0,
        "logic": logic,
    }


def _parse_rate(text: str) -> int:
    text = text.strip()
    if text.endswith(" MHz"):
        return int(float(text[:-4]) * 1_000_000)
    if text.endswith(" kHz"):
        return int(float(text[:-4]) * 1_000)
    if text.endswith(" Hz"):
        return int(float(text[:-3]))
    return int(text or 0)


def channel_samples(session: dict, probe_index: int) -> list[int]:
    """Extract one probe's bit stream from packed logic samples."""
    logic, unitsize = session["logic"], session["unitsize"]
    bits = []
    for start in range(0, len(logic) - unitsize + 1, unitsize):
        sample = int.from_bytes(logic[start:start + unitsize], "little")
        bits.append((sample >> (probe_index - 1)) & 1)
    return bits


def edges(bits: list[int]) -> list[dict]:
    """Return transition points (index, direction) in a bit stream."""
    found = []
    for index in range(1, len(bits)):
        if bits[index] != bits[index - 1]:
            found.append({"at_sample": index,
                          "direction": "rising" if bits[index] else "falling"})
    return found


def decode_uart(session: dict, probe_index: int, baud: int) -> dict:
    """Decode 8N1 UART from a probe's bit stream (idle-high, LSB first)."""
    bits = channel_samples(session, probe_index)
    samples_per_bit = session["samplerate_hz"] / baud
    decoded = []
    index = 1
    while index < len(bits):
        if bits[index - 1] == 1 and bits[index] == 0:  # start bit edge
            center = index + samples_per_bit * 1.5
            value = 0
            for bit_index in range(8):
                sample_at = int(center + bit_index * samples_per_bit)
                if sample_at >= len(bits):
                    value = None
                    break
                value |= bits[sample_at] << bit_index
            if value is None:
                break
            decoded.append(value)
            index = int(center + 8 * samples_per_bit)
        else:
            index += 1
    return {
        "baud": baud,
        "samples_per_bit": samples_per_bit,
        "bytes": decoded,
        "text": bytes(decoded).decode("ascii", "replace"),
        "limitations": ["8N1 assumed; framing errors are not detected at this scope"],
    }


def main(argv=None) -> int:
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Read a sigrok session and decode a UART probe.")
    parser.add_argument("path")
    parser.add_argument("--probe", type=int, default=1)
    parser.add_argument("--baud", type=int, default=9600)
    args = parser.parse_args(argv)
    session = parse_sr(open(args.path, "rb").read())
    summary = {k: v for k, v in session.items() if k != "logic"}
    summary["edges"] = edges(channel_samples(session, args.probe))
    summary["uart"] = decode_uart(session, args.probe, args.baud)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
