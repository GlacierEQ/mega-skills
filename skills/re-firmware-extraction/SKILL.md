---
name: re-firmware-extraction
description: "Firmware image analysis with REA: region inspection and caller-directed extraction through bring-your-own Binwalk/Unblob on Linux, with the extraction boundary treated as a safety decision, not a default."
---

# RE Firmware Extraction

Own the firmware lane. A firmware image is a container of other artifacts; REA's firmware tools map its regions and, on request, extract them with the operator's own Binwalk/Unblob. The lane's discipline is keeping the region map, the extraction result, and the analysis of extracted files as three separate evidence classes.

## Workflow

1. Inspect regions first: `inspect_firmware_regions` (when advertised) maps the image — offsets, identified structures, nested containers — without extracting anything. Most scoping questions are answered by the map.
2. Extract only when extraction is requested: `extract_firmware` requires a caller-selected **new** absolute output directory. Never extract into an existing tree; the output directory's freshness is part of the receipt.
3. Record the extraction toolchain in the receipt: Binwalk/Unblob are caller-supplied on Linux (bring-your-own; REA setup does not install them). Extraction failures and partial recoveries are recorded as coverage limits, not silently dropped.
4. Treat every extracted file as a new artifact: it re-enters through re-target-triage with its own identity and digest. A filesystem tree recovered from an image is evidence of what the image contains — not of what a running device does.
5. Preserve the source image digest across the whole lane; region and extraction records cite it.

## Safety gates

- Extracted content is untrusted content (re-untrusted-content-defense) — firmware is a classic hostile-artifact class, and extracted scripts/binaries are never executed from this lane.
- No extraction without an explicit request and a fresh output directory; inspection is the default.

## Output contract

- Firmware region Evidence record with coverage limits
- Extraction receipt with output directory and recovered inventory

## Related skills

- re-target-triage — routes firmware images here and re-triages extracted artifacts
- re-native-static-readers — structure of recovered ELF/PE payloads
- rea-operator — bring-your-own tool availability

## Validation commands

Run the repository-specific checks first. For this repository, run:

```bash
python scripts/validate_hierarchy.py
python -m unittest discover -s skills/re-firmware-extraction/tests -v
git diff --check
```
