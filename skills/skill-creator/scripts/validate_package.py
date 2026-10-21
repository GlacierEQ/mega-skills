#!/usr/bin/env python3
"""Read-only, stdlib-only preflight for an agent Skill package.

This is not a behavioral evaluator, runtime activation, or release certification.
"""
import argparse
import hashlib
import io
import zipfile
import json
import re
from pathlib import Path

NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK = re.compile(r"(?<!!)\[[^]]*\]\(([^)]+)\)")
SECRET = re.compile(r"(?i)(?:\b(?:api[_-]?key|access[_-]?token|client[_-]?secret)\b\s*[:=]\s*['\"]?(?!example\b|placeholder\b|your\b|\$\{)[a-z0-9_./+\-]{20,}|\bgh[pousr]_[A-Za-z0-9]{30,}\b)")


def _source_resource(path, root):
    relative = path.relative_to(root)
    return not any(part in {"__pycache__", ".git", ".DS_Store"} or part.endswith(".pyc") for part in relative.parts)


def inspect_skill(path):
    root = Path(path).resolve()
    errors, warnings, checks = [], [], []
    if not root.is_dir():
        return {"status": "FAIL", "errors": ["SKILL_DIRECTORY_MISSING"], "warnings": [], "checks": [], "behavioral_evaluation": "NOT_RUN", "package_sha256": None}
    manifest = root / "SKILL.md"
    if not manifest.is_file() or manifest.is_symlink():
        errors.append("SKILL_MANIFEST_MISSING_OR_LINKED")
        content = ""
    else:
        content = manifest.read_text(encoding="utf-8")
    meta = re.match(r"\A---\r?\n(.*?)\r?\n---\r?\n", content, re.S)
    if not meta:
        errors.append("FRONTMATTER_INVALID")
    else:
        properties = {}
        for line in meta.group(1).splitlines():
            match = re.match(r"^([a-z][a-z-]*):\s*(.*?)\s*$", line)
            if match:
                key, value = match.groups()
                if key in properties:
                    errors.append(f"DUPLICATE_METADATA:{key}")
                if value.startswith(("'", '"')) and (len(value) < 2 or value[-1] != value[0]):
                    errors.append(f"UNTERMINATED_FRONTMATTER_QUOTE:{key}")
                properties[key] = value.strip(' "\'')
        name, description = properties.get("name", ""), properties.get("description", "")
        if not NAME.fullmatch(name) or len(name) > 64 or name != root.name:
            errors.append("INVALID_OR_MISMATCHED_SKILL_NAME")
        if not description or len(description) > 1024:
            errors.append("DESCRIPTION_MISSING_OR_TOO_LONG")
        elif not re.search(r"\b(?:use|when|for|trigger|create|update|analy[sz]e)\b", description, re.I):
            warnings.append("DESCRIPTION_TRIGGER_NEEDS_REVIEW")
        checks.append("frontmatter_extracted")
    if len(content.strip()) < 180:
        errors.append("INSUFFICIENT_SKILL_PROCEDURE")
    if "#" not in content:
        warnings.append("NO_MARKDOWN_HEADINGS")
    if not re.search(r"\b(?:verify|validate|test|check)\b", content, re.I):
        warnings.append("NO_VERIFICATION_GUIDANCE")
    # Scan resources without following symlinks or allowing local references to escape root.
    files = []
    for p in sorted(root.rglob("*")):
        if not _source_resource(p, root):
            continue
        if p.is_symlink():
            errors.append(f"SYMLINK_RESOURCE:{p.relative_to(root)}")
        elif p.is_file():
            files.append(p)
    for raw in LINK.findall(content):
        target = raw.split("#", 1)[0].split("?", 1)[0].strip().strip('<>')
        scheme = re.match(r"^([a-z][a-z0-9+.-]*):", target, re.I)
        if scheme:
            if scheme.group(1).lower() not in {"https", "http", "mailto"}:
                errors.append(f"UNSAFE_REFERENCE_SCHEME:{scheme.group(1).lower()}")
            continue
        if not target:
            continue
        resolved = (root / target).resolve()
        if not resolved.is_relative_to(root):
            errors.append(f"REFERENCE_ESCAPES_SKILL:{target}")
        elif not resolved.is_file() or resolved.is_symlink():
            errors.append(f"BROKEN_LOCAL_REFERENCE:{target}")
    digest = hashlib.sha256()
    for p in files:
        rel = p.relative_to(root).as_posix()
        if p.name in {".env", "id_rsa", "id_ed25519", "credentials.json"} or p.name.startswith(".env.") or p.suffix.lower() in {".pem", ".p12", ".pfx", ".key"}:
            errors.append(f"SENSITIVE_RESOURCE_PATH:{rel}")
        data = p.read_bytes()
        digest.update(rel.encode() + b"\0" + data + b"\0")
        if len(data) > 2_000_000:
            warnings.append(f"LARGE_RESOURCE_REVIEW:{rel}")
        if p.suffix in {".md", ".json", ".yaml", ".yml", ".py", ".sh", ".txt"}:
            if SECRET.search(data.decode("utf-8", errors="replace")):
                errors.append(f"POTENTIAL_EMBEDDED_SECRET:{rel}")
    checks.extend(["resource_boundaries_checked", "package_digest_calculated"])
    return {
        "status": "FAIL" if errors else "PASS_STATIC_ONLY",
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
        "checks": checks,
        "behavioral_evaluation": "NOT_RUN",
        "provider_execution": "NOT_RUN",
        "package_sha256": digest.hexdigest(),
    }



def package_validated_skill(path, output_directory):
    """Create a stable ZIP-based .skill; never overwrite a different existing artifact."""
    root = Path(path).resolve()
    destination = Path(output_directory).resolve()
    if destination == root or destination.is_relative_to(root):
        raise ValueError("PACKAGE_OUTPUT_INSIDE_SOURCE")
    assessment = inspect_skill(root)
    if assessment["status"] != "PASS_STATIC_ONLY":
        raise ValueError("PACKAGE_STATIC_VALIDATION_FAILED:" + ",".join(assessment["errors"]))
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for file_path in sorted(root.rglob("*")):
            if not _source_resource(file_path, root) or not file_path.is_file():
                continue
            if file_path.is_symlink():
                raise ValueError("SYMLINK_RESOURCE")
            path_in_archive = root.name + "/" + file_path.relative_to(root).as_posix()
            info = zipfile.ZipInfo(path_in_archive, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, file_path.read_bytes())
    blob = buffer.getvalue()
    digest = hashlib.sha256(blob).hexdigest()
    destination.mkdir(parents=True, exist_ok=True)
    artifact = destination / (root.name + ".skill")
    if artifact.exists():
        if artifact.is_symlink() or hashlib.sha256(artifact.read_bytes()).hexdigest() != digest:
            raise FileExistsError("PACKAGE_ARTIFACT_ALREADY_EXISTS_DIFFERENT")
    else:
        artifact.write_bytes(blob)
    return {"artifact": artifact, "sha256": digest, "status": "PACKAGE_CREATED_NOT_ACTIVATED"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_directory", type=Path)
    parser.add_argument("--package", metavar="OUTPUT_DIRECTORY", type=Path, help="Package only after static validation; never install or activate")
    args = parser.parse_args(argv)
    result = inspect_skill(args.skill_directory)
    if args.package and result["status"] == "PASS_STATIC_ONLY":
        try:
            bundle = package_validated_skill(args.skill_directory, args.package)
            result["packaging"] = {"artifact": str(bundle["artifact"]), "sha256": bundle["sha256"], "status": bundle["status"]}
        except (OSError, ValueError) as exc:
            result["status"] = "FAIL"
            result["errors"].append(f"PACKAGING_FAILED:{exc}")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS_STATIC_ONLY" else 2


if __name__ == "__main__":
    raise SystemExit(main())