"""Behavioral tests for capture comparison and ELF core parsing."""
import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import dynamic


def _note(name, note_type, desc):
    encoded_name = name + b"\x00"
    out = struct.pack("<III", len(encoded_name), len(desc), note_type) + encoded_name
    out += b"\x00" * ((4 - len(encoded_name) % 4) % 4)
    out += desc
    out += b"\x00" * ((4 - len(desc) % 4) % 4)
    return out


def build_core():
    prstatus = bytearray(112)
    struct.pack_into("<H", prstatus, 12, 11)  # pr_cursig = SIGSEGV
    file_desc = struct.pack("<qq", 1, 4096) + struct.pack("<qqq", 0, 0x1000, 0) + b"/bin/crashy\x00"
    notes = _note(b"CORE", 3, bytes(prstatus)) + _note(b"CORE", 0x46494C45, file_desc)
    header = bytearray(64)
    header[0:4] = b"\x7fELF"
    header[4] = 2
    header[5] = 1
    struct.pack_into("<HHI", header, 16, 4, 62, 1)  # ET_CORE, x86-64
    struct.pack_into("<Q", header, 32, 64)          # phoff
    struct.pack_into("<HH", header, 52, 56, 1)      # phentsize, phnum
    phdr = struct.pack("<IIQQQQQQ", 4, 0, 64 + 56, 0, 0, len(notes), len(notes), 0)
    return bytes(header) + phdr + notes


class DynamicBehaviorTests(unittest.TestCase):
    def test_core_signal_and_files(self):
        result = dynamic.parse_elf_core(build_core())
        self.assertEqual(result["signal"], 11)
        self.assertEqual(result["signal_name"], "SIGSEGV")
        self.assertEqual(result["mapped_files"], ["/bin/crashy"])

    def test_unnormalized_timing_differs(self):
        left = {"terminal": "out", "exit": {"event": "exit", "code": 0, "elapsed_ms": 73}}
        right = {"terminal": "out", "exit": {"event": "exit", "code": 0, "elapsed_ms": 67}}
        result = dynamic.compare_captures(left, right)
        self.assertEqual(result["dimensions"]["exit"], "changed")
        self.assertEqual(result["status"], "changed")

    def test_declared_normalization_reconciles(self):
        left = {"terminal": "out", "exit": {"event": "exit", "code": 0, "elapsed_ms": 73}}
        right = {"terminal": "out", "exit": {"event": "exit", "code": 0, "elapsed_ms": 67}}
        result = dynamic.compare_captures(
            left, right, {"ignore_fields": ["elapsed_ms"], "time_bucket_ms": 10000})
        self.assertEqual(result["dimensions"]["exit"], "unchanged")
        self.assertEqual(result["status"], "unchanged")
        self.assertEqual(result["normalization"]["time_bucket_ms"], 10000)

    def test_terminal_change_detected(self):
        left = {"terminal": "R=600", "exit": {"event": "exit", "code": 0}}
        right = {"terminal": "R=700", "exit": {"event": "exit", "code": 0}}
        result = dynamic.compare_captures(left, right)
        self.assertEqual(result["dimensions"]["terminal"], "changed")


if __name__ == "__main__":
    unittest.main()
