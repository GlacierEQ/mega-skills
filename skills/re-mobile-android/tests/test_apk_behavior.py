"""Behavioral tests for the APK surface parser."""
import os
import struct
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import apk as apk_mod

STRINGS = ["manifest", "package", "com.example.panmix", "android", "versionCode", "versionName",
           "application", "label", "Panmix", "activity", "name", ".MainActivity", "exported",
           "uses-sdk", "minSdkVersion", "targetSdkVersion",
           "http://schemas.android.com/apk/res/android", "android"]


def _u16(n):
    return struct.pack("<H", n)


def _u32(n):
    return struct.pack("<I", n)


def _pool(strs):
    encoded = [s.encode("utf-16-le") for s in strs]
    offsets, pos = [], 0
    for e in encoded:
        offsets.append(pos)
        pos += 2 + len(e) + 2
    data = b"".join(_u16(len(s)) + e + b"\x00\x00" for s, e in zip(strs, encoded))
    strings_start = 28 + 4 * len(strs)
    chunk = _u16(0x0001) + _u16(28) + _u32(0) + _u32(len(strs)) + _u32(0) + _u32(0) + _u32(strings_start) + _u32(0)
    chunk += b"".join(_u32(o) for o in offsets) + data
    if len(chunk) % 4:
        chunk += b"\x00" * (4 - len(chunk) % 4)
    return chunk[:4] + _u32(len(chunk)) + chunk[8:]


def _start(name_idx, attrs, ns_idx=0xFFFFFFFF):
    size = 36 + len(attrs) * 20
    out = _u16(0x0102) + _u16(16) + _u32(size) + _u32(0) + _u32(0xFFFFFFFF)
    out += _u32(ns_idx & 0xFFFFFFFF) + _u32(name_idx)
    out += _u16(20) + _u16(20) + _u16(len(attrs)) + _u16(0) + _u16(0) + _u16(0)
    for ns, nm, raw, typ, data in attrs:
        out += _u32(ns & 0xFFFFFFFF) + _u32(nm & 0xFFFFFFFF) + _u32(raw & 0xFFFFFFFF)
        out += _u16(8) + b"\x00" + bytes([typ]) + _u32(data & 0xFFFFFFFF)
    return out


def _end(name_idx, ns_idx=0xFFFFFFFF):
    return _u16(0x0103) + _u16(16) + _u32(24) + _u32(0) + _u32(0xFFFFFFFF) + _u32(ns_idx & 0xFFFFFFFF) + _u32(name_idx)


def build_axml():
    ns = 16
    pool = _pool(STRINGS)
    body = _u16(0x0180) + _u16(8) + _u32(8)
    body += _u16(0x0100) + _u16(16) + _u32(24) + _u32(0) + _u32(0xFFFFFFFF) + _u32(17) + _u32(ns)
    body += _start(0, [(ns, 1, -1, 0x03, 2), (ns, 4, -1, 0x10, 1), (ns, 5, 8, 0x03, 8)])
    body += _start(13, [(ns, 14, -1, 0x10, 23), (ns, 15, -1, 0x10, 34)])
    body += _end(13)
    body += _start(6, [(0xFFFFFFFF, 7, 8, 0x03, 8)])
    body += _start(9, [(ns, 10, 11, 0x03, 11), (ns, 12, -1, 0x12, 0xFFFFFFFF)])
    body += _end(9)
    body += _end(6)
    body += _end(0)
    return _u16(0x0003) + _u16(8) + _u32(8 + len(pool) + len(body)) + pool + body


def build_dex():
    header = bytearray(112)
    header[0:8] = b"dex\n035\x00"
    struct.pack_into("<I", header, 32, 112)
    struct.pack_into("<I", header, 56, 42)   # string ids size
    struct.pack_into("<I", header, 64, 7)    # type ids size
    struct.pack_into("<I", header, 88, 5)    # method ids size
    struct.pack_into("<I", header, 96, 1)    # class defs size
    return bytes(header)


class ApkBehaviorTests(unittest.TestCase):
    def setUp(self):
        self.path = os.path.join(tempfile.mkdtemp(), "sample.apk")
        with zipfile.ZipFile(self.path, "w") as archive:
            archive.writestr("AndroidManifest.xml", build_axml())
            archive.writestr("classes.dex", build_dex())

    def test_manifest_parsed(self):
        result = apk_mod.inspect_apk(self.path)
        manifest = result["manifest"]
        self.assertEqual(manifest["package"], "com.example.panmix")
        self.assertEqual(manifest["version_code"], 1)
        self.assertEqual(manifest["version_name"], "Panmix")
        self.assertEqual(manifest["min_sdk"], 23)
        self.assertEqual(manifest["target_sdk"], 34)
        self.assertEqual(len(manifest["activities"]), 1)
        self.assertEqual(manifest["activities"][0]["name"], ".MainActivity")
        self.assertEqual(manifest["activities"][0]["exported"], True)

    def test_dex_header_parsed(self):
        result = apk_mod.inspect_apk(self.path)
        dex = result["dex"][0]
        self.assertEqual(dex["version"], "035")
        self.assertEqual(dex["string_count"], 42)
        self.assertEqual(dex["class_def_count"], 1)
        self.assertFalse(result["signed"])


if __name__ == "__main__":
    unittest.main()
