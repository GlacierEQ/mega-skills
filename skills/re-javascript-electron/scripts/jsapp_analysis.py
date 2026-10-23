#!/usr/bin/env python3
"""Static analysis of JavaScript / Electron application trees and ASARs.

Local companion to REA's live analyze_javascript_application (verified on
6.7.0 against extracted trees and ASAR archives): inventory the package,
find ipcMain channel registrations, contextBridge exposures in preloads,
and source-map presence. Static declarations only - a registered channel
proves the handler ships, not how it behaves at runtime.
"""
from __future__ import annotations

import json
import os
import re
import struct

IPC_HANDLE = re.compile(r"ipcMain\.(handle|on|once)\s*\(\s*['\"]([^'\"]+)['\"]")
BRIDGE_EXPOSE = re.compile(r"contextBridge\.exposeInMainWorld\s*\(\s*['\"]([^'\"]+)['\"]")
REQUIRE_ELECTRON = re.compile(r"require\s*\(\s*['\"]electron['\"]\s*\)|from\s+['\"]electron['\"]")


def scan_source(text: str) -> dict:
    """Scan one JS source file for IPC surface declarations."""
    channels = [{"channel": m.group(2), "method": m.group(1)} for m in IPC_HANDLE.finditer(text)]
    bridges = [m.group(1) for m in BRIDGE_EXPOSE.finditer(text)]
    return {"ipc_channels": channels, "bridge_keys": bridges,
            "uses_electron": bool(REQUIRE_ELECTRON.search(text))}


def scan_tree(root: str) -> dict:
    """Inventory a JS application directory."""
    package = {}
    pkg_path = os.path.join(root, "package.json")
    if os.path.exists(pkg_path):
        package = json.loads(open(pkg_path, encoding="utf-8").read())
    files = []
    channels, bridges = [], []
    source_maps = []
    for dirpath, _dirs, filenames in os.walk(root):
        for name in filenames:
            rel = os.path.relpath(os.path.join(dirpath, name), root)
            files.append(rel)
            if name.endswith(".map"):
                source_maps.append(rel)
            if name.endswith((".js", ".cjs", ".mjs", ".ts")):
                text = open(os.path.join(dirpath, name), encoding="utf-8", errors="replace").read()
                found = scan_source(text)
                for channel in found["ipc_channels"]:
                    channels.append({**channel, "file": rel})
                for key in found["bridge_keys"]:
                    bridges.append({"key": key, "file": rel})
    return {
        "format": "js_tree",
        "name": package.get("name"),
        "version": package.get("version"),
        "main": package.get("main"),
        "files": sorted(files),
        "ipc_channels": channels,
        "bridge_keys": bridges,
        "source_maps": source_maps,
        "limitations": ["static declarations only; handler behavior is a runtime question"],
    }


def parse_asar_header(data: bytes) -> dict:
    """Parse an ASAR archive header (Chromium pickle: two size words,
    then the JSON header) and return its file inventory."""
    if len(data) < 16:
        raise ValueError("asar too short")
    header_size = struct.unpack_from("<I", data, 4)[0]
    json_size = struct.unpack_from("<I", data, 12)[0]
    header = json.loads(data[16:16 + json_size].decode("utf-8"))
    files = []

    def walk(node, prefix=""):
        for name, entry in node.get("files", {}).items():
            path = f"{prefix}/{name}" if prefix else name
            if "files" in entry:
                walk(entry, path)
            else:
                files.append({"path": path, "size": entry.get("size"),
                              "offset": entry.get("offset"), "unpacked": entry.get("unpacked", False)})

    walk(header)
    return {"format": "asar", "header_size": header_size, "files": files,
            "data_offset": 8 + header_size}


def main(argv=None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Analyze a JS/Electron tree or ASAR archive.")
    parser.add_argument("path")
    args = parser.parse_args(argv)
    if os.path.isdir(args.path):
        result = scan_tree(args.path)
    else:
        result = parse_asar_header(open(args.path, "rb").read())
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
