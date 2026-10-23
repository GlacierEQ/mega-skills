"""Behavioral tests for target triage routing."""
import os
import struct
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import triage


def _write(path, data):
    with open(path, "wb") as handle:
        handle.write(data)


class TriageBehaviorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def test_elf_routes_to_layout_reader(self):
        path = os.path.join(self.tmp, "prog")
        _write(path, b"\x7fELF\x02\x01\x01\x00" + b"\x00" * 64)
        result = triage.classify_path(path)
        self.assertEqual(result["artifact_class"], "elf")
        self.assertEqual(result["first_tool"], "inspect_binary_layout")
        self.assertTrue(result["session_bound"])

    def test_wasm_and_sqlite_routes(self):
        wasm = os.path.join(self.tmp, "add.wasm")
        _write(wasm, b"\x00asm\x01\x00\x00\x00")
        result = triage.classify_path(wasm)
        self.assertEqual(result["family_skill"], "re-wasm-evm")
        db = os.path.join(self.tmp, "sample.db")
        _write(db, b"SQLite format 3\x00" + b"\x00" * 100)
        result = triage.classify_path(db)
        self.assertEqual(result["first_tool"], "inspect_sqlite_database")
        self.assertFalse(result["session_bound"])

    def test_model_and_game_classes_route_local(self):
        gguf = os.path.join(self.tmp, "model.gguf")
        _write(gguf, b"GGUF\x03\x00\x00\x00" + b"\x00" * 16)
        result = triage.classify_path(gguf)
        self.assertEqual(result["family_skill"], "re-gpu-model-artifacts")
        self.assertTrue(result["first_tool"].startswith("local:"))
        meta = os.path.join(self.tmp, "global-metadata.dat")
        _write(meta, struct.pack("<I", 0xFAB11BAF) + struct.pack("<i", 29) + b"\x00" * 32)
        result = triage.classify_path(meta)
        self.assertEqual(result["artifact_class"], "il2cpp_metadata")

    def test_apk_zip_detection(self):
        apk = os.path.join(self.tmp, "sample.apk")
        with zipfile.ZipFile(apk, "w") as archive:
            archive.writestr("AndroidManifest.xml", b"\x03\x00\x08\x00")
            archive.writestr("classes.dex", b"dex\n035\x00" + b"\x00" * 100)
        result = triage.classify_path(apk)
        self.assertEqual(result["artifact_class"], "apk")
        self.assertEqual(result["first_tool"], "inspect_android_package")

    def test_unknown_stays_unresolved(self):
        path = os.path.join(self.tmp, "mystery.bin")
        _write(path, b"\xff\xfe\xfd\xfc" * 8)
        result = triage.classify_path(path)
        self.assertFalse(result["identity_resolved"])
        self.assertIsNone(result["family_skill"])


if __name__ == "__main__":
    unittest.main()
