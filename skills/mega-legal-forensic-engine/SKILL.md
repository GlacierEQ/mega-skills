---
name: mega-legal-forensic-engine
description: Consolidated mega skill encompassing 5 sub-skills.
---

# MEGA-LEGAL-FORENSIC-ENGINE

> [!WARNING]
> **APEX COGNITIVE FIREWALL (INTERCEPTOR GATE)**
> This file contains dense legal warfare, forensic evidence ingestion, and court pleading compilation directives.
DO NOT READ FURTHER unless the current user mandate explicitly requires:
- Court pleadings, motions, docket timelines, evidence verification, or device forensics.
> If the current task does not specifically target this domain, **STOP READING HERE** to preserve token context.


## Sub-Skill: deep-soul-litigation-engine
# Deep Soul Litigation Engine

## Overview
This skill implements the **Deep Soul Protocol & AION-777** framework. It acts as an autonomous legal intelligence engine that processes local docket updates, runs WhisperX transcriptions, organizes semantic facts into Mem0/SuperMemory, and drafts/compiles high-form court pleadings (LaTeX) for state and federal courts.

## Dependencies
- `token-saver` (to manage large token dockets)
- `building-data-apps` (to visualize timelines and bias graphs)

## Quick Start
Run the in-repo dispatcher from the repository root:
```bash
python3 skills/mega-legal-forensic-engine/skill.py
```

## Utility Scripts
Deep Soul litigation workflows are operator procedures. WhisperX, docket PDF parsing, and LaTeX compilation require their local toolchains. The packaged dispatcher currently exposes `dependencies`, `quick_start`, and `sub-skill_deep-soul-litigation-engine`.

1. **Media Transcription (WhisperX)**: ingest `court_hearing.mp3` → `transcripts/court_hearing.json`
2. **Docket Parsing**: ingest `docket_export.pdf` → `docket_timeline.json`
3. **Bias & Temporal Anomaly Analysis**: ingest `docket_timeline.json` → `bias_report.json`
4. **Pleading Compilation (LaTeX)**: ingest `case_info.json` with the Hawaii template → `Motion_001_Stay.pdf`

## Common Mistakes
- **LaTeX Compilation Errors**: Make sure MacTeX/TeX Live is installed (`pdflatex` must be in the PATH).
- **Resource Exhaustion**: Large audio files should be split or handled via model lazy loading.

---

## Sub-Skill: forensic-legal-pipeline
# Forensic Legal Pipeline

Orchestrates the ingestion, transcription, semantic analysis, and litigation compiler flows.

## 1. Intake & Transcription
- Transcribe audio notes (Apple Voice Memos, court hearings) using WhisperX.
- Deduplicate and normalize timestamps to HST + UTC.

## 2. Pleading Compiler (LaTeX)
- Parse docket PDFs to build chronological case timelines.
- Compile compliance-checked pleadings (LaTeX) for state and federal courts.

## 3. Vector Storage & Search
- Store and retrieve evidence vectors using PGVector configurations.
- Verify index dimensions, recall matrices, and similarity distances.

---

## Sub-Skill: legal-automation-suite
# Legal Automation Suite (Complete Legal & Evidence Platform)

Single skill covering: motion generation, RICO analysis, FRCP compliance, evidence lifecycle, chain of custody, patent disclosure, citation verification, and court-safe tone.

---

## Architecture

```
LEGAL AUTOMATION SUITE
├── Motion Generator — FRCP-compliant motion templates
├── RICO Pattern Analyzer — Racketeering detection
├── Compliance Engine — FRCP rule checking
├── Forensic Evidence Engine — Ingestion, SHA-256, audit trails
├── Chain of Custody — Custody transfer tracking
├── Patent Disclosure Engine — Patent-ready drafts
├── Citation Gate — Legal citation verification
├── Court-Safe Tone — Clinical litigation phrasing
└── Drift Guard — Software decay prevention
```

---

## 1. Motion Generation

```python
from legal_automation_engine import LegalAutomationEngine
engine = LegalAutomationEngine()

# Motion to Compel (FRCP Rule 37)
motion = engine.generate_motion(
    type="motion_to_compel",
    case_id="1FDV-23-0001009",
    opposing_party="Defendant",
    discovery_requested="Financial records",
    basis="FRCP Rule 37"
)

# Motion to Dismiss
motion = engine.generate_motion(
    type="motion_to_dismiss",
    case_id="1FDV-23-0001009",
    ground="Lack of jurisdiction"
)
```

### Templates Available
| Template | Rule | Use Case |
|----------|------|----------|
| `motion_to_compel` | FRCP Rule 37 | Discovery enforcement |
| `motion_to_dismiss` | FRCP Rule 12 | Jurisdictional challenges |
| `section_1983_complaint` | 42 USC 1983 | Civil rights violations |
| `rico_complaint` | 18 USC 1962 | Racketeering claims |
| `injunction_motion` | FRCP Rule 65 | Emergency relief |

---

## 2. RICO Pattern Analysis

```python
from pattern_analysis_engine import PatternAnalysisEngine
analyzer = PatternAnalysisEngine()

results = analyzer.detect_rico([
    {"actor": "Officer A", "action": "extortion"},
    {"actor": "Sergeant B", "action": "coercion"},
    {"actor": "Lieutenant C", "action": "cover_up"}
])
# Returns: RICOMatch { predicate, actors, confidence, legalBasis }
```

---

## 3. FRCP Compliance Check

```python
from compliance_engine import ComplianceEngine
checker = ComplianceEngine()

status = checker.check_compliance(
    claim="Section 1983 violation",
    statute="42 USC 1983"
)
# Returns: ComplianceCheck { status, missingElements, recommendations }
```

### FRCP Rules Covered
- Rule 11: Signing and Representations
- Rule 26: Disclosure and Discovery
- Rule 37: Failure to Make Disclosures
- Rule 56: Summary Judgment
- Rule 65: Injunctions

---

## 4. Forensic Evidence Management

```python
from forensic_evidence_engine import ForensicEvidenceEngine
engine = ForensicEvidenceEngine()

# Ingest with automatic hashing
evidence = engine.ingest_evidence(
    file_path="/path/to/evidence.pdf",
    case_id="1FDV-23-0001009",
    source="digital_forensics",
    description="Police report"
)
# Returns: Exhibit { hash, certified, daubertCompliant }

# Validate integrity
is_valid = engine.validate_integrity(evidence_id="EX-001", expected_hash="sha256:abc123...")

# Detect tampering
tamper_report = engine.check_tampering(evidence_id="EX-001")
```

### Evidence Types Supported
- Documents (PDF, Word, images)
- Audio recordings
- Video footage
- Digital communications
- Financial records
- Phone records

### Integrity Features
- SHA-256 hashing at ingestion
- Tamper detection
- Daubert compliance checking
- Certification tracking
- Blockchain-ready hashes

---

## 5. Chain of Custody

```python
from chain_of_custody_engine import ChainOfCustodyEngine
coc = ChainOfCustodyEngine()

# Record transfer
coc.record_transfer(
    evidence_id="EX-001",
    from_custodian="Forensic Lab",
    to_custodian="Attorney",
    timestamp="2026-06-27T10:00:00Z",
    purpose="Legal review"
)

# Get full chain
chain = coc.get_chain(evidence_id="EX-001")
```

---

## 6. Audit Trail Generation

```python
# Generate complete audit trail
audit = engine.generate_audit_trail(
    case_id="1FDV-23-0001009",
    start_date="2026-01-01",
    end_date="2026-06-27"
)
audit.export_pdf("audit_trail.pdf")
```

---

## 7. Digital Law Library Modules

| Module | Purpose |
|--------|---------|
| **LL:PATENT_DISCLOSURE_ENGINE** | Invention concepts → patent-ready drafts |
| **LL:COMMERCIALIZATION_FORGE** | Invention language → licensing/product strategies |
| **LL:EVIDENCE_MATRIX** | Digital records, timestamps, hashes → structured evidence |
| **LL:CITATION_GATE** | Verify every statute, rule, case citation |
| **LL:COURT_SAFE_TONE** | Emotional language → clinical litigation phrasing |
| **LL:DRIFT_GUARD** | Linter, unit-test, rollback gates against decay |
| **LL:CONTROL_PLANE_HARDENING** | Phased rollouts, security boundaries, approval gateways |

---

## Integration Points

| Component | Endpoint |
|-----------|----------|
| Mastermind API | `POST /api/engine/legal-automation/generateMotion` |
| Nexus-API | `POST /api/v1/trigger/legal` |
| Alpha Strand | Legal analysis workflows |
| Omega Strand | Document generation workers |
| Evidence Vault | `/MISSIONS/THE_CATACLYSM/FORENSIC_EVIDENCE/` |

---

## Usage Triggers
- "Generate motion", "FRCP compliance", "RICO patterns"
- "Process evidence", "SHA-256 hash", "chain of custody"
- "Audit trail", "forensic report"
- "Patent disclosure", "citation verification"
- "Court-safe tone", "legal document"
- "Litigation automation", "Section 1983"

---

## Sub-Skill: ios-mac-device-forensics-and-recovery
# iOS/iPadOS/macOS Device Forensics & Recovery Suite

A specialized operational framework for low-level USB hardware detection, iOS/iPadOS recovery state analysis, Activation Lock resolution, and mobile device protocol management.

---

## 1. Low-Level USB Hardware Diagnostics

### Command Suite
```bash
# 1. Full USB Bus Inspection
system_profiler SPUSBDataType

# 2. Real-time IOUSB Hardware Tree
ioreg -p IOUSB -w0

# 3. Direct Filter for Apple Mobile Devices
ioreg -p IOUSB -l | grep -A 25 -i "iPhone\|iPad\|iPod\|Apple Mobile Device"
```

### USB Product ID (PID) State Matrix

| Product ID (Hex) | Product ID (Dec) | Device State | Description |
|---|---|---|---|
| `0x12a8` | 4776 | **Normal Booted** | Device is powered on, booted to iOS/iPadOS lock/setup screen. |
| `0x1281` | 4737 | **Recovery Mode** | Screen shows Computer + Cable logo. Ready for iTunes/Finder restore. |
| `0x1227` | 4647 | **DFU Mode** | Screen is completely black, low-level bootrom interface active. |
| `0x12a0` / `0x12a2` | 4768 / 4770 | **Restore / Diagnostic** | Device in diagnostic mode or early restore phase. |

---

## 2. Hardware Chip Architecture & Exploit Mapping (Checkm8 Eligibility)

If Activation Lock cannot be cleared via credentials, hardware exploit capability depends strictly on SoC generation:

| SoC Chip | Device Models | Checkm8 Compatible? | Notes |
|---|---|---|---|
| **A7 / A8 / A8X** | iPad Air 1, iPad mini 2/3/4 | **YES** | Full bootrom exploit supported |
| **A9 / A9X** | iPad 5th gen, iPad Pro 9.7/12.9 (1st gen) | **YES** | Full bootrom exploit supported |
| **A10 / A10X** | iPad 6th/7th gen, iPad Pro 10.5/12.9 (2nd gen) | **YES** | Full bootrom exploit supported |
| **A12+ / M1+** | iPad 8th+ gen, iPad Air 3rd+ gen, iPad Pro 3rd+ gen | **NO** | No hardware bootrom exploit; must use official unlock |

---

## 3. iCloud Activation Lock Resolution Pathways

### Pathway 1: Account Recovery (Lost 2FA / Old Phone)
1. Navigate to [iforgot.apple.com](https://iforgot.apple.com).
2. Enter target Apple ID.
3. When prompted for old trusted phone number, **type the old phone number** to verify identity.
4. On SMS prompt, select **"Don't have access to this number?"** $\rightarrow$ **"Continue anyway"**.
5. Wait for Apple's 24h–72h automated Account Recovery evaluation.

### Pathway 2: Remote iCloud Device Removal (Fastest)
If the owner has *any* active Apple device (iPhone/Mac) or can sign into [icloud.com/find](https://www.icloud.com/find):
* **On iPhone/Mac:** Settings $\rightarrow$ [Account Name] $\rightarrow$ Select old iPad $\rightarrow$ **Remove from Account**.
* **On Web:** Sign into iCloud.com $\rightarrow$ Find My $\rightarrow$ All Devices $\rightarrow$ Select iPad $\rightarrow$ **Erase** $\rightarrow$ **Remove from Account**.
* **Result:** Reboot old iPad and connect to Wi-Fi; Activation Lock clears instantly.

### Pathway 3: Official Apple Support Unlock Request
Submit serial number + original proof of purchase (receipt) to [al-support.apple.com](https://al-support.apple.com). Apple handles unlock server-side.

---

## 4. macOS Local Intelligence & Tool Integration

Local assets available in vault:
* `/Volumes/ANTIGRAVITY_MEMORY_01/APEX_PROJECTS_VAULT/apple-mcp` — Apple Multi-Agent Device Control System.
* `/Volumes/ANTIGRAVITY_MEMORY_01/APEX_PROJECTS_VAULT/apex-ish-mobile-nexus` — iOS/iPadOS Terminal & Device Nexus.

---

## Sub-Skill: voice-memo-processor
# Voice Memo Processing Engine

Automates structural analysis, diarization, and semantic extraction for audio memos.

## 🛠️ Execution Pipeline

1. **Intake & Hashing**:
   - Compute standard SHA-256 hash of raw file before editing.
   - Run `ffmpeg -i <file>` to extract duration, bitrate, and capture date.
2. **Transcription & Diarization**:
   - Transcribe with raw confidence metrics (0.0 - 1.0).
   - Use speaker identifiers (`SPEAKER_00`, `SPEAKER_01`, etc.) linked to contextual evidence before assigning actual names.
3. **Structured Context Mapping**:
   - Normalization layout (sections 1-17): Topic, Duration, Location Inference, Entities, Action Items, Legal Warnings.
   - Output structured JSON and appends a summary row to local indexing CSVs.

---
