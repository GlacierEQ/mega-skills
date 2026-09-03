#!/usr/bin/env python3
"""Deep-casebuilding cluster activation driver for GlacierEQ/mega-skills.

Activates the casebuilding capability chain by driving the repository's own
readiness assay (scripts/readiness_assay.py) instead of hand-editing maturity
flags:

    skills:  audio-forensic-core, forensic-evidence-chain-core, epistemic-gate
    combos:  court-evidence-compiler, voice-evidence-authenticator,
             forensic-docket-intelligence, epistemic-verification-chain
    mega:    apex-forensic-litigation-sentinel (promotion)

Stages:
  1. Preflight: target scripts carry no stub markers and behavioral tests exist.
  2. Behavioral proof: run each target skill's unittest suite (direct file
     execution, because hyphenated package dirs are not importable by
     unittest discovery).
  3. Fresh readiness verdicts via readiness_assay.inspect_skill.
  4. Dry-run (default): print the planned promotion set. Unchanged dependencies
     resolve from the recorded readiness registry and are labeled
     "mixed_evidence"; target packages use fresh sandbox evidence.
  5. --apply (full clone only): run assay pass-2 maturity reconciliation,
     sync versions, apply the apex-legal-forensic-powerhouse rewiring when
     absent, and write a hash-bound receipt under evidence/casebuilding-activation/.

The --apply path refuses to run against a partial slice: every registered
skill package directory must exist so the assay never downgrades absent
packages it cannot inspect.
"""

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry"

TARGET_SKILLS = ["audio-forensic-core", "forensic-evidence-chain-core", "epistemic-gate"]
TARGET_COMBOS = [
    "court-evidence-compiler",
    "voice-evidence-authenticator",
    "forensic-docket-intelligence",
    "epistemic-verification-chain",
]
TARGET_MEGAS = ["apex-forensic-litigation-sentinel"]
SKILL_VERSION_BUMPS = {
    "audio-forensic-core": "0.2.0",
    "forensic-evidence-chain-core": "0.2.0",
    "epistemic-gate": "1.0.1",
}
MEGA_VERSION_BUMPS = {"apex-forensic-litigation-sentinel": "1.1.0"}
POWERHOUSE_REWIRE = {
    "id": "apex-legal-forensic-powerhouse",
    "required_combos": ["long-horizon-core", "forensic-docket-intelligence", "court-evidence-compiler"],
    "conditional_combos": [
        "capability-readiness",
        "voice-evidence-authenticator",
        "epistemic-verification-chain",
        "evidence-to-evolution-loop",
    ],
    "version": "0.2.0",
}
STUB_MARKERS = ("Status: STUB - implement per skill contract", "# TODO: Implement")
BEHAVIOR_MARKERS = ("TODO: Add actual behavioral tests", "TODO: implement actual behavioral tests")


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def dump_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_assay():
    spec = importlib.util.spec_from_file_location("readiness_assay", ROOT / "scripts" / "readiness_assay.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def preflight():
    problems = []
    for skill_id in TARGET_SKILLS:
        scripts = ROOT / "skills" / skill_id / "scripts"
        tests = ROOT / "skills" / skill_id / "tests"
        for path in sorted(scripts.glob("*.py")):
            text = path.read_text(encoding="utf-8", errors="replace")
            for marker in STUB_MARKERS:
                if marker in text:
                    problems.append(f"{skill_id}: stub marker in {path.name}")
        test_files = list(tests.glob("test_*.py"))
        if not test_files:
            problems.append(f"{skill_id}: no test files")
            continue
        combined = "".join(p.read_text(encoding="utf-8", errors="replace") for p in test_files)
        for marker in BEHAVIOR_MARKERS:
            if marker in combined:
                problems.append(f"{skill_id}: behavioral tests still marked pending")
        if "unittest.TestCase" not in combined:
            problems.append(f"{skill_id}: no unittest.TestCase behavioral class")
    return problems


def run_skill_suites():
    results = {}
    for skill_id in TARGET_SKILLS:
        tests_dir = ROOT / "skills" / skill_id / "tests"
        for test_file in sorted(tests_dir.glob("test_*.py")):
            proc = subprocess.run(
                [sys.executable, str(test_file)],
                capture_output=True, text=True, cwd=ROOT)
            results[f"{skill_id}:{test_file.name}"] = {
                "returncode": proc.returncode,
                "tail": (proc.stdout + proc.stderr).strip().splitlines()[-5:],
            }
    return results


def fresh_skill_verdicts(assay, skills_doc):
    entries = {entry["id"]: entry for entry in skills_doc.get("entries", [])}
    verdicts = {}
    for skill_id in TARGET_SKILLS:
        if skill_id in entries:
            verdicts[skill_id] = assay.inspect_skill(entries[skill_id])
    return verdicts


def combo_frontmatter_version(entry):
    doc = ROOT / entry.get("entrypoint", "")
    if not doc.is_file():
        return None
    text = doc.read_text(encoding="utf-8", errors="replace")
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    for line in parts[1].splitlines():
        key, sep, value = line.partition(":")
        if sep and key.strip() == "version":
            return value.strip()
    return None


def mixed_combo_verdicts(assay, combos_doc, external_doc, fresh, recorded):
    skill_states = dict(recorded)
    skill_states.update(fresh)
    external_ids = {entry["id"] for entry in external_doc.get("entries", [])}
    verdicts = {}
    for entry in combos_doc.get("entries", []):
        if entry["id"] in TARGET_COMBOS:
            verdict = assay.inspect_combo(entry, skill_states, external_ids)
            verdict["evidence"] = "mixed: fresh target skills + recorded dependency readiness"
            verdicts[entry["id"]] = verdict
    return verdicts


def mega_verdicts(megas_doc, combo_verdicts, recorded_combos):
    combo_states = dict(recorded_combos)
    combo_states.update(combo_verdicts)
    verdicts = {}
    for entry in megas_doc.get("entries", []):
        if entry["id"] not in TARGET_MEGAS + [POWERHOUSE_REWIRE["id"]]:
            continue
        reasons = []
        for combo_id in entry.get("required_combos", []):
            state = combo_states.get(combo_id)
            if state is None or not state.get("ready"):
                reasons.append(f"required combo not ready: {combo_id}")
        verdicts[entry["id"]] = {
            "id": entry["id"],
            "ready": not reasons,
            "state": "mission_contract_ready" if not reasons else "mission_candidate",
            "reasons": reasons,
            "evidence": "mixed: fresh combo verdicts + recorded combo readiness",
        }
    return verdicts


def apply_activation(assay, receipt):
    skills_doc = load_json(REGISTRY / "skills.json")
    missing = [entry["id"] for entry in skills_doc.get("entries", [])
               if not (ROOT / entry["path"]).is_dir()]
    if missing:
        receipt["aborted"] = (
            f"--apply requires a full clone; {len(missing)} registered skill packages "
            f"are absent (first: {missing[0]}). Refusing to let the assay downgrade "
            "packages it cannot inspect."
        )
        return 1
    before = {name: sha256_file(REGISTRY / name)
              for name in ("skills.json", "combo-skills.json", "mega-skills.json", "skill-readiness.json")}
    report = assay.build_report()
    not_ready = [entry["id"] for entry in report["skills"]
                 if entry["id"] in TARGET_SKILLS and not entry["ready"]]
    if not_ready:
        receipt["aborted"] = f"target skills still not ready after proof stage: {not_ready}"
        return 1
    receipt["maturity_changes"] = assay.apply_maturity(report)
    final_report = assay.build_report()
    final_report["pass"] = 2
    assay.dump_json(assay.READINESS_REGISTRY, final_report)
    skills_doc = load_json(REGISTRY / "skills.json")
    for entry in skills_doc.get("entries", []):
        if entry["id"] in SKILL_VERSION_BUMPS and entry.get("version") != SKILL_VERSION_BUMPS[entry["id"]]:
            entry["version"] = SKILL_VERSION_BUMPS[entry["id"]]
    dump_json(REGISTRY / "skills.json", skills_doc)
    combos_doc = load_json(REGISTRY / "combo-skills.json")
    for entry in combos_doc.get("entries", []):
        if entry["id"] in TARGET_COMBOS:
            frontmatter_version = combo_frontmatter_version(entry)
            if frontmatter_version and entry.get("version") != frontmatter_version:
                entry["version"] = frontmatter_version
    dump_json(REGISTRY / "combo-skills.json", combos_doc)
    megas_doc = load_json(REGISTRY / "mega-skills.json")
    for entry in megas_doc.get("entries", []):
        if entry["id"] in MEGA_VERSION_BUMPS and entry.get("maturity") == "active" \
                and entry.get("version") != MEGA_VERSION_BUMPS[entry["id"]]:
            entry["version"] = MEGA_VERSION_BUMPS[entry["id"]]
        if entry["id"] == POWERHOUSE_REWIRE["id"]:
            rewired = entry.get("required_combos") == POWERHOUSE_REWIRE["required_combos"] and \
                entry.get("conditional_combos") == POWERHOUSE_REWIRE["conditional_combos"]
            if not rewired:
                entry["required_combos"] = list(POWERHOUSE_REWIRE["required_combos"])
                entry["conditional_combos"] = list(POWERHOUSE_REWIRE["conditional_combos"])
                entry["combos"] = list(POWERHOUSE_REWIRE["required_combos"])
                receipt["powerhouse_rewire_applied"] = True
            receipt["powerhouse_rewire_present"] = True
            if entry.get("version") != POWERHOUSE_REWIRE["version"]:
                entry["version"] = POWERHOUSE_REWIRE["version"]
    dump_json(REGISTRY / "mega-skills.json", megas_doc)
    after = {name: sha256_file(REGISTRY / name)
             for name in ("skills.json", "combo-skills.json", "mega-skills.json", "skill-readiness.json")}
    receipt["registry_sha256"] = {"before": before, "after": after}
    receipt["applied"] = True
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="Deep-casebuilding cluster activation driver.")
    parser.add_argument("--apply", action="store_true", help="Apply registry promotions (full clone required).")
    parser.add_argument("--report", default="evidence/casebuilding-activation/activation-receipt.json")
    parser.add_argument("--skip-tests", action="store_true", help="Skip the behavioral suite stage (evidence already on file).")
    args = parser.parse_args(argv)

    receipt = {
        "schema_version": 1,
        "driver": "casebuilding_activation.py",
        "mode": "apply" if args.apply else "dry_run",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "target_skills": TARGET_SKILLS,
        "target_combos": TARGET_COMBOS,
        "target_megas": TARGET_MEGAS,
    }

    problems = preflight()
    receipt["preflight_problems"] = problems
    if problems:
        dump_json(Path(args.report) if Path(args.report).is_absolute() else ROOT / args.report, receipt)
        print(json.dumps(receipt, indent=2, sort_keys=True))
        return 1

    if not args.skip_tests:
        suites = run_skill_suites()
        receipt["skill_test_suites"] = suites
        failed = [name for name, row in suites.items() if row["returncode"] != 0]
        if failed:
            receipt["aborted"] = f"behavioral suites failing: {failed}"
            dump_json(Path(args.report) if Path(args.report).is_absolute() else ROOT / args.report, receipt)
            print(json.dumps(receipt, indent=2, sort_keys=True))
            return 1

    assay = load_assay()
    skills_doc = load_json(REGISTRY / "skills.json")
    combos_doc = load_json(REGISTRY / "combo-skills.json")
    megas_doc = load_json(REGISTRY / "mega-skills.json")
    external_doc = load_json(REGISTRY / "external-skills.json")
    recorded_readiness = load_json(REGISTRY / "skill-readiness.json") if (REGISTRY / "skill-readiness.json").is_file() else {}
    recorded_skills = {row["id"]: row for row in recorded_readiness.get("skills", [])}
    recorded_combos = {row["id"]: row for row in recorded_readiness.get("combos", [])}

    fresh = fresh_skill_verdicts(assay, skills_doc)
    combo_verdicts = mixed_combo_verdicts(assay, combos_doc, external_doc, fresh, recorded_skills)
    mega_verdict_map = mega_verdicts(megas_doc, combo_verdicts, recorded_combos)
    receipt["fresh_skill_verdicts"] = fresh
    receipt["combo_verdicts"] = combo_verdicts
    receipt["mega_verdicts"] = mega_verdict_map

    ready = (
        len(fresh) == len(TARGET_SKILLS)
        and all(row["ready"] for row in fresh.values())
        and all(row["ready"] for row in combo_verdicts.values())
        and mega_verdict_map.get(TARGET_MEGAS[0], {}).get("ready", False)
    )
    receipt["activation_ready"] = ready

    if args.apply and ready:
        code = apply_activation(assay, receipt)
        if code != 0:
            dump_json(Path(args.report) if Path(args.report).is_absolute() else ROOT / args.report, receipt)
            print(json.dumps(receipt, indent=2, sort_keys=True))
            return code

    report_path = Path(args.report)
    dump_json(report_path if report_path.is_absolute() else ROOT / report_path, receipt)
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if ready else 1


if __name__ == "__main__":
    sys.exit(main())
