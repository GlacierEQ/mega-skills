"""Behavioral tests for the local static readers."""
import os
import sqlite3
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import readers


class ReadersBehaviorTests(unittest.TestCase):
    def test_elf_header_parse(self):
        data = b"\x7fELF" + bytes([2, 1, 1, 0]) + b"\x00" * 8
        data += struct.pack("<HHIQQQIHHHHHH", 3, 62, 1, 0x1010, 64, 0, 0, 64, 56, 2, 64, 3, 2)
        data += b"\x00" * 128
        result = readers.parse_elf_header(data)
        self.assertEqual(result["bits"], 64)
        self.assertEqual(result["type"], "DYN")
        self.assertEqual(result["machine"], 62)
        self.assertEqual(result["entry"], 0x1010)
        self.assertEqual(len(result["sha256"]), 64)

    def test_elf_rejects_non_elf(self):
        with self.assertRaises(ValueError):
            readers.parse_elf_header(b"MZ" + b"\x00" * 64)

    def test_pyc_timestamp_and_hash_variants(self):
        header = bytes([0xCB, 0x0D, 0x0D, 0x0A]) + struct.pack("<III", 0, 1700000000, 4321) + b"\x42" * 8
        result = readers.parse_pyc_header(header)
        self.assertEqual(result["provenance"], "timestamp/size (PEP 552)")
        self.assertEqual(result["source_mtime"], 1700000000)
        self.assertEqual(result["source_size"], 4321)
        hashed = bytes([0xCB, 0x0D, 0x0D, 0x0A]) + struct.pack("<I", 1) + bytes(range(8)) + b"\x42" * 8
        result = readers.parse_pyc_header(hashed)
        self.assertTrue(result["hash_based"])
        self.assertEqual(result["source_sha256_prefix"], bytes(range(8)).hex())

    def test_sqlite_header_from_real_database(self):
        path = os.path.join(tempfile.mkdtemp(), "t.db")
        conn = sqlite3.connect(path)
        conn.execute("CREATE TABLE t (id INTEGER PRIMARY KEY, body TEXT)")
        conn.execute("INSERT INTO t VALUES (1, 'x')")
        conn.commit()
        conn.close()
        result = readers.parse_sqlite_header(open(path, "rb").read())
        self.assertEqual(result["page_size"], 4096)
        self.assertEqual(result["encoding"], "utf-8")
        self.assertGreaterEqual(result["database_pages"], 1)

    def test_beam_chunk_inventory(self):
        def chunk(cid, payload):
            pad = b"\x00" if len(payload) % 2 else b""
            return cid + struct.pack(">I", len(payload)) + payload + pad
        body = b"BEAM" + chunk(b"AtU8", b"\x00" * 6) + chunk(b"Code", b"\x00" * 10)
        data = b"FOR1" + struct.pack(">I", len(body)) + body
        result = readers.parse_beam_header(data)
        self.assertEqual([c["id"] for c in result["chunks"]], ["AtU8", "Code"])
        self.assertEqual(result["form_size"], len(body))


if __name__ == "__main__":
    unittest.main()
