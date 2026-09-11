"""
Cross-App Pipeline
GlacierEQ APEX | computer-user skill

Master orchestrator wiring:
  Voice Memos (iCloud) → WhisperX → classification → routing:
    LEGAL     → /automation/tasklet/cataclysm/evidence/
    PERSONAL  → Notion page
    EMAIL     → Gmail draft
    GENERAL   → /automation/tasklet/voice-memos/processed/

Platform-agnostic: runs on Tasklet, Puppeteer, or any browser backend.
Case ref: 1FDV-23-0001009
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# ── Universal imports ────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
try:
    from paths import (
        CATACLYSM_DIR,
        NOTION_QUEUE_DIR, GMAIL_DRAFTS_DIR, PIPELINE_REPORTS_DIR,
    )
except ImportError:
    BASE_DIR = Path.home() / ".apex"
    CATACLYSM_DIR = BASE_DIR / "cataclysm"
    NOTION_QUEUE_DIR = BASE_DIR / "notion_queue"
    GMAIL_DRAFTS_DIR = BASE_DIR / "gmail_drafts"
    PIPELINE_REPORTS_DIR = BASE_DIR / "pipeline_reports"

# ── Sibling skill imports ────────────────────────────────────────────────────
try:
    from icloud_voice_memos.harvester import run as harvest_voice_memos
except ImportError:
    harvest_voice_memos = None
try:
    from gmail_orchestrator.orchestrator import GmailOrchestrator
except ImportError:
    GmailOrchestrator = None


# ── Whisper model ────────────────────────────────────────────────────────────
WHISPER_MODEL = __import__("os").environ.get("WHISPER_MODEL", "medium")

# ── Classification keywords ──────────────────────────────────────────────────
LEGAL_KEYWORDS = [
    "court", "case", "judge", "motion", "filing", "hearing", "attorney",
    "hpd", "police", "barton", "kekoa", "1009", "515", "1fdv",
    "cataclysm", "evidence", "void", "ab initio", "rico", "warrant",
    "restraining", "order", "custody", "surveillance", "hack", "spoliation",
    "april 17", "april 16", "2025", "password change", "glacier",
]

EMAIL_KEYWORDS = [
    "send email", "email", "draft", "reply", "write to", "message to",
    "respond", "follow up", "let them know",
]


def classify_transcript(text: str) -> str:
    lower = text.lower()
    if any(kw in lower for kw in LEGAL_KEYWORDS):
        return "LEGAL"
    if any(kw in lower for kw in EMAIL_KEYWORDS):
        return "EMAIL"
    return "PERSONAL"


def transcribe_audio(audio_path: Path) -> dict:
    try:
        from whisperx_audio_processing.transcriber import transcribe
        return transcribe(str(audio_path), model=WHISPER_MODEL)
    except ImportError:
        pass
    cmd = ["whisper", str(audio_path), "--model", WHISPER_MODEL, "--output_format", "json"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    out_json = audio_path.with_suffix(".json")
    if out_json.exists():
        return json.loads(out_json.read_text())
    return {"text": result.stdout.strip(), "segments": []}


def route_memo(memo: dict, transcript: str) -> dict:
    category = classify_transcript(transcript)
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    title = memo.get("title", "Untitled").replace(" ", "_")[:40]

    out = {
        "memo": memo, "transcript": transcript,
        "category": category, "routed_at": ts,
        "case_ref": "1FDV-23-0001009" if category == "LEGAL" else None,
    }

    if category == "LEGAL":
        dest = CATACLYSM_DIR / f"VM_{ts}_{title}.json"
    elif category == "EMAIL":
        dest = GMAIL_DRAFTS_DIR / f"draft_{ts}.json"
        out = {"source": "voice_memo", "transcript": transcript,
               "title": memo.get("title", ""), "timestamp": ts, "status": "pending_send"}
    else:
        dest = NOTION_QUEUE_DIR / f"note_{ts}_{title}.json"

    dest.write_text(json.dumps(out, indent=2))
    print(f"[pipeline] {'⚖️' if category=='LEGAL' else '📧' if category=='EMAIL' else '📓'}  {category} → {dest}")
    return {"category": category, "destination": str(dest)}


def run_full_pipeline(
    apple_id: Optional[str] = None,
    apple_pw: Optional[str] = None,
    gmail_acct: str = "casey.barton92@gmail.com",
    run_forensic: bool = True,
    run_voice: bool = True,
    run_triage: bool = True,
) -> dict:
    report = {"started_at": datetime.utcnow().isoformat() + "Z", "stages": {}}

    if run_voice:
        print("[pipeline] 🎙️  Stage 1: Harvesting Voice Memos...")
        vm_result = harvest_voice_memos(apple_id=apple_id, password=apple_pw)
        memos = []
        if vm_result.get("output"):
            data = json.loads(Path(vm_result["output"]).read_text())
            memos = data.get("memos", [])

        routes = []
        for memo in memos:
            transcript = memo.get("transcript", "")
            if not transcript:
                audio_src = memo.get("audio_path", "")
                if audio_src and Path(audio_src).exists():
                    wx = transcribe_audio(Path(audio_src))
                    transcript = wx.get("text", "")
            if transcript:
                routes.append(route_memo(memo, transcript))

        report["stages"]["voice_memos"] = {
            "memos_harvested": len(memos), "memos_routed": len(routes), "routes": routes
        }
        print(f"[pipeline] ✅  {len(routes)}/{len(memos)} memos processed & routed")

    if run_forensic:
        print("[pipeline] 🔍  Stage 2: Forensic Gmail extraction...")
        ocr = GmailOrchestrator()
        creds = __import__("paths", fromlist=["load_credentials"]).load_credentials("gmail", gmail_acct)
        ocr.login(creds.get("email", gmail_acct), creds.get("password", ""))
        f_result = ocr.forensic_extraction(account=gmail_acct)
        report["stages"]["forensic_gmail"] = f_result
        print("[pipeline] ✅  Forensic extraction complete")

    if run_triage:
        print("[pipeline] 📬  Stage 3: Gmail inbox triage...")
        ocr = GmailOrchestrator()
        creds = __import__("paths", fromlist=["load_credentials"]).load_credentials("gmail", gmail_acct)
        ocr.login(creds.get("email", gmail_acct), creds.get("password", ""))
        t_result = ocr.triage_inbox()
        report["stages"]["gmail_triage"] = t_result
        print("[pipeline] ✅  Inbox triage complete")

    report["completed_at"] = datetime.utcnow().isoformat() + "Z"
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    rpt_path = PIPELINE_REPORTS_DIR / f"pipeline_report_{ts}.json"
    rpt_path.write_text(json.dumps(report, indent=2))
    print(f"[pipeline] 📋  Pipeline report → {rpt_path}")
    return report


if __name__ == "__main__":
    import sys as _sys
    run_voice = "--no-voice" not in _sys.argv
    run_forensic = "--no-forensic" not in _sys.argv
    run_triage = "--no-triage" not in _sys.argv
    result = run_full_pipeline(run_voice=run_voice, run_forensic=run_forensic, run_triage=run_triage)
    print(json.dumps(result, indent=2))
