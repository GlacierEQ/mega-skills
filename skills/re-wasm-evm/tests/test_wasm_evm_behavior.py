"""Behavioral tests for the WASM/EVM surface parsers."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import wasm_evm


def _uleb(value):
    out = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        if value:
            out.append(byte | 0x80)
        else:
            out.append(byte)
            return bytes(out)


def _section(section_id, body):
    return bytes([section_id]) + _uleb(len(body)) + body


def _vec(items):
    return _uleb(len(items)) + b"".join(items)


def build_add_wasm(exports=("add",)):
    types = _section(1, _vec([b"\x60\x02\x7f\x7f\x01\x7f"]))
    funcs = _section(3, _vec([b"\x00"]))
    export_entries = []
    for index, name in enumerate(exports):
        encoded = name.encode()
        export_entries.append(_uleb(len(encoded)) + encoded + b"\x00" + _uleb(index))
    exports_section = _section(7, _vec(export_entries))
    body = b"\x00\x20\x00\x20\x01\x6a\x0b"
    code = _section(10, _vec([_uleb(len(body)) + body]))
    return b"\x00asm\x01\x00\x00\x00" + types + funcs + exports_section + code


class WasmBehaviorTests(unittest.TestCase):
    def test_parse_add_module(self):
        result = wasm_evm.parse_wasm(build_add_wasm())
        self.assertEqual(result["interface"], ["add"])
        self.assertEqual(result["counts"]["types"], 1)
        self.assertEqual(result["counts"]["functions"], 1)
        self.assertEqual(result["counts"]["code_bodies"], 1)
        self.assertEqual([s["name"] for s in result["sections"]],
                         ["type", "function", "export", "code"])

    def test_interface_comparison(self):
        left = wasm_evm.parse_wasm(build_add_wasm(("add",)))
        right = wasm_evm.parse_wasm(build_add_wasm(("add", "sub")))
        diff = wasm_evm.compare_wasm_interfaces(left, right)
        self.assertEqual(diff["added"], ["sub"])
        self.assertEqual(diff["unchanged"], ["add"])
        self.assertEqual(diff["status"], "changed")

    def test_evm_selector_extraction(self):
        code = bytes([0x60, 0x00, 0x35, 0x63, 0xAA, 0xBB, 0xCC, 0xDD, 0x14,
                      0x60, 0x08, 0x57, 0x00])
        result = wasm_evm.parse_evm_selectors(code)
        self.assertEqual(result["selectors"], ["0xaabbccdd"])
        no_match = wasm_evm.parse_evm_selectors(bytes([0x63, 1, 2, 3, 4, 0x15]))
        self.assertEqual(no_match["selectors"], [])


if __name__ == "__main__":
    unittest.main()
