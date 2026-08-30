"""
iCloud Voice Memos Harvester
GlacierEQ APEX | computer-user skill

Browser-based harvester: logs into iCloud.com via Chromium,
extracts Voice Memos with full metadata (transcript, GPS, duration,
timestamp, title) and deposits structured JSON.

Platform-agnostic: runs on Tasklet, Puppeteer, or any browser backend.
No app breach. No jailbreak. Pure browser automation.
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
from paths import VOICE_MEMOS_DIR, load_credentials

SESSION_FILE = VOICE_MEMOS_DIR / "session.json"
INDEX_FILE = VOICE_MEMOS_DIR / "INDEX.json"

ICLOUD_URL = "https://www.icloud.com"
VOICE_MEMOS_URL = "https://www.icloud.com/voicememos/"


class VoiceMemosHarvester:
    """Browser-based iCloud Voice Memos extraction."""

    def __init__(self, backend: Optional[BrowserBackend] = None):
        self.b = backend or get_backend()

    def login(self, apple_id: str, password: str) -> bool:
        """Login to iCloud.com — handles 2FA pause."""
        self.b.navigate(ICLOUD_URL)
        self.b.wait(3000)

        self.b.fill("Apple ID", apple_id)
        self.b.wait(800)
        self.b.click("text=Continue")
        self.b.wait(2000)

        self.b.fill("Password", password)
        self.b.wait(800)
        self.b.click("text=Sign In")
        self.b.wait(5000)

        page = self.b.get_text().lower()
        if "verification code" in page or "two-factor" in page:
            print("[harvester] ⏳  2FA required — waiting 60s for manual input...")
            time.sleep(60)

        self.b.navigate(VOICE_MEMOS_URL)
        self.b.wait(4000)
        return True

    def extract_memos(self) -> list:
        """Scrape Voice Memos page via JS injection."""
        js_extractor = """
        (() => {
            const memoEls = document.querySelectorAll('[class*="memo"], [class*="recording"], li[data-memo-id]');
            const results = [];
            memoEls.forEach(el => {
                const title     = el.querySelector('[class*="title"], [class*="name"]')?.innerText?.trim() || 'Untitled';
                const duration  = el.querySelector('[class*="duration"], [class*="time"]')?.innerText?.trim() || '';
                const timestamp = el.querySelector('[class*="date"], [class*="created"], time')?.innerText?.trim()
                               || el.querySelector('time')?.getAttribute('datetime') || '';
                const transcript= el.querySelector('[class*="transcript"], [class*="text"]')?.innerText?.trim() || '';
                const memoId    = el.getAttribute('data-memo-id') || el.id || '';
                const gpsRaw    = el.getAttribute('data-location') || el.getAttribute('aria-label') || '';
                results.push({ title, duration, timestamp, transcript, memo_id: memoId, gps_raw: gpsRaw });
            });
            return JSON.stringify(results);
        })()
        """

        raw = self.b.eval_js(js_extractor)
        try:
            memos = json.loads(raw) if isinstance(raw, str) else raw
        except (json.JSONDecodeError, TypeError):
            memos = []

        for m in memos:
            m["harvested_at"] = datetime.utcnow().isoformat() + "Z"
            m["source"] = "icloud.com"

        return memos

    def save(self, memos: list) -> Path:
        """Persist memos to disk with rolling index."""
        run_id = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        out_path = VOICE_MEMOS_DIR / f"voice_memos_{run_id}.json"
        out_path.write_text(json.dumps({"run_id": run_id, "count": len(memos), "memos": memos}, indent=2))

        index = []
        if INDEX_FILE.exists():
            try:
                index = json.loads(INDEX_FILE.read_text())
            except Exception:
                pass
        index.append({"run_id": run_id, "file": str(out_path), "count": len(memos)})
        INDEX_FILE.write_text(json.dumps(index, indent=2))

        print(f"[harvester] ✅  {len(memos)} memos saved → {out_path}")
        return out_path


def run(apple_id: Optional[str] = None, password: Optional[str] = None) -> dict:
    if not apple_id:
        creds = load_credentials("apple")
        apple_id = creds.get("email", creds.get("apple_id", ""))
        password = creds.get("password", "")

    if not apple_id:
        raise EnvironmentError(
            "Apple ID not found. Set APEX_APPLE_EMAIL + APEX_APPLE_PASSWORD "
            "or add 'apple' block to ~/.apex/connections.json"
        )

    print(f"[harvester] 🍎  Logging into iCloud as {apple_id}...")
    h = VoiceMemosHarvester()
    h.login(apple_id, password)

    print("[harvester] 🎙️  Extracting Voice Memos...")
    memos = h.extract_memos()

    if not memos:
        print("[harvester] ⚠️  No memos found — page structure may have changed.")
        return {"status": "empty", "count": 0}

    out_path = h.save(memos)
    return {"status": "ok", "count": len(memos), "output": str(out_path)}


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2))
