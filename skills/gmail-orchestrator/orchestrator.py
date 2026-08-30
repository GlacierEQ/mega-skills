"""
Gmail Orchestrator
GlacierEQ APEX | computer-user skill

Headless browser-based Gmail orchestration:
  - Inbox triage (label, archive, flag, prioritize)
  - Draft generation (LLM-written, tone-matched)
  - Scheduled sends
  - FORENSIC MODE: targeted extraction of surveillance-period emails
    Default forensic window: Apr 15–18, 2025  (casey.barton92@gmail.com)
    Case ref: 1FDV-23-0001009 / THE_CATACLYSM

Platform-agnostic: runs on Tasklet, Puppeteer, or any browser backend.
Credentials in ~/.apex/connections.json or env vars. No security theater.
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

# ── Universal imports ────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from browser_adapter import get_backend, BrowserBackend
from paths import GMAIL_FORENSIC_DIR, GMAIL_DRAFTS_DIR, load_credentials

# ── URLs ──────────────────────────────────────────────────────────────────────
GMAIL_URL = "https://mail.google.com"
GMAIL_SEARCH = "https://mail.google.com/mail/u/0/#search/{query}"

# ── Forensic config ───────────────────────────────────────────────────────────
FORENSIC_ACCOUNTS = ["casey.barton92@gmail.com"]
FORENSIC_DATE_START = "2025/04/15"
FORENSIC_DATE_END = "2025/04/18"
CASE_REF = "1FDV-23-0001009"


# ─────────────────────────────────────────────────────────────────────────────
# Gmail Orchestrator class
# ─────────────────────────────────────────────────────────────────────────────

class GmailOrchestrator:
    """Browser-based Gmail automation with platform-agnostic backend."""

    def __init__(self, backend: Optional[BrowserBackend] = None):
        self.b = backend or get_backend()

    def login(self, email: str, password: str) -> bool:
        """Login to Gmail via Google sign-in flow."""
        self.b.navigate(GMAIL_URL)
        self.b.wait(3000)

        page = self.b.get_text().lower()
        if "inbox" in page:
            print(f"[gmail] Already logged in as {email}")
            return True

        # Google sign-in flow — fill by visible label
        self.b.fill("Email or phone", email)
        self.b.wait(800)
        self.b.click("text=Next")
        self.b.wait(2000)
        self.b.fill("Enter your password", password)
        self.b.wait(800)
        self.b.click("text=Next")
        self.b.wait(5000)

        page = self.b.get_text().lower()
        if "inbox" in page or "compose" in page:
            print(f"[gmail] ✅  Logged in as {email}")
            return True

        if "verify" in page or "2-step" in page or "phone" in page:
            print("[gmail] ⏳  2FA required — waiting 60s for manual input...")
            time.sleep(60)

        return True

    def triage_inbox(self, rules: Optional[list] = None) -> dict:
        """
        Auto-triage inbox.
        rules: list of dicts with keys: query, action (label/archive/star/trash), label_name
        """
        default_rules = [
            {"query": "is:unread older_than:7d", "action": "archive"},
            {"query": 'subject:"court" OR subject:"case"', "action": "label", "label_name": "LEGAL"},
            {"query": 'subject:"security alert"', "action": "label", "label_name": "SECURITY_ALERTS"},
            {"query": 'from:noreply OR from:no-reply', "action": "label", "label_name": "AUTOMATED"},
        ]
        rules = rules or default_rules
        results = []

        for rule in rules:
            q = rule["query"]
            action = rule["action"]
            url = GMAIL_SEARCH.format(query=q.replace(" ", "+"))
            self.b.navigate(url)
            self.b.wait(2000)

            self.b.click("text=Select all")
            self.b.wait(500)

            if action == "archive":
                self.b.click("text=Archive")
            elif action == "label" and rule.get("label_name"):
                self.b.click("text=Label")
                self.b.wait(500)
                self.b.fill("Search labels", rule["label_name"])
                self.b.wait(500)
                self.b.click(f"text={rule['label_name']}")
            elif action == "star":
                self.b.click("text=Star")
            elif action == "trash":
                self.b.click("text=Delete")

            self.b.wait(1000)
            results.append({"rule": rule, "status": "applied"})
            print(f"[gmail] triage → {action} on '{q}'")

        return {"triage_rules_applied": len(results), "details": results}

    def create_draft(
        self, to: str, subject: str, body: str,
        cc: str = "", send_now: bool = False
    ) -> dict:
        """Compose and optionally send an email via browser."""
        self.b.navigate(GMAIL_URL)
        self.b.wait(2000)
        self.b.click("text=Compose")
        self.b.wait(1500)

        self.b.fill("To", to)
        self.b.wait(400)
        if cc:
            self.b.click("text=Cc")
            self.b.fill("Cc", cc)
            self.b.wait(400)
        self.b.fill("Subject", subject)
        self.b.wait(400)
        self.b.click("Message Body")
        self.b.fill("Message Body", body)
        self.b.wait(400)

        status = "draft_saved"
        if send_now:
            self.b.click("text=Send")
            self.b.wait(2000)
            status = "sent"
        else:
            self.b.wait(1500)

        print(f"[gmail] ✅  Email {status} → {to}")
        ts = datetime.utcnow().isoformat() + "Z"
        out = {"to": to, "subject": subject, "status": status, "timestamp": ts}

        out_path = GMAIL_DRAFTS_DIR / f"draft_{ts.replace(':', '-')}.json"
        out_path.write_text(json.dumps(out, indent=2))

        return out

    def forensic_extraction(
        self, account: str = "casey.barton92@gmail.com",
        date_start: str = FORENSIC_DATE_START,
        date_end: str = FORENSIC_DATE_END,
        query_extra: str = ""
    ) -> dict:
        """
        Surgical forensic extraction of emails from surveillance window.
        Captures: sender, recipient, subject, timestamp, snippet, message_id.
        """
        query = f"after:{date_start} before:{date_end} {query_extra}".strip()
        url = GMAIL_SEARCH.format(query=query.replace(" ", "+"))

        self.b.navigate(url)
        self.b.wait(3000)

        js_extract = """
        (() => {
            const rows = document.querySelectorAll('tr.zA, div[role="row"]');
            const emails = [];
            rows.forEach(row => {
                const sender  = row.querySelector('.yP, [email], .zF')?.getAttribute('email')
                             || row.querySelector('.yP')?.innerText?.trim() || '';
                const subject = row.querySelector('.y6, [data-thread-id] span')?.innerText?.trim() || '';
                const snippet = row.querySelector('.y2')?.innerText?.trim() || '';
                const time_el = row.querySelector('.xW span, td.xW');
                const ts      = time_el?.getAttribute('title') || time_el?.innerText?.trim() || '';
                const msg_id  = row.getAttribute('data-legacy-message-id')
                             || row.getAttribute('data-thread-id') || '';
                if (sender || subject) {
                    emails.push({ sender, subject, snippet, timestamp: ts, message_id: msg_id });
                }
            });
            return JSON.stringify(emails);
        })()
        """

        raw = self.b.eval_js(js_extract)
        data = []
        try:
            data = json.loads(raw) if isinstance(raw, str) else raw
        except Exception:
            pass

        result = {
            "case_ref": CASE_REF,
            "account": account,
            "query": query,
            "date_start": date_start,
            "date_end": date_end,
            "extracted_at": datetime.utcnow().isoformat() + "Z",
            "email_count": len(data),
            "emails": data,
            "forensic_notes": (
                "Surveillance window: coordinated password change (bkitzcreig), "
                "Google Meet API key injection Apr 16 2025, "
                "glacier.equilibrium simultaneous access. "
                "Ref: THE_CATACLYSM / VOID AB INITIO motion."
            )
        }

        tag = f"{date_start.replace('/', '')}_{date_end.replace('/', '')}"
        out_path = GMAIL_FORENSIC_DIR / f"CASE_{tag}_{CASE_REF}.json"
        out_path.write_text(json.dumps(result, indent=2))

        print(f"[gmail] 🔍  Forensic extraction: {len(data)} emails → {out_path}")
        return result


# ─────────────────────────────────────────────────────────────────────────────
# Convenience functions (backward-compatible with old API)
# ─────────────────────────────────────────────────────────────────────────────

_ocr = None

def _get_ocr():
    global _ocr
    if _ocr is None:
        _ocr = GmailOrchestrator()
    return _ocr

def nav(url):        _get_ocr().b.navigate(url)
def click(q):        _get_ocr().b.click(q)
def fill(q, v):      _get_ocr().b.fill(q, v)
def wait(ms=2000):   _get_ocr().b.wait(ms)
def js(script):      return _get_ocr().b.eval_js(script)
def snap():          return _get_ocr().b.get_text()


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def run(
    account: str = "casey.barton92@gmail.com",
    mode: str = "triage",
    draft_to: str = "",
    draft_subject: str = "",
    draft_body: str = "",
    send_now: bool = False,
    forensic_start: str = FORENSIC_DATE_START,
    forensic_end: str = FORENSIC_DATE_END,
) -> dict:
    creds = load_credentials("gmail", account)
    email = creds.get("email", account)
    password = creds.get("password", "")

    ocr = GmailOrchestrator()
    ocr.login(email, password)

    results = {}
    if mode in ("triage", "full"):
        results["triage"] = ocr.triage_inbox()
    if mode in ("forensic", "full"):
        results["forensic"] = ocr.forensic_extraction(
            account=account, date_start=forensic_start, date_end=forensic_end
        )
    if mode in ("draft", "full") and draft_to:
        results["draft"] = ocr.create_draft(
            to=draft_to, subject=draft_subject, body=draft_body, send_now=send_now
        )
    return results


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "forensic"
    print(json.dumps(run(mode=mode), indent=2))
