#!/usr/bin/env python3
"""
Overlay Isolator
Isolates local modifications to protected overlay directories.
"""

import subprocess
import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Set, Optional
from dataclasses import dataclass


PROTECTED_OVERLAYS = [
    "extensions/",
    "sidecars/",
    "plugins/",
    "overlays/",
    "custom/",
    "local/",
    "patches/",
]


@dataclass
class OverlayAnalysis:
    repo_path: str
    protected_dirs: List[str]
    modified_files: List[str]
    protected_modified: List[str]
    unprotected_modified: List[str]
    untracked_files: List[str]
    clean: bool


def run_git(repo_path: Path, args: List[str]) -> Tuple[int, str, str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_path)] + args,
            capture_output=True, text=True, timeout=30
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "timeout"
    except Exception as e:
        return -1, "", str(e)


def get_modified_files(repo_path: Path) -> List[str]:
    """Get all modified files in working tree."""
    code, stdout, _ = run_git(repo_path, ["status", "--porcelain"])
    if code != 0:
        return []
    
    files = []
    for line in stdout.split('\n'):
        if line.strip():
            # Format: "XY filename"
            parts = line.split(maxsplit=1)
            if len(parts) >= 2:
                files.append(parts[1])
    return files


def classify_modifications(repo_path: Path, protected_patterns: List[str] = None) -> OverlayAnalysis:
    """Classify modifications as protected or unprotected."""
    patterns = protected_patterns or PROTECTED_OVERLAYS
    repo_path = Path(repo_path).resolve()
    
    modified = get_modified_files(repo_path)
    protected_modified = []
    unprotected_modified = []
    
    for f in modified:
        is_protected = any(f.startswith(p.rstrip('/')) or f.startswith(p.rstrip('/') + '/') for p in patterns)
        if is_protected:
            protected_modified.append(f)
        else:
            unprotected_modified.append(f)
    
    # Get untracked files
    code, stdout, _ = run_git(repo_path, ["ls-files", "--others", "--exclude-standard"])
    untracked = [f for f in stdout.split('\n') if f.strip()] if code == 0 else []
    
    # Check clean
    clean = len(modified) == 0 and len(untracked) == 0
    
    return OverlayAnalysis(
        repo_path=str(repo_path),
        protected_dirs=patterns,
        modified_files=modified,
        protected_modified=protected_modified,
        unprotected_modified=unprotected_modified,
        untracked_files=untracked,
        clean=clean
    )


def verify_overlay_integrity(repo_path: Path, patterns: List[str] = None) -> Dict:
    """Verify overlay directories are intact and unmodified by upstream."""
    analysis = classify_modifications(repo_path, patterns)
    
    return {
        "repo_path": analysis.repo_path,
        "protected_dirs": analysis.protected_dirs,
        "total_modified": len(analysis.modified_files),
        "protected_modified_count": len(analysis.protected_modified),
        "unprotected_modified_count": len(analysis.unprotected_modified),
        "untracked_count": len(analysis.untracked_files),
        "clean": analysis.clean,
        "protected_modified": analysis.protected_modified,
        "unprotected_modified": analysis.unprotected_modified,
        "untracked": analysis.untracked_files,
        "integrity_ok": len(analysis.unprotected_modified) == 0 and analysis.clean
    }


def isolate_overlay_changes(repo_path: Path, output_dir: Path, patterns: List[str] = None) -> Dict:
    """Extract overlay changes to separate directory for safekeeping."""
    analysis = classify_modifications(repo_path, patterns)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    extracted = []
    for f in analysis.protected_modified:
        src = repo_path / f
        dst = output_dir / f
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            import shutil
            shutil.copy2(src, dst)
            extracted.append(f)
    
    return {
        "repo_path": str(repo_path),
        "output_dir": str(output_dir),
        "extracted_files": extracted,
        "count": len(extracted)
    }


def restore_overlay_changes(repo_path: Path, overlay_dir: Path, patterns: List[str] = None) -> Dict:
    """Restore overlay changes from backup directory."""
    overlay_dir = Path(overlay_dir)
    restored = []
    errors = []
    
    for pattern in patterns or PROTECTED_OVERLAYS:
        for src_file in overlay_dir.rglob(pattern.rstrip('/') + '/*' if pattern.endswith('/') else pattern):
            if src_file.is_file():
                rel_path = src_file.relative_to(overlay_dir)
                dst = repo_path / rel_path
                try:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    import shutil
                    shutil.copy2(src_file, dst)
                    restored.append(str(rel_path))
                except Exception as e:
                    errors.append(f"{rel_path}: {e}")
    
    return {
        "repo_path": str(repo_path),
        "overlay_dir": str(overlay_dir),
        "restored_files": restored,
        "errors": errors
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: overlay_isolator.py <command> [repo_path] [options]")
        print("Commands:")
        print("  analyze [repo_path]          - Analyze modifications (default: .)")
        print("  verify [repo_path]           - Verify overlay integrity (default: .)")
        print("  extract [repo_path] <out_dir> - Extract overlay changes to dir")
        print("  restore [repo_path] <overlay_dir> - Restore from overlay dir")
        sys.exit(1)
    
    command = sys.argv[1]
    repo_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")
    
    if command == "analyze":
        analysis = classify_modifications(repo_path)
        print(json.dumps({
            "repo_path": analysis.repo_path,
            "protected_dirs": analysis.protected_dirs,
            "modified_files": analysis.modified_files,
            "protected_modified": analysis.protected_modified,
            "unprotected_modified": analysis.unprotected_modified,
            "untracked_files": analysis.untracked_files,
            "clean": analysis.clean
        }, indent=2))
    
    elif command == "verify":
        result = verify_overlay_integrity(repo_path)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["integrity_ok"] else 1)
    
    elif command == "extract":
        if len(sys.argv) < 4:
            print("Usage: overlay_isolator.py extract <repo_path> <output_dir>")
            sys.exit(1)
        output_dir = Path(sys.argv[3])
        result = isolate_overlay_changes(repo_path, output_dir)
        print(json.dumps(result, indent=2))
    
    elif command == "restore":
        if len(sys.argv) < 4:
            print("Usage: overlay_isolator.py restore <repo_path> <overlay_dir>")
            sys.exit(1)
        overlay_dir = Path(sys.argv[3])
        result = restore_overlay_changes(repo_path, overlay_dir)
        print(json.dumps(result, indent=2))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
