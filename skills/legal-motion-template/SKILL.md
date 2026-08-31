---
name: legal-motion-template
description: "Generate Hawaii family court motions with proper captions, service certificates, jurisdiction hooks, and Kalua Doctrine traps. Compliant with HAWAII RULES OF CIVIL PROCEDURE (HRCP)."
---

# Legal Motion Template Skill

## Overview
Generates publication-ready legal motions formatted per Hawaii family court requirements. Includes proper case captions, service certificate blocks, constitutional hooks (§1983), and strategic Kalua Doctrine logic traps.

## Motion Types

### 1. Motion to Stay Proceedings
- **Basis**: Constitutional violation / Judicial bias
- **Kalua Trap**: Either GAL must recuse (win) OR stay issued (win)
- **Timeline**: Halt case pending constitutional resolution
- **References**: 42 USC §1983, HAWAII RULES OF CIVIL PROCEDURE

### 2. Motion for Protective Order
- **Basis**: Discovery abuse / Child safety
- **Scope**: Restrict frivolous depositions
- **Remedy**: JEFS filing + service on opposing counsel

### 3. Motion for Sanctions
- **Basis**: GAL misconduct / Bad faith litigation
- **Evidence**: Deposition transcripts + audio (CoC hashed)
- **Remedy**: Attorney fees + case management sanctions

### 4. Motion to Disqualify GAL
- **Basis**: Bias / Conflict of interest / §1983 violation
- **Standard**: Clear and convincing evidence
- **Strategic**: Kalua Doctrine forces replacement or appellate reversal

### 5. Demand for Jury Trial
- **Basis**: Constitutional right (7th Amendment)
- **Scope**: All factual issues not previously resolved
- **Remedy**: Federal court removal option if denied

## Document Structure

```
┌─────────────────────────────────────────┐
│ CASE CAPTION                            │
│ ─────────────────────────────────────── │
│ IN THE FAMILY COURT OF THE FIRST       │
│ CIRCUIT, STATE OF HAWAII               │
│                                         │
│ In the matter of CHILD-A (DOB XXXX),   │
│ Respondent.                            │
│                                         │
│ Case No. 1FDV-23-0001009                │
├─────────────────────────────────────────┤
│ MOTION TO [ACTION]                      │
│                                         │
│ [Movant] respectfully submits this      │
│ Motion by and through the undersigned   │
│ counsel and states as follows:          │
├─────────────────────────────────────────┤
│ I. INTRODUCTION                         │
│ II. FACTUAL BACKGROUND                  │
│ III. LEGAL STANDARD                     │
│ IV. ARGUMENT                            │
│    A. Ground 1                          │
│    B. Ground 2                          │
│ V. CONCLUSION                           │
│ VI. PRAYER FOR RELIEF                   │
├─────────────────────────────────────────┤
│ CERTIFICATE OF SERVICE                  │
│ (Signed, notarized if required)         │
└─────────────────────────────────────────┘
```

## Key Components

### Case Caption
```
IN THE FAMILY COURT OF THE FIRST
CIRCUIT, STATE OF HAWAII

In the Matter of [CHILD NAME] (DOB [DATE]),
                                          Respondent.

[Your Name],
                                          Petitioner.
_________________________

Case No. 1FDV-23-0001009
```

### Jurisdiction Hooks
- **Hawaii Family Court jurisdiction**: HRS §571-1
- **Personal jurisdiction**: HRS §603-36
- **Federal jurisdiction**: 28 USC §1331 (federal question)
- **Subject matter**: Family law + constitutional rights

### Service Certificate
```
CERTIFICATE OF SERVICE

I hereby certify that I served a true and
correct copy of the foregoing [DOCUMENT]
upon all parties to this action by:

☐ Personal delivery
☐ Mail (certified, return receipt)
☐ JEFS electronic service

on this _____ day of __________, 20__.

Dated: ________________
       Signature

Print Name: ________________
```

### Kalua Doctrine Framework

**Strategic Binary**:
- **Prong 1** (Recusal): GAL recuses due to bias allegations → Win
- **Prong 2** (Stay): Court grants stay pending investigation → Win
- **Result**: Case cannot proceed without resolution

## Variables (Template)

```json
{
  "case_number": "1FDV-23-0001009",
  "child_name": "[CONFIDENTIAL]",
  "child_dob": "[CONFIDENTIAL]",
  "petitioner": "[Your Name]",
  "respondent": "[Other Party]",
  "gal_name": "[GAL Name]",
  "motion_type": "Stay|Protective|Sanctions|Disqualify|JuryDemand",
  "grounds": ["§1983 Violation", "Judicial Bias", "Discovery Abuse"],
  "relief_requested": "Stay pending constitutional review",
  "service_date": "YYYY-MM-DD",
  "service_method": "JEFS|Mail|Personal",
  "attorney_name": "[Your Name/Counsel]",
  "attorney_bar": "[Hawaii Bar Number]",
  "signature_date": "YYYY-MM-DD"
}
```

## Integration Points

### JEFS Filing
```bash
# Court filing via JEFS (manual auth required)
# Account: webu350142
# Case: 1FDV-23-0001009
# Upload: motion.pdf (Appendices A-D attached)
```

### Evidence References
```
Exhibit A: Deposition transcript (Teresa, p. 47-52)
Exhibit B: Audio CoC record (SHA-256: [hash])
Exhibit C: GAL bias evidence (discovery request response)
Exhibit D: Constitutional standards (42 USC §1983)
```

### Notion Tracking
- DB: `SUPERLUMINAL_CASE_MATRIX`
- Page: `FEDERAL_WARFARE_PHASE/[motion-type]`
- Link: Citation to source motion file
- Status: Draft → Filed → Responded → Ruled

## Output Artifacts

- **motion.pdf** — Publication-ready with signature blocks
- **motion_variables.json** — Filled parameters for record
- **exhibits/** — Referenced attachments
- **service_proof.pdf** — Certificate of service
- **jefs_filing_checklist.md** — Step-by-step JEFS upload guide

## Use When
- Drafting state court motions (Hawaii Family Court)
- Building constitutional challenges (§1983)
- Executing Kalua Doctrine traps
- Filing via JEFS system
- Coordinating with expert witnesses
- Building appellate record
