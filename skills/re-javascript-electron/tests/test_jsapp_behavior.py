"""Behavioral tests for the JS/Electron static analysis."""
import json
import os
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import jsapp_analysis


class JsAppBehaviorTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        with open(os.path.join(self.root, "package.json"), "w") as handle:
            json.dump({"name": "panmix-app", "version": "1.0.0", "main": "main.js"}, handle)
        with open(os.path.join(self.root, "main.js"), "w") as handle:
            handle.write(
                "const { app, BrowserWindow, ipcMain } = require('electron');\n"
                "ipcMain.handle('pan:mix', async (event, request) => request);\n"
                "ipcMain.on('app:version', (event) => { event.returnValue = '1.0.0'; });\n")
        with open(os.path.join(self.root, "preload.js"), "w") as handle:
            handle.write(
                "const { contextBridge } = require('electron');\n"
                "contextBridge.exposeInMainWorld('panmix', { mix: () => {} });\n")
        with open(os.path.join(self.root, "main.js.map"), "w") as handle:
            handle.write("{}")

    def test_tree_scan_finds_channels_and_bridges(self):
        result = jsapp_analysis.scan_tree(self.root)
        self.assertEqual(result["name"], "panmix-app")
        channels = {(c["channel"], c["method"]) for c in result["ipc_channels"]}
        self.assertEqual(channels, {("pan:mix", "handle"), ("app:version", "on")})
        self.assertEqual([b["key"] for b in result["bridge_keys"]], ["panmix"])
        self.assertEqual(result["source_maps"], ["main.js.map"])

    def test_asar_header_inventory(self):
        header = {"files": {
            "index.html": {"size": 139, "offset": "0"},
            "dist": {"files": {"main.js": {"size": 55, "offset": "139"}}},
        }}
        payload = json.dumps(header).encode()
        padded = payload + b"\x00" * ((4 - len(payload) % 4) % 4)
        blob = struct.pack("<IIII", 4, 4 + 4 + len(padded), 4 + len(padded), len(payload)) + padded + b"DATA"
        result = jsapp_analysis.parse_asar_header(blob)
        paths = {f["path"]: f["size"] for f in result["files"]}
        self.assertEqual(paths, {"index.html": 139, "dist/main.js": 55})


if __name__ == "__main__":
    unittest.main()
