#!/usr/bin/env python3
"""
Trace validator message to named entry/field, common failure boundaries
Part of mega-skills-test-runner skill.
"""

import argparse
import json
import re
import sys
from pathlib import Path


def diagnose_failure(error_text: str) -> dict:
    """Trace validator message to named entry/field and common failure boundaries."""
    entry_match = re.search(r'(?:entry|skill|combo|mega|id|file):\s*([a-zA-Z0-9_\-/\.]+)', error_text, re.IGNORECASE)
    field_match = re.search(r'(?:field|property|key|attribute):\s*([a-zA-Z0-9_]+)', error_text, re.IGNORECASE)
    line_match = re.search(r'line\s+(\d+)', error_text, re.IGNORECASE)

    boundary = "unknown"
    if "syntax" in error_text.lower() or "indentation" in error_text.lower():
        boundary = "syntax_error"
    elif "schema" in error_text.lower() or "validation" in error_text.lower() or "registry" in error_text.lower():
        boundary = "schema_validation"
    elif "assertion" in error_text.lower() or "fail" in error_text.lower():
        boundary = "test_assertion"

    return {
        "boundary": boundary,
        "entry": entry_match.group(1) if entry_match else None,
        "field": field_match.group(1) if field_match else None,
        "line": int(line_match.group(1)) if line_match else None,
        "raw_message": error_text.strip().splitlines()[-1] if error_text.strip() else "",
    }


def main():
    parser = argparse.ArgumentParser(description="Diagnose validator or test failure message")
    parser.add_argument("--message", help="Error message string to diagnose")
    parser.add_argument("--file", type=Path, help="File containing failure output")
    args = parser.parse_args()

    text = ""
    if args.file and args.file.is_file():
        text = args.file.read_text(encoding="utf-8")
    elif args.message:
        text = args.message
    else:
        text = sys.stdin.read()

    diagnostic = diagnose_failure(text)
    print(json.dumps(diagnostic, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

