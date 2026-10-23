#!/usr/bin/env python3
"""Read-only SDK manifest reconnaissance. No imports, network, or shell execution."""
import argparse
import hashlib
import json
import re
from pathlib import Path

SDK_NAME = re.compile(r"(?:^|[-_/.@])(?:sdk|client|api)(?:$|[-_/])", re.I)
KNOWN_CLIENT_PACKAGES = {"openai", "anthropic", "ai", "@openai/agents", "boto3", "botocore", "google-genai", "@google/genai", "@modelcontextprotocol/sdk", "mcp", "@anthropic-ai/sdk", "@ai-sdk/openai", "@ai-sdk/anthropic", "@ai-sdk/google", "stripe", "@stripe/stripe-js", "aws-sdk", "@aws-sdk/client-s3", "@azure/identity", "azure-identity"}
SAFE_PACKAGE = re.compile(r"^(?:@[A-Za-z0-9_.-]+/)?[A-Za-z0-9_.-]+$")
SAFE_SPEC = re.compile(r"^[\^~<>=!v*0-9][\w.*+~^<>=!|, \-]*$|^workspace:[\w.*^~\-]+$")


def safe_spec(value):
    return value if isinstance(value, str) and len(value) <= 100 and SAFE_SPEC.fullmatch(value) else "SPEC_REDACTED_OR_UNSUPPORTED"


def add_candidate(candidates, ecosystem, name, constraint, source):
    if not isinstance(name, str) or not (SDK_NAME.search(name) or name.lower() in KNOWN_CLIENT_PACKAGES):
        return
    candidates.append({"ecosystem": ecosystem, "package": name, "declared_spec": safe_spec(constraint), "source": source, "installed_version": None, "public_exports_verified": False})


def inspect(root):
    root = Path(root).resolve()
    if not root.is_dir():
        raise ValueError("ROOT_NOT_DIRECTORY")
    report = {"schema_version": 1, "manifests": [], "sdk_candidates": [], "package_identity": None, "warnings": [], "execution": "READ_ONLY_STATIC_DISCOVERY", "provider_verified": False}
    for name in ("package.json", "pyproject.toml", "go.mod", "Cargo.toml"):
        path = root / name
        if not path.exists():
            continue
        if path.is_symlink() or not path.is_file():
            report["warnings"].append("SKIPPED_UNSAFE_MANIFEST:" + name)
            continue
        blob = path.read_bytes()
        report["manifests"].append({"path": name, "sha256": hashlib.sha256(blob).hexdigest()})
        if name == "package.json":
            try:
                obj = json.loads(blob)
                if not isinstance(obj, dict):
                    raise ValueError("expected object")
                exports = obj.get("exports") or {}
                conditions = set()
                if isinstance(exports, dict):
                    for field in exports.values():
                        if isinstance(field, dict):
                            conditions.update(k for k in field if k in {"import", "require", "types", "default", "node", "browser"})
                name_value = obj.get("name")
                report["package_identity"] = {
                    "ecosystem": "npm", "package": name_value if isinstance(name_value, str) and SAFE_PACKAGE.fullmatch(name_value) else "UNKNOWN_OR_REDACTED",
                    "declared_version": safe_spec(obj.get("version")), "export_conditions": sorted(conditions), "exports_verified": False
                }
                for section in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
                    for pkg, spec in (obj.get(section) or {}).items():
                        add_candidate(report["sdk_candidates"], "npm", pkg, spec, name + ":" + section)
            except (ValueError, AttributeError, TypeError):
                report["warnings"].append("PARSE_FAILED:" + name)
        elif name in ("pyproject.toml", "Cargo.toml"):
            try:
                import tomllib
                obj = tomllib.loads(blob.decode("utf-8"))
                if name == "pyproject.toml":
                    dep_sections = [obj.get("project", {}).get("dependencies", [])]
                    dep_sections += list(obj.get("project", {}).get("optional-dependencies", {}).values())
                    for seq in dep_sections:
                        for dep in seq:
                            if isinstance(dep, str):
                                match = re.match(r"^([A-Za-z0-9_.-]+)\s*(.*)$", dep)
                                if match:
                                    add_candidate(report["sdk_candidates"], "pypi", match[1], match[2].strip() or "*", name)
                    for pkg, spec in obj.get("tool", {}).get("poetry", {}).get("dependencies", {}).items():
                        add_candidate(report["sdk_candidates"], "pypi", pkg, spec, name + ":poetry")
                else:
                    for pkg, spec in obj.get("dependencies", {}).items():
                        add_candidate(report["sdk_candidates"], "cargo", pkg, spec if isinstance(spec, str) else spec.get("version"), name)
            except (ImportError, UnicodeDecodeError, ValueError, TypeError, AttributeError):
                report["warnings"].append("PARSE_FAILED_OR_TOMLLIB_UNAVAILABLE:" + name)
        elif name == "go.mod":
            for line in blob.decode("utf-8", errors="replace").splitlines():
                match = re.match(r"^\s*([A-Za-z0-9._/-]+)\s+(v\d[^\s]*)", line)
                if match:
                    add_candidate(report["sdk_candidates"], "go", match[1], match[2], name)
    report["sdk_candidates"].sort(key=lambda c: (c["ecosystem"], c["package"], c["source"]))
    if not report["manifests"]:
        report["warnings"].append("NO_SUPPORTED_ROOT_MANIFEST")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", help="Existing checked-out project root (read only)")
    args = parser.parse_args()
    try:
        report = inspect(args.root)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
