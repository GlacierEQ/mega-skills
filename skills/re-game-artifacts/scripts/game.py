#!/usr/bin/env python3
"""Game artifact headers: IL2CPP metadata, Godot PCK, Flutter markers.

rea-agents 6.7.0 exposes NO IL2CPP metadata tool and refuses Godot PCK at
open_binary (unsupported format); the Flutter lane is live
(identify_flutter_build, inspect_dart_aot). This module carries the
metadata/PCK lanes locally: parse the IL2CPP global-metadata header
(magic 0xFAB11BAF; supported versions 24/27/29/31/39) and the Godot PCK
directory, and scan an archive listing for Flutter/Dart markers. Header
scope only: counts without a linked binary stay unknown, and metadata
pairing never proves the binary is the same build.
"""
from __future__ import annotations

import struct
import zipfile

IL2CPP_MAGIC = 0xFAB11BAF
SUPPORTED_METADATA_VERSIONS = {24, 27, 29, 31, 39}

# (offset of pair, name) for the first section pairs of the v29 header:
# string literals, string literal data, strings, images, ...
SECTION_NAMES = [
    "string_literal", "string_literal_data", "string", "events", "properties",
    "methods", "parameter_fields", "parameters", "fields", "generic_parameters",
    "generic_parameter_constraints", "generic_containers", "nested_types",
    "interfaces", "vtable_methods", "interface_offsets", "type_definitions",
]


def parse_il2cpp_metadata(data: bytes) -> dict:
    """Parse the global-metadata.dat header: magic, version, section
    (offset, count) pairs. Unsupported versions and bad magic are named,
    never silently absorbed - unrecognized magic may mean an encrypted
    metadata file, recorded as unknown, not as absence."""
    if len(data) < 8:
        raise ValueError("metadata file too short")
    magic, version = struct.unpack_from("<Ii", data, 0)
    if magic != IL2CPP_MAGIC:
        return {"format": "il2cpp_metadata", "recognized": False,
                "reason": "magic mismatch (possibly encrypted metadata)",
                "supported": False}
    sections = {}
    for index, name in enumerate(SECTION_NAMES):
        offset, count = struct.unpack_from("<II", data, 8 + index * 8)
        sections[name] = {"offset": offset, "count": count}
    return {
        "format": "il2cpp_metadata",
        "recognized": True,
        "version": version,
        "supported": version in SUPPORTED_METADATA_VERSIONS,
        "sections": sections,
        "limitations": [
            "header scope: without a linked binary, native method addresses remain unknown",
            "metadata pairing never proves the binary is the same build",
        ],
    }


def parse_godot_pck(data: bytes) -> dict:
    """Parse a Godot PCK header and file directory (format v1/v2)."""
    if data[:4] != b"GDPC":
        raise ValueError("not a Godot PCK archive")
    format_version, major, minor, patch = struct.unpack_from("<IIII", data, 4)
    flags = struct.unpack_from("<I", data, 20)[0]
    file_base = struct.unpack_from("<Q", data, 24)[0]
    if format_version >= 2:
        dir_offset = struct.unpack_from("<Q", data, 32)[0]
        pos = dir_offset
    else:
        pos = 4 + 16 + 4 + 8 + 4 + 64
    file_count = struct.unpack_from("<I", data, pos)[0]
    pos += 4
    files = []
    for _ in range(file_count):
        path_len = struct.unpack_from("<I", data, pos)[0]
        pos += 4
        path = data[pos:pos + path_len].rstrip(b"\x00").decode("utf-8", "replace")
        pos += path_len
        while (pos - 0) % 4:
            pos += 1
        offset, size = struct.unpack_from("<QQ", data, pos)
        pos += 16
        md5 = data[pos:pos + 16].hex()
        pos += 16
        if format_version >= 2:
            pos += 4  # per-file flags in v2
        files.append({"path": path, "offset": offset, "size": size, "md5": md5})
    return {
        "format": "godot_pck",
        "format_version": format_version,
        "godot_version": f"{major}.{minor}.{patch}",
        "encrypted": bool(flags & 1),
        "file_base": file_base,
        "files": files,
        "limitations": ["directory scope; embedded assets are located evidence, not behavior"],
    }


def flutter_markers(names: list[str]) -> dict:
    """Scan an archive listing for Flutter/Dart AOT markers."""
    lowered = [n.lower() for n in names]
    return {
        "libapp_so": any("libapp.so" in n for n in lowered),
        "libflutter_so": any("libflutter.so" in n for n in lowered),
        "app_framework": any("app.framework" in n for n in lowered),
        "flutter_assets": any("flutter_assets" in n for n in lowered),
        "is_flutter": any(("libapp.so" in n or "app.framework" in n) for n in lowered),
    }


def main(argv=None) -> int:
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Parse a game artifact header.")
    parser.add_argument("path")
    parser.add_argument("--kind", choices=["il2cpp", "pck", "flutter"], required=True)
    args = parser.parse_args(argv)
    data = open(args.path, "rb").read()
    if args.kind == "il2cpp":
        result = parse_il2cpp_metadata(data)
    elif args.kind == "pck":
        result = parse_godot_pck(data)
    else:
        names = zipfile.ZipFile(args.path).namelist() if zipfile.is_zipfile(args.path) else []
        result = flutter_markers(names)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
