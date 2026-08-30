#!/usr/bin/env python3
"""
Traceback Parser
Parses pytest, npm test, cargo test failure tracebacks to extract exact file/line/defect.
"""

import re
import json
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class TracebackFrame:
    file: str
    line: int
    function: str
    code_context: str
    snippet: str = ""


@dataclass
class ParsedTraceback:
    test_command: str
    error_type: str
    error_message: str
    frames: List[TracebackFrame]
    root_cause_frame: Optional[TracebackFrame]


def extract_code_snippet(file_path: Path, line: int, context: int = 10) -> str:
    """Extract code snippet around the error line."""
    try:
        lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()
        start = max(0, line - context - 1)
        end = min(len(lines), line + context)
        snippet = []
        for i in range(start, end):
            marker = ">>> " if i == line - 1 else "    "
            snippet.append(f"{marker}{i+1:4d}: {lines[i]}")
        return "\n".join(snippet)
    except Exception:
        return ""


def parse_pytest_traceback(output: str) -> Optional[ParsedTraceback]:
    """Parse pytest traceback output (modern pytest format with FAILURES section)."""
    frames = []
    
    # Extract FAILURES section
    failures_match = re.search(
        r'={10,}\s*FAILURES\s*={10,}(.*?)(?:={10,}\s*(?:ERRORS|warnings|short test summary|passed|failed)|$)',
        output, re.DOTALL | re.IGNORECASE
    )
    
    failure_blocks = []
    if failures_match:
        failures_text = failures_match.group(1)
        # Split by test separators
        failure_blocks = re.findall(
            r'_{10,}\s*(.*?)\s*_{10,}(.*?)(?=_{10,}|={10,}|$)',
            failures_text, re.DOTALL
        )
    
    error_type = "AssertionError"
    error_message = ""
    
    for test_name, block in failure_blocks:
        # Extract E lines (error messages)
        e_lines = re.findall(r'^E\s+(.+)$', block, re.MULTILINE)
        if e_lines and not error_message:
            error_message = e_lines[0]
            # Determine error type from first E line
            first_e = e_lines[0]
            if "AssertionError" in first_e:
                error_type = "AssertionError"
            elif "TypeError" in first_e:
                error_type = "TypeError"
            elif "AttributeError" in first_e:
                error_type = "AttributeError"
            elif "KeyError" in first_e:
                error_type = "KeyError"
            elif "IndexError" in first_e:
                error_type = "IndexError"
            elif "ValueError" in first_e:
                error_type = "ValueError"
            elif "ZeroDivisionError" in first_e:
                error_type = "ZeroDivisionError"
            elif "ImportError" in first_e:
                error_type = "ImportError"
            elif "ModuleNotFoundError" in first_e:
                error_type = "ModuleNotFoundError"
            elif "NameError" in first_e:
                error_type = "NameError"
            elif "SyntaxError" in first_e:
                error_type = "SyntaxError"
            else:
                # Extract error type from message
                match = re.match(r'(\w+(?:Error|Exception))', first_e)
                if match:
                    error_type = match.group(1)
        
        # Extract code lines (indented with 4 spaces)
        code_lines = re.findall(r'^    (\S.+)$', block, re.MULTILINE)
        
        # Look for traceback lines: File "file.py", line N, in func
        tb_pattern = re.compile(r'File "([^"]+)", line (\d+), in (\w+)\n\s*(.+)')
        for match in tb_pattern.finditer(block):
            file_path, line_str, func_name, code = match.groups()
            frames.append(TracebackFrame(
                file=file_path,
                line=int(line_str),
                function=func_name,
                code_context=code.strip()
            ))
        
        # Also look for file.py:line: Error format at end of block
        file_line_pattern = re.compile(r'^(\S+\.py):(\d+):\s*(\w+(?:Error|Exception))?:?\s*(.*)$', re.MULTILINE)
        for match in file_line_pattern.finditer(block):
            file_path, line_str, err_type, msg = match.groups()
            # Skip if it's just the test file summary line
            if file_path.startswith('test_') and not msg and not err_type:
                continue
            frames.append(TracebackFrame(
                file=file_path,
                line=int(line_str),
                function="",
                code_context=msg.strip() if msg else (err_type or "error")
            ))
    
    # If no frames from FAILURES section, try whole output
    if not frames:
        # Look for traceback format in full output
        tb_pattern = re.compile(r'File "([^"]+)", line (\d+), in (\w+)\n\s*(.+)')
        for match in tb_pattern.finditer(output):
            file_path, line_str, func_name, code = match.groups()
            frames.append(TracebackFrame(
                file=file_path,
                line=int(line_str),
                function=func_name,
                code_context=code.strip()
            ))
        
        # Also check for file:line pattern in full output
        file_line_pattern = re.compile(r'^(\S+\.py):(\d+):\s*(\w+(?:Error|Exception))?:?\s*(.*)$', re.MULTILINE)
        for match in file_line_pattern.finditer(output):
            file_path, line_str, err_type, msg = match.groups()
            frames.append(TracebackFrame(
                file=file_path,
                line=int(line_str),
                function="",
                code_context=msg.strip() if msg else (err_type or "error")
            ))
    
    # Extract error type/message from E lines in full output if not found
    if not error_message:
        e_lines = re.findall(r'^E\s+(.+)$', output, re.MULTILINE)
        if e_lines:
            error_message = e_lines[0]
            if "AssertionError" in error_message:
                error_type = "AssertionError"
            elif "TypeError" in error_message:
                error_type = "TypeError"
            elif "AttributeError" in error_message:
                error_type = "AttributeError"
            elif "KeyError" in error_message:
                error_type = "KeyError"
            elif "IndexError" in error_message:
                error_type = "IndexError"
            elif "ValueError" in error_message:
                error_type = "ValueError"
            elif "ZeroDivisionError" in error_message:
                error_type = "ZeroDivisionError"
            elif "ImportError" in error_message:
                error_type = "ImportError"
            elif "ModuleNotFoundError" in error_message:
                error_type = "ModuleNotFoundError"
            elif "NameError" in error_message:
                error_type = "NameError"
            elif "SyntaxError" in error_message:
                error_type = "SyntaxError"
    
    # Deduplicate frames
    seen = set()
    unique_frames = []
    for f in frames:
        key = (f.file, f.line)
        if key not in seen:
            seen.add(key)
            unique_frames.append(f)
    
    if not unique_frames:
        return None
    
    # Enrich frames with snippets and function names
    for frame in unique_frames:
        frame.snippet = extract_code_snippet(Path(frame.file), frame.line)
        if not frame.function:
            for line in frame.snippet.split('\n'):
                if 'def ' in line and '>>> ' in line:
                    match = re.search(r'def (\w+)', line)
                    if match:
                        frame.function = match.group(1)
                        break
    
    root_cause = unique_frames[0] if unique_frames else None
    
    return ParsedTraceback(
        test_command="pytest",
        error_type=error_type if 'error_type' in locals() else "AssertionError",
        error_message=error_message,
        frames=unique_frames,
        root_cause_frame=root_cause
    )


def parse_npm_traceback(output: str) -> Optional[ParsedTraceback]:
    """Parse npm/Jest traceback output."""
    frames = []
    pattern = re.compile(r'\s+at (\w+(?:\.\w+)*)\s+\(([^:]+):(\d+):(\d+)\)')
    for match in pattern.finditer(output):
        func_name, file_path, line_str, col_str = match.groups()
        frames.append(TracebackFrame(
            file=file_path,
            line=int(line_str),
            function=func_name,
            code_context=f"at {func_name}"
        ))
    
    error_lines = [l for l in output.split('\n') if 'Error:' in l or 'error:' in l.lower()]
    error_message = error_lines[0].strip() if error_lines else "Unknown error"
    error_type = "JavaScriptError"
    
    if not frames:
        return None
    
    for frame in frames:
        frame.snippet = extract_code_snippet(Path(frame.file), frame.line)
    
    return ParsedTraceback(
        test_command="npm test",
        error_type=error_type,
        error_message=error_message,
        frames=frames,
        root_cause_frame=frames[-1] if frames else None
    )


def parse_cargo_traceback(output: str) -> Optional[ParsedTraceback]:
    """Parse cargo test traceback output."""
    frames = []
    pattern = re.compile(r'--->\s+([^:]+):(\d+):(\d+)\n\s+\|\n\s+(\d+)\s+\|\s+(.+)')
    for match in pattern.finditer(output):
        file_path, line_str, col_str, line_num_str, code = match.groups()
        frames.append(TracebackFrame(
            file=file_path,
            line=int(line_str),
            function=f"line_{line_num_str}",
            code_context=code.strip()
        ))
    
    panic_match = re.search(r'panicked at\s+(.+)', output)
    error_message = panic_match.group(1) if panic_match else "Panic"
    error_type = "PanicError"
    
    if not frames:
        return None
    
    for frame in frames:
        frame.snippet = extract_code_snippet(Path(frame.file), frame.line)
    
    return ParsedTraceback(
        test_command="cargo test",
        error_type=error_type,
        error_message=error_message,
        frames=frames,
        root_cause_frame=frames[-1] if frames else None
    )


def parse_traceback(output: str, test_command: str = "auto") -> Optional[ParsedTraceback]:
    """Auto-detect test runner and parse traceback."""
    if test_command == "auto":
        if "pytest" in output.lower() or "assertionerror" in output.lower() or "FAILURES" in output:
            test_command = "pytest"
        elif "npm test" in output.lower() or ("at " in output and ".js" in output):
            test_command = "npm"
        elif "cargo test" in output.lower() or "--->" in output:
            test_command = "cargo"
    
    if test_command == "pytest":
        return parse_pytest_traceback(output)
    elif test_command == "npm":
        return parse_npm_traceback(output)
    elif test_command == "cargo":
        return parse_cargo_traceback(output)
    
    for parser in [parse_pytest_traceback, parse_npm_traceback, parse_cargo_traceback]:
        result = parser(output)
        if result:
            return result
    return None


def main():
    if len(sys.argv) < 2:
        print("Usage: traceback_parser.py <test_output_file> [--command pytest|npm|cargo]")
        print("       traceback_parser.py --stdin [--command pytest|npm|cargo]")
        sys.exit(1)
    
    test_command = "auto"
    if "--command" in sys.argv:
        idx = sys.argv.index("--command")
        if idx + 1 < len(sys.argv):
            test_command = sys.argv[idx + 1]
    
    if sys.argv[1] == "--stdin":
        output = sys.stdin.read()
    else:
        output_path = Path(sys.argv[1])
        output = output_path.read_text()
    
    result = parse_traceback(output, test_command)
    
    if result:
        print(json.dumps({
            "test_command": result.test_command,
            "error_type": result.error_type,
            "error_message": result.error_message,
            "frames": [
                {
                    "file": f.file,
                    "line": f.line,
                    "function": f.function,
                    "code_context": f.code_context,
                    "snippet": f.snippet
                }
                for f in result.frames
            ],
            "root_cause": {
                "file": result.root_cause_frame.file,
                "line": result.root_cause_frame.line,
                "function": result.root_cause_frame.function,
                "code_context": result.root_cause_frame.code_context,
                "snippet": result.root_cause_frame.snippet
            } if result.root_cause_frame else None
        }, indent=2))
    else:
        print("No traceback parsed")
        sys.exit(1)


if __name__ == "__main__":
    main()
