#!/usr/bin/env python3
"""
apex-orchestration v1.1.0 — Holographic Mesh Orchestrator (Skill entry point).

Real implementation, not a stub. Subcommands:
  packets        list all 16 logic packets and their maturity
  schema         print the receipt/schema paths
  mesh           list all 12 lanes with model and dispatch trigger
  validate <id>  validate a JSON file against a packet's contract
  hash-chain <files...> compute the receipt chain hash (Packet 03)
  routes         print the 8 routing heuristics (Packet 04)
  failures       print the 13 failure codes (Packet 09)
  receipt-test   run the test fixtures and print a summary
  ml             ML/self-improving layer info (Packets 13-16)
  route          route a single subtask to a lane (Packet 04 + 13)
  mission        run the full 6-stage lifecycle (Packets 02-07)
  validate-receipt  validate a receipt file against schema + gates
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent
PACKETS_DIR = SKILL_ROOT / "packets"
SCHEMAS_DIR = SKILL_ROOT / "schemas"

LANES = [
    (
        "REASON",
        "nvidia/nemotron-3-ultra-550b-a55b:free",
        "plan_required OR invariants > 3 OR cross_domain",
    ),
    ("CODE", "poolside/laguna-s-2.1:free", "code_edit OR code_create"),
    (
        "CODE-FAST",
        "poolside/laguna-xs-2.1:free",
        "subagent == true AND scope < 200_lines",
    ),
    ("VERIFY", "z-ai/glm-5.2:free", "verify_required OR audit"),
    ("REVIEW", "cohere/north-mini-code:free", "refactor OR simplify"),
    ("LONG-CTX", "thinkingmachines/inkling:free", "input_tokens > 500_000"),
    (
        "LONG-CTX-ALT",
        "minimax/minimax-m3:free",
        "input_tokens > 500_000 AND inkling_unavailable",
    ),
    (
        "THINK-DEEP",
        "minimax/minimax-m2.7:free",
        "mission.horizon == 'long' AND requires_evolution",
    ),
    (
        "NANO-PERCEPTION",
        "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
        "input_modality IN {image, video, audio}",
    ),
    (
        "DOMAIN-MED",
        "inclusionai/ling-3.0-flash-sante:free",
        "domain == medical OR clinical",
    ),
    (
        "DOMAIN-FIN",
        "inclusionai/ling-3.0-flash-fin:free",
        "domain == finance OR quantitative",
    ),
    (
        "ROUTER-FREE",
        "openrouter/free",
        "smoke_test OR cost == 0 AND quality < critical",
    ),
]

ROUTES = [
    ("R-MEDICAL", "DOMAIN-MED", "subtask.domain IN {medical, clinical}", True),
    ("R-FINANCE", "DOMAIN-FIN", "subtask.domain IN {finance, quantitative}", True),
    (
        "R-MULTIMODAL",
        "NANO-PERCEPTION",
        "subtask.input_modality IN {image, video, audio}",
        True,
    ),
    ("R-LONGCTX", "LONG-CTX", "subtask.input_tokens > 500_000", True),
    (
        "R-PLAN",
        "REASON",
        "subtask.kind == plan OR invariants > 3 OR cross_domain",
        True,
    ),
    ("R-CODE-EDIT", "CODE", "subtask.kind IN {code_edit, code_create}", False),
    (
        "R-CODE-FAST",
        "CODE-FAST",
        "subtask.subagent == true AND estimated_lines < 200",
        False,
    ),
    ("R-DEFAULT", "ROUTER-FREE", "always (with VERIFY audit)", False),
]

FAILURE_CODES = [
    ("F-INT-01", "scope_ambiguous", "INTAKE", "operator", "ask one question, BLOCK"),
    ("F-INT-02", "budget_exceeded", "INTAKE", "operator", "BLOCK with cost breakdown"),
    ("F-DEC-01", "dag_cycle", "DECOMPOSE", "operator", "refuse DAG, re-decompose"),
    ("F-DEC-02", "lane_unavailable", "DECOMPOSE", "operator", "swap to fallback"),
    (
        "F-DIS-01",
        "dispatch_timeout",
        "DISPATCH",
        "orchestrator",
        "re-dispatch once, then BLOCK",
    ),
    ("F-DIS-02", "quota_exhausted", "DISPATCH", "orchestrator", "BLOCK mission"),
    ("F-VER-01", "l2_proof_missing", "VERIFY", "operator", "re-dispatch"),
    (
        "F-VER-02",
        "three_sig_missing",
        "VERIFY",
        "operator",
        "re-dispatch missing signature",
    ),
    ("F-FUSE-01", "draft_input", "FUSE", "operator", "drop drafts, BLOCK if empty"),
    ("F-FUSE-02", "conflict_unresolved", "FUSE", "operator", "BLOCK with both options"),
    (
        "F-DEL-01",
        "memory_write_failed",
        "DELIVERY",
        "operator",
        "BLOCK, retry once, then REFUSE",
    ),
    ("F-DEL-02", "chain_hash_drift", "DELIVERY", "operator", "REFUSE"),
]


def cmd_packets(_args):
    rows = []
    for p in sorted(PACKETS_DIR.glob("*.md")):
        txt = p.read_text(encoding="utf-8")
        # Extract "Maturity:" line
        m = next(
            (line for line in txt.splitlines() if line.startswith("**Maturity:**")), ""
        )
        rows.append((p.name, m.replace("**Maturity:**", "").strip()))
    print(f"{'PACKET':<40}  MATURITY")
    print("-" * 70)
    for name, mat in rows:
        print(f"{name:<40}  {mat}")
    print(f"\nTotal: {len(rows)} packets (target: >= 9, all >= maturity 9)")


def cmd_schema(_args):
    print(f"Receipt schema:   {SCHEMAS_DIR / 'receipt.schema.json'}")
    print(f"Stage schema:     {SCHEMAS_DIR / 'stage-receipt.schema.json'}")
    print(f"Delivery schema:  {SCHEMAS_DIR / 'delivery.schema.json'}")


def cmd_mesh(_args):
    print(f"{'LANE':<18}  {'MODEL':<58}  TRIGGER")
    print("-" * 140)
    for lane, model, trigger in LANES:
        print(f"{lane:<18}  {model:<58}  {trigger}")
    print(f"\nTotal: {len(LANES)} lanes (Packet 01)")


def cmd_routes(_args):
    print(f"{'RULE':<14}  {'LANE':<18}  {'HARD?':<6}  PREDICATE")
    print("-" * 90)
    for rule, lane, pred, hard in ROUTES:
        print(f"{rule:<14}  {lane:<18}  {('YES' if hard else 'no'):<6}  {pred}")


def cmd_failures(_args):
    print(
        f"{'CODE':<11}  {'NAME':<22}  {'STAGE':<10}  {'OWNER':<14}  DEFAULT RESOLUTION"
    )
    print("-" * 110)
    for code, name, stage, owner, res in FAILURE_CODES:
        print(f"{code:<11}  {name:<22}  {stage:<10}  {owner:<14}  {res}")


def cmd_validate(args):
    p = PACKETS_DIR / args.packet
    if not p.exists():
        print(f"ERROR: packet not found: {args.packet}", file=sys.stderr)
        return 2
    target = Path(args.path)
    if not target.exists():
        print(f"ERROR: file not found: {args.path}", file=sys.stderr)
        return 2
    payload = json.loads(target.read_text())
    if args.packet.startswith("01") or args.packet == "receipt":
        schema_path = SCHEMAS_DIR / "receipt.schema.json"
    elif args.packet.startswith("02"):
        schema_path = SCHEMAS_DIR / "stage-receipt.schema.json"
    elif args.packet.startswith("07"):
        schema_path = SCHEMAS_DIR / "delivery.schema.json"
    else:
        print(
            f"NOTE: packet {args.packet} does not have a JSON-Schema. Markdown presence only."
        )
        return 0
    try:
        import jsonschema

        jsonschema.validate(payload, json.loads(schema_path.read_text()))
        print(f"OK  {target}  conforms to  {schema_path.name}")
        return 0
    except ImportError:
        # Fall back: at least confirm required fields present
        schema = json.loads(schema_path.read_text())
        required = schema.get("required", [])
        missing = [k for k in required if k not in payload]
        if missing:
            print(f"FAIL  missing required fields: {missing}")
            return 1
        print(f"OK  (no jsonschema installed; required fields present)")
        return 0
    except jsonschema.ValidationError as e:
        print(f"FAIL  {e.message}")
        return 1


def cmd_hash_chain(args):
    h = hashlib.sha256()
    for f in args.files:
        p = Path(f)
        if not p.exists():
            print(f"ERROR: {f} not found", file=sys.stderr)
            return 2
        h.update(p.read_bytes())
    print(h.hexdigest())
    return 0


def cmd_receipt_test(_args):
    fixtures = SKILL_ROOT / "tests" / "fixtures"
    if not fixtures.exists():
        print("No fixtures dir; skipping")
        return 0
    ok = 0
    fail = 0
    for f in sorted(fixtures.glob("*.json")):
        try:
            payload = json.loads(f.read_text())
            required = ["lane", "model", "task", "l2_proof"]
            missing = [k for k in required if k not in payload]
            if missing or payload.get("l2_proof") is not True:
                print(
                    f"FAIL  {f.name}  missing={missing} l2_proof={payload.get('l2_proof')}"
                )
                fail += 1
            else:
                print(f"OK    {f.name}  lane={payload['lane']}")
                ok += 1
        except Exception as e:
            print(f"FAIL  {f.name}  {e}")
            fail += 1
    print(f"\n{ok} OK, {fail} FAIL")
    return 0 if fail == 0 else 1


def cmd_ml(_args):
    """Print ML/self-improving layer info from the ml_routing module."""
    sys.path.insert(0, str(SKILL_ROOT / "scripts"))
    import ml_routing

    info = {
        "WEIGHTS_VERSION": ml_routing.WEIGHTS_VERSION,
        "PARENT_VERSION": ml_routing.PARENT_VERSION,
        "EMBEDDING_DIM": ml_routing.EMBEDDING_DIM,
        "ROLLING_WINDOW": ml_routing.ROLLING_WINDOW,
        "REGRESSION_THRESHOLD": ml_routing.REGRESSION_THRESHOLD,
        "WATCHDOG_DROP_THRESHOLD": ml_routing.WATCHDOG_DROP_THRESHOLD,
        "WATCHDOG_MISSIONS": ml_routing.WATCHDOG_MISSIONS,
        "DEFAULT_WEIGHTS": ml_routing.DEFAULT_WEIGHTS,
        "LANES": ml_routing.ALL_LANES,
        "PACKETS": [
            "13-ml-routing (select_lane with 6-component score)",
            "14-receipt-mining (online receipt -> lane_stats + anti-patterns)",
            "15-embedding-memory (384-dim deterministic intent store)",
            "16-self-improving-loop (Hebbian update + regression gate + watchdog)",
        ],
    }
    print(json.dumps(info, indent=2))
    return 0


def cmd_route(args):
    """Route a single subtask to a lane (delegates to orchestrator.route)."""
    scripts_dir = str(SKILL_ROOT / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    from orchestrator import MissionOrchestrator

    orch = MissionOrchestrator()
    result = orch.route(args.subtask_json)
    print(json.dumps(result, indent=2))
    return 0


def cmd_mission(args):
    """Run the full 6-stage mission lifecycle (INTAKE→DECOMPOSE→DISPATCH→VERIFY→FUSE→DELIVER)."""
    scripts_dir = str(SKILL_ROOT / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    from orchestrator import MissionOrchestrator

    orch = MissionOrchestrator()
    receipts = json.loads(args.receipts_json) if args.receipts_json else []
    run_quality = json.loads(args.run_quality_json) if args.run_quality_json else None
    delivery = orch.run(
        description=args.description,
        budget=args.budget,
        blast_radius=args.blast_radius,
        receipts=receipts,
        run_quality=run_quality,
    )
    print(json.dumps(delivery.to_dict(), indent=2))
    return 0 if delivery.status == "SHIPPED" else 1


def cmd_validate_receipt(args):
    """Validate a receipt file against the schema + l2_proof + three-sig gates."""
    scripts_dir = str(SKILL_ROOT / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    from orchestrator import MissionOrchestrator

    orch = MissionOrchestrator()
    result = orch.validate_receipt(args.path)
    print(json.dumps(result, indent=2))
    return 0


def main():
    ap = argparse.ArgumentParser(
        prog="apex-orchestration", description="Holographic Mesh Orchestrator v1.1.0"
    )
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("packets")
    sub.add_parser("schema")
    sub.add_parser("mesh")
    sub.add_parser("routes")
    sub.add_parser("failures")
    sub.add_parser("receipt-test")
    sub.add_parser("ml")

    p_route = sub.add_parser("route", help="Route a single subtask to a lane")
    p_route.add_argument(
        "--subtask-json",
        required=True,
        help="JSON: {kind, domain, task/description, input_tokens, etc.}",
    )

    p_mission = sub.add_parser("mission", help="Run full 6-stage mission lifecycle")
    p_mission.add_argument("--description", required=True)
    p_mission.add_argument("--budget", type=float, default=1.0)
    p_mission.add_argument(
        "--blast-radius", default="local", choices=["local", "remote", "cross_domain"]
    )
    p_mission.add_argument("--receipts-json", default="[]")
    p_mission.add_argument("--run-quality-json", default="")

    p_vr = sub.add_parser("validate-receipt", help="Validate a receipt file")
    p_vr.add_argument("--path", required=True)

    p_val = sub.add_parser("validate")
    p_val.add_argument("packet")
    p_val.add_argument("path")
    p_hash = sub.add_parser("hash-chain")
    p_hash.add_argument("files", nargs="+")
    args = ap.parse_args()
    dispatch = {
        "packets": cmd_packets,
        "schema": cmd_schema,
        "mesh": cmd_mesh,
        "routes": cmd_routes,
        "failures": cmd_failures,
        "validate": cmd_validate,
        "hash-chain": cmd_hash_chain,
        "receipt-test": cmd_receipt_test,
        "ml": cmd_ml,
        "route": cmd_route,
        "mission": cmd_mission,
        "validate-receipt": cmd_validate_receipt,
    }
    return dispatch[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
