"""Behavioral tests for game artifact header parsing."""
import hashlib
import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import game


def build_metadata(version=29, sections=17):
    out = struct.pack("<Ii", 0xFAB11BAF, version)
    for index in range(sections):
        out += struct.pack("<II", 1024 + index * 16, index * 3)
    return out


def build_pck():
    entries = [("res://main.tscn", b"scene-bytes"), ("res://icon.svg", b"<svg/>")]
    header_size = 4 + 16 + 4 + 8 + 4 + 64
    file_base = header_size
    directory = struct.pack("<I", len(entries))
    body = b""
    offset = file_base
    # directory is written after the fixed header; compute entry offsets
    dir_size = 4
    for path, data in entries:
        dir_size += 4 + len(path.encode()) + ((4 - len(path.encode()) % 4) % 4) + 16 + 16
    data_base = header_size + dir_size
    cursor = data_base
    for path, data in entries:
        encoded = path.encode()
        directory += struct.pack("<I", len(encoded)) + encoded
        directory += b"\x00" * ((4 - len(encoded) % 4) % 4)
        directory += struct.pack("<QQ", cursor, len(data))
        directory += hashlib.md5(data).digest()
        body += data
        cursor += len(data)
    header = b"GDPC" + struct.pack("<IIII", 1, 4, 2, 1) + struct.pack("<I", 0)
    header += struct.pack("<Q", file_base) + struct.pack("<I", header_size) + b"\x00" * 64
    return header + directory + body


class GameBehaviorTests(unittest.TestCase):
    def test_il2cpp_supported_version(self):
        result = game.parse_il2cpp_metadata(build_metadata(29))
        self.assertTrue(result["recognized"])
        self.assertTrue(result["supported"])
        self.assertEqual(result["version"], 29)
        self.assertEqual(result["sections"]["methods"], {"offset": 1024 + 5 * 16, "count": 15})

    def test_il2cpp_unsupported_version_named(self):
        result = game.parse_il2cpp_metadata(build_metadata(35))
        self.assertTrue(result["recognized"])
        self.assertFalse(result["supported"])

    def test_il2cpp_bad_magic_is_unknown_not_absence(self):
        result = game.parse_il2cpp_metadata(b"\xde\xad\xbe\xef" + b"\x00" * 64)
        self.assertFalse(result["recognized"])
        self.assertIn("encrypted", result["reason"])

    def test_godot_pck_directory(self):
        result = game.parse_godot_pck(build_pck())
        self.assertEqual(result["godot_version"], "4.2.1")
        self.assertFalse(result["encrypted"])
        paths = {f["path"]: f["size"] for f in result["files"]}
        self.assertEqual(paths, {"res://main.tscn": 11, "res://icon.svg": 6})
        md5s = {f["path"]: f["md5"] for f in result["files"]}
        self.assertEqual(md5s["res://icon.svg"], hashlib.md5(b"<svg/>").hexdigest())

    def test_flutter_markers(self):
        result = game.flutter_markers(["lib/arm64-v8a/libapp.so", "lib/arm64-v8a/libflutter.so",
                                        "assets/flutter_assets/AssetManifest.json"])
        self.assertTrue(result["is_flutter"])
        self.assertTrue(result["libapp_so"])
        plain = game.flutter_markers(["classes.dex", "AndroidManifest.xml"])
        self.assertFalse(plain["is_flutter"])


if __name__ == "__main__":
    unittest.main()
