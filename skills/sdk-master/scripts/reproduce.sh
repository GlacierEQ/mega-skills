#!/usr/bin/env bash
# Version-pinned SDK Master reproduction; no external provider mutation.
set -euo pipefail
SDK_ROOT="${1:?Usage: bash reproduce.sh /path/to/sdk-ts [verify|accept]}"
MODE="${2:-verify}"
SKILL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXPECTED_REVISION="8594587e77a6d31f649ebd4b40fe4a6189770461"
OBSERVED_REVISION="$(git -C "$SDK_ROOT" rev-parse HEAD)"
test "$OBSERVED_REVISION" = "$EXPECTED_REVISION" || {
  echo "REVISION_MISMATCH expected=$EXPECTED_REVISION actual=$OBSERVED_REVISION" >&2
  exit 2
}
python3.12 -m unittest discover -s "$SKILL_ROOT/tests" -p 'test_*.py' -v
python3.12 "$SKILL_ROOT/scripts/inspect_sdk.py" "$SDK_ROOT" > /tmp/sdk-master-inspection.json
(
 cd "$SDK_ROOT"
 yarn install --frozen-lockfile --ignore-scripts --non-interactive
 ./scripts/build
 ./scripts/lint
 if curl --silent --max-time 3 http://127.0.0.1:4010 >/dev/null 2>&1; then
   TEST_API_BASE_URL=http://127.0.0.1:4010 ./scripts/test
 else
   ./scripts/test
 fi
)
SDK_REVISION="$OBSERVED_REVISION" node "$SKILL_ROOT/tests/sdk_ts_runtime_conformance.cjs" "$SDK_ROOT"
if [[ "$MODE" == "accept" ]]; then
 python3.12 "$SKILL_ROOT/scripts/completion_gate.py" "$SKILL_ROOT/receipts/MISSION_STATE.json"
else
 set +e
 python3.12 "$SKILL_ROOT/scripts/completion_gate.py" "$SKILL_ROOT/receipts/MISSION_STATE.json"
 gate_exit=$?
 set -e
 echo "COMPLETION_GATE_EXIT:$gate_exit"
fi
echo "REPRODUCE_EXECUTION=PASS"
echo "SDK_REVISION=$OBSERVED_REVISION"
