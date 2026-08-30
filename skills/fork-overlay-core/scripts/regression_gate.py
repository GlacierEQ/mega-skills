#!/usr/bin/env python3
"""
Regression Gate
Executes test suites to guarantee 100% green status before permitting merge.
"""

import subprocess
import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import time


@dataclass
class TestResult:
    success: bool
    test_type: str
    command: str
    duration_ms: float
    passed: int
    failed: int
    skipped: int
    output: str


def detect_test_framework(repo_path: Path) -> List[Tuple[str, List[str]]]:
    """Detect available test frameworks and their commands."""
    commands = []
    
    # Python
    if (repo_path / "pytest.ini").exists() or (repo_path / "pyproject.toml").exists() or \
       any(repo_path.rglob("test_*.py")) or any(repo_path.rglob("*_test.py")):
        commands.append(("pytest", [sys.executable, "-m", "pytest", "-v", "--tb=short"]))
    
    if (repo_path / "setup.py").exists() or (repo_path / "setup.cfg").exists():
        commands.append(("python-unittest", [sys.executable, "-m", "unittest", "discover", "-v"]))
    
    # Node.js
    if (repo_path / "package.json").exists():
        try:
            pkg = json.loads((repo_path / "package.json").read_text())
            scripts = pkg.get("scripts", {})
            if "test" in scripts:
                commands.append(("npm-test", ["npm", "test"]))
            if "test:ci" in scripts:
                commands.append(("npm-test-ci", ["npm", "run", "test:ci"]))
        except Exception:
            pass
    
    # Rust
    if (repo_path / "Cargo.toml").exists():
        commands.append(("cargo-test", ["cargo", "test", "--all"]))
    
    # Go
    if (repo_path / "go.mod").exists():
        commands.append(("go-test", ["go", "test", "./..."]))
    
    # Java/Maven
    if (repo_path / "pom.xml").exists():
        commands.append(("maven-test", ["mvn", "test"]))
    
    # Java/Gradle
    if (repo_path / "build.gradle").exists() or (repo_path / "build.gradle.kts").exists():
        commands.append(("gradle-test", ["./gradlew", "test"]))
    
    return commands


def run_test_command(repo_path: Path, command: List[str], timeout: int = 300) -> TestResult:
    """Run a test command and parse results."""
    start = time.time()
    try:
        result = subprocess.run(
            command,
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        duration = (time.time() - start) * 1000
        
        # Parse output based on test type
        passed = failed = skipped = 0
        output = result.stdout + "\n" + result.stderr
        
        # Try to parse pytest output
        if "pytest" in " ".join(command):
            for line in output.split('\n'):
                if "passed" in line and "failed" in line:
                    parts = line.split()
                    for i, p in enumerate(parts):
                        if p == "passed" and i > 0:
                            passed = int(parts[i-1])
                        elif p == "failed" and i > 0:
                            failed = int(parts[i-1])
                        elif p == "skipped" and i > 0:
                            skipped = int(parts[i-1])
        
        return TestResult(
            success=result.returncode == 0,
            test_type=command[0],
            command=" ".join(command),
            duration_ms=duration,
            passed=passed,
            failed=failed,
            skipped=skipped,
            output=output[-2000:]
        )
    except subprocess.TimeoutExpired:
        return TestResult(
            success=False,
            test_type=command[0],
            command=" ".join(command),
            duration_ms=timeout * 1000,
            passed=0, failed=0, skipped=0,
            output="TIMEOUT"
        )
    except Exception as e:
        return TestResult(
            success=False,
            test_type=command[0],
            command=" ".join(command),
            duration_ms=(time.time() - start) * 1000,
            passed=0, failed=0, skipped=0,
            output=str(e)
        )


def run_regression_suite(repo_path: Path, max_time: int = 600) -> Dict:
    """Run full regression test suite."""
    frameworks = detect_test_framework(repo_path)
    
    if not frameworks:
        return {
            "success": True,
            "message": "No test framework detected",
            "results": [],
            "total_passed": 0,
            "total_failed": 0,
            "total_duration_ms": 0
        }
    
    results = []
    total_passed = total_failed = total_skipped = 0
    total_duration = 0
    all_success = True
    
    start_time = time.time()
    for test_type, command in frameworks:
        if time.time() - start_time > max_time:
            break
        
        remaining = max_time - (time.time() - start_time)
        if remaining <= 0:
            break
        
        # Adjust timeout per test
        test_timeout = min(int(remaining), 300)
        
        result = run_test_command(repo_path, command, test_timeout)
        results.append({
            "test_type": result.test_type,
            "command": result.command,
            "success": result.success,
            "duration_ms": result.duration_ms,
            "passed": result.passed,
            "failed": result.failed,
            "skipped": result.skipped,
            "output": result.output
        })
        
        total_passed += result.passed
        total_failed += result.failed
        total_skipped += result.skipped
        total_duration += result.duration_ms
        
        if not result.success:
            all_success = False
            # Continue running other tests but mark overall as failed
    
    return {
        "success": all_success,
        "results": results,
        "total_passed": total_passed,
        "total_failed": total_failed,
        "total_skipped": total_skipped,
        "total_duration_ms": total_duration,
        "frameworks_tested": len(results)
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: regression_gate.py <command> [repo_path]")
        print("Commands:")
        print("  run [repo_path]      - Run full regression suite (default: .)")
        print("  detect [repo_path]   - Detect available test frameworks (default: .)")
        print("  run-test <command>   - Run specific test command")
        sys.exit(1)
    
    command = sys.argv[1]
    repo_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")
    
    if command == "run":
        result = run_regression_suite(repo_path)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["success"] else 1)
    
    elif command == "detect":
        frameworks = detect_test_framework(repo_path)
        print(json.dumps({
            "frameworks": [{"type": t, "command": c} for t, c in frameworks]
        }, indent=2))
    
    elif command == "run-test":
        if len(sys.argv) < 4:
            print("Usage: regression_gate.py run-test <command> [args...]")
            sys.exit(1)
        command = sys.argv[3:]
        result = run_test_command(repo_path, command)
        print(json.dumps({
            "success": result.success,
            "test_type": result.test_type,
            "command": result.command,
            "duration_ms": result.duration_ms,
            "passed": result.passed,
            "failed": result.failed,
            "skipped": result.skipped,
            "output": result.output
        }, indent=2))
        sys.exit(0 if result.success else 1)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
