#!/usr/bin/env python3
"""
State Verifier
Verifies action outcomes through screen delta, clipboard inspection, process exit status.
"""

import subprocess
import json
import sys
import hashlib
import time
from pathlib import Path
from typing import Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class VerificationResult:
    success: bool
    method: str
    details: Dict


def compute_image_hash(image_path: str) -> str:
    """Compute SHA-256 hash of image file."""
    import hashlib
    h = hashlib.sha256()
    with open(image_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def compare_images(before_path: str, after_path: str, threshold: float = 0.01) -> Tuple[bool, float]:
    """Compare two images using sips/imagemagick if available, fallback to hash."""
    try:
        # Try using imagemagick compare if available
        result = subprocess.run(
            ["compare", "-metric", "AE", before_path, after_path, "/dev/null"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            diff_pixels = int(result.stderr.strip())
            return diff_pixels == 0, 0.0
    except Exception:
        pass
    
    # Fallback: hash comparison
    hash1 = compute_image_hash(before_path)
    hash2 = compute_image_hash(after_path)
    return hash1 == hash2, 0.0 if hash1 == hash2 else 1.0


def verify_screen_delta(before_path: str, after_path: str, threshold: float = 0.01) -> VerificationResult:
    """Verify visual state change via screen delta."""
    try:
        identical, diff_ratio = compare_images(before_path, after_path)
        return VerificationResult(
            success=identical,
            method="screen_delta",
            details={
                "before": before_path,
                "after": after_path,
                "identical": identical,
                "diff_ratio": diff_ratio
            }
        )
    except Exception as e:
        return VerificationResult(
            success=False,
            method="screen_delta",
            details={"error": str(e)}
        )


def get_clipboard_text() -> str:
    """Get clipboard text content."""
    try:
        result = subprocess.run(
            ["pbpaste"],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout
    except Exception:
        return ""


def get_clipboard_image(output_path: str) -> bool:
    """Save clipboard image to file."""
    try:
        result = subprocess.run(
            ["osascript", "-e", f'tell application "System Events" to write (the clipboard as «class PNGf») to (open for access "{output_path}" with write permission)'],
            capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except Exception:
        return False


def verify_clipboard_contains(expected: str, case_sensitive: bool = True) -> VerificationResult:
    """Verify clipboard contains expected text."""
    actual = get_clipboard_text()
    
    if not case_sensitive:
        expected = expected.lower()
        actual = actual.lower()
    
    contains = expected in actual
    return VerificationResult(
        success=contains,
        method="clipboard_text",
        details={
            "expected": expected[:100],
            "actual_length": len(actual),
            "actual_preview": actual[:100]
        }
    )


def verify_clipboard_changed(before_hash: str) -> VerificationResult:
    """Verify clipboard content changed."""
    actual = get_clipboard_text()
    current_hash = hashlib.sha256(actual.encode()).hexdigest()
    changed = current_hash != before_hash
    return VerificationResult(
        success=changed,
        method="clipboard_change",
        details={
            "before_hash": before_hash[:16],
            "after_hash": current_hash[:16],
            "changed": changed
        }
    )


def get_process_exit_status(pid: int) -> Optional[int]:
    """Get exit status of a process (if terminated)."""
    try:
        result = subprocess.run(
            ["wait", str(pid)],
            capture_output=True, text=True, timeout=1
        )
        return result.returncode
    except Exception:
        return None


def is_process_alive(pid: int) -> bool:
    """Check if process is still running."""
    try:
        result = subprocess.run(
            ["ps", "-p", str(pid)],
            capture_output=True, text=True
        )
        return result.returncode == 0 and str(pid) in result.stdout
    except Exception:
        return False


def wait_for_process_exit(pid: int, timeout: float = 30.0) -> Optional[int]:
    """Wait for process to exit and return exit code."""
    start = time.time()
    while time.time() - start < timeout:
        if not is_process_alive(pid):
            return get_process_exit_status(pid)
        time.sleep(0.1)
    return None


def verify_process_terminated(pid: int, timeout: float = 5.0) -> VerificationResult:
    """Verify process has terminated."""
    start = time.time()
    while time.time() - start < timeout:
        if not is_process_alive(pid):
            exit_code = get_process_exit_status(pid)
            return VerificationResult(
                success=True,
                method="process_exit",
                details={"pid": pid, "exit_code": exit_code, "terminated": True}
            )
        time.sleep(0.1)
    
    return VerificationResult(
        success=False,
        method="process_exit",
        details={"pid": pid, "terminated": False, "timeout": timeout}
    )


def verify_process_running(pid: int) -> VerificationResult:
    """Verify process is running."""
    alive = is_process_alive(pid)
    return VerificationResult(
        success=alive,
        method="process_running",
        details={"pid": pid, "alive": alive}
    )


def main():
    if len(sys.argv) < 2:
        print("Usage: state_verifier.py <command> [args...]")
        print("Commands:")
        print("  screen-delta <before> <after>      - Compare two screenshots")
        print("  clipboard-contains <text>          - Check clipboard contains text")
        print("  clipboard-changed <before_hash>    - Check clipboard changed")
        print("  process-exit <pid> [timeout]       - Wait for process exit")
        print("  process-running <pid>              - Check if process alive")
        print("  process-terminated <pid> [timeout] - Verify process terminated")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "screen-delta":
        if len(sys.argv) < 4:
            print("Usage: state_verifier.py screen-delta <before.png> <after.png>")
            sys.exit(1)
        result = verify_screen_delta(sys.argv[2], sys.argv[3])
        print(json.dumps({
            "success": result.success,
            "method": result.method,
            "details": result.details
        }, indent=2))
    
    elif command == "clipboard-contains":
        if len(sys.argv) < 3:
            print("Usage: state_verifier.py clipboard-contains <text>")
            sys.exit(1)
        result = verify_clipboard_contains(" ".join(sys.argv[2:]))
        print(json.dumps({
            "success": result.success,
            "method": result.method,
            "details": result.details
        }, indent=2))
    
    elif command == "clipboard-changed":
        if len(sys.argv) < 3:
            print("Usage: state_verifier.py clipboard-changed <before_hash>")
            sys.exit(1)
        result = verify_clipboard_changed(sys.argv[2])
        print(json.dumps({
            "success": result.success,
            "method": result.method,
            "details": result.details
        }, indent=2))
    
    elif command == "process-exit":
        if len(sys.argv) < 3:
            print("Usage: state_verifier.py process-exit <pid> [timeout]")
            sys.exit(1)
        pid = int(sys.argv[2])
        timeout = float(sys.argv[3]) if len(sys.argv) > 3 else 30.0
        exit_code = wait_for_process_exit(pid, timeout)
        print(json.dumps({
            "success": exit_code is not None,
            "method": "process_wait",
            "details": {"pid": pid, "exit_code": exit_code}
        }, indent=2))
    
    elif command == "process-running":
        if len(sys.argv) < 3:
            print("Usage: state_verifier.py process-running <pid>")
            sys.exit(1)
        pid = int(sys.argv[2])
        from state_verifier import is_process_alive
        alive = is_process_alive(pid)
        print(json.dumps({"success": alive, "method": "process_running", "details": {"pid": pid, "alive": alive}}, indent=2))
    
    elif command == "process-terminated":
        if len(sys.argv) < 3:
            print("Usage: state_verifier.py process-terminated <pid> [timeout]")
            sys.exit(1)
        pid = int(sys.argv[2])
        timeout = float(sys.argv[3]) if len(sys.argv) > 3 else 5.0
        result = verify_process_terminated(pid, timeout)
        print(json.dumps({
            "success": result.success,
            "method": result.method,
            "details": result.details
        }, indent=2))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
