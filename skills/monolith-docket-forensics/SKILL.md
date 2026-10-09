---
name: "monolith-docket-forensics"
description: "Docket timestamp and NEF forensics from raw sources. Use for filing-date disputes, timestamp anomalies, and notice-timing questions on the 1FDV docket."
metadata: { "includeInPrompt": true }
---

# Monolith Docket Forensics

## Purpose
Filing-date truth lives in three raw artifacts: the docket row, the NEF body,
and the email headers. Compare all three; they don't always agree, and the
disagreement is the finding.

## Workflow
1. **Docket row** — parse `1FDV-23-0001009/RAW_METADATA/docket_raw_final.html`
   directly (table cells; date and time are separate cells). Never trust a
   manifest's rendering over the cells.
2. **NEF body** — pull the NEF from glacier Gmail, read the HTML part:
   `Filing Date / Time` and `Filing Parties` are the court's own assertions.
   `COURT FILED BY COURT` in Filing Parties means manual court entry.
3. **Email headers** — compare `Date` (composed) against the `Received` chain.
   Transit is seconds; a hours-long gap between filing time and Date is the
   court's internal delay, not network.
4. **Document stamp** — the "Electronically Filed ... Dkt. N" stamp on the PDF
   itself; compare against the docket row.

## The :00-seconds rule (verified 2026-10-09 across 214 rows)
- Machine JEFS stamps carry real seconds (13:20:16, 23:58:19).
- `:00` seconds on a FILING timestamp indicates manual human entry
  (confirmed: Operator's window-filed batch reads 16:09:00; *MINH hearing
  times are scheduled and naturally round — excluded).
- `:00` + `COURT FILED BY COURT` + no pending hearing = manual court entry.

## Operating Rules
- HEFSR 3.3: filing date/time is the NEF timestamp — but verify the NEF's
  internal Filing Date/Time against its email Date header; they can differ.
- Asymmetric precision is the frame: the system judges filer timestamps to the
  second while its own entries are hand-rounded. Name it when the record shows it.
- Never concede a filing date from a later characterization (order, minutes);
  always go to the NEF/file stamp first.
- Directionality is evidence: random errors scatter; errors that all cut one
  way are pattern. State the direction; don't assign motive.
