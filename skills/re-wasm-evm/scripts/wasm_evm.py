#!/usr/bin/env python3
"""WASM module and EVM dispatcher surface parsers.

Local companions to REA's live inspect_wasm_artifact / inspect_evm_interface
/ compare_wasm_interfaces tools (verified live on rea-agents 6.7.0): parse
the module's section inventory and exported interface, and extract an EVM
runtime's PUSH4 selector table. Interface scope only — exported names and
selectors prove what a contract/module declares, not what its code does.
"""
from __future__ import annotations

import struct

SECTION_NAMES = {0: "custom", 1: "type", 2: "import", 3: "function", 4: "table",
                 5: "memory", 6: "global", 7: "export", 8: "start", 9: "element",
                 10: "code", 11: "data", 12: "datacount"}


def _uleb(data: bytes, offset: int) -> tuple[int, int]:
    value = 0
    shift = 0
    while True:
        byte = data[offset]
        offset += 1
        value |= (byte & 0x7F) << shift
        shift += 7
        if not byte & 0x80:
            return value, offset


def _name(data: bytes, offset: int) -> tuple[str, int]:
    length, offset = _uleb(data, offset)
    return data[offset:offset + length].decode("utf-8", "replace"), offset + length


def parse_wasm(data: bytes) -> dict:
    """Walk a WASM module: sections, type/import/function/code counts,
    and the exported interface (name + kind)."""
    if data[:4] != b"\x00asm":
        raise ValueError("not a WASM module")
    version = struct.unpack_from("<I", data, 4)[0]
    sections = []
    exports = []
    counts = {"types": 0, "imports": 0, "functions": 0, "code_bodies": 0}
    offset = 8
    while offset < len(data):
        section_id = data[offset]
        offset += 1
        size, offset = _uleb(data, offset)
        body_start = offset
        sections.append({"id": section_id, "name": SECTION_NAMES.get(section_id, "?"), "size": size})
        if section_id == 1:
            counts["types"], _ = _uleb(data, offset)
        elif section_id == 2:
            counts["imports"], _ = _uleb(data, offset)
        elif section_id == 3:
            counts["functions"], _ = _uleb(data, offset)
        elif section_id == 10:
            counts["code_bodies"], _ = _uleb(data, offset)
        elif section_id == 7:
            total, pos = _uleb(data, offset)
            for _ in range(total):
                name, pos = _name(data, pos)
                kind = data[pos]
                pos += 1
                _index, pos = _uleb(data, pos)
                exports.append({"name": name,
                                "kind": {0: "func", 1: "table", 2: "memory", 3: "global"}.get(kind, "?")})
        offset = body_start + size
    return {"format": "wasm", "version": version, "sections": sections,
            "counts": counts, "exports": exports,
            "interface": sorted(e["name"] for e in exports if e["kind"] == "func")}


def compare_wasm_interfaces(left: dict, right: dict) -> dict:
    """Diff two parsed modules' function interfaces — the local mirror of
    compare_wasm_interfaces (complete records required, never summaries)."""
    lset, rset = set(left["interface"]), set(right["interface"])
    return {
        "added": sorted(rset - lset),
        "removed": sorted(lset - rset),
        "unchanged": sorted(lset & rset),
        "status": "changed" if (rset - lset or lset - rset) else "unchanged",
    }


def parse_evm_selectors(code: bytes) -> dict:
    """Extract a dispatcher surface: PUSH4 immediates that feed an EQ
    comparison are candidate function selectors."""
    selectors = []
    i = 0
    while i < len(code):
        opcode = code[i]
        if 0x60 <= opcode <= 0x7F:  # PUSH1..PUSH32
            width = opcode - 0x5F
            immediate = code[i + 1:i + 1 + width]
            if opcode == 0x63 and i + 5 < len(code) and code[i + 5] == 0x14:  # PUSH4 .. EQ
                selectors.append("0x" + immediate.hex())
            i += 1 + width
        else:
            i += 1
    return {"format": "evm", "bytecode_bytes": len(code),
            "selectors": selectors,
            "limitations": ["selector candidates from PUSH4/EQ pattern only; reachability not proven"]}


def main(argv=None) -> int:
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Parse a WASM module or EVM bytecode surface.")
    parser.add_argument("path")
    parser.add_argument("--kind", choices=["wasm", "evm"], required=True)
    args = parser.parse_args(argv)
    data = open(args.path, "rb").read()
    result = parse_wasm(data) if args.kind == "wasm" else parse_evm_selectors(data)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
