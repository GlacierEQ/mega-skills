"""Behavioral tests for Apple bundle resource analysis."""
import os
import plistlib
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import bundle as bundle_mod

INFO = {
    "CFBundleIdentifier": "com.example.panmix",
    "CFBundleExecutable": "Panmix",
    "CFBundleShortVersionString": "1.0.0",
    "CFBundleVersion": "42",
    "CFBundleURLTypes": [{"CFBundleURLSchemes": ["panmix", "panmix-dev"]}],
    "UIBackgroundModes": ["audio"],
    "NSMicrophoneUsageDescription": "Panmix mixes audio you play.",
}


class BundleBehaviorTests(unittest.TestCase):
    def test_declared_configuration(self):
        result = bundle_mod.declared_configuration(INFO)
        self.assertEqual(result["bundle_id"], "com.example.panmix")
        self.assertEqual(result["url_schemes"], ["panmix", "panmix-dev"])
        self.assertEqual(result["background_modes"], ["audio"])
        self.assertEqual(list(result["privacy_usage_strings"]), ["NSMicrophoneUsageDescription"])

    def test_openable_requires_executable_file(self):
        root = tempfile.mkdtemp()
        missing = bundle_mod.openable(INFO, root)
        self.assertFalse(missing["openable"])
        macos = os.path.join(root, "Contents", "MacOS")
        os.makedirs(macos)
        open(os.path.join(macos, "Panmix"), "wb").write(b"\xcf\xfa\xed\xfe")
        present = bundle_mod.openable(INFO, root)
        self.assertTrue(present["openable"])

    def test_keyed_archive_graph_decoded(self):
        archive = {
            "$version": 100000,
            "$archiver": "NSKeyedArchiver",
            "$top": {"root": plistlib.UID(1)},
            "$objects": [
                "$null",
                {"$class": plistlib.UID(3), "name": "PanmixSettings",
                 "stored-value": plistlib.UID(2)},
                "linear-taper",
                {"$classname": "PanmixSettings", "$classes": ["NSObject"]},
            ],
        }
        result = bundle_mod.decode_keyed_archive(archive)
        self.assertEqual(result["root"]["root"]["name"], "PanmixSettings")
        self.assertEqual(result["root"]["root"]["stored-value"], "linear-taper")
        self.assertEqual(result["classes"], ["PanmixSettings"])
        self.assertEqual(result["object_count"], 4)

    def test_binary_plist_round_trip(self):
        blob = plistlib.dumps(INFO, fmt=plistlib.FMT_BINARY)
        parsed = bundle_mod.parse_plist_bytes(blob)
        result = bundle_mod.declared_configuration(parsed)
        self.assertEqual(result["executable"], "Panmix")


if __name__ == "__main__":
    unittest.main()
