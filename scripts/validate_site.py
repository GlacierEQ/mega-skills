#!/usr/bin/env python3
"""Deterministic validation for the self-contained Mega-Skills architecture site."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site" / "index.html"

REQUIRED_IDS = {
    "top",
    "architecture",
    "snowball",
    "operating-model",
    "inspectability",
    "readiness",
    "missions",
    "provenance",
    "why",
}
REQUIRED_PHRASES = {
    "Capability that",
    "The capability hierarchy",
    "Nothing gets bigger merely by repeating instructions.",
    "Long-horizon work without context drift.",
    "Readiness before claims.",
    "Source meaning survives every layer.",
    "Build capability that survives the next turn.",
}
FORBIDDEN_PLACEHOLDERS = {
    "lorem ipsum",
    "template placeholder",
    "todo:",
    "fixme:",
}
FORBIDDEN_PRIVATE_REFERENCES = {
    "github.com/GlacierEQ/mega-skills",
    "api.github.com/repos/GlacierEQ/mega-skills",
}

class SiteParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.internal_hrefs: list[str] = []
        self.external_assets: list[str] = []
        self.title_depth = 0
        self.title_parts: list[str] = []
        self.description = ""

    def handle_starttag(self, tag: str, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        href = attrs.get("href")
        if tag == "a" and href and href.startswith("#"):
            self.internal_hrefs.append(href[1:])
        if tag == "script":
            src = attrs.get("src", "")
            if src.startswith(("http://", "https://", "//")):
                self.external_assets.append(src)
        if tag == "link":
            href = attrs.get("href", "")
            if href.startswith(("http://", "https://", "//")):
                self.external_assets.append(href)
        if tag in {"img", "source", "video", "audio"}:
            src = attrs.get("src", "")
            if src.startswith(("http://", "https://", "//")):
                self.external_assets.append(src)
        if tag == "meta" and attrs.get("name") == "description":
            self.description = attrs.get("content", "")
        if tag == "title":
            self.title_depth += 1

    def handle_endtag(self, tag: str):
        if tag == "title" and self.title_depth:
            self.title_depth -= 1

    def handle_data(self, data: str):
        if self.title_depth:
            self.title_parts.append(data)


def check(name: str, condition: bool, detail: str, results: list[dict]) -> None:
    results.append({"check": name, "ok": bool(condition), "detail": detail})


def main() -> int:
    if not SITE.exists():
        print(json.dumps({"ok": False, "error": f"missing {SITE}"}))
        return 2

    raw = SITE.read_bytes()
    text = raw.decode("utf-8")
    lower = text.lower()
    parser = SiteParser()
    parser.feed(text)

    results: list[dict] = []
    title = "".join(parser.title_parts).strip()
    missing_ids = sorted(REQUIRED_IDS - parser.ids)
    missing_anchors = sorted({a for a in parser.internal_hrefs if a and a not in parser.ids})
    missing_phrases = sorted(p for p in REQUIRED_PHRASES if p not in text)
    placeholders = sorted(p for p in FORBIDDEN_PLACEHOLDERS if p in lower)
    private_refs = sorted(p for p in FORBIDDEN_PRIVATE_REFERENCES if p.lower() in lower)

    check("doctype", text.lstrip().lower().startswith("<!doctype html>"), "HTML5 doctype", results)
    check("document_language", '<html lang="en">' in text, "lang=en", results)
    check("viewport", 'name="viewport"' in text, "responsive viewport metadata", results)
    check("seo_title", title == "Mega-Skills — Compounding AI Agent Capability Systems", title, results)
    check("seo_description", bool(parser.description.strip()), parser.description, results)
    check("required_sections", not missing_ids, f"missing={missing_ids}", results)
    check("internal_anchor_integrity", not missing_anchors, f"missing={missing_anchors}", results)
    check("required_content", not missing_phrases, f"missing={missing_phrases}", results)
    check("reduced_motion", "prefers-reduced-motion" in text, "reduced-motion CSS present", results)
    check("self_contained", not parser.external_assets, f"external_assets={parser.external_assets}", results)
    check("no_placeholders", not placeholders, f"found={placeholders}", results)
    check("no_private_repo_reference", not private_refs, f"found={private_refs}", results)

    digest = hashlib.sha256(raw).hexdigest()
    ok = all(r["ok"] for r in results)
    report = {
        "ok": ok,
        "site": str(SITE.relative_to(ROOT)),
        "bytes": len(raw),
        "sha256": digest,
        "checks": results,
    }
    print(json.dumps(report, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
