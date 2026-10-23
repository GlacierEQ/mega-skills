#!/usr/bin/env python3
"""APK surface parser: zip inventory, binary AXML manifest, dex header.

Local companion to REA's live Android lane (inspect_android_package /
inspect_android_class / search_android_classes via the checksum-pinned
jadx-headless-mcp JAR, decode_android_resources via apktool - all verified
live on 6.7.0). This module reads the package's declared surface without
any engine: manifest package/activities/SDK levels from binary XML, and
the dex header's declared counts. Declarations are what the package
claims; behavior belongs to the JADX/dynamic lanes.
"""
from __future__ import annotations

import struct
import zipfile

RES_STRING_POOL = 0x0001
RES_XML_START_ELEMENT = 0x0102
TYPE_STRING = 0x03
TYPE_INT_DEC = 0x10
TYPE_INT_BOOL = 0x12


def _string_pool(data: bytes, offset: int) -> list[str]:
    _type, header_size, _size, count, _styles, flags, strings_start, _styles_start = struct.unpack_from("<HHIIIIII", data, offset)
    utf8 = bool(flags & 0x100)
    strings = []
    offsets_base = offset + header_size
    for index in range(count):
        entry_offset = struct.unpack_from("<I", data, offsets_base + index * 4)[0]
        pos = offset + strings_start + entry_offset
        if utf8:
            while data[pos] & 0x80:
                pos += 1
            pos += 1
            length = data[pos]
            pos += 1
            if length & 0x80:
                length = ((length & 0x7F) << 8) | data[pos]
                pos += 1
            strings.append(data[pos:pos + length].decode("utf-8", "replace"))
        else:
            length = struct.unpack_from("<H", data, pos)[0]
            pos += 2
            if length & 0x8000:
                low = struct.unpack_from("<H", data, pos)[0]
                pos += 2
                length = ((length & 0x7FFF) << 16) | low
            strings.append(data[pos:pos + length * 2].decode("utf-16-le", "replace"))
    return strings


def _typed_value(strings, raw, value_type, value_data):
    if raw != 0xFFFFFFFF and raw < len(strings):
        return strings[raw]
    if value_type == TYPE_STRING and value_data < len(strings):
        return strings[value_data]
    if value_type == TYPE_INT_DEC:
        return value_data
    if value_type == TYPE_INT_BOOL:
        return value_data != 0
    return value_data


def parse_axml(data: bytes) -> dict:
    """Parse binary Android XML: elements and their attributes."""
    if struct.unpack_from("<H", data, 0)[0] != 0x0003:
        raise ValueError("not a binary XML file")
    strings: list[str] = []
    elements = []
    offset = 8
    total = struct.unpack_from("<I", data, 4)[0]
    while offset + 8 <= min(total, len(data)):
        chunk_type, _header_size, chunk_size = struct.unpack_from("<HHI", data, offset)
        if chunk_size == 0:
            break
        if chunk_type == RES_STRING_POOL:
            strings = _string_pool(data, offset)
        elif chunk_type == RES_XML_START_ELEMENT:
            _line, _comment, _ns, name_idx = struct.unpack_from("<IIII", data, offset + 8)
            attr_start, attr_size, attr_count = struct.unpack_from("<HHH", data, offset + 24)
            attrs = {}
            for index in range(attr_count):
                base = offset + 16 + attr_start + index * attr_size
                a_ns, a_name, a_raw = struct.unpack_from("<III", data, base)
                v_size, _zero, v_type, v_data = struct.unpack_from("<HBBI", data, base + 12)
                key = strings[a_name] if a_name < len(strings) else str(a_name)
                attrs[key] = _typed_value(strings, a_raw, v_type, v_data)
            elements.append({"name": strings[name_idx] if name_idx < len(strings) else str(name_idx),
                             "attributes": attrs})
        offset += chunk_size
    manifest = next((e for e in elements if e["name"] == "manifest"), {"attributes": {}})
    activities = [e["attributes"] for e in elements if e["name"] == "activity"]
    sdk = next((e["attributes"] for e in elements if e["name"] == "uses-sdk"), {})
    return {
        "format": "axml",
        "package": manifest["attributes"].get("package"),
        "version_code": manifest["attributes"].get("versionCode"),
        "version_name": manifest["attributes"].get("versionName"),
        "min_sdk": sdk.get("minSdkVersion"),
        "target_sdk": sdk.get("targetSdkVersion"),
        "activities": activities,
        "element_count": len(elements),
    }


def parse_dex_header(data: bytes) -> dict:
    """Parse a dex header's declared table sizes (header scope only)."""
    if data[:4] != b"dex\n":
        raise ValueError("not a dex file")
    fields = struct.unpack_from("<I", data, 8)  # checksum position guard
    return {
        "format": "dex",
        "version": data[4:7].decode("ascii", "replace"),
        "file_size": struct.unpack_from("<I", data, 32)[0],
        "string_count": struct.unpack_from("<I", data, 56)[0],
        "type_count": struct.unpack_from("<I", data, 64)[0],
        "method_count": struct.unpack_from("<I", data, 88)[0],
        "class_def_count": struct.unpack_from("<I", data, 96)[0],
    }


def inspect_apk(path: str) -> dict:
    """Inventory an APK: entries, parsed manifest, dex headers."""
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        result = {"format": "apk", "entries": names}
        if "AndroidManifest.xml" in names:
            result["manifest"] = parse_axml(archive.read("AndroidManifest.xml"))
        dexes = [n for n in names if n.endswith(".dex")]
        result["dex"] = [parse_dex_header(archive.read(n)) for n in dexes]
        result["signed"] = any(n.startswith("META-INF/") and n.endswith((".SF", ".RSA", ".DSA", ".EC")) for n in names)
    result["limitations"] = [
        "declared surface only; code inspection belongs to the JADX lane",
        "in 6.7.0, APK signing detail surfaces through the package lane; inspect_signature is Mach-O code signing",
    ]
    return result


def main(argv=None) -> int:
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Inspect an APK's declared surface.")
    parser.add_argument("path")
    args = parser.parse_args(argv)
    result = inspect_apk(args.path)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
