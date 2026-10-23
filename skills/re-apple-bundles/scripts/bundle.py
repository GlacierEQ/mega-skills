#!/usr/bin/env python3
"""Apple bundle resource analysis: plists and NSKeyedArchiver graphs.

Local companion to REA's bundle lane. Verified 6.7.0 surface: a bundle
opens with open_binary (its CFBundleExecutable must exist) and
inspect_keyed_archive reads archives by bundle-relative path on Linux;
inspect_plist and inspect_asset_catalog are native-macOS provider
operations and are unavailable off macOS - this module carries the plist
and archive lanes locally with plistlib so the discipline (declared vs
exercised, located findings) holds on any host.
"""
from __future__ import annotations

import os
import plistlib


def parse_plist_bytes(data: bytes):
    """Parse an XML or binary plist into Python objects."""
    return plistlib.loads(data)


def declared_configuration(info: dict) -> dict:
    """Extract the declarations an Info.plist makes about the bundle:
    identity, executable, URL schemes, background modes, privacy usage
    strings. Declarations are claims, recorded as declared evidence."""
    declared = {
        "bundle_id": info.get("CFBundleIdentifier"),
        "executable": info.get("CFBundleExecutable"),
        "version": info.get("CFBundleShortVersionString"),
        "build": info.get("CFBundleVersion"),
        "url_schemes": [],
        "background_modes": info.get("UIBackgroundModes", []),
        "privacy_usage_strings": {},
    }
    for entry in info.get("CFBundleURLTypes", []) or []:
        declared["url_schemes"].extend(entry.get("CFBundleURLSchemes", []) or [])
    for key, value in info.items():
        if key.startswith("NS") and key.endswith("UsageDescription"):
            declared["privacy_usage_strings"][key] = value
    return declared


def openable(info: dict, bundle_root: str) -> dict:
    """REA's open_binary on a bundle requires the CFBundleExecutable file
    to exist; report that precondition explicitly."""
    executable = info.get("CFBundleExecutable")
    if not executable:
        return {"openable": False, "reason": "Info.plist names no CFBundleExecutable"}
    path = os.path.join(bundle_root, "Contents", "MacOS", executable)
    if not os.path.exists(path):
        return {"openable": False, "reason": f"executable missing at Contents/MacOS/{executable}"}
    return {"openable": True, "executable_path": path}


def decode_keyed_archive(archive: dict) -> dict:
    """Walk an NSKeyedArchiver object graph ($objects with UID refs) and
    return the reconstructed root object plus the class inventory. The
    graph is evidence of what was serialized, not of live runtime state."""
    objects = archive.get("$objects")
    if objects is None:
        raise ValueError("not an NSKeyedArchiver archive (no $objects)")
    classes = set()

    def resolve(node, depth=0):
        if depth > 40:
            return "<depth limit>"
        if isinstance(node, plistlib.UID):
            return resolve(objects[node.data], depth + 1)
        if isinstance(node, dict):
            if "$class" in node:
                class_ref = node["$class"]
                if isinstance(class_ref, plistlib.UID):
                    class_obj = objects[class_ref.data]
                    if isinstance(class_obj, dict):
                        classes.add(class_obj.get("$classname", "?"))
                return {k: resolve(v, depth + 1) for k, v in node.items() if k != "$class"}
            return {k: resolve(v, depth + 1) for k, v in node.items()}
        if isinstance(node, list):
            return [resolve(v, depth + 1) for v in node]
        return node

    top = archive.get("$top", {})
    root = {key: resolve(value) for key, value in top.items()}
    return {"root": root, "classes": sorted(classes), "object_count": len(objects),
            "limitations": ["serialized state only; not live runtime state"]}


def main(argv=None) -> int:
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Read a plist file or keyed archive.")
    parser.add_argument("path")
    args = parser.parse_args(argv)
    parsed = parse_plist_bytes(open(args.path, "rb").read())
    if isinstance(parsed, dict) and "$objects" in parsed:
        result = decode_keyed_archive(parsed)
    else:
        result = declared_configuration(parsed)
    print(json.dumps(result, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
