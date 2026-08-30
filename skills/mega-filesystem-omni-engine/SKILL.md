---
name: mega-filesystem-omni-engine
description: Consolidated mega skill for filesystem perception, document parsing (PDF, Doc, LaTeX, Pandoc), tabular data & spreadsheets, cloud storage orchestration (Rclone, Google Suite, Dropbox, S3), atomic file operations, visual infographics/slides, and audio/podcast processing.
---

# MEGA-FILESYSTEM-OMNI-ENGINE

> **Role:** Universal File System Perception, Document Engineering, Cloud Storage Synchronization, and Media/Publishing Pipeline.

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    MEGA-FILESYSTEM-OMNI-ENGINE                           │
│                                                                          │
│  [Perception & Hashing]  ──▶  [Documents: PDF/DOCX/LaTeX/Typst/Pandoc]   │
│  [Tabular: Excel/Sheets] ──▶  [Cloud Storage: Rclone/GDrive/S3/Dropbox]  │
│  [Atomic File Ops]       ──▶  [Visuals: Charts/Infographics/Slides]     │
│  [Media & Podcasts]      ──▶  [Legal Bates Stamping & Provenance]        │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Sub-Skill: filesystem-view-and-recognition
# Filesystem Perception, Structural Auditing & Fingerprinting

Advanced directory traversal, MIME-type recognition, and cryptographic integrity fingerprinting.

### 1. High-Performance Recursive Tree & Metadata Scanner
```python
import os
import hashlib
import mimetypes
from pathlib import Path

def scan_directory_tree(root_path: str, max_depth: int = 4) -> dict:
    """Generate a structured AST of directory hierarchy with file metrics."""
    root = Path(root_path).resolve()
    result = {"path": str(root), "name": root.name, "type": "directory", "children": []}
    
    def _walk(current_path: Path, current_depth: int):
        if current_depth > max_depth:
            return None
        entries = []
        try:
            for item in sorted(current_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
                if item.name.startswith((".", "$RECYCLE.BIN", "node_modules", "__pycache__")):
                    continue
                if item.is_dir():
                    child = {"path": str(item), "name": item.name, "type": "directory"}
                    sub = _walk(item, current_depth + 1)
                    if sub is not None:
                        child["children"] = sub
                    entries.append(child)
                else:
                    mime, _ = mimetypes.guess_type(str(item))
                    stat = item.stat()
                    entries.append({
                        "path": str(item),
                        "name": item.name,
                        "type": "file",
                        "size_bytes": stat.st_size,
                        "mime_type": mime or "application/octet-stream",
                        "modified_at": stat.st_mtime
                    })
        except PermissionError:
            pass
        return entries

    result["children"] = _walk(root, 1) or []
    return result

def compute_file_sha256(filepath: str, chunk_size: int = 65536) -> str:
    """Compute deterministic SHA-256 hash for verification."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            hasher.update(chunk)
    return hasher.hexdigest()
```

---

## Sub-Skill: document-pdf-latex-pandoc-engine
# Document Engineering (PDF, DOCX, LaTeX, Typst, Pandoc)

Multi-format document generation, academic publishing, and forensic text extraction.

### 1. Robust PDF Extraction & Merging
```python
from pypdf import PdfReader, PdfWriter
import fitz  # PyMuPDF for high-speed rendering & text extraction

def extract_pdf_forensic_text(pdf_path: str) -> list[dict]:
    """Extract structured page text, bounding boxes, and images."""
    doc = fitz.open(pdf_path)
    pages = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        pages.append({
            "page": page_num + 1,
            "text": page.get_text("text"),
            "word_count": len(page.get_text("words")),
            "rect": list(page.rect),
            "images_count": len(page.get_images())
        })
    return pages

def merge_pdf_packets(input_pdfs: list[str], output_pdf: str):
    """Merge multiple PDF exhibits into a single signed document packet."""
    writer = PdfWriter()
    for pdf in input_pdfs:
        reader = PdfReader(pdf)
        for page in reader.pages:
            writer.add_page(page)
    with open(output_pdf, "wb") as f:
        writer.write(f)
```

### 2. LaTeX & Typst Publishing Patterns
```latex
% Canonical Publication Template for Technical & Legal Briefs
\documentclass[11pt,letterpaper]{article}
\usepackage[utf8]{inputenc}
\usepackage{geometry}
\geometry{margin=1in}
\usepackage{amsmath,amssymb}
\usepackage{booktabs}
\usepackage{hyperref}

\title{\textbf{APEX System Forensic & Architecture Report}}
\author{APEX Sovereign Intelligence Grid}
\date{\today}

\begin{document}
\maketitle
\begin{abstract}
Structured mathematical proof and cryptographic receipt validation across multi-language execution environments.
\end{abstract}
\section{Formal Invariants}
Let $\mathcal{S}$ denote the state space of the sovereign mesh. Every state transition $\sigma \to \sigma'$ satisfies:
\begin{equation}
\mathrm{Verify}(\sigma, \pi) = \mathrm{True} \implies \sigma' \in \mathcal{S}_{\text{valid}}
\end{equation}
\end{document}
```

---

## Sub-Skill: tabular-spreadsheet-google-suite
# Tabular Data, Excel, Parquet & Google Workspace

Bi-directional synchronization between local tabular formats (CSV, Parquet, Excel) and Google Sheets.

### 1. Excel Generation with Formatting (`openpyxl`)
```python
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

def create_styled_excel_report(data: list[dict], output_path: str, sheet_title: str = "Summary"):
    """Generate production-grade formatted Excel spreadsheet."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = sheet_title

    headers = list(data[0].keys()) if data else []
    
    # Header Styling
    header_fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num, value=header.replace("_", " ").title())
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")

    # Data Rows
    for row_num, row_data in enumerate(data, 2):
        for col_num, key in enumerate(headers, 1):
            val = row_data.get(key, "")
            cell = ws.cell(row=row_num, column=col_num, value=val)
            cell.alignment = Alignment(vertical="center")

    # Auto-adjust column widths
    for col in ws.columns:
        max_len = max(len(str(cell.value or "")) for cell in col)
        col_letter = openpyxl.utils.get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

    wb.save(output_path)
```

---

## Sub-Skill: cloud-storage-rclone-orchestrator
# Multi-Cloud Orchestration (Rclone, Google Drive, Dropbox, S3, R2)

Unified remote storage control across 40+ storage providers with delta syncing, verification, and rate limiting.

### 1. Essential Rclone Commands
```bash
# Verify remote connection and list top-level directories
rclone lsd <remote_name>:

# Synchronize local directory to cloud remote with dry-run verification
rclone sync /local/path <remote_name>:backup_dir --dry-run -v

# High-speed parallel delta sync with cryptographic checksum check
rclone sync /local/path <remote_name>:backup_dir \
    --checksum \
    --transfers 8 \
    --checkers 16 \
    --fast-list \
    --progress

# Copy single file or directory without deleting remote files
rclone copy /local/path <remote_name>:backup_dir

# Check integrity between local and remote datasets
rclone check /local/path <remote_name>:backup_dir --one-way
```

---

## Sub-Skill: sovereign-file-operations-and-bates
# Atomic File Manipulation & Legal Bates Numbering

Safe filesystem mutations, collision-free moves, mass regex renamers, and legal document stamping.

### 1. Forensic Legal Bates Numbering
```python
def generate_bates_sequence(prefix: str, start_number: int, count: int, padding: int = 6) -> list[str]:
    """Generate sequential Bates numbering series for court filings."""
    return [f"{prefix}-{str(start_number + i).zfill(padding)}" for i in range(count)]

def apply_bates_stamps_to_pdf(input_pdf: str, output_pdf: str, prefix: str, start_num: int):
    """Stamp bottom-right Bates labels onto each page of a legal exhibit."""
    doc = fitz.open(input_pdf)
    for i, page in enumerate(doc):
        bates_label = f"{prefix}-{str(start_num + i).zfill(6)}"
        rect = page.rect
        # Position in bottom-right corner (margin 36pt = 0.5in)
        point = fitz.Point(rect.width - 120, rect.height - 20)
        page.insert_text(point, bates_label, fontsize=10, color=(0, 0, 0))
    doc.save(output_pdf)
```

---

## Sub-Skill: visual-charts-infographics-slides
# Visual Infographics, Architecture Charts & Slide Decks

Generating clear presentation assets, Graphviz trees, Plotly interactive graphics, and Marp markdown slide decks.

### 1. Matplotlib / Seaborn Infographic Generator
```python
import matplotlib.pyplot as plt
import seaborn as sns

def generate_metric_card(title: str, value: str, change: str, output_path: str):
    """Render high-contrast visual metric card."""
    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(6, 3), dpi=200)
    ax.axis("off")
    
    ax.text(0.5, 0.7, title.upper(), fontsize=14, color="#94A3B8", ha="center", weight="bold")
    ax.text(0.5, 0.4, value, fontsize=32, color="#38BDF8", ha="center", weight="heavy")
    ax.text(0.5, 0.15, change, fontsize=12, color="#4ADE80", ha="center")
    
    fig.patch.set_facecolor("#0F172A")
    plt.tight_layout()
    plt.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
```

### 2. Marp Presentation Deck Template
```markdown
---
marp: true
theme: uncover
class: invert
paginate: true
---

# APEX Sovereign Architecture
### Multi-Agent Distributed Execution Matrix

---

## The Paradigm Shift
- **Expansion over Minimum Viable**
- **Compiler Proofs over LLM Vibes**
- **Durable Memory over Ephemeral Transcripts**

---

## System Invariants
1. Mathematical Verification ($L_2$)
2. Zero Data Loss Doctrine
3. Real-Time Hardware Watchdogs
```

---

## Sub-Skill: audio-podcast-media-transcription
# Media Engineering, Podcast Processing & Diarization

FFMPEG audio transformations, multi-speaker diarization formatting, and podcast transcript extraction.

### 1. FFMPEG Audio Extraction & Normalization
```bash
# Extract mono 16kHz WAV for Whisper transcription from video/audio
ffmpeg -i input_media.mp4 -vn -ar 16000 -ac 1 -c:a pcm_s16le output_mono16k.wav

# Normalize loudness to podcast standard (-16 LUFS)
ffmpeg -i input.wav -af loudnorm=I=-16:TP=-1.5:LRA=11 -ar 44100 output_mastered.mp3

# Slice audio chunk for targeted evidence playback (from 01:23 to 02:45)
ffmpeg -ss 00:01:23 -to 00:02:45 -i input.mp3 -c copy clip_segment.mp3
```

---
