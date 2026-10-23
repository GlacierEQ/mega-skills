"""Behavioral tests for the PE/CLI managed-surface parser."""
import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import managed


def build_pe(with_cli=True):
    """Minimal PE32, one .text section; optional CLI header + BSJB root."""
    dos = bytearray(128)
    dos[0:2] = b"MZ"
    struct.pack_into("<I", dos, 0x3C, 128)
    coff = struct.pack("<HHIIIHH", 0x14C, 1, 0, 0, 0, 224, 0x0102)
    opt = bytearray(224)
    struct.pack_into("<H", opt, 0, 0x10B)
    section_rva = 0x2000
    if with_cli:
        struct.pack_into("<II", opt, 96 + 14 * 8, section_rva, 72)
    raw_ptr = 128 + 4 + 20 + 224 + 40
    section = b".text\x00\x00\x00" + struct.pack(
        "<IIIIIIHHI", 0x1000, section_rva, 0x1000, raw_ptr, 0, 0, 0, 0, 0x60000020)
    body = bytearray(0x1000)
    if with_cli:
        meta_rva = section_rva + 0x100
        struct.pack_into("<IHHIII", body, 0, 72, 2, 5, meta_rva, 0x200, 0x1)
        meta = bytearray(0x200)
        meta[0:4] = b"BSJB"
        struct.pack_into("<HHI", meta, 4, 1, 1, 0)
        struct.pack_into("<I", meta, 12, 12)
        meta[16:28] = b"v4.0.30319\x00\x00"
        pos = 16 + 12
        struct.pack_into("<HH", meta, pos, 0, 5)
        pos += 4
        for stream in ("#~", "#Strings", "#US", "#GUID", "#Blob"):
            struct.pack_into("<II", meta, pos, 0, 0)
            pos += 8
            encoded = stream.encode() + b"\x00"
            meta[pos:pos + len(encoded)] = encoded
            pos += len(encoded)
            while pos % 4:
                pos += 1
        body[0x100:0x100 + len(meta)] = meta
    return bytes(dos) + b"PE\x00\x00" + coff + bytes(opt) + section + bytes(body)


class ManagedBehaviorTests(unittest.TestCase):
    def test_managed_pe_detected_with_streams(self):
        result = managed.parse_pe(build_pe(True))
        self.assertTrue(result["managed"])
        self.assertEqual(result["machine"], "x86")
        self.assertEqual(result["metadata"]["streams"],
                         ["#~", "#Strings", "#US", "#GUID", "#Blob"])
        self.assertFalse(result["metadata"]["strong_name_signed"])

    def test_native_pe_has_no_cli_directory(self):
        result = managed.parse_pe(build_pe(False))
        self.assertFalse(result["managed"])
        self.assertIsNone(result["cli_header"])

    def test_rejects_non_pe(self):
        with self.assertRaises(ValueError):
            managed.parse_pe(b"\x7fELF" + b"\x00" * 128)


if __name__ == "__main__":
    unittest.main()
