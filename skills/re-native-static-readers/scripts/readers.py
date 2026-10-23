#!/usr/bin/env python3
"""Local static readers for formats REA 6.7.0 does not expose as tools.

rea-agents 6.7.0 exposes inspect_binary_layout, inspect_pe_resources,
inspect_go_binary, inspect_rust_binary, inspect_sqlite_database, and
inspect_with_objdump live. It does NOT expose PE-certificate, ELF-note,
native-export, CPython-pyc, or Erlang-BEAM readers (those services exist
in REA's source tree but are wired to no MCP tool or CLI command in
6.7.0). This module carries those lanes locally with the same discipline:
parse declarations, preserve digests, state coverage limits, never
execute the artifact.
"""
from __future__ import annotations

import hashlib
import struct


def parse_elf_header(data: bytes) -> dict:
    """Parse an ELF header: class, endianness, type, machine, entry,
    section/program header locations. Header scope only."""
    if data[:4] != b"\x7fELF":
        raise ValueError("not an ELF file")
    ei_class = data[4]
    endian = "<" if data[5] == 1 else ">"
    is64 = ei_class == 2
    if is64:
        fields = struct.unpack_from(endian + "HHIQQQIHHHHHH", data, 16)
        (e_type, e_machine, _ver, e_entry, e_phoff, e_shoff, _flags,
         _ehsize, _phentsize, e_phnum, _shentsize, e_shnum, e_shstrndx) = fields
    else:
        fields = struct.unpack_from(endian + "HHIIIIIHHHHHH", data, 16)
        (e_type, e_machine, _ver, e_entry, e_phoff, e_shoff, _flags,
         _ehsize, _phentsize, e_phnum, _shentsize, e_shnum, e_shstrndx) = fields
    type_names = {1: "REL", 2: "EXEC", 3: "DYN", 4: "CORE"}
    return {
        "format": "elf",
        "bits": 64 if is64 else 32,
        "endian": "little" if endian == "<" else "big",
        "type": type_names.get(e_type, f"0x{e_type:x}"),
        "machine": e_machine,
        "entry": e_entry,
        "program_headers": e_phnum,
        "section_headers": e_shnum,
        "sha256": hashlib.sha256(data).hexdigest(),
        "limitations": ["header scope only; segment/section contents not interpreted"],
    }


def parse_pyc_header(data: bytes) -> dict:
    """Parse a CPython .pyc header (3.7+): magic, PEP 552 flags, and the
    hash-based or timestamp-based provenance fields. The marshal body is
    digested, never executed or decompiled."""
    if len(data) < 16:
        raise ValueError("pyc too short for a 3.7+ header")
    magic = data[:4]
    flags = struct.unpack_from("<I", data, 4)[0]
    hash_based = bool(flags & 0b1)
    check_source = bool(flags & 0b10)
    result = {
        "format": "pyc",
        "magic_hex": magic.hex(),
        "python_magic_number": struct.unpack_from("<H", magic, 0)[0],
        "pep552_flags": flags,
        "hash_based": hash_based,
        "check_source": check_source,
    }
    if hash_based:
        result["source_sha256_prefix"] = data[8:16].hex()
        result["provenance"] = "source hash (PEP 552)"
    else:
        mtime, size = struct.unpack_from("<II", data, 8)
        result["source_mtime"] = mtime
        result["source_size"] = size
        result["provenance"] = "timestamp/size (PEP 552)"
    result["bytecode_sha256"] = hashlib.sha256(data[16:]).hexdigest()
    result["limitations"] = ["bytecode is digested, not decompiled; a header never proves the matching .py exists"]
    return result


def parse_sqlite_header(data: bytes) -> dict:
    """Parse the 100-byte SQLite database header."""
    if not data.startswith(b"SQLite format 3\x00"):
        raise ValueError("not a SQLite 3 database")
    page_size = struct.unpack_from(">H", data, 16)[0]
    if page_size == 1:
        page_size = 65536
    return {
        "format": "sqlite",
        "page_size": page_size,
        "write_version": data[18],
        "read_version": data[19],
        "database_pages": struct.unpack_from(">I", data, 28)[0],
        "schema_cookie": struct.unpack_from(">I", data, 40)[0],
        "schema_format": struct.unpack_from(">I", data, 44)[0],
        "encoding": {1: "utf-8", 2: "utf-16le", 3: "utf-16be"}.get(
            struct.unpack_from(">I", data, 56)[0], "unknown"),
        "limitations": ["header scope; inspect a quiescent snapshot, never a live WAL pair assumed atomic"],
    }


def parse_beam_header(data: bytes) -> dict:
    """Parse an Erlang BEAM (IFF) header: form size and chunk inventory."""
    if data[:4] != b"FOR1" or data[8:12] != b"BEAM":
        raise ValueError("not a BEAM file")
    form_size = struct.unpack_from(">I", data, 4)[0]
    chunks = []
    offset = 12
    while offset + 8 <= len(data):
        chunk_id = data[offset:offset + 4].decode("ascii", "replace")
        chunk_size = struct.unpack_from(">I", data, offset + 4)[0]
        chunks.append({"id": chunk_id, "size": chunk_size})
        offset += 8 + chunk_size + (chunk_size % 2)
    return {
        "format": "beam",
        "form_size": form_size,
        "chunks": chunks,
        "limitations": ["chunk inventory only; bytecode is not executed"],
    }


def main(argv=None) -> int:
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Run a local static reader over a file header.")
    parser.add_argument("path")
    parser.add_argument("--reader", choices=["elf", "pyc", "sqlite", "beam"], required=True)
    args = parser.parse_args(argv)
    data = open(args.path, "rb").read()
    parse = {"elf": parse_elf_header, "pyc": parse_pyc_header,
             "sqlite": parse_sqlite_header, "beam": parse_beam_header}[args.reader]
    result = parse(data)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
