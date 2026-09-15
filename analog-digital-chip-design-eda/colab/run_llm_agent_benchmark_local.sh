#!/usr/bin/env bash
set -euo pipefail

SESSION_NAME="${COLAB_SESSION_NAME:-aimc-llm-agent}"
GPU_TYPE="${COLAB_GPU_TYPE:-T4}"
RUN_ID="${COLAB_RUN_ID:-aimc-llm-agent-$(date -u +%Y%m%dT%H%M%SZ)}"
TIMEOUT_SECONDS="${COLAB_TIMEOUT_SECONDS:-10800}"
MODEL_ID="${COLAB_MODEL_ID:-Qwen/Qwen2.5-0.5B-Instruct}"
ASSIGN_RETRIES="${COLAB_ASSIGN_RETRIES:-3}"
ASSIGN_BACKOFF_SECONDS="${COLAB_ASSIGN_BACKOFF_SECONDS:-20}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ARTIFACT_DIR="${ROOT_DIR}/.artifacts/colab-llm"
ARCHIVE="${ARTIFACT_DIR}/aimc-llm-agent.tgz"
CONFIG="${ARTIFACT_DIR}/aimc-llm-agent-config.json"
DEST="${ROOT_DIR}/.artifacts/llm-agent-colab/${RUN_ID}"

mkdir -p "${ARTIFACT_DIR}" "${DEST}"
command -v colab >/dev/null 2>&1 || { echo "ERROR: run scripts/bootstrap_colab_cli_auth.sh first" >&2; exit 1; }
[[ "${ASSIGN_RETRIES}" =~ ^[1-9][0-9]*$ ]] || { echo "ERROR: COLAB_ASSIGN_RETRIES must be a positive integer" >&2; exit 1; }
[[ "${ASSIGN_BACKOFF_SECONDS}" =~ ^[0-9]+$ ]] || { echo "ERROR: COLAB_ASSIGN_BACKOFF_SECONDS must be a nonnegative integer" >&2; exit 1; }

if colab --auth oauth2 sessions 2>/dev/null | rg -F "[${SESSION_NAME}]" >/dev/null 2>&1; then
  echo "ERROR: refusing to reuse existing session ${SESSION_NAME}" >&2
  exit 2
fi

tar \
  --exclude='.git' \
  --exclude='.artifacts' \
  --exclude='evidence' \
  --exclude='**/runs' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --transform='s,^analog-digital-chip-design-eda\(/\|$\),aimc-llm-agent\1,' \
  -czf "${ARCHIVE}" \
  -C "$(dirname "${ROOT_DIR}")" "$(basename "${ROOT_DIR}")"

printf '{\n  "run_id": "%s",\n  "model_id": "%s"\n}\n' "${RUN_ID}" "${MODEL_ID}" > "${CONFIG}"

cleanup() {
  colab --auth oauth2 stop -s "${SESSION_NAME}" >/dev/null 2>&1 || true
}
trap cleanup EXIT

ASSIGN_OUTPUT=""
ASSIGN_STATUS=1
ASSIGN_ATTEMPTS=0
while [[ "${ASSIGN_ATTEMPTS}" -lt "${ASSIGN_RETRIES}" ]]; do
  ASSIGN_ATTEMPTS=$((ASSIGN_ATTEMPTS + 1))
  set +e
  CURRENT_ASSIGN_OUTPUT="$(colab --auth oauth2 new -s "${SESSION_NAME}" --gpu "${GPU_TYPE}" 2>&1)"
  CURRENT_ASSIGN_STATUS=$?
  set -e
  # Keep each attempt independently inspectable while bounding the failure
  # receipt even when the CLI emits a long traceback.
  if [[ "${#CURRENT_ASSIGN_OUTPUT}" -gt 3000 ]]; then
    CURRENT_ASSIGN_OUTPUT="...<truncated attempt prefix>...\n${CURRENT_ASSIGN_OUTPUT: -3000}"
  fi
  ASSIGN_OUTPUT+="attempt ${ASSIGN_ATTEMPTS}/${ASSIGN_RETRIES} (returncode ${CURRENT_ASSIGN_STATUS})\n${CURRENT_ASSIGN_OUTPUT}\n"
  ASSIGN_STATUS="${CURRENT_ASSIGN_STATUS}"
  if [[ "${ASSIGN_STATUS}" -eq 0 ]]; then
    break
  fi
  if [[ "${ASSIGN_ATTEMPTS}" -lt "${ASSIGN_RETRIES}" && "${ASSIGN_BACKOFF_SECONDS}" -gt 0 ]]; then
    sleep "${ASSIGN_BACKOFF_SECONDS}"
  fi
done
if [[ "${ASSIGN_STATUS}" -ne 0 ]]; then
  printf '%s\n' "${ASSIGN_OUTPUT}" >&2
  ASSIGN_OUTPUT="${ASSIGN_OUTPUT}" ASSIGN_STATUS="${ASSIGN_STATUS}" ASSIGN_ATTEMPTS="${ASSIGN_ATTEMPTS}" SESSION_NAME="${SESSION_NAME}" GPU_TYPE="${GPU_TYPE}" RUN_ID="${RUN_ID}" python3 - "${DEST}/colab-launch-failure.json" <<'PY'
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

path = Path(sys.argv[1])
payload = {
    "schema_version": "colab-launch-failure-v1",
    "status": "blocked",
    "run_id": os.environ["RUN_ID"],
    "session_name": os.environ["SESSION_NAME"],
    "gpu_type": os.environ["GPU_TYPE"],
    "assignment_returncode": int(os.environ["ASSIGN_STATUS"]),
    "assignment_attempts": int(os.environ["ASSIGN_ATTEMPTS"]),
    "assignment_output": os.environ["ASSIGN_OUTPUT"][-10000:],
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "session_created": False,
    "claim_boundary": "Colab capacity/assignment failure only; no model or verification evidence was produced.",
}
path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps({"status": payload["status"], "artifact": str(path)}, sort_keys=True))
PY
  exit "${ASSIGN_STATUS}"
fi
colab --auth oauth2 upload -s "${SESSION_NAME}" "${ARCHIVE}" /content/aimc-llm-agent.tgz
colab --auth oauth2 upload -s "${SESSION_NAME}" "${CONFIG}" /content/aimc-llm-agent-config.json
colab --auth oauth2 exec -s "${SESSION_NAME}" -f "${ROOT_DIR}/colab/run_llm_agent_benchmark.py" --timeout "${TIMEOUT_SECONDS}"
colab --auth oauth2 download -s "${SESSION_NAME}" /content/aimc-llm-agent/aimc-llm-agent-colab-summary.json "${DEST}/aimc-llm-agent-colab-summary.json"
colab --auth oauth2 download -s "${SESSION_NAME}" /content/aimc-llm-agent/.artifacts/llm-agent-benchmark-colab.json "${DEST}/llm-agent-benchmark-colab.json"
colab --auth oauth2 download -s "${SESSION_NAME}" /content/aimc-llm-agent/.artifacts/real-four-workstream-colab.json "${DEST}/real-four-workstream-colab.json"
colab --auth oauth2 download -s "${SESSION_NAME}" /content/aimc-llm-agent/.artifacts/agent-repair-heldout-colab/agent-repair-heldout-evaluation-report.json "${DEST}/agent-repair-heldout-evaluation-report.json"
colab --auth oauth2 download -s "${SESSION_NAME}" /content/aimc-llm-agent/.artifacts/aimc-mutation-case/mutation-case.json "${DEST}/aimc-mutation-case.json"

python3 - "${DEST}/llm-agent-benchmark-colab.json" <<'PY'
import json, sys
payload = json.load(open(sys.argv[1], encoding="utf-8"))
rows = payload.get("model_runs", {}).get("local-batch-command", [])
if len(rows) != 11 or any(row.get("status") != "available" or row.get("grounded") is not True or row.get("diagnosis_match") is not True or row.get("adversarial_review", {}).get("accepted") is not True for row in rows):
    raise SystemExit("downloaded model report failed the real-model acceptance contract")
aimc = payload.get("aimc_mutation_run", {})
if aimc.get("status") != "available" or aimc.get("grounded") is not True or aimc.get("diagnosis_match") is not True or aimc.get("root_cause_supported") is not True or aimc.get("adversarial_review", {}).get("accepted") is not True or aimc.get("mutation_case", {}).get("status") != "failed_baseline_observed":
    raise SystemExit("downloaded model report failed the AIMC mutation acceptance contract")
print("real-model acceptance contract passed: 11/11 cases")
print("AIMC mutation diagnosis acceptance contract passed")
repair = payload.get("aimc_mutation_repair_run", {})
if repair.get("status") != "available" or repair.get("grounded") is not True or repair.get("repair_match") is not True or repair.get("adversarial_review", {}).get("accepted") is not True:
    raise SystemExit("downloaded model report failed the AIMC repair acceptance contract")
print("AIMC model repair acceptance contract passed")
counter = payload.get("counter_repair_run", {})
if counter.get("status") != "available" or counter.get("grounded") is not True or counter.get("repair_match") is not True or counter.get("adversarial_review", {}).get("accepted") is not True:
    raise SystemExit("downloaded model report failed the seeded_counter repair acceptance contract")
print("seeded_counter model repair acceptance contract passed")
timeout = payload.get("timeout_repair_run", {})
if timeout.get("status") != "available" or timeout.get("grounded") is not True or timeout.get("repair_match") is not True or timeout.get("adversarial_review", {}).get("accepted") is not True:
    raise SystemExit("downloaded model report failed the seeded_timeout repair acceptance contract")
print("seeded_timeout model repair acceptance contract passed")
register = payload.get("register_repair_run", {})
if register.get("status") != "available" or register.get("grounded") is not True or register.get("repair_match") is not True or register.get("adversarial_review", {}).get("accepted") is not True:
    raise SystemExit("downloaded model report failed the register_peripheral repair acceptance contract")
print("register_peripheral model repair acceptance contract passed")
PY

python3 "${ROOT_DIR}/scripts/verify_llm_model_evaluation.py" \
  "${DEST}/llm-agent-benchmark-colab.json" --require-real-model

python3 "${ROOT_DIR}/scripts/check_heldout_agent_repair_evaluation.py" \
  "${DEST}/agent-repair-heldout-evaluation-report.json" --require-real-backend

python3 - "${DEST}/real-four-workstream-colab.json" <<'PY'
import json, sys
payload = json.load(open(sys.argv[1], encoding="utf-8"))
if payload.get("status") != "passed":
    raise SystemExit("real-model four-workstream pipeline did not pass")
if payload.get("claim_status") not in {"review_required", "evidence_only"}:
    raise SystemExit("real-model four-workstream pipeline has an invalid claim status")
print("real-model four-workstream pipeline acceptance contract passed")
PY

echo "Downloaded Colab LLM evidence to ${DEST}"
