#!/usr/bin/env bash
set -euo pipefail

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  echo "Usage: COLAB_SESSION_NAME=<name> COLAB_RUN_ID=<id> $0"
  echo "Creates a fresh authenticated Colab T4, runs the pinned GPT-2 profile, and downloads its receipt."
  exit 0
fi

SESSION_NAME="${COLAB_SESSION_NAME:-gpt2-sar-t4-$(date -u +%Y%m%dT%H%M%SZ)}"
RUN_ID="${COLAB_RUN_ID:-gpt2-sar-t4-$(date -u +%Y%m%dT%H%M%SZ)}"
TIMEOUT_SECONDS="${COLAB_TIMEOUT_SECONDS:-7200}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../" && pwd)"
ARTIFACT_DIR="${ROOT_DIR}/analog-in-memory-ai-inference/software-architecture/.artifacts/colab-t4"
ARCHIVE="${ARTIFACT_DIR}/${RUN_ID}.tgz"
DEST="${ROOT_DIR}/analog-in-memory-ai-inference/software-architecture/experiments/gpt2-hybrid-v1/runs/${RUN_ID}"

if ! command -v colab >/dev/null 2>&1; then
  echo "ERROR: colab CLI is not on PATH" >&2
  exit 1
fi
if colab --auth oauth2 sessions 2>/dev/null | rg -F "[${SESSION_NAME}]" >/dev/null 2>&1; then
  echo "ERROR: session already exists: ${SESSION_NAME}" >&2
  exit 2
fi
mkdir -p "${ARTIFACT_DIR}" "${DEST}"
mkdir -p "${DEST}/model-evaluation"

tar --exclude='*/.venv' --exclude='*/.data' --exclude='*/__pycache__' \
  --exclude='*.pyc' -C "$(dirname "${ROOT_DIR}")" -czf "${ARCHIVE}" \
  "$(basename "${ROOT_DIR}")/analog-in-memory-ai-inference/software-architecture/scripts" \
  "$(basename "${ROOT_DIR}")/analog-in-memory-ai-inference/software-architecture/colab" \
  "$(basename "${ROOT_DIR}")/analog-in-memory-ai-inference/software-architecture/experiments/gpt2-hybrid-v1/fixture.json" \
  "$(basename "${ROOT_DIR}")/analog-in-memory-ai-inference/software-architecture/experiments/gpt2-hybrid-v1/qualification" \
  "$(basename "${ROOT_DIR}")/analog-in-memory-ai-inference/software-architecture/experiments/gpt2-hybrid-v1/runs/20260909-recovery-projection/evaluation.json" \
  "$(basename "${ROOT_DIR}")/analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/active-converter-macro-transient" \
  "$(basename "${ROOT_DIR}")/gpu-mode-curriculum/gpu-runs/imports/colab-real-model-persistent-page-cache-long-gpt2-20260909/real-model-device-resident-arrival-load.json"

cleanup() { colab --auth oauth2 stop -s "${SESSION_NAME}" >/dev/null 2>&1 || true; }
trap cleanup EXIT
colab --auth oauth2 new -s "${SESSION_NAME}" --gpu T4
colab --auth oauth2 upload -s "${SESSION_NAME}" "${ARCHIVE}" /content/ai-hardware-analysis.tgz
colab --auth oauth2 exec -s "${SESSION_NAME}" -f "$(dirname "${BASH_SOURCE[0]}")/remote_run_t4.py" --timeout "${TIMEOUT_SECONDS}"
colab --auth oauth2 download -s "${SESSION_NAME}" /content/gpt2-sar-t4/colab-receipt.json "${DEST}/colab-receipt.json"
colab --auth oauth2 download -s "${SESSION_NAME}" /content/gpt2-sar-t4/model-evaluation/evaluation.json "${DEST}/model-evaluation/evaluation.json"
colab --auth oauth2 download -s "${SESSION_NAME}" /content/gpt2-sar-t4/model-evaluation/README.md "${DEST}/model-evaluation/README.md"
colab --auth oauth2 download -s "${SESSION_NAME}" /content/gpt2-sar-t4/model-evaluation/manifest.json "${DEST}/model-evaluation/manifest.json"
colab --auth oauth2 download -s "${SESSION_NAME}" /content/gpt2-sar-t4/workload-holdout-check.json "${DEST}/workload-holdout-check.json"
colab --auth oauth2 download -s "${SESSION_NAME}" /content/gpt2-sar-t4/profile-driven-workload-trace.json "${DEST}/profile-driven-workload-trace.json"
colab --auth oauth2 download -s "${SESSION_NAME}" /content/gpt2-sar-t4/converter-dispatch-simulation.json "${DEST}/converter-dispatch-simulation.json"
echo "Downloaded T4 receipt to ${DEST}"
