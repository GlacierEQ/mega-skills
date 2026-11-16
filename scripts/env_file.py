"""Parse and quote env assignments. Unquoted # starts a comment; quoted # does not."""

from __future__ import annotations

import re
from typing import Dict, List, Tuple

ASSIGNMENT = re.compile(
    r"""([A-Za-z_][A-Za-z0-9_]*)\s*=\s*("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|[^\s#]+)"""
)


def cut_unquoted_comment(line: str) -> str:
    quote = ""
    escaped = False
    for index, char in enumerate(line):
        if quote:
            if escaped:
                escaped = False
                continue
            if char == "\\" and quote == '"':
                escaped = True
                continue
            if char == quote:
                quote = ""
            continue
        if char in {'"', "'"}:
            quote = char
            continue
        if char == "#":
            return line[:index]
    return line


def unquote_env(raw: str) -> str:
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in {'"', "'"}:
        inner = raw[1:-1]
        if raw[0] == "'":
            return inner
        return _unescape_double(inner)
    return raw


def _unescape_double(value: str) -> str:
    output: List[str] = []
    escaped = False
    for char in value:
        if escaped:
            output.append({"n": "\n", "r": "\r", "t": "\t", '"': '"', "\\": "\\"}.get(char, char))
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        output.append(char)
    if escaped:
        output.append("\\")
    return "".join(output)


def quote_env(value: str) -> str:
    if value == "" or any(char.isspace() or char in '#"\'\\$' for char in value):
        escaped = (
            value.replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("\n", "\\n")
            .replace("\r", "\\r")
        )
        return f'"{escaped}"'
    return value


def parse_line(raw: str) -> List[Tuple[str, str]]:
    line = re.sub(r"^(export\s+|declare\s+-x\s+)", "", raw.strip())
    if not line or line.startswith("#"):
        return []
    found: List[Tuple[str, str]] = []
    for match in ASSIGNMENT.finditer(cut_unquoted_comment(line)):
        key = match.group(1)
        value = unquote_env(match.group(2)).strip()
        if key and value:
            found.append((key, value))
    return found


def parse_env_text(text: str) -> Dict[str, str]:
    env: Dict[str, str] = {}
    for raw in text.splitlines():
        for key, value in parse_line(raw):
            env[key] = value
    return env
