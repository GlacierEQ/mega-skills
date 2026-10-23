"""Behavioral tests for model/GPU artifact header parsing."""
import json
import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import model_artifacts


def _gguf_string(value):
    encoded = value.encode()
    return struct.pack("<Q", len(encoded)) + encoded


def build_gguf():
    out = b"GGUF" + struct.pack("<IQQ", 3, 2, 2)
    out += _gguf_string("general.architecture") + struct.pack("<I", 8) + _gguf_string("panmix-net")
    out += _gguf_string("general.file_type") + struct.pack("<I", 4) + struct.pack("<I", 1)
    out += b"\x00" * 64  # tensor payload stand-in
    return out


class ModelBehaviorTests(unittest.TestCase):
    def test_gguf_header_and_hash_scope(self):
        blob = build_gguf()
        result = model_artifacts.parse_gguf(blob)
        self.assertEqual(result["version"], 3)
        self.assertEqual(result["tensor_count"], 2)
        self.assertEqual(result["metadata_strings"], {"general.architecture": "panmix-net"})
        self.assertEqual(result["hash_scope"], "header")
        self.assertTrue(result["file_identity"].startswith("unknown"))
        full = model_artifacts.parse_gguf(blob, full_hash=True)
        self.assertEqual(full["file_identity"], "full file sha256 recorded")
        self.assertNotEqual(full["full_sha256"], full["header_sha256"])

    def test_safetensors_header(self):
        header = {"__metadata__": {"format": "pt"},
                  "weight": {"dtype": "F32", "shape": [2, 2], "data_offsets": [0, 16]}}
        payload = json.dumps(header).encode()
        blob = struct.pack("<Q", len(payload)) + payload + b"\x00" * 16
        result = model_artifacts.parse_safetensors(blob)
        self.assertEqual(result["tensors"]["weight"]["dtype"], "F32")
        self.assertEqual(result["tensors"]["weight"]["shape"], [2, 2])
        self.assertEqual(result["metadata"], {"format": "pt"})

    def test_ptx_scan(self):
        ptx = (".version 8.3\n.target sm_90\n.address_size 64\n"
               ".visible .entry panmix_kernel(.param .u64 input) {\n"
               "  ld.global.u32 %r1, [%rd1];\n  st.shared.u32 [%r2], %r1;\n}\n")
        result = model_artifacts.scan_ptx(ptx)
        self.assertEqual(result["version"], "8.3")
        self.assertEqual(result["target"], "sm_90")
        self.assertEqual(result["entries"], ["panmix_kernel"])
        self.assertEqual(result["address_spaces"], ["global", "param", "shared"])


if __name__ == "__main__":
    unittest.main()
