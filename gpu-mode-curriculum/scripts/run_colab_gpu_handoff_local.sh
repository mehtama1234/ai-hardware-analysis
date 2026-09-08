#!/usr/bin/env bash
set -euo pipefail

SESSION_NAME="${COLAB_SESSION_NAME:-gpu-mode-handoff}"
GPU_TYPE="${COLAB_GPU_TYPE:-T4}"
RUN_ID="${COLAB_RUN_ID:-colab-advanced-phase}"
TIMEOUT_SECONDS="${COLAB_TIMEOUT_SECONDS:-7200}"
STOP_AFTER="${COLAB_STOP_AFTER:-1}"
MODE="${COLAB_HANDOFF_MODE:-full}"

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

if colab --auth oauth2 sessions 2>/dev/null | rg -F "[${SESSION_NAME}]" >/dev/null 2>&1; then
  echo "ERROR: Colab session ${SESSION_NAME} already exists; refusing to reuse another job's session." >&2
  echo "Choose COLAB_SESSION_NAME explicitly after confirming ownership." >&2
  exit 2
fi

echo "Packaging curriculum archive ..."
tar \
  --exclude='.git' \
  --exclude='.artifacts' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --transform='s,^gpu-kernels-serving-lab/,gpu-mode-curriculum/gpu-kernels-serving-lab/,' \
  -C "$(dirname "${ROOT_DIR}")" \
  -czf "${ARCHIVE}" \
  "$(basename "${ROOT_DIR}")" \
  "gpu-kernels-serving-lab/common" \
  "gpu-kernels-serving-lab/08-quantized-inference" \
  "gpu-kernels-serving-lab/13-capstone-mini-serving-engine"

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
printf '{\n  "run_id": "%s",\n  "mode": "%s"\n}\n' "${RUN_ID}" "${MODE}" > "${CONFIG}"
colab --auth oauth2 upload -s "${SESSION_NAME}" "${ARCHIVE}" /content/gpu-mode-curriculum.tgz
colab --auth oauth2 upload -s "${SESSION_NAME}" "${CONFIG}" /content/colab-run-config.json

echo "Executing remote handoff ..."
colab --auth oauth2 exec -s "${SESSION_NAME}" -f "${ROOT_DIR}/scripts/run_colab_gpu_handoff.py" --timeout "${TIMEOUT_SECONDS}"

echo "Downloading Colab artifacts ..."
if [[ "${MODE}" == "paged-kv" || "${MODE}" == "paged-attention" || "${MODE}" == "serving-tail" || "${MODE}" == "digits-quality" || "${MODE}" == "eager-kernels" || "${MODE}" == "wmma-profiler" || "${MODE}" == "batch1-decode" ]]; then
  DEST="${ROOT_DIR}/gpu-runs/imports/${RUN_ID}"
  mkdir -p "${DEST}"
  if [[ "${MODE}" == "batch1-decode" ]]; then
    REPORT_NAME="decode-comparison.json"
  elif [[ "${MODE}" == "paged-attention" ]]; then
    REPORT_NAME="paged-attention-cuda.json"
  elif [[ "${MODE}" == "serving-tail" ]]; then
    REPORT_NAME="serving-tail-load-cuda.json"
  elif [[ "${MODE}" == "digits-quality" ]]; then
    REPORT_NAME="digits-quality-cuda.json"
  elif [[ "${MODE}" == "eager-kernels" ]]; then
    REPORT_NAME="kernel-benchmark-report.json"
  elif [[ "${MODE}" == "wmma-profiler" ]]; then
    REPORT_NAME="profiler-evidence.json"
  else
    REPORT_NAME="paged-kv-cuda.json"
  fi
  if [[ "${MODE}" == "batch1-decode" ]]; then
    REPORT_DIR="batch1-decode-vertical-slice/reports"
  elif [[ "${MODE}" == "digits-quality" ]]; then
    REPORT_DIR="quantization-memory-formats/reports"
  elif [[ "${MODE}" == "eager-kernels" ]]; then
    REPORT_DIR="kernel-benchmarks/reports"
  elif [[ "${MODE}" == "wmma-profiler" ]]; then
    REPORT_DIR="tensor-core-gemm"
  else
    REPORT_DIR="model-integration/reports"
  fi
  colab --auth oauth2 download -s "${SESSION_NAME}" "/content/gpu-mode-curriculum/${REPORT_DIR}/${REPORT_NAME}" "${DEST}/${REPORT_NAME}"
  if [[ "${MODE}" == "batch1-decode" ]]; then
    colab --auth oauth2 download -s "${SESSION_NAME}" "/content/gpu-mode-curriculum/batch1-decode-vertical-slice/reports/serving-bridge.json" "${DEST}/serving-bridge.json"
  fi
else
  colab --auth oauth2 download -s "${SESSION_NAME}" "/content/gpu-mode-curriculum/gpu-runs/imports/${RUN_ID}.json" "${ROOT_DIR}/gpu-runs/imports/${RUN_ID}.json"
fi
if [[ "${MODE}" != "paged-kv" && "${MODE}" != "paged-attention" && "${MODE}" != "serving-tail" && "${MODE}" != "digits-quality" && "${MODE}" != "eager-kernels" && "${MODE}" != "wmma-profiler" && "${MODE}" != "batch1-decode" ]]; then
  colab --auth oauth2 download -s "${SESSION_NAME}" "/content/gpu-mode-curriculum/gpu-promotion/suite-run-report.json" "${ARTIFACT_DIR}/suite-run-report.json" || true
  colab --auth oauth2 download -s "${SESSION_NAME}" "/content/gpu-mode-curriculum/gpu-measurement-queue/gpu-measurement-queue.json" "${ARTIFACT_DIR}/gpu-measurement-queue.json" || true
  colab --auth oauth2 download -s "${SESSION_NAME}" "/content/gpu-mode-curriculum/capstone-acceptance/capstone-acceptance.json" "${ARTIFACT_DIR}/capstone-acceptance.json" || true
  colab --auth oauth2 download -s "${SESSION_NAME}" "/content/gpu-mode-curriculum/colab-gpu-handoff-summary.json" "${ARTIFACT_DIR}/colab-gpu-handoff-summary.json" || true
fi

echo
echo "Downloaded GPU run import:"
echo "  ${ROOT_DIR}/gpu-runs/imports/${RUN_ID}"
echo
echo "Next local verification:"
echo "  python3 scripts/build_gpu_runs.py"
echo "  python3 scripts/build_gpu_provenance.py"
echo "  python3 scripts/build_gpu_measurement_queue.py"
echo "  python3 scripts/verify_gpu_measurement_queue.py"
