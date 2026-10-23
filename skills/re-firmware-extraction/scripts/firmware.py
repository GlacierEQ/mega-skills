#!/usr/bin/env python3
"""Firmware image carving: magic scan, gzip members, cpio listings.

Local companion to REA's extract_firmware lane (verified live on 6.7.0
via caller-supplied unblob; the pip binwalk build is broken upstream -
its package raises ModuleNotFoundError for binwalk.core). This module
carries the first-pass carve locally: locate known magics at offsets,
decompress gzip members, and list cpio contents. A located region proves
bytes are present at an offset, not that a boot path reaches them.
"""
from __future__ import annotations

import gzip
import io
import struct

MAGICS = [
    (b"\x27\x05\x19\x56", "uimage"),
    (b"\x1f\x8b\x08", "gzip"),
    (b"hsqs", "squashfs_le"),
    (b"070701", "cpio_newc"),
    (b"PK\x03\x04", "zip"),
    (b"\x7fELF", "elf"),
    (b"UBI#", "ubi"),
]


def scan_magics(data: bytes) -> list[dict]:
    """Find every known magic and its offset(s)."""
    found = []
    for magic, name in MAGICS:
        start = 0
        while True:
            offset = data.find(magic, start)
            if offset < 0:
                break
            found.append({"kind": name, "offset": offset})
            start = offset + 1
    return sorted(found, key=lambda item: item["offset"])


def parse_cpio_newc(data: bytes) -> list[dict]:
    """List a newc cpio archive's entries (name, size, mode)."""
    entries = []
    pos = 0
    while data[pos:pos + 6] == b"070701":
        fields = [int(data[pos + 6 + i * 8:pos + 14 + i * 8], 16) for i in range(13)]
        _ino, mode, _uid, _gid, _nlink, _mtime, file_size = fields[0], fields[1], fields[2], fields[3], fields[4], fields[5], fields[6]
        name_size = fields[11]
        name_start = pos + 110
        name = data[name_start:name_start + name_size - 1].decode("utf-8", "replace")
        data_start = name_start + name_size
        data_start += (4 - data_start % 4) % 4
        entries.append({"name": name, "size": file_size, "mode": oct(mode)})
        pos = data_start + file_size
        pos += (4 - pos % 4) % 4
        if name == "TRAILER!!!":
            break
    return entries


def extract_gzip_member(data: bytes, offset: int) -> dict:
    """Decompress the gzip member starting at offset and, when it is a
    cpio archive, list its entries."""
    raw = gzip.decompress(data[offset:])
    result = {"offset": offset, "decompressed_bytes": len(raw),
              "sha256": __import__("hashlib").sha256(raw).hexdigest()}
    if raw[:6] == b"070701":
        result["cpio_entries"] = parse_cpio_newc(raw)
    return result


def carve(data: bytes) -> dict:
    """Full first-pass carve: regions plus decoded gzip/cpio content."""
    regions = scan_magics(data)
    decoded = []
    for region in regions:
        if region["kind"] == "gzip":
            try:
                decoded.append(extract_gzip_member(data, region["offset"]))
            except Exception as exc:  # truncated or multi-member stream
                decoded.append({"offset": region["offset"], "error": type(exc).__name__})
    return {"regions": regions, "decoded": decoded,
            "limitations": ["carve is byte-pattern scope; carved content is untrusted data"]}


def main(argv=None) -> int:
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Carve a firmware image's known regions.")
    parser.add_argument("path")
    args = parser.parse_args(argv)
    result = carve(open(args.path, "rb").read())
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
