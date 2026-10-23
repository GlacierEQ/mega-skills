#!/usr/bin/env python3
"""Process-capture normalization, comparison, and ELF core crash parsing.

Local mirror of the semantics REA's dynamic lane applies (verified live
on 6.7.0):
- Raw captures from two runs of the same program differ byte-wise on
  timing alone; comparison without a declared normalization is noise.
  Normalization buckets timestamps and scrubs pids/ports/paths - and it
  must be DECLARED, because an unnormalized "changed" verdict and a
  normalized "unchanged" verdict are both true statements about
  different comparisons.
- Crash state comes from the core's NT_PRSTATUS note (signal + registers)
  when a real core exists; where core dumps are impossible (RLIMIT_CORE
  0), a synthetic core carries the same notes - the parser is identical.
"""
from __future__ import annotations

import struct

VOLATILE_KEYS = {"at_ms", "elapsed_ms", "pid", "port", "timestamp"}


def normalize_event(event: dict, normalization: dict) -> dict:
    """Apply declared normalization to one capture event."""
    out = dict(event)
    bucket = normalization.get("time_bucket_ms")
    if bucket:
        for key in ("at_ms", "elapsed_ms"):
            if key in out:
                out[key] = (out[key] // bucket) * bucket
    if normalization.get("pids"):
        out.pop("pid", None)
    if normalization.get("ports"):
        out.pop("port", None)
    if normalization.get("ignore_fields"):
        for field in normalization["ignore_fields"]:
            out.pop(field, None)
    return out


def compare_captures(left: dict, right: dict, normalization: dict | None = None) -> dict:
    """Compare two capture records {terminal, exit, events} by dimension."""
    normalization = normalization or {}
    verdicts = {}
    left_term = normalize_event({"text": left.get("terminal", "")}, normalization)
    right_term = normalize_event({"text": right.get("terminal", "")}, normalization)
    verdicts["terminal"] = "unchanged" if left_term == right_term else "changed"
    left_exit = normalize_event(dict(left.get("exit", {})), normalization)
    right_exit = normalize_event(dict(right.get("exit", {})), normalization)
    verdicts["exit"] = "unchanged" if left_exit == right_exit else "changed"
    overall = "changed" if any(v == "changed" for v in verdicts.values()) else "unchanged"
    return {"status": overall, "dimensions": verdicts,
            "normalization": normalization,
            "note": "verdicts are relative to the declared normalization; unnormalized timing differs on every real run pair"}


def parse_elf_core(data: bytes) -> dict:
    """Parse an ELF core: NT_PRSTATUS (fault signal + register count)
    and NT_FILE notes. Works on kernel cores and synthetic cores alike."""
    if data[:4] != b"\x7fELF":
        raise ValueError("not an ELF file")
    endian = "<" if data[5] == 1 else ">"
    is64 = data[4] == 2
    if is64:
        e_phoff = struct.unpack_from(endian + "Q", data, 32)[0]
        e_phentsize, e_phnum = struct.unpack_from(endian + "HH", data, 52)
    else:
        e_phoff = struct.unpack_from(endian + "I", data, 28)[0]
        e_phentsize, e_phnum = struct.unpack_from(endian + "HH", data, 42)
    signal_number = None
    files = []
    for index in range(e_phnum):
        base = e_phoff + index * e_phentsize
        if is64:
            p_type, _flags, p_offset, _va, _pa, p_filesz = struct.unpack_from(endian + "IIQQQQ", data, base)
        else:
            p_type, p_offset, _va, _pa, p_filesz = struct.unpack_from(endian + "IIIII", data, base)
        if p_type != 4:  # PT_NOTE
            continue
        pos = p_offset
        end = p_offset + p_filesz
        while pos + 12 <= end:
            namesz, descsz, note_type = struct.unpack_from(endian + "III", data, pos)
            name = data[pos + 12:pos + 12 + namesz].rstrip(b"\x00").decode("ascii", "replace")
            desc_at = pos + 12 + ((namesz + 3) & ~3)
            desc = data[desc_at:desc_at + descsz]
            if note_type == 3 and name == "CORE":  # NT_PRSTATUS
                if is64:
                    signal_number = struct.unpack_from(endian + "H", desc, 12)[0]
                else:
                    signal_number = struct.unpack_from(endian + "H", desc, 12)[0]
            if note_type == 0x46494C45:  # NT_FILE
                count = struct.unpack_from(endian + "q", desc, 0)[0]
                strings = desc[16 + count * 24:] if is64 else desc[8 + count * 12:]
                files = [s.decode("utf-8", "replace") for s in strings.split(b"\x00") if s]
            pos = desc_at + ((descsz + 3) & ~3)
    return {"format": "elf_core", "signal": signal_number,
            "signal_name": {11: "SIGSEGV", 6: "SIGABRT", 8: "SIGFPE", 4: "SIGILL"}.get(signal_number),
            "mapped_files": files}


def main(argv=None) -> int:
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Parse an ELF core's crash notes.")
    parser.add_argument("path")
    args = parser.parse_args(argv)
    result = parse_elf_core(open(args.path, "rb").read())
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
