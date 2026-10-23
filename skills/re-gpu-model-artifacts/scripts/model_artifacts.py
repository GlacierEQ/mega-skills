#!/usr/bin/env python3
"""Model and GPU artifact headers: GGUF, safetensors, PTX.

rea-agents 6.7.0 exposes no model or GPU-code-object tool and open_binary
refuses these formats outright; this module carries the lane locally with
REA's own discipline preserved:
- Hash scope is part of the evidence: the default digest covers the
  header only and leaves full-file identity UNKNOWN; a full hash is a
  separate, explicitly labeled value. A header hash is never reported
  as a file identity.
- Declared architecture/tensors are what the file claims to be. Never
  infer model behavior from declared metadata.
"""
from __future__ import annotations

import hashlib
import json
import re
import struct

GGUF_STRING = 8
GGUF_ARRAY = 9
GGUF_VALUE_SIZES = {0: 1, 1: 1, 2: 2, 3: 2, 4: 4, 5: 4, 6: 4, 7: 1, 10: 8, 11: 8, 12: 8}


def _gguf_string(data, pos):
    length = struct.unpack_from("<Q", data, pos)[0]
    pos += 8
    return data[pos:pos + length].decode("utf-8", "replace"), pos + length


def _gguf_skip_value(data, pos, value_type):
    if value_type == GGUF_STRING:
        _value, pos = _gguf_string(data, pos)
        return pos
    if value_type == GGUF_ARRAY:
        elem_type = struct.unpack_from("<I", data, pos)[0]
        pos += 4
        count = struct.unpack_from("<Q", data, pos)[0]
        pos += 8
        if elem_type == GGUF_STRING:
            for _ in range(count):
                _value, pos = _gguf_string(data, pos)
            return pos
        return pos + count * GGUF_VALUE_SIZES[elem_type]
    return pos + GGUF_VALUE_SIZES[value_type]


def parse_gguf(data, full_hash=False):
    """Parse a GGUF header: version, tensor/KV counts, string metadata."""
    if data[:4] != b"GGUF":
        raise ValueError("not a GGUF file")
    version = struct.unpack_from("<I", data, 4)[0]
    tensor_count, kv_count = struct.unpack_from("<QQ", data, 8)
    pos = 24
    metadata = {}
    for _ in range(kv_count):
        key, pos = _gguf_string(data, pos)
        value_type = struct.unpack_from("<I", data, pos)[0]
        pos += 4
        if value_type == GGUF_STRING:
            value, pos = _gguf_string(data, pos)
            metadata[key] = value
        else:
            pos = _gguf_skip_value(data, pos, value_type)
    result = {
        "format": "gguf",
        "version": version,
        "tensor_count": tensor_count,
        "metadata_count": kv_count,
        "metadata_strings": metadata,
        "header_sha256": hashlib.sha256(data[:pos]).hexdigest(),
        "hash_scope": "header",
        "file_identity": "unknown (header hash only)",
        "limitations": ["declared metadata only; behavior is never inferred from architecture or tensor types"],
    }
    if full_hash:
        result["full_sha256"] = hashlib.sha256(data).hexdigest()
        result["file_identity"] = "full file sha256 recorded"
    return result


def parse_safetensors(data):
    """Parse a safetensors header: dtype/shape/offset table + metadata.
    Weights are never read; the header length bounds the parse."""
    if len(data) < 8:
        raise ValueError("safetensors file too short")
    header_len = struct.unpack_from("<Q", data, 0)[0]
    header = json.loads(data[8:8 + header_len].decode("utf-8"))
    tensors = {}
    metadata = {}
    for name, entry in header.items():
        if name == "__metadata__":
            metadata = entry
        else:
            tensors[name] = {"dtype": entry["dtype"], "shape": entry["shape"],
                             "data_offsets": entry["data_offsets"]}
    return {
        "format": "safetensors",
        "header_bytes": header_len,
        "tensors": tensors,
        "metadata": metadata,
        "header_sha256": hashlib.sha256(data[:8 + header_len]).hexdigest(),
        "hash_scope": "header",
        "file_identity": "unknown (header hash only)",
        "limitations": ["declarations only; tensor contents not read"],
    }


def scan_ptx(text):
    """Extract PTX declarations: version, target, entry kernels, spaces.
    Presence proves a kernel shipped, not that a host path executes it."""
    version = re.search(r"\.version\s+(\d+\.\d+)", text)
    target = re.search(r"\.target\s+(\S+)", text)
    entries = re.findall(r"\.entry\s+([A-Za-z_][\w]*)", text)
    spaces = sorted(set(re.findall(r"\.(global|local|shared|const|param|reg)\b", text)))
    return {"format": "ptx",
            "version": version.group(1) if version else None,
            "target": target.group(1) if target else None,
            "entries": entries,
            "address_spaces": spaces,
            "limitations": ["declaration scope; host-side reachability not proven"]}


def main(argv=None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Parse a model/GPU artifact header.")
    parser.add_argument("path")
    parser.add_argument("--kind", choices=["gguf", "safetensors", "ptx"], required=True)
    parser.add_argument("--full-hash", action="store_true")
    args = parser.parse_args(argv)
    raw = open(args.path, "rb").read()
    if args.kind == "gguf":
        result = parse_gguf(raw, full_hash=args.full_hash)
    elif args.kind == "safetensors":
        result = parse_safetensors(raw)
    else:
        result = scan_ptx(raw.decode("utf-8", "replace"))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
