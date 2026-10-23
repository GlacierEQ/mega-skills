"""Behavioral tests for firmware carving."""
import gzip
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import firmware


def _cpio(files):
    out = b""
    ino = 1
    for name, data in files:
        header = ("070701" + f"{ino:08x}" + "000081a4" + "00000000" + "00000000" +
                  "00000001" + "00000000" + f"{len(data):08x}" + "00000000" * 4 +
                  f"{len(name) + 1:08x}" + "00000000")
        record = header.encode() + name.encode() + b"\x00"
        record += b"\x00" * ((4 - len(record) % 4) % 4)
        record += data + b"\x00" * ((4 - len(data) % 4) % 4)
        out += record
        ino += 1
    header = ("070701" + f"{ino:08x}" + "000081a4" + "00000000" + "00000000" +
              "00000001" + "00000000" + "00000000" + "00000000" * 4 + f"{11:08x}" + "00000000")
    record = header.encode() + b"TRAILER!!!\x00"
    record += b"\x00" * ((4 - len(record) % 4) % 4)
    return out + record


def build_image():
    archive = _cpio([("init", b"#!/bin/sh\n"), ("bin/panmix", b"\x7fELF-fake")])
    image = b"\x00" * 512 + b"\x27\x05\x19\x56" + b"\x00" * 60 + gzip.compress(archive)
    return image, archive


class FirmwareBehaviorTests(unittest.TestCase):
    def test_magic_scan_offsets(self):
        image, _archive = build_image()
        result = firmware.scan_magics(image)
        kinds = {(r["kind"], r["offset"]) for r in result}
        self.assertIn(("uimage", 512), kinds)
        self.assertTrue(any(kind == "gzip" and offset == 576 for kind, offset in kinds))

    def test_cpio_listing(self):
        _image, archive = build_image()
        entries = firmware.parse_cpio_newc(archive)
        names = [e["name"] for e in entries]
        self.assertEqual(names, ["init", "bin/panmix", "TRAILER!!!"])
        sizes = {e["name"]: e["size"] for e in entries}
        self.assertEqual(sizes["init"], 10)

    def test_full_carve_decodes_gzip_member(self):
        image, archive = build_image()
        result = firmware.carve(image)
        self.assertEqual(len(result["decoded"]), 1)
        decoded = result["decoded"][0]
        self.assertEqual(decoded["decompressed_bytes"], len(archive))
        self.assertEqual([e["name"] for e in decoded["cpio_entries"]][:2], ["init", "bin/panmix"])


if __name__ == "__main__":
    unittest.main()
