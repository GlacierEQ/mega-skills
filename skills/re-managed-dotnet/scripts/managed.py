#!/usr/bin/env python3
"""PE/CLI (managed .NET) surface parser.

Companion to REA's live inspect_managed_artifact / inspect_managed_members
(built-in rea-dotnet-static provider, verified live on 6.7.0 against a real
NuGet assembly): parse the PE headers, locate the CLI header through data
directory 14, and inventory the metadata streams. A PE with no CLI
directory is native - NativeAOT output routes to the native lanes.
"""
from __future__ import annotations

import struct

PE_SIGNATURE = b"PE\x00\x00"
METADATA_SIGNATURE = b"BSJB"


def parse_pe(data: bytes) -> dict:
    """Parse DOS/PE/COFF/optional headers and the CLI data directory."""
    if data[:2] != b"MZ":
        raise ValueError("not a PE file (no MZ signature)")
    pe_offset = struct.unpack_from("<I", data, 0x3C)[0]
    if data[pe_offset:pe_offset + 4] != PE_SIGNATURE:
        raise ValueError("not a PE file (no PE signature)")
    coff = pe_offset + 4
    machine, section_count, _ts, _symtab, _nsyms, opt_size, _chars = struct.unpack_from("<HHIIIHH", data, coff)
    opt = coff + 20
    magic = struct.unpack_from("<H", data, opt)[0]
    is64 = magic == 0x20B
    if magic not in (0x10B, 0x20B):
        raise ValueError("unknown optional-header magic 0x%x" % magic)
    dir_base = opt + (112 if is64 else 96)
    cli_rva, cli_size = struct.unpack_from("<II", data, dir_base + 14 * 8)
    sections = []
    sec_base = opt + opt_size
    for index in range(section_count):
        base = sec_base + index * 40
        name = data[base:base + 8].split(b"\x00")[0].decode("ascii", "replace")
        vsize, vaddr, raw_size, raw_ptr = struct.unpack_from("<IIII", data, base + 8)
        sections.append({"name": name, "vaddr": vaddr, "vsize": vsize,
                         "raw_ptr": raw_ptr, "raw_size": raw_size})
    result = {
        "format": "pe",
        "machine": {0x14C: "x86", 0x8664: "x86_64", 0xAA64: "arm64"}.get(machine, hex(machine)),
        "pe32_plus": is64,
        "sections": sections,
        "managed": cli_rva != 0,
        "cli_header": {"rva": cli_rva, "size": cli_size} if cli_rva else None,
    }
    if cli_rva:
        cli_offset = _rva_to_offset(sections, cli_rva)
        if cli_offset is not None:
            result["metadata"] = _parse_cli(data, sections, cli_offset)
    result["limitations"] = [
        "header/metadata scope; member inventory comes from the REA managed lane",
        "a missing CLI directory means native output (incl. NativeAOT) - route to native lanes",
    ]
    return result


def _rva_to_offset(sections, rva):
    for section in sections:
        span = max(section["vsize"], section["raw_size"])
        if section["vaddr"] <= rva < section["vaddr"] + span:
            return section["raw_ptr"] + (rva - section["vaddr"])
    return None


def _parse_cli(data, sections, cli_offset):
    _cb, _maj, _min, meta_rva, meta_size, flags = struct.unpack_from("<IHHIII", data, cli_offset)
    return {"metadata_rva": meta_rva, "metadata_size": meta_size,
            "flags": flags, "strong_name_signed": bool(flags & 0x8),
            "streams": _metadata_streams(data, sections, meta_rva)}


def _metadata_streams(data, sections, meta_rva):
    meta_offset = _rva_to_offset(sections, meta_rva)
    if meta_offset is None or data[meta_offset:meta_offset + 4] != METADATA_SIGNATURE:
        return []
    version_len = struct.unpack_from("<I", data, meta_offset + 12)[0]
    pos = meta_offset + 16 + version_len + 2
    stream_count = struct.unpack_from("<H", data, pos)[0]
    pos += 2
    streams = []
    for _ in range(stream_count):
        pos += 8  # stream offset + size
        end = data.index(b"\x00", pos)
        streams.append(data[pos:end].decode("ascii", "replace"))
        pos = end + 1
        while (pos - meta_offset) % 4:
            pos += 1
    return streams


def main(argv=None) -> int:
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Parse a PE file's managed (.NET) surface.")
    parser.add_argument("path")
    args = parser.parse_args(argv)
    result = parse_pe(open(args.path, "rb").read())
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
