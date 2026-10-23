#!/usr/bin/env python3
"""Target triage: classify an artifact and route it to its first tool.

Implements the re-target-triage routing discipline against the rea-agents
6.7.0 live surface. Classification is by magic bytes first, extension
second. The route names the family skill, the first REA tool (or the local
route when 6.7.0 exposes no tool for the class), and whether the lane is
session-bound (open_binary) or target-free.
"""
from __future__ import annotations

import os
import struct
import zipfile

# (family_skill, first_tool, session_bound, note)
ROUTES = {
    "elf": ("re-native-static-readers", "inspect_binary_layout", True, "ELF layout via caller-supplied pwntools"),
    "pe": ("re-native-static-readers", "inspect_pe_resources", False, "PE resources target-free; managed check routes to re-managed-dotnet"),
    "macho": ("re-engine-bridges", "open_binary", True, "Mach-O deep work needs a provider session"),
    "wasm": ("re-wasm-evm", "inspect_wasm_artifact", False, "WAT + interface, target-free"),
    "sqlite": ("re-native-static-readers", "inspect_sqlite_database", False, "schema-first inventory"),
    "gguf": ("re-gpu-model-artifacts", "local:gguf_header", False, "6.7.0 open_binary refuses GGUF; local header parser carries the lane"),
    "safetensors": ("re-gpu-model-artifacts", "local:safetensors_header", False, "6.7.0 exposes no model tool; local header parser"),
    "pck": ("re-game-artifacts", "local:godot_pck", False, "6.7.0 refuses Godot PCK at open_binary; local parser"),
    "il2cpp_metadata": ("re-game-artifacts", "local:il2cpp_header", False, "no inspect_il2cpp_metadata tool in 6.7.0; local header parser"),
    "apk": ("re-mobile-android", "inspect_android_package", False, "JADX-backed package inspection, explicit path"),
    "asar": ("re-javascript-electron", "analyze_javascript_application", False, "tree or ASAR, explicit path"),
    "js_tree": ("re-javascript-electron", "analyze_javascript_application", False, "directory with package.json"),
    "har": ("re-web-network-analysis", "inspect_web_network_capture", False, "strict HAR validation applies"),
    "pcap": ("re-web-network-analysis", "inspect_pcap_capture", False, "requires caller-supplied tshark/capinfos"),
    "firmware": ("re-firmware-extraction", "extract_firmware", False, "carve with caller-supplied unblob/binwalk"),
    "sr": ("re-signal-recordings", "local:sigrok_session", False, "REA signal readers need sigrok-cli; local session parser is the fallback"),
    "pyc": ("re-native-static-readers", "local:pyc_header", False, "no inspect_python_pyc tool in 6.7.0; local header parser"),
    "dex": ("re-mobile-android", "inspect_android_package", False, "dex rides inside an APK for the JADX lane"),
    "evm": ("re-wasm-evm", "inspect_evm_interface", False, "selector dispatcher surface"),
    "unknown": (None, None, False, "identify before routing; never guess a lane"),
}


def classify_bytes(head: bytes, name: str = "") -> str:
    if head.startswith(b"\x7fELF"):
        return "elf"
    if head.startswith(b"MZ"):
        return "pe"
    if head[:4] in (b"\xfe\xed\xfa\xce", b"\xfe\xed\xfa\xcf", b"\xce\xfa\xed\xfe",
                    b"\xcf\xfa\xed\xfe", b"\xca\xfe\xba\xbe"):
        return "macho"
    if head.startswith(b"\x00asm"):
        return "wasm"
    if head.startswith(b"SQLite format 3\x00"):
        return "sqlite"
    if head.startswith(b"GGUF"):
        return "gguf"
    if head.startswith(b"GDPC"):
        return "pck"
    if head[:4] == struct.pack("<I", 0xFAB11BAF):
        return "il2cpp_metadata"
    if head.startswith(b"dex\n"):
        return "dex"
    if head.startswith(b"\xd4\xc3\xb2\xa1") or head.startswith(b"\xa1\xb2\xc3\xd4"):
        return "pcap"
    if head.startswith(b"\x27\x05\x19\x56"):  # uImage magic
        return "firmware"
    ext = os.path.splitext(name)[1].lower()
    if ext == ".safetensors":
        return "safetensors"
    if ext == ".pyc":
        return "pyc"
    if ext == ".har":
        return "har"
    if ext == ".sr":
        return "sr"
    if ext == ".hex" and name.startswith("evm"):
        return "evm"
    return "unknown"


def classify_path(path: str) -> dict:
    """Classify a file or JS tree directory and return the triage record."""
    if os.path.isdir(path):
        kind = "js_tree" if os.path.exists(os.path.join(path, "package.json")) else "unknown"
        return _record(path, kind)
    with open(path, "rb") as handle:
        head = handle.read(16)
    kind = classify_bytes(head, os.path.basename(path))
    if kind == "unknown" and zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
        if "AndroidManifest.xml" in names and any(n.endswith(".dex") for n in names):
            kind = "apk"
        elif any(n == "header.json" or n.endswith(".asar") for n in names) or path.endswith(".asar"):
            kind = "asar"
        elif "metadata" in names and path.endswith(".sr"):
            kind = "sr"
    if path.endswith(".asar"):
        kind = "asar"
    if path.endswith(".sr"):
        kind = "sr"
    return _record(path, kind)


def _record(path: str, kind: str) -> dict:
    family, tool, session_bound, note = ROUTES[kind]
    return {
        "target": path,
        "artifact_class": kind,
        "family_skill": family,
        "first_tool": tool,
        "session_bound": session_bound,
        "note": note,
        "identity_resolved": kind != "unknown",
    }


def main(argv=None) -> int:
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Classify and route a reverse-engineering target.")
    parser.add_argument("path")
    args = parser.parse_args(argv)
    record = classify_path(args.path)
    print(json.dumps(record, indent=2))
    return 0 if record["identity_resolved"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
