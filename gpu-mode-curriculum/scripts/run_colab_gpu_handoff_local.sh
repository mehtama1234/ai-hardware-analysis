#!/usr/bin/env bash
set -euo pipefail

SESSION_NAME="${COLAB_SESSION_NAME:-gpu-mode-handoff}"
GPU_TYPE="${COLAB_GPU_TYPE:-T4}"
RUN_ID="${COLAB_RUN_ID:-colab-advanced-phase}"
TIMEOUT_SECONDS="${COLAB_TIMEOUT_SECONDS:-7200}"
STOP_AFTER="${COLAB_STOP_AFTER:-1}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ARTIFACT_DIR="${ROOT_DIR}/.artifacts/colab"
ARCHIVE="${ARTIFACT_DIR}/gpu-mode-curriculum.tgz"
CONFIG="${ARTIFACT_DIR}/colab-run-config.json"

mkdir -p "${ARTIFACT_DIR}" "${ROOT_DIR}/gpu-runs/imports"

echo "== Colab GPU handoff =="
echo "Repo: ${ROOT_DIR}"
echo "Session: ${SESSION_NAME}"
echo "GPU: ${GPU_TYPE}"
echo "Run ID: ${RUN_ID}"
echo

if ! command -v colab >/dev/null 2>&1; then
  echo "ERROR: colab CLI is not on PATH. Run scripts/bootstrap_colab_cli_auth.sh first." >&2
  exit 1
fi

echo "Packaging curriculum archive ..."
tar \
  --exclude='.git' \
  --exclude='.artifacts' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  -C "$(dirname "${ROOT_DIR}")" \
  -czf "${ARCHIVE}" \
  "$(basename "${ROOT_DIR}")"

cleanup() {
  if [[ "${STOP_AFTER}" == "1" ]]; then
    echo "Stopping Colab session ${SESSION_NAME} ..."
    colab --auth oauth2 stop -s "${SESSION_NAME}" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

echo "Starting Colab GPU session ..."
colab --auth oauth2 new -s "${SESSION_NAME}" --gpu "${GPU_TYPE}"

echo "Uploading archive ..."
printf '{\n  "run_id": "%s"\n}\n' "${RUN_ID}" > "${CONFIG}"
colab --auth oauth2 upload -s "${SESSION_NAME}" "${ARCHIVE}" /content/gpu-mode-curriculum.tgz
colab --auth oauth2 upload -s "${SESSION_NAME}" "${CONFIG}" /content/colab-run-config.json

echo "Executing remote handoff ..."
colab --auth oauth2 exec -s "${SESSION_NAME}" -f "${ROOT_DIR}/scripts/run_colab_gpu_handoff.py" --timeout "${TIMEOUT_SECONDS}"

echo "Downloading Colab artifacts ..."
colab --auth oauth2 download -s "${SESSION_NAME}" "/content/gpu-mode-curriculum/gpu-runs/imports/${RUN_ID}.json" "${ROOT_DIR}/gpu-runs/imports/${RUN_ID}.json"
colab --auth oauth2 download -s "${SESSION_NAME}" "/content/gpu-mode-curriculum/gpu-promotion/suite-run-report.json" "${ARTIFACT_DIR}/suite-run-report.json" || true
colab --auth oauth2 download -s "${SESSION_NAME}" "/content/gpu-mode-curriculum/gpu-measurement-queue/gpu-measurement-queue.json" "${ARTIFACT_DIR}/gpu-measurement-queue.json" || true
colab --auth oauth2 download -s "${SESSION_NAME}" "/content/gpu-mode-curriculum/capstone-acceptance/capstone-acceptance.json" "${ARTIFACT_DIR}/capstone-acceptance.json" || true
colab --auth oauth2 download -s "${SESSION_NAME}" "/content/gpu-mode-curriculum/colab-gpu-handoff-summary.json" "${ARTIFACT_DIR}/colab-gpu-handoff-summary.json" || true

echo
echo "Downloaded GPU run import:"
echo "  ${ROOT_DIR}/gpu-runs/imports/${RUN_ID}.json"
echo
echo "Next local verification:"
echo "  python3 scripts/build_gpu_runs.py"
echo "  python3 scripts/build_gpu_provenance.py"
echo "  python3 scripts/build_gpu_measurement_queue.py"
echo "  python3 scripts/verify_gpu_measurement_queue.py"
