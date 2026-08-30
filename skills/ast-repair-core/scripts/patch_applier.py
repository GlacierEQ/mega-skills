#!/usr/bin/env python3
"""
Patch Applier
Applies surgical diffs to source files with backup and verification.
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import difflib


@dataclass
class PatchResult:
    success: bool
    file_path: str
    original_hash: str
    new_hash: str
    diff: str
    backup_path: Optional[str]
    verification: Dict


def compute_hash(content: str) -> str:
    import hashlib
    return hashlib.sha256(content.encode()).hexdigest()


def compute_file_hash(path: Path) -> str:
    import hashlib
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def create_backup(file_path: Path) -> Path:
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = file_path.with_suffix(f".backup_{timestamp}{file_path.suffix}")
    shutil.copy2(file_path, backup_path)
    return backup_path


def apply_patch(file_path: Path, original_code: str, replacement_code: str) -> Tuple[bool, str]:
    try:
        content = file_path.read_text(encoding="utf-8")
        
        if original_code not in content:
            lines = content.splitlines()
            orig_lines = original_code.splitlines()
            
            best_match = -1
            best_score = 0
            for i in range(len(lines) - len(orig_lines) + 1):
                window = "\n".join(lines[i:i+len(orig_lines)])
                score = sum(1 for a, b in zip(window.splitlines(), orig_lines) if a.strip() == b.strip())
                if score > best_score:
                    best_score = score
                    best_match = i
            
            if best_match >= 0 and best_score > len(orig_lines) * 0.7:
                new_lines = lines[:best_match] + replacement_code.splitlines() + lines[best_match+len(orig_lines):]
                new_content = "\n".join(new_lines)
                file_path.write_text(new_content, encoding="utf-8")
                return True, "fuzzy_match"
            
            return False, "original_code not found in file"
        
        new_content = content.replace(original_code, replacement_code, 1)
        file_path.write_text(new_content, encoding="utf-8")
        return True, "exact_match"
        
    except Exception as e:
        return False, f"apply error: {e}"


def generate_diff(original: str, modified: str, file_path: str) -> str:
    diff = difflib.unified_diff(
        original.splitlines(keepends=True),
        modified.splitlines(keepends=True),
        fromfile=f"a/{file_path}",
        tofile=f"b/{file_path}",
        lineterm=""
    )
    return "\n".join(diff)


def verify_syntax(file_path: Path) -> Tuple[bool, str]:
    try:
        import ast
        source = file_path.read_text(encoding="utf-8")
        ast.parse(source)
        return True, "Syntax OK"
    except SyntaxError as e:
        return False, f"SyntaxError: {e}"
    except Exception as e:
        return False, f"Verify error: {e}"


def has_test_functions(file_path: Path) -> bool:
    """Check if file contains test functions."""
    try:
        content = file_path.read_text(encoding="utf-8")
        return "def test_" in content or "class Test" in content
    except Exception:
        return False


def run_tests(file_path: Path, test_command: str = "pytest") -> Tuple[bool, str]:
    """Run tests - check for test functions in file, then dedicated test file, then module."""
    try:
        test_dir = file_path.parent
        
        # 1. Check if file itself has test functions
        if has_test_functions(file_path):
            result = subprocess.run(
                [sys.executable, "-m", "pytest", str(file_path), "-v", "--tb=short", "-p no:warnings"],
                capture_output=True, text=True, timeout=60, cwd=test_dir
            )
            return result.returncode == 0, result.stdout[-1000:]
        
        # 2. Check for dedicated test file
        test_file = test_dir / "tests" / f"test_{file_path.stem}.py"
        if test_file.exists():
            result = subprocess.run(
                [sys.executable, "-m", "pytest", str(test_file), "-v", "--tb=short", "-p no:warnings"],
                capture_output=True, text=True, timeout=60, cwd=test_dir
            )
            return result.returncode == 0, result.stdout[-1000:]
        
        # 3. Check for test file in same directory
        test_file_same = test_dir / f"test_{file_path.stem}.py"
        if test_file_same.exists():
            result = subprocess.run(
                [sys.executable, "-m", "pytest", str(test_file_same), "-v", "--tb=short", "-p no:warnings"],
                capture_output=True, text=True, timeout=60, cwd=test_dir
            )
            return result.returncode == 0, result.stdout[-1000:]
        
        return True, "No test file found"
    except subprocess.TimeoutExpired:
        return False, "Test timeout"
    except Exception as e:
        return False, f"Test error: {e}"


def apply_patch_file(patch_file: Path) -> 'PatchResult':
    data = json.loads(patch_file.read_text())
    
    file_path = Path(data["file_path"])
    original_code = data["original_code"]
    replacement_code = data["replacement_code"]
    
    if not file_path.exists():
        return PatchResult(
            success=False,
            file_path=str(file_path),
            original_hash="",
            new_hash="",
            diff="",
            backup_path=None,
            verification={"error": "File not found"}
        )
    
    backup_path = create_backup(file_path)
    original_hash = compute_file_hash(file_path)
    
    success, method = apply_patch(file_path, original_code, replacement_code)
    
    if not success:
        shutil.copy2(backup_path, file_path)
        return PatchResult(
            success=False,
            file_path=str(file_path),
            original_hash=original_hash,
            new_hash=original_hash,
            diff="",
            backup_path=str(backup_path),
            verification={"error": f"Patch apply failed: {method}"}
        )
    
    new_hash = compute_file_hash(file_path)
    original_content = backup_path.read_text(encoding="utf-8")
    new_content = file_path.read_text(encoding="utf-8")
    diff = generate_diff(original_content, new_content, file_path.name)
    
    syntax_ok, syntax_msg = verify_syntax(file_path)
    
    test_passed = False
    test_output = ""
    if syntax_ok:
        test_passed, test_output = run_tests(file_path)
        if not test_passed:
            shutil.copy2(backup_path, file_path)
            new_hash = original_hash
            success = False
    
    return PatchResult(
        success=success,
        file_path=str(file_path),
        original_hash=original_hash,
        new_hash=new_hash,
        diff=diff,
        backup_path=str(backup_path),
        verification={
            "syntax_ok": syntax_ok,
            "syntax_msg": syntax_msg,
            "test_passed": test_passed,
            "test_output": test_output[-1000:] if test_output else "",
            "apply_method": method
        }
    )


def main():
    if len(sys.argv) < 2:
        print("Usage: patch_applier.py <patch_json_file>")
        print("       patch_applier.py --file <target.py> --original 'code' --replacement 'code'")
        sys.exit(1)
    
    if sys.argv[1] == "--file":
        if len(sys.argv) < 7:
            print("Usage: patch_applier.py --file <target.py> --original 'code' --replacement 'code'")
            sys.exit(1)
        
        file_path = Path(sys.argv[2])
        args = " ".join(sys.argv[3:])
        if "--original" in args and "--replacement" in args:
            parts = args.split("--original")
            orig_part = parts[1].split("--replacement")[0].strip()
            repl_part = parts[1].split("--replacement")[1].strip()
            
            if orig_part.startswith("'") and orig_part.endswith("'"):
                orig_part = orig_part[1:-1]
            if repl_part.startswith("'") and repl_part.endswith("'"):
                repl_part = repl_part[1:-1]
            
            patch_data = {
                "file_path": str(file_path),
                "original_code": orig_part,
                "replacement_code": repl_part
            }
            
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(patch_data, f)
                patch_file = Path(f.name)
        else:
            print("Invalid arguments")
            sys.exit(1)
    else:
        patch_file = Path(sys.argv[1])
    
    result = apply_patch_file(patch_file)
    
    print(json.dumps({
        "success": result.success,
        "file_path": result.file_path,
        "original_hash": result.original_hash,
        "new_hash": result.new_hash,
        "diff": result.diff,
        "backup_path": result.backup_path,
        "verification": result.verification
    }, indent=2))
    
    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()
