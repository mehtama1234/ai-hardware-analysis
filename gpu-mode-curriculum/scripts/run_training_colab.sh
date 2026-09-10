#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SESSION_NAME="${COLAB_SESSION_NAME:-training-capstone-$(date -u +%Y%m%dT%H%M%S)}"
DEST="${ROOT_DIR}/gpu-runs/imports/${SESSION_NAME}"
mkdir -p "${DEST}"
if colab --auth oauth2 sessions | rg -F "[${SESSION_NAME}]"; then
  echo 'Session name already exists; refusing to reuse.' >&2
  exit 2
fi
colab --auth oauth2 new -s "${SESSION_NAME}" --gpu T4
trap 'colab --auth oauth2 stop -s "${SESSION_NAME}"' EXIT
CURRICULUM="${ROOT_DIR}/fused-training-kernels"
ARCHIVE="${DEST}/training-capstone-input.tgz"
CONFIG_FILE="${DEST}/training-config.json"
cat > "${CONFIG_FILE}" <<EOF
{"steps": ${TRAINING_STEPS:-16}, "sequence": ${TRAINING_SEQUENCE:-64}, "chunk_size": ${TRAINING_CHUNK_SIZE:-16}, "load_seconds": ${TRAINING_LOAD_SECONDS:-4}, "seeds": [7, 19]}
EOF
tar -czf "${ARCHIVE}" -C "${CURRICULUM}" \
  prepare_training_data.py run_real_training.py verify_real_training.py \
  verify_checkpoint_artifacts.py build_training_decision.py \
  run_gpu_checkpoint_serving.py verify_gpu_checkpoint_serving.py \
  -C "${ROOT_DIR}/batch1-decode-vertical-slice" \
  run_continuous_load.py verify_continuous_load.py microbatch_control.py \
  run_serving_comparison.py verify_serving_comparison.py replay_serving_comparison.py \
  replay_graph_decode.py \
  -C "${CURRICULUM}" \
  fused_training_kernels/linear_cross_entropy.py fused_training_kernels/evaluation.py \
  data/tinyshakespeare.txt \
  -C "${ROOT_DIR}/batch1-decode-vertical-slice" \
  continuous_http.py continuous_service.py real_model_service.py slot_decode.py graph_decode.py \
  -C "${DEST}" training-config.json
colab --auth oauth2 upload -s "${SESSION_NAME}" "${ARCHIVE}" /content/training-capstone.tgz
colab --auth oauth2 exec -s "${SESSION_NAME}" -f "${ROOT_DIR}/scripts/run_training_colab.py" --timeout 3600 || REMOTE_STATUS=$?
REMOTE_STATUS="${REMOTE_STATUS:-0}"
colab --auth oauth2 download -s "${SESSION_NAME}" /content/training-capstone-results.tar.gz "${DEST}/training-capstone-results.tar.gz"
tar -xzf "${DEST}/training-capstone-results.tar.gz" -C "${DEST}"
echo "Evidence saved in ${DEST}"
exit "${REMOTE_STATUS}"
