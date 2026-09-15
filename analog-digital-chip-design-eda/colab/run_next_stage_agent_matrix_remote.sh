#!/usr/bin/env bash
set -euo pipefail

SESSION_NAME="${COLAB_SESSION_NAME:-next-stage-agent-matrix-$(date -u +%Y%m%dT%H%M%SZ)}"
GPU_TYPE="${COLAB_GPU_TYPE:-T4}"
TIMEOUT_SECONDS="${COLAB_TIMEOUT_SECONDS:-18000}"
MODEL_ID="${COLAB_MODEL_ID:-Qwen/Qwen2.5-0.5B-Instruct}"
START_INDEX="${COLAB_START_INDEX:-0}"
MAX_TASKS="${COLAB_MAX_TASKS:-}"
ASSIGN_RETRIES="${COLAB_ASSIGN_RETRIES:-3}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ARTIFACT_DIR="${ROOT_DIR}/.artifacts/llm-agent-colab/${SESSION_NAME}"
ARCHIVE="${ROOT_DIR}/.artifacts/colab-next-stage-agent-matrix.tgz"
CONFIG="${ROOT_DIR}/.artifacts/colab-next-stage-agent-matrix-config.json"
mkdir -p "${ROOT_DIR}/.artifacts" "${ARTIFACT_DIR}"
[[ "${START_INDEX}" =~ ^[0-9]+$ ]] || { echo "ERROR: COLAB_START_INDEX must be a nonnegative integer" >&2; exit 1; }
if [[ -n "${MAX_TASKS}" && ! "${MAX_TASKS}" =~ ^[1-9][0-9]*$ ]]; then
  echo "ERROR: COLAB_MAX_TASKS must be a positive integer" >&2
  exit 1
fi
[[ "${ASSIGN_RETRIES}" =~ ^[1-9][0-9]*$ ]] || { echo "ERROR: COLAB_ASSIGN_RETRIES must be a positive integer" >&2; exit 1; }
command -v colab >/dev/null 2>&1 || { echo "ERROR: Colab CLI is not installed" >&2; exit 1; }
if colab --auth oauth2 sessions 2>/dev/null | rg -F "[${SESSION_NAME}]" >/dev/null 2>&1; then
  echo "ERROR: refusing to reuse existing session ${SESSION_NAME}" >&2
  exit 2
fi
tar --exclude='.git' --exclude='.artifacts' --exclude='evidence' --exclude='**/runs' --exclude='__pycache__' --exclude='*.pyc' \
  --transform='s,^analog-digital-chip-design-eda\(/\|$\),next-stage-agent-matrix\1,' \
  -czf "${ARCHIVE}" -C "$(dirname "${ROOT_DIR}")" "$(basename "${ROOT_DIR}")"
if [[ -n "${MAX_TASKS}" ]]; then
  printf '{"model_id":"%s","start_index":%s,"max_tasks":%s}\n' "${MODEL_ID}" "${START_INDEX}" "${MAX_TASKS}" > "${CONFIG}"
else
  printf '{"model_id":"%s","start_index":%s}\n' "${MODEL_ID}" "${START_INDEX}" > "${CONFIG}"
fi
cleanup() { colab --auth oauth2 stop -s "${SESSION_NAME}" >/dev/null 2>&1 || true; }
trap cleanup EXIT
assigned=0
for attempt in $(seq 1 "${ASSIGN_RETRIES}"); do
  if colab --auth oauth2 new -s "${SESSION_NAME}" --gpu "${GPU_TYPE}" >>"${ARTIFACT_DIR}/session-create.stdout.log" 2>>"${ARTIFACT_DIR}/session-create.stderr.log"; then
    assigned=1
    break
  fi
  if ! rg -qi "service unavailable|503" "${ARTIFACT_DIR}/session-create.stderr.log"; then
    break
  fi
  if (( attempt < ASSIGN_RETRIES )); then
    sleep 5
  fi
done
if (( assigned == 0 )); then
  python3 - "${ARTIFACT_DIR}/colab-launch-failure.json" "${SESSION_NAME}" <<'PY'
import json
from pathlib import Path
import sys

output = Path(sys.argv[1])
session = sys.argv[2]
stderr = output.with_name("session-create.stderr.log")
record = {
    "schema_version": "colab-launch-failure-v1",
    "status": "blocked",
    "session_name": session,
    "error_tail": stderr.read_text(encoding="utf-8", errors="replace")[-5000:] if stderr.is_file() else "",
    "claim_boundary": "Colab assignment failure; no model or verification result",
}
output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps({"status": record["status"], "session": session, "report": str(output)}, sort_keys=True))
PY
  exit 1
fi
colab --auth oauth2 upload -s "${SESSION_NAME}" "${ARCHIVE}" /content/next-stage-agent-matrix.tgz
colab --auth oauth2 upload -s "${SESSION_NAME}" "${CONFIG}" /content/next-stage-agent-matrix-config.json
colab --auth oauth2 exec -s "${SESSION_NAME}" -f "${ROOT_DIR}/colab/run_next_stage_agent_matrix_remote.py" --timeout "${TIMEOUT_SECONDS}"
colab --auth oauth2 download -s "${SESSION_NAME}" /content/next-stage-agent-matrix/.artifacts/next-stage-agent-matrix-remote-summary.json "${ARTIFACT_DIR}/next-stage-agent-matrix-remote-summary.json"
colab --auth oauth2 download -s "${SESSION_NAME}" /content/next-stage-agent-matrix/.artifacts/next-stage-real/next-stage-colab-report.json "${ARTIFACT_DIR}/next-stage-colab-report.json"
python3 - "${ARTIFACT_DIR}/next-stage-agent-matrix-remote-summary.json" <<'PY'
import json, sys
payload = json.load(open(sys.argv[1], encoding='utf-8'))
if payload.get('status') != 'passed':
    raise SystemExit('real next-stage Colab run did not pass')
report = payload.get('report') or {}
if report.get('all_machine_stages_passed') is not True:
    raise SystemExit('next-stage Colab report failed machine-stage acceptance')
print('real next-stage Colab matrix acceptance passed')
PY
python3 "${ROOT_DIR}/colab/check_next_stage_real_colab.py" "${ARTIFACT_DIR}/next-stage-colab-report.json" "${ARTIFACT_DIR}/next-stage-agent-matrix-remote-summary.json"
echo "Downloaded next-stage Colab evidence to ${ARTIFACT_DIR}"
